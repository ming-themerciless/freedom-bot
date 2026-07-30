import logging
import math

import discord
from discord.ext import commands
from discord.commands import Option
from typing import Dict, Any, List

from models.actor import Actor
from models.item import Item
from application.actor_locks import locked_actor_option
from config import DT_CHANNEL_ID, GUILD_ID
from helpers.renderers import render_resources
from helpers.utils import to_currency, roll_dice
from helpers.craft_calculator import calculate_craft

logger = logging.getLogger(__name__)

# Define choices for the tool dropdown
TOOL_CHOICES = [
    "Alchemist's Supplies", "Brewer's Supplies", "Calligrapher's Supplies",
    "Carpenter's Tools", "Cartographer's Tools", "Cobbler's Tools",
    "Cook's Utensils", "Glassblower's Tools", "Herbalism Kit",
    "Jeweler's Tools", "Leatherworker's Tools", "Mason's Tools",
    "Painter's Supplies", "Poisoner's Kit", "Potter's Tools",
    "Smith's Tools", "Tinker's Tools", "Weaver's Tools",
    "Woodcarver's Tools", "Disguise Kit", "Forgery Kit",
    "Thieves' Tools"
]

class Craft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[GUILD_ID], name="craft", description="Spend downtime and gold to craft items.")
    @locked_actor_option()
    async def craft(self, ctx: discord.ApplicationContext,
                    actor_name:          Option(str, name="character", required=True, description="The name of the character crafting."),
                    item_name:           Option(str, name="item_name", required=True, description="Name of the item being crafted."),
                    rarity:              Option(str, name="rarity", choices=["standard", "common", "uncommon", "rare", "very rare", "legendary"], required=True),
                    craft_type:          Option(str, name="type", choices=["non-consumable", "consumable", "scroll", "tattoo", "poison", "brew", "meal"], required=True),
                    tool:                Option(str, name="tool", choices=TOOL_CHOICES, required=True, description="The tool being used for crafting."),
                    quantity:            Option(int, name="quantity", default=1, required=False, description="Number of items to craft."),
                    base_price:          Option(float, name="base_price", default=None, required=False, description="Price in GP of the standard item (only needed for standard rarity)."),
                    spell_level:         Option(int, name="spell_level", default=None, required=False, description="Level of the spell (0-9, required for scrolls, tattoos, and brews)."),
                    has_concentration:   Option(bool, name="has_concentration", default=False, required=False, description="Whether the brew spell has concentration (brews only)."),
                    extra_cost:          Option(float, name="extra_cost", default=0.0, required=False, description="Extra component GP cost for consumables/scrolls/tattoos/brews."),
                    is_masterpiece:      Option(bool, name="is_masterpiece", default=False, required=False, description="Set to True if this is your Masterpiece craft (costs 0 downtime)."),
                    gather_ingredients:  Option(bool, name="gather_ingredients", default=False, required=False, description="Gather ingredients yourself (doubles DT, 0 GP cost, Herbalism Kit only)."),
                    description:         Option(str, name="description", default="", required=False, description="Item description."),
                    benefits:            Option(str, name="benefits", default="", required=False, description="Item mechanical benefits."),
                    link:                Option(str, name="link", default="", required=False, description="Web link to the item."),
                    legendary_dt_spend:  Option(int, name="legendary_dt_spend", default=5, required=False, description="Downtime in days to spend on a legendary craft project.")):
        
        # Restrict command execution to the designated downtime channel
        if ctx.channel.id != DT_CHANNEL_ID:
            return await ctx.respond("This rite may not be invoked in this chamber.", ephemeral=True)

        if quantity <= 0:
            return await ctx.respond("Quantity must be at least 1.", ephemeral=True)
            
        if not math.isfinite(extra_cost) or extra_cost < 0:
            return await ctx.respond("Extra cost must be a non-negative finite number.", ephemeral=True)
        if base_price is not None and (not math.isfinite(base_price) or base_price < 0):
            return await ctx.respond("Base price must be a non-negative finite number.", ephemeral=True)

        await ctx.defer()
        actor = Actor(actor_name)
        try:
            await self.bot.loop.run_in_executor(None, actor.load_from_sheet)
        except ValueError as e:
            return await ctx.followup.send(str(e), ephemeral=True)

        # 1. Verify tool proficiency
        tool_level = actor.skills.get_current_tool_level(tool)
        if not tool_level:
            return await ctx.followup.send(f"{actor.name} is not proficient with '{tool}'.", ephemeral=True)

        # Masterpiece check for already having masterpiece (character specific validation)
        if is_masterpiece and actor.masterpiece and actor.masterpiece.strip() not in ("", "-", "None"):
            return await ctx.followup.send(f"{actor.name} already has a masterpiece: {actor.masterpiece}.", ephemeral=True)

        # 2. Perform validations and calculate costs.
        # A Master rank in *any* tool stops CRP accruing everywhere, because a
        # character may only ever master one artisan's tool (homebrew rules
        # 6.3.3.1, PDF p.17). See docs/rules/rule-catalogue.md RC-07.
        has_master_tool = any(lvl == "master" for lvl in actor.skills.crafting.values()) or \
                          any(lvl == "master" for lvl in actor.skills.tool_proficiencies.values())

        try:
            craft_result = calculate_craft(
                craft_type=craft_type,
                rarity=rarity,
                tool=tool,
                tool_level=tool_level,
                quantity=quantity,
                item_name=item_name,
                base_price=base_price,
                spell_level=spell_level,
                has_concentration=has_concentration,
                extra_cost=extra_cost,
                is_masterpiece=is_masterpiece,
                gather_ingredients=gather_ingredients,
                has_master_tool=has_master_tool
            )
        except ValueError as e:
            return await ctx.followup.send(str(e), ephemeral=True)

        gp_cost = craft_result["gp_cost"]
        moradinium_cost = craft_result["moradinium_cost"]
        dt_cost = craft_result["dt_cost"]
        is_legendary_project = craft_result["is_legendary_project"]
        earned_crp = craft_result["earned_crp"]

        # A reputation award has to land on a column W value the adapter read in
        # full, or the save would overwrite a cell it did not understand
        # (docs/discovery/sheet-inventory.md 3.2, F-S3a). Checked here, before any
        # resource is spent, so such a row is refused rather than half-applied.
        if earned_crp > 0 and not actor.skills.can_record_tool_crp():
            return await ctx.followup.send(
                f"{actor.name}'s crafting reputation could not be read from the records, so this "
                "craft cannot be recorded. Please ask the Guild Council to correct it.",
                ephemeral=True
            )

        # Validate resource availability
        if moradinium_cost > actor.resources.moradinium:
            return await ctx.followup.send(
                f"Not enough Moradinium. Requires {moradinium_cost}, has {actor.resources.moradinium}.",
                ephemeral=True
            )

        if not is_legendary_project:
            if dt_cost > actor.resources.downtime:
                return await ctx.followup.send(
                    f"Not enough downtime. Requires {dt_cost} days, has {actor.resources.downtime} days.",
                    ephemeral=True
                )

        # 3. Execute Crafting
        rolls_detail = []
        is_completed = True
        
        # Helper to clean tool name for CRP list
        tool_clean = actor.skills._clean_tool_name(tool).lower()

        if is_legendary_project:
            # Check DT spend
            if legendary_dt_spend < 5 or legendary_dt_spend % 5 != 0:
                return await ctx.followup.send("Legendary project downtime spend must be in multiples of 5 days.", ephemeral=True)
            if legendary_dt_spend > actor.resources.downtime:
                return await ctx.followup.send(f"Not enough downtime to spend {legendary_dt_spend} days.", ephemeral=True)

            # Direct lookup in the downtime progress dictionary
            project_key = f"crafting {item_name} ({tool_clean})".lower()
            active_project = actor.skills.downtime_progress.get(project_key)

            # If new project, deduct materials GP and Moradinium first
            if active_project is None:
                try:
                    gold_d, silver_d, copper_d, _ = to_currency(gp_cost)
                    actor.resources.deduct(gold=gold_d, silver=silver_d, copper=copper_d, moradinium=moradinium_cost)
                except ValueError as e:
                    return await ctx.followup.send(f"Failed to deduct crafting materials cost: {e}", ephemeral=True)
                
                # Setup new project in downtime_progress dictionary
                active_project = {
                    "percent": 0.0,
                    "level": "legendary",
                    "orig_level": "legendary",
                    "name": f"crafting {item_name} ({tool_clean})",
                    "raw": ""
                }
                actor.skills.downtime_progress[project_key] = active_project

            current_percent = active_project["percent"]

            # Perform rolls (1 d20 roll per 5 days)
            rolls_count = legendary_dt_spend // 5
            total_gained = 0
            for _ in range(rolls_count):
                results, total = roll_dice(self.bot, sides=20, rolls=1, modifier=0, roll_mode="normal", actor_name=actor.name)
                total_gained += results[0]
                rolls_detail.append(results[0])

            current_percent += total_gained
            active_project["percent"] = current_percent
            actor.resources.downtime -= legendary_dt_spend

            if current_percent >= 100.0:
                current_percent = 100.0
                is_completed = True
                # Remove from downtime progress dictionary
                actor.skills.downtime_progress.pop(project_key, None)
            else:
                is_completed = False
        else:
            # Deduct GP/Moradinium and DT
            try:
                gold_d, silver_d, copper_d, _ = to_currency(gp_cost)
                actor.resources.deduct(gold=gold_d, silver=silver_d, copper=copper_d, moradinium=moradinium_cost)
            except ValueError as e:
                return await ctx.followup.send(f"Failed to deduct currency: {e}", ephemeral=True)
            actor.resources.downtime -= dt_cost

        # 4. Apply Notable Items or Masterpiece additions (only for non-consumables on completion)
        if is_completed and craft_type == "non-consumable":
            if is_masterpiece:
                actor.masterpiece = item_name
            else:
                new_item = Item(name=item_name, description=description, benefits=benefits, link=link, rarity=rarity)
                actor.items.append(new_item)

        # 5. Apply CRP updates. Skills owns the identity rules, so that an award
        #    accumulates on the entry the Master gate reads (rules 6.3.3.1 p.17)
        #    instead of adding a second spelling of the same tool.
        if earned_crp > 0:
            try:
                actor.skills.add_tool_crp(tool, earned_crp)
            except ValueError as e:
                # Pre-checked above, so this is a record that changed shape in
                # between; nothing has been saved, so nothing is half-applied.
                interaction_id = getattr(getattr(ctx, "interaction", None), "id", "unknown")
                logger.warning(
                    "Craft reputation award refused interaction_id=%s: %s",
                    interaction_id,
                    e,
                )
                return await ctx.followup.send(
                    f"{actor.name}'s crafting reputation could not be recorded, so this craft "
                    "was not applied. Please ask the Guild Council to check the records.",
                    ephemeral=True
                )

        # 6. Save actor changes
        try:
            await self.bot.loop.run_in_executor(None, actor.save_to_sheet)
        except Exception:
            interaction_id = getattr(getattr(ctx, "interaction", None), "id", "unknown")
            logger.exception(
                "Failed to save craft result interaction_id=%s",
                interaction_id,
            )
            return await ctx.followup.send(
                "The craft could not be saved. Please try again or contact a bot administrator.",
                ephemeral=True,
            )

        # 7. Format response
        embed_item = Item(name=item_name, description=description, benefits=benefits, link=link)
        
        lines = []
        if is_legendary_project:
            # Project progress update
            lines.append(f"🛠️ **{actor.name}** spent {legendary_dt_spend} days of downtime working on the Legendary craft **{item_name}**.")
            for idx, r in enumerate(rolls_detail, start=1):
                lines.append(f"• Roll {idx}: d20({r}) -> Progress gained: +{r}%")
            
            if is_completed:
                lines.append(f"\n🎉 **Legendary Craft Complete!** '{item_name}' has been added to {actor.name}'s Notable Items.")
            else:
                lines.append(f"\nUpdated Legendary Progress: **{current_percent:.1f}%**")
        else:
            lines.append(f"🛠️ **{actor.name}** successfully crafted **{item_name}** (x{quantity})!")
            spent_str = f"• Spent: {gp_cost} GP" + (f", {moradinium_cost} Moradinium" if moradinium_cost else "") + (f", {dt_cost} days of downtime" if dt_cost else "")
            if gather_ingredients:
                spent_str += " (gathered ingredients)"
            lines.append(spent_str)
            
            if craft_type == "non-consumable":
                if is_masterpiece:
                    lines.append(f"• Saved as **Masterpiece**.")
                else:
                    lines.append(f"• Added to **Notable Items** ({rarity.title()}).")
            else:
                lines.append(f"• Consumable crafted (not added to Notable Items list).")

        if earned_crp > 0:
            lines.append(f"• Earned **+{earned_crp} CRP** in **{tool_clean.capitalize()}**.")

        lines.append("\n" + render_resources(actor.resources, include_money=True, include_moradinium=True, include_downtime=True))
        lines.append(actor.skills.get_summary())

        # If completed, send item summary
        if is_completed and (description or benefits or link):
            lines.append("\n" + embed_item.get_summary())

        await ctx.followup.send("\n".join(lines))

def setup(bot):
    bot.add_cog(Craft(bot))
