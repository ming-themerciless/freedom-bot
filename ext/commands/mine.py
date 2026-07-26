import discord
from discord.ext import commands
from discord.commands import Option
from models.actor import Actor
from config import DT_CHANNEL_ID, GUILD_ID
from helpers.renderers import render_resources
from application.actor_locks import actor_locks

class Mine(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[GUILD_ID], name="mine", description="Search for Moradinium using downtime.")
    async def mine(self, ctx: discord.ApplicationContext,
                   actor_name:        Option(str, name="character", required=True),
                   downtime:          Option(int, name="downtime", required=False, default=5)):
        if ctx.channel.id != DT_CHANNEL_ID:
            return await ctx.respond("This rite may not be invoked in this chamber.", ephemeral=True)

        await ctx.defer()
        async with actor_locks.acquire(actor_name):
            actor = Actor(actor_name)
            try:
                await self.bot.loop.run_in_executor(None, actor.load_from_sheet)
                rolls = actor.resources.mine_moradinium(
                    bot=self.bot, downtime=downtime, actor_name=actor.name
                )
                await self.bot.loop.run_in_executor(None, actor.save_to_sheet)
            except ValueError as e:
                return await ctx.followup.send(str(e), ephemeral=True)

        total = sum(r[2] for r in rolls)
        msg = (f"{actor.name} used {downtime} days of downtime and mined {total} Moradinium.\n\n"
               + render_resources(actor.resources, include_money=False, include_moradinium=True, include_downtime=True))
        await ctx.followup.send(msg)

def setup(bot):
    bot.add_cog(Mine(bot))
