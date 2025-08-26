import discord
from discord.ext import commands
from discord.commands import Option
from models.actor import Actor
from models.resource import Resource
from models.trade import Trade
from config import TRADE_CHANNEL_ID
from helpers.renderers import render_resources
from helpers.config import GUILD_ID

class TradeCmd(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[GUILD_ID], name="trade", description="Trade money and goods between actors.")
    async def trade(self, ctx: discord.ApplicationContext,
                    buyer_name:  Option(str, name="buyer",  required=False, default="Shop"),
                    seller_name: Option(str, name="seller", required=False, default="Shop"),
                    good:        Option(str, name="good",   required=False, default="Goods"),
                    platinum:    Option(int, name="platinum", required=False, default=0),
                    gold:        Option(int, name="gold",     required=False, default=0),
                    silver:      Option(int, name="silver",   required=False, default=0),
                    copper:      Option(int, name="copper",   required=False, default=0),
                    moradinium:  Option(int, name="moradinium", required=False, default=0)):
        if ctx.channel.id != TRADE_CHANNEL_ID:
            return await ctx.respond("This rite may not be invoked in this chamber.", ephemeral=True)

        await ctx.defer()
        buyer_actor = None
        if buyer_name.lower() not in ["shop","store"]:
            buyer_actor = Actor(buyer_name)
            try:
                await self.bot.loop.run_in_executor(None, buyer_actor.load_from_sheet)
            except ValueError as e:
                return await ctx.followup.send(f"Buyer error: {e}", ephemeral=True)

        seller_actor = None
        if seller_name.lower() not in ["shop","store"]:
            seller_actor = Actor(seller_name)
            try:
                await self.bot.loop.run_in_executor(None, seller_actor.load_from_sheet)
            except ValueError as e:
                return await ctx.followup.send(f"Seller error: {e}", ephemeral=True)

        price = Resource(platinum=platinum, gold=gold, silver=silver, copper=copper, moradinium=moradinium)
        trade = Trade(buyer=buyer_actor, seller=seller_actor, price=price)

        try:
            await self.bot.loop.run_in_executor(None, trade.perform_trade)
        except ValueError as e:
            return await ctx.followup.send(f"Trade failed: {e}", ephemeral=True)

        paid = ", ".join(filter(None, [
            f"{platinum}pp" if platinum else "",
            f"{gold}gp"     if gold     else "",
            f"{silver}sp"   if silver   else "",
            f"{copper}cp"   if copper   else "",
            f"{moradinium} Moradinium" if moradinium else ""
        ])) or "nothing"

        summary = ""
        if buyer_actor:
            summary = "\n\n" + render_resources(buyer_actor.resources, include_money=True, include_moradinium=True)
        elif seller_actor:
            summary = "\n\n" + render_resources(seller_actor.resources, include_money=True, include_moradinium=True)

        await ctx.followup.send(f"{buyer_name} bought '{good}' from {seller_name} for {paid}.{summary}")

def setup(bot):
    bot.add_cog(TradeCmd(bot))
