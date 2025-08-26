import discord
from discord.ext import commands
from discord.commands import Option
from models.actor import Actor
from config import TRADE_CHANNEL_ID
from helpers.renderers import render_resources
from helpers.config import GUILD_ID

class Wholesale(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[GUILD_ID], name="wholesale", description="Sell items wholesale to a merchant.")
    async def wholesale(self, ctx: discord.ApplicationContext,
                        actor_name: Option(str, name="character", required=True),
                        item:       Option(str, name="item", required=True),
                        crafting_cost: Option(float, name="cost", required=True),
                        quantity:   Option(int, name="quantity", required=False, default=1),
                        persuasion_modifier: Option(int, name="persuasion", required=False, default=0),
                        haggle:     Option(bool, name="haggle", required=False, default=True),
                        roll_mode:  Option(str, name="mode", choices=["normal","advantage","disadvantage"], required=False, default="normal"),
                        reroll:     Option(int, name="reroll", required=False, default=0)):
        if ctx.channel.id != TRADE_CHANNEL_ID:
            return await ctx.respond("This rite may not be invoked in this chamber.", ephemeral=True)

        await ctx.defer()
        actor = Actor(actor_name)
        try:
            await self.bot.loop.run_in_executor(None, actor.load_from_sheet)
            sale_msg = actor.resources.wholesale_sale(
                bot=self.bot, item=item, crafting_cost=crafting_cost, quantity=quantity,
                persuasion_modifier=persuasion_modifier, roll_mode=roll_mode, reroll=reroll,
                haggle=haggle, actor_name=actor.name
            )
            await self.bot.loop.run_in_executor(None, actor.save_to_sheet)
        except ValueError as e:
            return await ctx.followup.send(str(e), ephemeral=True)

        response = (f"{actor.name} has sold items in their emporium:\n"
                    f"{sale_msg}\n\n"
                    + render_resources(actor.resources, include_money=True, include_moradinium=False, include_downtime=True))
        await ctx.followup.send(response)

def setup(bot):
    bot.add_cog(Wholesale(bot))
