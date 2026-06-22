import discord
from discord.ext import commands
from discord.commands import Option
from models.actor import Actor
from config import DT_CHANNEL_ID, GUILD_ID
from helpers.renderers import render_resources

class LifestyleCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[GUILD_ID], name="lc", description="Pay for lifestyle weeks + expenses.")
    async def lc(self, ctx: discord.ApplicationContext,
                 actor_name: Option(str, name="character", required=True),
                 lifestyle:  Option(str, name="lifestyle", choices=["wretched","modest","comfortable","wealthy","aristocratic"], required=False, default=""),
                 weeks:      Option(int, name="weeks", required=False, default=None),
                 expenses:   Option(float, name="expenses", description="Extra expenses in silver pieces (e.g. 3.5 = 3sp 5cp)", required=False, default=0.0)):
        if ctx.channel.id != DT_CHANNEL_ID:
            return await ctx.respond("This rite may not be invoked in this chamber.", ephemeral=True)
        await ctx.defer()
        actor = Actor(actor_name)
        try:
            await self.bot.loop.run_in_executor(None, actor.load_from_sheet)
        except ValueError as e:
            return await ctx.followup.send(str(e), ephemeral=True)

        if lifestyle:
            actor.lifestyle.lifestyle_type = lifestyle.lower()

        if weeks is None:
            weeks = actor.lifestyle.living_weeks

        try:
            weeks_gp, (exp_gp, exp_sp, exp_cp) = actor.lifestyle.pay_for_weeks(
                actor_resources=actor.resources,
                weeks=weeks,
                extra_expenses_sp=expenses,
            )
            await self.bot.loop.run_in_executor(None, actor.save_to_sheet)
        except ValueError as e:
            return await ctx.followup.send(f"Error: {e}", ephemeral=True)
        
        lines = []
        if weeks > 0:
            lines.append(f"**Living Cost:** {weeks_gp} gp")

        if (exp_gp or exp_sp or exp_cp):
            exp_parts = []
            if exp_gp: exp_parts.append(f"{exp_gp} gp")
            if exp_sp: exp_parts.append(f"{exp_sp} sp")
            if exp_cp: exp_parts.append(f"{exp_cp} cp")
            lines.append("**Extra Expenses:** " + " ".join(exp_parts))

        paid_block = "\n".join(lines) if lines else "**Nothing paid.**"

        msg = (
            f"{actor.name} has paid:\n{paid_block}\n"
            f"for a {actor.lifestyle.lifestyle_type} lifestyle over {weeks} week(s).\n\n"
            + actor.resources.get_summary(include_money=True, include_moradinium=False, include_downtime=True)
        )
        await ctx.followup.send(msg)

def setup(bot):
    bot.add_cog(LifestyleCmd(bot))