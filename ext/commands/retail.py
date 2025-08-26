import discord
from discord.ext import commands
from discord.commands import Option
from models.actor import Actor
from config import TRADE_CHANNEL_ID
from helpers.renderers import render_resources
from helpers.config import GUILD_ID

class Retail(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[GUILD_ID], name="retail", description="Sell crafted items in your shop.")
    async def retail(self, ctx: discord.ApplicationContext,
                     actor_name: Option(str, name="character", required=True),
                     item:       Option(str, name="item", required=True),
                     crafting_cost: Option(float, name="cost", required=True),
                     quantity:   Option(int, name="quantity", required=False, default=1),
                     downtime:   Option(int, name="downtime", required=False, default=1),
                     persuasion_modifier: Option(int, name="persuasion", required=False, default=0),
                     material:   Option(int, name="material", required=False, default=0),
                     roll_mode:  Option(str, name="mode", choices=["normal","advantage","disadvantage"], required=False, default="normal"),
                     reroll:     Option(int, name="reroll", required=False, default=0)):
        if ctx.channel.id != TRADE_CHANNEL_ID:
            return await ctx.respond("This rite may not be invoked in this chamber.", ephemeral=True)
        if "shop owner" not in [r.name.lower() for r in ctx.author.roles]:
            return await ctx.respond("You must bear the Shop Owner sigil to cast this invocation.", ephemeral=True)

        await ctx.defer()
        actor = Actor(actor_name)
        try:
            await self.bot.loop.run_in_executor(None, actor.load_from_sheet)
            sale_msg = actor.resources.retail_sale(
                bot=self.bot, item=item, downtime=downtime, persuasion_modifier=persuasion_modifier,
                roll_mode=roll_mode, reroll=reroll, crafting_cost=crafting_cost, quantity=quantity,
                material=material, actor_name=actor.name
            )
            await self.bot.loop.run_in_executor(None, actor.save_to_sheet)
        except ValueError as e:
            return await ctx.followup.send(str(e), ephemeral=True)

        response = (f"{actor.name} has sold items in their emporium:\n"
                    f"{sale_msg}\n\n"
                    + render_resources(actor.resources, include_money=True, include_moradinium=False, include_downtime=True))
        await ctx.followup.send(response)

def setup(bot):
    bot.add_cog(Retail(bot))
