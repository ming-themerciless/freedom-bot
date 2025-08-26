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
                 weeks:      Option(int, name="weeks", required=False, default=1),
                 expenses:   Option(int, name="expenses", required=False, default=0)):
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

        try:
            gp_paid, sp_paid = actor.lifestyle.pay_for_weeks(actor_resources=actor.resources, weeks=weeks, extra_expenses_sp=expenses)
            await self.bot.loop.run_in_executor(None, actor.save_to_sheet)
        except ValueError as e:
            return await ctx.followup.send(f"Error: {e}", ephemeral=True)

        msg = (f"{actor.name} has paid {gp_paid} gp" 
        + f" for a {actor.lifestyle.lifestyle_type} lifestyle"
        + (f" and {sp_paid} sp in expenses" if sp_paid else "")
        + f" over {weeks} week(s).\n\n"
        + render_resources(actor.resources, include_money=True, include_moradinium=False, include_downtime=True))
        await ctx.followup.send(msg)

def setup(bot):
    bot.add_cog(LifestyleCmd(bot))