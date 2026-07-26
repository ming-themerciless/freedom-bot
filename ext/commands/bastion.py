import discord
from discord.ext import commands
from discord.commands import Option
from models.actor import Actor
from config import BASTION_CHANNEL_ID, GUILD_ID
from helpers.renderers import render_resources
from application.actor_locks import actor_locks

class BastionCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[GUILD_ID], name="bastion", description="Manage bastion upkeep and turns.")
    async def bastion(self, ctx: discord.ApplicationContext,
                      actor_name: Option(str, name="character", required=True),
                      special_facilities: Option(int, name="special_facilities", required=False, default=0)):
        if ctx.channel.id != BASTION_CHANNEL_ID:
            return await ctx.respond("This ritual may only be performed in the #bastion-turns chamber.", ephemeral=True)

        await ctx.defer()
        async with actor_locks.acquire(actor_name):
            actor = Actor(actor_name)
            try:
                await self.bot.loop.run_in_executor(None, actor.load_from_sheet)
            except ValueError as e:
                return await ctx.followup.send(str(e), ephemeral=True)

            bastion = actor.lifestyle.bastion
            if bastion.bastion_flag == 0:
                return await ctx.followup.send(f"{actor.name} does not yet command a bastion.", ephemeral=True)

            try:
                cost = bastion.maintain_bastion(actor_resources=actor.resources, level=actor.level, special_facilities=special_facilities)
                await self.bot.loop.run_in_executor(None, actor.save_to_sheet)
            except ValueError as e:
                return await ctx.followup.send(str(e), ephemeral=True)

        msg = (f"{actor.name} has expended **{cost} gp** to maintain the bastion.\n"
               "Bastion upkeep is complete; a turn now lies before you.\n\n"
               + render_resources(actor.resources, include_money=True, include_moradinium=False))
        await ctx.followup.send(msg)

def setup(bot):
    bot.add_cog(BastionCmd(bot))
