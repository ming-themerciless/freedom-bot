import discord
from discord.ext import commands
from discord.commands import Option
from models.actor import Actor
from config import TRADE_CHANNEL_ID, GUILD_ID
from helpers.renderers import render_resources
from application.actor_locks import actor_locks

class Retail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[GUILD_ID], name="sale", description="Selling thing.")
    async def retail(self, ctx: discord.ApplicationContext,
                     actor_name:            Option(str, name="character", required=True),
                     item:                  Option(str, name="item", required=True),
                     crafting_cost:         Option(float, name="cost", required=True),
                     point_of_sale:         Option(str, name="point_of_sale", choices=["general store", "your own shop"], required=False, default="general store"),
                     quantity:              Option(int, name="quantity", required=False, default=1),
                     persuasion_modifier:   Option(int, name="persuasion", required=False, default=0),
                     material:              Option(int, name="material", required=False, default=0)):
        if ctx.channel.id != TRADE_CHANNEL_ID:
            return await ctx.respond("This rite may not be invoked in this chamber.", ephemeral=True)
        if crafting_cost < 0 or quantity <= 0 or material < 0:
            return await ctx.respond("Cost, quantity, and material must be non-negative (quantity must be at least 1).", ephemeral=True)
        if "shop owner" not in [r.name.lower() for r in ctx.author.roles]: point_of_sale="general store"

        await ctx.defer()
        async with actor_locks.acquire(actor_name):
            actor = Actor(actor_name)
            try:
                await self.bot.loop.run_in_executor(None, actor.load_from_sheet)
                sale_msg = actor.resources.sale(
                    bot=self.bot, item=item, persuasion_modifier=persuasion_modifier,
                    roll_mode="normal", crafting_cost=crafting_cost, quantity=quantity,
                    material=material, actor_name=actor.name, point_of_sale=point_of_sale
                )
                await self.bot.loop.run_in_executor(None, actor.save_to_sheet)
            except ValueError as e:
                return await ctx.followup.send(str(e), ephemeral=True)

        response = (f"{actor.name} has sold items " + f"{("in their emporium: ") if point_of_sale=="your own shop" else "to the general store: "}\n"
                    + f"{sale_msg}\n\n"
                    + render_resources(actor.resources, include_money=True, include_moradinium=False, include_downtime=True))
        await ctx.followup.send(response)

def setup(bot):
    bot.add_cog(Retail(bot))
