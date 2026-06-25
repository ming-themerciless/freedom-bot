import discord
from discord.ext import commands
from discord.commands import Option
from typing import Dict, Any, List

from models.actor import Actor
from models.item import Item
from config import DT_CHANNEL_ID, GUILD_ID
from helpers.renderers import render_resources
from helpers.utils import to_currency, roll_dice

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

# Poisons table from PDF page 24-25
POISON_TABLE = {
    "assassin's blood": {"gp": 75, "j": 1.0, "e": 0.5, "m": 0.25},
    "truth serum": {"gp": 75, "j": 1.0, "e": 0.5, "m": 0.25},
    "carrion crawler mucus": {"gp": 100, "j": 1.0, "e": 0.5, "m": 0.25},
    "lolth's sting": {"gp": 100, "j": 1.0, "e": 0.5, "m": 0.25},
    "serpent venom": {"gp": 100, "j": 2.0, "e": 1.0, "m": 0.5},
    "malice": {"gp": 125, "j": 2.0, "e": 1.0, "m": 0.5},
    "pale tincture": {"gp": 125, "j": 2.0, "e": 1.0, "m": 0.5},
    "essence of ether": {"gp": 150, "j": 2.0, "e": 1.0, "m": 0.5},
    "biza's breath": {"gp": 200, "j": None, "e": 2.0, "m": 1.0},
    "oil of taggit": {"gp": 200, "j": None, "e": 2.0, "m": 1.0},
    "burnt othur fumes": {"gp": 250, "j": None, "e": 2.0, "m": 1.0},
    "torpor": {"gp": 300, "j": None, "e": 2.0, "m": 1.0},
    "wyvern poison": {"gp": 600, "j": None, "e": None, "m": 2.0},
    "midnight tears": {"gp": 750, "j": None, "e": None, "m": 2.5},
    "yserthrax's corruption": {"gp": 750, "j": None, "e": None, "m": 2.5},
    "purple worm poison": {"gp": 1500, "j": None, "e": None, "m": 3.0}
}

# Spell Scrolls & Tattoos table from PDF page 23-24
SCROLL_TATTOO_TABLE = {
    0: {"j": 1.0, "e": 0.5, "m": 0.25, "tattoo": 40, "scroll": 25},
    1: {"j": 2.0, "e": 1.0, "m": 0.5,  "tattoo": 60, "scroll": 40},
    2: {"j": None, "e": 1.5, "m": 1.0, "tattoo": 80, "scroll": 50},
    3: {"j": None, "e": 2.0, "m": 1.5, "tattoo": 150, "scroll": 100},
    4: {"j": None, "e": None, "m": 2.0, "tattoo": 300, "scroll": 200},
    5: {"j": None, "e": None, "m": 3.0, "tattoo": 450, "scroll": 300},
    6: {"j": None, "e": None, "m": 5.0, "tattoo": None, "scroll": 400},
    7: {"j": None, "e": None, "m": 10.0, "tattoo": None, "scroll": 600},
    8: {"j": None, "e": None, "m": 15.0, "tattoo": None, "scroll": 1000},
    9: {"j": None, "e": None, "m": 20.0, "tattoo": None, "scroll": 2000}
}

# Brews table from PDF page 27
# Key: (spell_level, has_concentration)
BREW_TABLE = {
    (0, False): {"j": 0.5, "e": 0.25, "m": 0.125, "gp": 25},
    (0, True):  {"j": 1.0, "e": 0.5,  "m": 0.25,  "gp": 30},
    (1, False): {"j": 2.0, "e": 1.0,  "m": 0.5,   "gp": 40},
    (1, True):  {"j": None, "e": 1.5, "m": 1.0,   "gp": 50},
    (2, False): {"j": None, "e": 2.0, "m": 1.5,   "gp": 100},
    (2, True):  {"j": None, "e": None, "m": 2.0,   "gp": 200},
    (3, False): {"j": None, "e": None, "m": 3.0,   "gp": 300}
}

class Craft(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[GUILD_ID], name="craft", description="Spend downtime and gold to craft items.")
    async def craft(self, ctx: discord.ApplicationContext,
                    actor_name:          Option(str, name="character", required=True, description="The name of the character crafting."),
                    item_name:           Option(str, name="item_name", required=True, description="Name of the item being crafted."),
                    rarity:              Option(str, name="rarity", choices=["standard", "common", "uncommon", "rare", "very rare", "legendary"], required=True),
                    craft_type:          Option(str, name="type", choices=["non-consumable", "consumable", "scroll", "tattoo", "poison", "brew"], required=True),
                    tool:                Option(str, name="tool", choices=TOOL_CHOICES, required=True, description="The tool being used for crafting."),
                    quantity:            Option(int, name="quantity", default=1, required=False, description="Number of items to craft."),
                    base_price:          Option(float, name="base_price", default=None, required=False, description="Price in GP of the standard item (only needed for standard rarity)."),
                    spell_level:         Option(int, name="spell_level", default=None, required=False, description="Level of the spell (0-9, required for scrolls, tattoos, and brews)."),
                    has_concentration:   Option(bool, name="has_concentration", default=False, required=False, description="Whether the brew spell has concentration (brews only)."),
                    extra_cost:          Option(float, name="extra_cost", default=0.0, required=False, description="Extra component GP cost for consumables/scrolls/tattoos/brews."),
                    is_masterpiece:      Option(bool, name="is_masterpiece", default=False, required=False, description="Set to True if this is your Masterpiece craft (costs 0 downtime)."),
                    description:         Option(str, name="description", default="", required=False, description="Item description."),
                    benefits:            Option(str, name="benefits", default="", required=False, description="Item mechanical benefits."),
                    link:                Option(str, name="link", default="", required=False, description="Web link to the item."),
                    legendary_dt_spend:  Option(int, name="legendary_dt_spend", default=5, required=False, description="Downtime in days to spend on a legendary craft project.")):
        
        # Restrict command execution to the designated downtime channel
        if ctx.channel.id != DT_CHANNEL_ID:
            return await ctx.respond("This rite may not be invoked in this chamber.", ephemeral=True)

        if quantity <= 0:
            return await ctx.respond("Quantity must be at least 1.", ephemeral=True)
            
        if extra_cost < 0:
            return await ctx.respond("Extra cost cannot be negative.", ephemeral=True)

        if rarity == "standard" and base_price is None:
            return await ctx.respond("Base price must be specified when crafting a standard item.", ephemeral=True)

        if craft_type in ("scroll", "tattoo", "brew") and spell_level is None:
            return await ctx.respond("Spell level must be specified for scrolls, tattoos, and brews.", ephemeral=True)

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

        tool_level_abbr = {"journeyman": "j", "expert": "e", "master": "m"}.get(tool_level, tool_level)

        # 2. Check if tool level matches rarity requirements
        rarity_allowed = {
            "journeyman": ["standard", "common"],
            "expert": ["standard", "common", "uncommon"],
            "master": ["standard", "common", "uncommon", "rare", "very rare", "legendary"]
        }
        if rarity not in rarity_allowed.get(tool_level, []):
            return await ctx.followup.send(
                f"{tool_level.capitalize()} level with {tool} is insufficient to craft a {rarity} item. Requires higher proficiency.",
                ephemeral=True
            )

        # 3. Masterpiece validations
        if is_masterpiece:
            if tool_level != "master":
                return await ctx.followup.send("You must have Master level in the tool to craft a Masterpiece.", ephemeral=True)
            if actor.masterpiece and actor.masterpiece.strip() not in ("", "-", "None"):
                return await ctx.followup.send(f"{actor.name} already has a masterpiece: {actor.masterpiece}.", ephemeral=True)
            if craft_type != "non-consumable":
                return await ctx.followup.send("Masterpieces must be non-consumable items.", ephemeral=True)

        # 4. Cost and Downtime calculation
        gp_cost = 0.0
        moradinium_cost = 0
        dt_cost = 0.0
        is_legendary_project = (rarity == "legendary" and craft_type == "non-consumable")

        if is_legendary_project:
            gp_cost = 100000.0 * quantity
            moradinium_cost = 256 * quantity
            # DT cost is not fixed; handled via roll progression below
        else:
            # Consumable vs Non-Consumable rules
            if craft_type == "non-consumable":
                if rarity == "standard":
                    gp_cost = (base_price / 2.0) * quantity
                    dt_div = {"journeyman": 10.0, "expert": 25.0, "master": 75.0}[tool_level]
                    dt_cost = (base_price / dt_div) * quantity
                elif rarity == "common":
                    gp_cost = 50.0 * quantity
                    moradinium_cost = 1 * quantity
                    dt_cost = {"journeyman": 5.0, "expert": 3.0, "master": 1.0}[tool_level] * quantity
                elif rarity == "uncommon":
                    gp_cost = 200.0 * quantity
                    moradinium_cost = 4 * quantity
                    dt_cost = {"expert": 5.0, "master": 3.0}[tool_level] * quantity
                elif rarity == "rare":
                    gp_cost = 2000.0 * quantity
                    moradinium_cost = 16 * quantity
                    dt_cost = 5.0 * quantity
                elif rarity == "very rare":
                    gp_cost = 20000.0 * quantity
                    moradinium_cost = 64 * quantity
                    dt_cost = 20.0 * quantity
            elif craft_type == "consumable":
                if rarity == "standard":
                    gp_cost = (base_price / 2.0) * quantity + extra_cost
                    dt_div = {"journeyman": 25.0, "expert": 50.0, "master": 100.0}[tool_level]
                    dt_cost = (base_price / dt_div) * quantity
                elif rarity == "common":
                    gp_cost = 25.0 * quantity + extra_cost
                    dt_cost = {"journeyman": 1.0, "expert": 0.5, "master": 0.25}[tool_level] * quantity
                elif rarity == "uncommon":
                    gp_cost = 50.0 * quantity + extra_cost
                    dt_cost = {"expert": 1.0, "master": 0.5}[tool_level] * quantity
                elif rarity == "rare":
                    gp_cost = 200.0 * quantity + extra_cost
                    dt_cost = 1.0 * quantity
                elif rarity == "very rare":
                    gp_cost = 400.0 * quantity + extra_cost
                    dt_cost = 5.0 * quantity
                elif rarity == "legendary":
                    gp_cost = 1000.0 * quantity + extra_cost
                    dt_cost = 20.0 * quantity
            elif craft_type in ("scroll", "tattoo"):
                # Enforce appropriate tool for scrolls and tattoos
                if craft_type == "scroll" and "calligrapher" not in tool.lower():
                    return await ctx.followup.send("Scrolls require Calligrapher's Supplies.", ephemeral=True)
                if craft_type == "tattoo" and "painter" not in tool.lower():
                    return await ctx.followup.send("Spellwrought Tattoos require Painter's Supplies.", ephemeral=True)

                level_data = SCROLL_TATTOO_TABLE.get(spell_level)
                if not level_data:
                    return await ctx.followup.send(f"Invalid spell level {spell_level}.", ephemeral=True)
                
                # Check if this type (tattoo) is available for this spell level
                item_base_gp = level_data.get(craft_type)
                if item_base_gp is None:
                    return await ctx.followup.send(f"Cannot craft a {craft_type} of spell level {spell_level}.", ephemeral=True)
                
                dt_per_item = level_data.get(tool_level_abbr)
                if dt_per_item is None:
                    return await ctx.followup.send(
                        f"Your level {tool_level} is insufficient to craft a {spell_level}-level {craft_type}.",
                        ephemeral=True
                    )
                
                gp_cost = float(item_base_gp) * quantity + extra_cost
                dt_cost = float(dt_per_item) * quantity
            elif craft_type == "brew":
                # Check brewer supplies
                if "brewer" not in tool.lower():
                    return await ctx.followup.send("Brews require Brewer's Supplies.", ephemeral=True)
                
                level_data = BREW_TABLE.get((spell_level, has_concentration))
                if not level_data:
                    return await ctx.followup.send(
                        f"No brew recipe found for spell level {spell_level} (concentration: {has_concentration}).",
                        ephemeral=True
                    )
                
                dt_per_item = level_data.get(tool_level_abbr)
                if dt_per_item is None:
                    return await ctx.followup.send(
                        f"Your level {tool_level} is insufficient to brew a {spell_level}-level spell (concentration: {has_concentration}).",
                        ephemeral=True
                    )
                
                gp_cost = float(level_data["gp"]) * quantity + extra_cost
                dt_cost = float(dt_per_item) * quantity
            elif craft_type == "poison":
                # Check poisoner kit or similar
                clean_item = item_name.strip().lower()
                poison_data = POISON_TABLE.get(clean_item)
                if not poison_data:
                    # Fallback to standard consumable calculation if item name is custom
                    # Determine rarity category first
                    if rarity == "common":
                        gp_cost = 25.0 * quantity + extra_cost
                        dt_cost = {"journeyman": 1.0, "expert": 0.5, "master": 0.25}[tool_level] * quantity
                    elif rarity == "uncommon":
                        gp_cost = 50.0 * quantity + extra_cost
                        dt_cost = {"expert": 1.0, "master": 0.5}[tool_level] * quantity
                    elif rarity == "rare":
                        gp_cost = 200.0 * quantity + extra_cost
                        dt_cost = 1.0 * quantity
                    elif rarity == "very rare":
                        gp_cost = 400.0 * quantity + extra_cost
                        dt_cost = 5.0 * quantity
                    elif rarity == "legendary":
                        gp_cost = 1000.0 * quantity + extra_cost
                        dt_cost = 20.0 * quantity
                    else:  # standard
                        gp_cost = (base_price / 2.0) * quantity + extra_cost
                        dt_div = {"journeyman": 25.0, "expert": 50.0, "master": 100.0}[tool_level]
                        dt_cost = (base_price / dt_div) * quantity
                else:
                    dt_per_item = poison_data.get(tool_level_abbr)
                    if dt_per_item is None:
                        return await ctx.followup.send(
                            f"Your level {tool_level} is insufficient to craft poison '{item_name}'.",
                            ephemeral=True
                        )
                    gp_cost = float(poison_data["gp"]) * quantity + extra_cost
                    dt_cost = float(dt_per_item) * quantity

        # Override DT for masterpieces
        if is_masterpiece:
            dt_cost = 0.0

        # Validate resource availability
        if int(gp_cost) > 0:
            # We want to check GP deduction. Since deduct accepts coins, we check if they have enough
            # We will catch ValueError inside deduct if they lack money
            pass
        if moradinium_cost > actor.resources.moradinium:
            return await ctx.followup.send(
                f"Not enough Moradinium. Requires {moradinium_cost}, has {actor.resources.moradinium}.",
                ephemeral=True
            )

        if not is_legendary_project:
            # Validate DT availability
            # Note: dt_cost can be fractional, but sheet stores floats, so it's fine.
            # However, validate_downtime checks multiples of 5, which applies to study rolls.
            # Standard crafting consumes DT directly. We just check if they have enough DT.
            if dt_cost > actor.resources.downtime:
                return await ctx.followup.send(
                    f"Not enough downtime. Requires {dt_cost} days, has {actor.resources.downtime} days.",
                    ephemeral=True
                )

        # 5. Execute Crafting
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
                    actor.resources.deduct(gold=int(gp_cost), moradinium=moradinium_cost)
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
                actor.resources.deduct(gold=int(gp_cost), moradinium=moradinium_cost)
            except ValueError as e:
                return await ctx.followup.send(f"Failed to deduct currency: {e}", ephemeral=True)
            actor.resources.downtime -= dt_cost

        # 6. Apply Notable Items or Masterpiece additions (only for non-consumables on completion)
        if is_completed and craft_type == "non-consumable":
            if is_masterpiece:
                actor.masterpiece = item_name
            else:
                new_item = Item(name=item_name, description=description, benefits=benefits, link=link, rarity=rarity)
                actor.items.append(new_item)

        # 7. Apply CRP updates
        has_master_tool = any(lvl == "master" for lvl in actor.skills.crafting.values()) or \
                          any(lvl == "master" for lvl in actor.skills.tool_proficiencies.values())

        earned_crp = 0.0
        if not has_master_tool:
            if rarity == "common":
                if craft_type == "non-consumable":
                    earned_crp = 2.5 * quantity
                else:
                    earned_crp = 0.5 * quantity
            elif rarity == "uncommon":
                if craft_type == "non-consumable":
                    earned_crp = 7.5 * quantity
                else:
                    earned_crp = 1.5 * quantity

        if earned_crp > 0:
            current_crp = actor.skills.crp_dict.get(tool_clean, 0.0)
            new_crp = current_crp + earned_crp
            actor.skills.crp_dict[tool_clean] = int(new_crp) if new_crp.is_integer() else new_crp
            actor.skills.crp_modified = True

        # 8. Save actor changes
        try:
            await self.bot.loop.run_in_executor(None, actor.save_to_sheet)
        except Exception as e:
            return await ctx.followup.send(f"Failed to save actor data to Google Sheet: {e}", ephemeral=True)

        # 9. Format response
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
            lines.append(f"• Spent: {gp_cost} GP" + (f", {moradinium_cost} Moradinium" if moradinium_cost else "") + (f", {dt_cost} days of downtime" if dt_cost else ""))
            
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
