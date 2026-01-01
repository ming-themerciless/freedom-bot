import discord
from discord.ext import commands
from discord.commands import Option
from models.actor import Actor
from config import DT_CHANNEL_ID, GUILD_ID
from helpers.renderers import render_resources

class Work(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[GUILD_ID], name="work", description="Earning money using your tool proficiencies and downtime.")
    async def work(self, ctx: discord.ApplicationContext,
                   actor_name:  Option(str, name="character", required=True),
                   tool:        Option(str, name="tool", required=False, default="Instrument"),
                   modifier:    Option(int, name="modifier", required=False, default=0),
                   downtime:    Option(int, name="downtime", required=False, default=5),
                   roll_mode:   Option(str, name="roll_mode", choices=["normal","advantage","disadvantage"], required=False, default="normal")):
        if ctx.channel.id != DT_CHANNEL_ID:
            return await ctx.respond("This rite may not be invoked in this chamber.", ephemeral=True)

        await ctx.defer()
        actor = Actor(actor_name)
        try:
            await self.bot.loop.run_in_executor(None, actor.load_from_sheet)
            rolls = actor.resources.earn_money(
                bot=self.bot, downtime=downtime, modifier=modifier,
                roll_mode=roll_mode, actor_name=actor.name
            )
            await self.bot.loop.run_in_executor(None, actor.save_to_sheet)
        except ValueError as e:
            return await ctx.followup.send(str(e), ephemeral=True)

        total = sum(r[2] for r in rolls)
        msg = (f"{actor.name} used {downtime} days of downtime and earned {total} Gold while using the tool: {tool}.\n\n"
               + render_resources(actor.resources, include_money=True, include_moradinium=False, include_downtime=True))
        await ctx.followup.send(msg)

def setup(bot):
    bot.add_cog(Work(bot))
