import logging

import discord
from discord.ext import commands
from discord.commands import Option

from application.actor_locks import locked_actor_option
from models.actor import Actor
from models.exchange import calculate_exchange
from config import TRADE_CHANNEL_ID, GUILD_ID
from helpers.renderers import render_resources

logger = logging.getLogger(__name__)

class XChange(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[GUILD_ID], name="xchange", description="Exchange currency between denominations.")
    @locked_actor_option()
    async def xchange(self, ctx: discord.ApplicationContext,
                      actor_name: Option(str, name="character", required=True, description="The name of the character exchanging."),
                      from_denom: Option(str, name="from_denomination", choices=["pp", "gp", "sp", "cp"], required=True, description="The denomination you want to change."),
                      amount:     Option(int, name="amount", required=True, description="The amount of coins you want to change."),
                      to_denom:   Option(str, name="to_denomination", choices=["pp", "gp", "sp", "cp"], required=True, description="The destination denomination.")):
        
        # Restrict command execution to the trade channel
        if ctx.channel.id != TRADE_CHANNEL_ID:
            return await ctx.respond("This rite may not be invoked in this chamber.", ephemeral=True)

        if amount <= 0:
            return await ctx.respond("Amount must be a positive integer.", ephemeral=True)

        if from_denom == to_denom:
            return await ctx.respond(f"Cannot exchange {from_denom.upper()} to itself.", ephemeral=True)

        await ctx.defer()
        actor = Actor(actor_name)
        try:
            await self.bot.loop.run_in_executor(None, actor.load_from_sheet)
        except ValueError as e:
            return await ctx.followup.send(str(e), ephemeral=True)

        current_wallet = {
            "platinum": actor.resources.platinum,
            "gold": actor.resources.gold,
            "silver": actor.resources.silver,
            "copper": actor.resources.copper
        }

        try:
            net_changes = calculate_exchange(
                from_denomination=from_denom,
                to_denomination=to_denom,
                amount=amount,
                current_wallet=current_wallet
            )
        except ValueError as e:
            return await ctx.followup.send(str(e), ephemeral=True)

        # Apply net changes
        actor.resources.platinum += net_changes["platinum"]
        actor.resources.gold += net_changes["gold"]
        actor.resources.silver += net_changes["silver"]
        actor.resources.copper += net_changes["copper"]

        # Save actor changes
        try:
            await self.bot.loop.run_in_executor(None, actor.save_to_sheet)
        except Exception:
            interaction_id = getattr(getattr(ctx, "interaction", None), "id", "unknown")
            logger.exception(
                "Failed to save currency exchange interaction_id=%s",
                interaction_id,
            )
            return await ctx.followup.send(
                "The currency exchange could not be saved. Please try again or contact a bot administrator.",
                ephemeral=True,
            )

        # Format output summary
        lines = []
        lines.append(f"🛠️ **{actor.name}** exchanged **{amount} {from_denom.upper()}** to **{to_denom.upper()}**.")
        
        # Detail changes
        details = []
        if net_changes["platinum"] != 0:
            sign = "+" if net_changes["platinum"] > 0 else ""
            details.append(f"{sign}{net_changes['platinum']} pp")
        if net_changes["gold"] != 0:
            sign = "+" if net_changes["gold"] > 0 else ""
            details.append(f"{sign}{net_changes['gold']} gp")
        if net_changes["silver"] != 0:
            sign = "+" if net_changes["silver"] > 0 else ""
            details.append(f"{sign}{net_changes['silver']} sp")
        if net_changes["copper"] != 0:
            sign = "+" if net_changes["copper"] > 0 else ""
            details.append(f"{sign}{net_changes['copper']} cp")

        lines.append(f"• Changes applied: {', '.join(details)}")
        lines.append("\n" + render_resources(actor.resources, include_money=True, include_moradinium=True, include_downtime=True))

        await ctx.followup.send("\n".join(lines))

def setup(bot):
    bot.add_cog(XChange(bot))
