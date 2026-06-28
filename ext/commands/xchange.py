import discord
from discord.ext import commands
from discord.commands import Option
from typing import Dict, Any

from models.actor import Actor
from config import TRADE_CHANNEL_ID, GUILD_ID
from helpers.renderers import render_resources

RATES_IN_COPPER = {
    "pp": 1000,
    "gp": 100,
    "sp": 10,
    "cp": 1
}

DENOM_ATTRS = {
    "pp": "platinum",
    "gp": "gold",
    "sp": "silver",
    "cp": "copper"
}

def perform_exchange_calculation(
    from_denom: str,
    to_denom: str,
    amount: int,
    current_wallet: Dict[str, int]
) -> Dict[str, int]:
    """
    Computes the net changes for each denomination.
    Raises ValueError on validation failures.
    """
    from_denom = from_denom.strip().lower()
    to_denom = to_denom.strip().lower()

    if amount <= 0:
        raise ValueError("Amount must be a positive integer.")
    if from_denom not in RATES_IN_COPPER or to_denom not in RATES_IN_COPPER:
        raise ValueError("Invalid denomination specified.")
    if from_denom == to_denom:
        raise ValueError(f"Cannot exchange {from_denom.upper()} to itself.")

    from_attr = DENOM_ATTRS[from_denom]
    current_amount = current_wallet.get(from_attr, 0)
    if current_amount < amount:
        raise ValueError(f"Not enough {from_denom.upper()} to exchange. Needs {amount}, has {current_amount}.")

    # Calculate total copper to convert
    total_copper = amount * RATES_IN_COPPER[from_denom]
    
    # Calculate target amount
    dest_rate = RATES_IN_COPPER[to_denom]
    dest_amount = total_copper // dest_rate
    remainder_copper = total_copper % dest_rate

    # Distribute remainder to lower denominations
    distributed = {
        "pp": 0,
        "gp": 0,
        "sp": 0,
        "cp": 0
    }
    distributed[to_denom] = dest_amount

    # List of denominations from highest to lowest
    order = ["pp", "gp", "sp", "cp"]
    to_idx = order.index(to_denom)
    
    # We only distribute to denominations lower than the target denomination
    rem = remainder_copper
    for denom in order[to_idx + 1:]:
        rate = RATES_IN_COPPER[denom]
        distributed[denom] = rem // rate
        rem = rem % rate

    # Calculate net changes
    net_changes = {
        "platinum": 0,
        "gold": 0,
        "silver": 0,
        "copper": 0
    }
    
    # Spent from_denom
    net_changes[DENOM_ATTRS[from_denom]] -= amount
    # Received distributed denoms
    for k, v in distributed.items():
        net_changes[DENOM_ATTRS[k]] += v

    # Check if there is a net change (i.e. not all zero)
    if all(v == 0 for v in net_changes.values()):
        raise ValueError(
            f"This exchange has no effect. The amount {amount} {from_denom.upper()} "
            f"is too small to obtain any {to_denom.upper()} or intermediate coins."
        )

    return net_changes

class XChange(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(guild_ids=[GUILD_ID], name="xchange", description="Exchange currency between denominations.")
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
            net_changes = perform_exchange_calculation(
                from_denom=from_denom,
                to_denom=to_denom,
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
        except Exception as e:
            return await ctx.followup.send(f"Failed to save actor data to Google Sheet: {e}", ephemeral=True)

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
