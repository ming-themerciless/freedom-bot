import discord
from discord.ext import commands
from discord.commands import Option
from models.actor import Actor
from helpers.renderers import render_actor_summary
from config import GUILD_ID

class Info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[GUILD_ID], name="info", description="Show character summary.")
    async def info(self, ctx: discord.ApplicationContext,
                   actor_name: Option(str, name="character", required=True)):
        await ctx.defer()
        actor = Actor(actor_name)
        try:
            await self.bot.loop.run_in_executor(None, actor.load_from_sheet)
        except ValueError as e:
            return await ctx.followup.send(str(e), ephemeral=True)
        await ctx.followup.send(render_actor_summary(actor))

def setup(bot):
    bot.add_cog(Info(bot))
