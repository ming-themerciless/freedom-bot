import discord
from discord.ext import commands
from discord.commands import Option
from application.actor_locks import locked_actor_option
from models.actor import Actor
from config import DT_CHANNEL_ID, GUILD_ID
from helpers.renderers import render_resources

class Learn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[GUILD_ID], name="learn", description="Spend downtime and gold to learn a tool, language, or weapon proficiency.")
    @locked_actor_option()
    async def learn(self, ctx: discord.ApplicationContext,
                    actor_name: Option(str, name="character", required=True, description="The name of the character learning."),
                    modifier:   Option(int, name="modifier", required=True, description="The ability score modifier to add to the rolls."),
                    downtime:   Option(int, name="downtime", required=False, default=5, description="The downtime in days to spend (must be a multiple of 5)."),
                    gp_cost:    Option(int, name="gp_cost", required=False, default=None, description="Override the automatic GP cost per roll."),
                    tool:       Option(str, name="tool", required=False, default=None, choices=[
                        "Alchemist's Supplies", "Brewer's Supplies", "Calligrapher's Supplies",
                        "Carpenter's Tools", "Cartographer's Tools", "Cobbler's Tools",
                        "Cook's Utensils", "Glassblower's Tools", "Herbalism Kit",
                        "Jeweler's Tools", "Leatherworker's Tools", "Mason's Tools",
                        "Painter's Supplies", "Poisoner's Kit", "Potter's Tools",
                        "Smith's Tools", "Tinker's Tools", "Weaver's Tools",
                        "Woodcarver's Tools", "Disguise Kit", "Forgery Kit",
                        "Thieves' Tools", "Scroll Proficiency"
                    ], description="Select a predefined tool to learn (automatically determines next level)."),
                    language:   Option(str, name="language", required=False, default=None, choices=[
                        "Abyssal", "Celestial", "Common", "Common Sign Language", "Deep Speech",
                        "Draconic", "Druidic", "Dwarvish", "Elvish", "Giant", "Gnomish", "Goblin",
                        "Halfling", "Infernal", "Orc", "Primordial", "Sylvan", "Thieves' Cant",
                        "Undercommon"
                    ], description="Select a predefined language to learn."),
                    new_target: Option(str, name="new_target", required=False, default=None, description="Specify what you want to learn if starting a new target (not in the tool or language dropdown)."),
                    new_type:   Option(str, name="new_type", required=False, default=None, choices=["language", "instrument", "gaming set", "martial weapon", "weapon mastery", "vehicle"], description="Select the type if starting a custom non-tool target."),
                    roll_mode:  Option(str, name="roll_mode", choices=["normal","advantage","disadvantage"], required=False, default="normal", description="Select roll mode.")):
        """
        Slash command to spend downtime in 5-day increments, perform learning checks, and update the character sheet.
        """
        # Restrict command execution to the designated downtime channel
        if ctx.channel.id != DT_CHANNEL_ID:
            return await ctx.respond("This rite may not be invoked in this chamber.", ephemeral=True)

        # Validate downtime increments
        if downtime < 5 or downtime % 5 != 0:
            return await ctx.respond("Downtime must be spent in increments of five days.", ephemeral=True)
        if gp_cost is not None and gp_cost < 0:
            return await ctx.respond("GP cost override cannot be negative.", ephemeral=True)

        # Predefined tool, language and custom target name are mutually exclusive
        targets_specified = sum(1 for x in [tool, language, new_target] if x is not None)
        if targets_specified > 1:
            return await ctx.respond("Please select at most one of 'tool', 'language', or 'new_target'.", ephemeral=True)

        if language:
            new_target = language
            new_type = "language"

        await ctx.defer()
        actor = Actor(actor_name)
        try:
            # Load character data from the Google Sheet
            await self.bot.loop.run_in_executor(None, actor.load_from_sheet)
            
            # Execute learning rolls, deducting downtime and gold and adjusting sheets data
            rolls, spent_dt, spent_gp, target_name, target_level = actor.skills.learn_proficiency(
                actor=actor,
                bot=self.bot,
                ability_modifier=modifier,
                downtime=downtime,
                gp_cost_override=gp_cost,
                tool=tool,
                new_target=new_target,
                new_type=new_type,
                roll_mode=roll_mode
            )
            
            # Save updated data back to sheet
            await self.bot.loop.run_in_executor(None, actor.save_to_sheet)
        except ValueError as e:
            return await ctx.followup.send(str(e), ephemeral=True)

        # Construct and format a rich Discord response detailing the learning rolls
        lines = []
        target_desc = f"{target_name} ({target_level})"
        lines.append(f"**{actor.name}** spent {spent_dt} days of downtime and {spent_gp} GP studying **{target_desc}**.\n")
        
        for idx, r in enumerate(rolls, start=1):
            nat20_str = " (Natural 20! +1% bonus)" if r["nat_20"] else ""
            lines.append(f"• Roll {idx}: d20({r['roll']}) + {r['modifier']} = {r['total']}{nat20_str} -> Progress: {r['new_percent']}%")

        if rolls and rolls[-1]["new_percent"] >= 100:
            lines.append(f"\n🎉 **{actor.name} has successfully completed learning {target_desc}!**")

        if actor.skills.downtime_progress not in ("", "-", "None"):
            lines.append(f"\nRemaining Progress: **{actor.skills.downtime_progress}**")

        # Show updated resources summary
        lines.append("\n" + render_resources(actor.resources, include_money=True, include_moradinium=False, include_downtime=True))

        await ctx.followup.send("\n".join(lines))

def setup(bot):
    bot.add_cog(Learn(bot))
