from __future__ import annotations
from helpers.utils import to_currency, roll_dice
from typing import List, Tuple
import discord

class Resource:
    def __init__(self, downtime=0, platinum=0, gold=0, silver=0, copper=0, moradinium=0):
        self.downtime = downtime
        self.platinum = platinum
        self.gold = gold
        self.silver = silver
        self.copper = copper
        self.moradinium = moradinium

    def get_summary(self, include_money=True, include_moradinium=True, include_downtime=False) -> str:
        parts = []
        if include_money:
            money = []
            if self.platinum > 0: money.append(f"{self.platinum}pp")
            if self.gold > 0:     money.append(f"{self.gold}gp")
            if self.silver > 0:   money.append(f"{self.silver}sp")
            if self.copper > 0:   money.append(f"{self.copper}cp")
            if money:
                parts.append("**Money:** " + ", ".join(money))
        if include_moradinium:
            parts.append(f"**Moradinium:** {self.moradinium}")
        if include_downtime:
            parts.append(f"**Downtime:** {self.downtime} days")
        return "\n".join(parts) if parts else "*No relevant resources.*"

    def deduct(self, platinum=0, gold=0, silver=0, copper=0, moradinium=0):
        if moradinium > self.moradinium:
            raise ValueError("Not enough Moradinium to pay.")
        self.moradinium -= moradinium
        wallet = {"pp": self.platinum, "gp": self.gold, "sp": self.silver, "cp": self.copper}
        required = {"pp": platinum, "gp": gold, "sp": silver, "cp": copper}
        rates = {"pp": 10, "gp": 10, "sp": 10}
        order = ["cp", "sp", "gp", "pp"]
        for i, curr in enumerate(order):
            if required[curr] > wallet[curr]:
                if curr == "pp":
                    raise ValueError("Not enough platinum pieces and no higher currency available.")
                bigger = order[i + 1]
                needed = required[curr] - wallet[curr]
                exchange_needed = (needed // rates[bigger]) + (1 if needed % rates[bigger] else 0)
                if wallet[bigger] < exchange_needed:
                    raise ValueError(f"Not enough {bigger} to convert into {curr}.")
                wallet[bigger] -= exchange_needed
                wallet[curr] += exchange_needed * rates[bigger]
            wallet[curr] -= required[curr]
        self.copper = wallet["cp"]
        self.silver = wallet["sp"]
        self.gold = wallet["gp"]
        self.platinum = wallet["pp"]

    def add(self, platinum=0, gold=0, silver=0, copper=0, moradinium=0):
        self.platinum += platinum
        self.gold += gold
        self.silver += silver
        self.copper += copper
        self.moradinium += moradinium

    def mine_moradinium(self, bot: discord.Client, downtime: int, investigation_mod: int=0, roll_mode="normal", reroll=0, actor_name=""):
        if downtime < 5 or downtime % 5 != 0:
            raise ValueError("Downtime must be spent in increments of five days.")
        if downtime > self.downtime:
            raise ValueError(f"Not enough downtime available: {self.downtime} days.")
        mining_weeks = downtime // 5
        roll_results: List[Tuple[int,int,int]] = []
        total_moradinium = 0
        for _ in range(mining_weeks):
            rolls, total = roll_dice(bot, modifier=investigation_mod, roll_mode=roll_mode, reroll=reroll, actor_name=actor_name)
            roll_val = rolls[0]
            earned = max(1, total // 5)
            total_moradinium += earned
            roll_results.append((roll_val, total, earned))
        self.moradinium += total_moradinium
        self.downtime -= downtime
        return roll_results

    def earn_money(self, bot: discord.Client, downtime: int, modifier: int=0, roll_mode="normal", reroll= 0, actor_name=""):
        if downtime < 5 or downtime % 5 != 0:
            raise ValueError("Downtime must be spent in increments of five days.")
        if downtime > self.downtime:
            raise ValueError(f"Not enough downtime available: {self.downtime} days.")
        earning_weeks = downtime // 5
        roll_results: List[Tuple[int,int,int]] = []
        total_gold = 0
        for _ in range(earning_weeks):
            rolls, total = roll_dice(bot, modifier=modifier, roll_mode=roll_mode, reroll=reroll, actor_name=actor_name)
            roll_val = rolls[0]
            earned = min(((total - 15) // 5) * 30 + 10, 100) if total >= 15 else 0
            total_gold += earned
            roll_results.append((roll_val, total, earned))
        self.gold += total_gold
        self.downtime -= downtime
        return roll_results

    def retail_sale(self, bot: discord.Client, item: str, downtime: int, persuasion_modifier: int, roll_mode: str, reroll: int, 
                    crafting_cost: float, quantity: int, material: int, actor_name: str):
        from helpers.utils import to_currency
        if downtime < 1:
            raise ValueError("You must spend at least one day of downtime.")
        if self.downtime < downtime:
            raise ValueError(f"Not enough downtime available: {self.downtime} days.")
        rolls, total_persuasion = roll_dice(bot, modifier=persuasion_modifier + downtime,
                                            roll_mode=roll_mode, reroll=reroll, actor_name=actor_name)
        earnings_percent = min(total_persuasion * 5, 140) / 100
        earnings = crafting_cost * earnings_percent
        sale_price_per_item = material + crafting_cost + earnings
        total_sale_price = sale_price_per_item * quantity

        earnings_gold, earnings_silver, earnings_copper, earnings_amount = to_currency(earnings)
        item_gold, item_silver, item_copper, item_amount = to_currency(sale_price_per_item)
        total_gold, total_silver, total_copper, total_amount = to_currency(total_sale_price)

        self.add(gold=total_gold,silver=total_silver, copper=total_copper)
        self.downtime -= downtime
        
        msg = (f"Item(s): {item}\n"
               f"Roll: {rolls[0]} + {persuasion_modifier + downtime} = {total_persuasion}\n"
               f"Earnings rate: {earnings_percent * 100:.0f}%\n"
               f"Profit per item: {earnings_amount}\n"
               f"Sale price per item: {item_amount}\n")
        if quantity > 1:
            msg += f"Total sale price for {quantity} items: {total_amount}"
        else:
            msg += f"Total sale price: {total_amount}"
        return msg

    def wholesale_sale(self, bot: discord.Client, item: str, crafting_cost: float, quantity: int, persuasion_modifier: int,
                       roll_mode: str, reroll: int, haggle: bool, actor_name: str):
        from helpers.utils import to_currency
        if haggle:
            rolls, total = roll_dice(bot, modifier=persuasion_modifier, roll_mode=roll_mode, reroll=reroll, actor_name=actor_name)
            percentage = min(max(total * 10, 80), 180) / 100
            roll_info = f"Roll: {rolls[0]} + {persuasion_modifier} (Persuasion) = {total}"
        else:
            percentage = 1
            roll_info = ""
        
        total_sale_price = crafting_cost * percentage * quantity
        total_gold, total_silver, total_copper, total_amount = to_currency(total_sale_price)
        self.add(gold=total_gold,silver=total_silver, copper=total_copper)

        msg = (
            f"Item(s): {item}\n"
            f"Sale to merchant {'with' if haggle else 'without'} haggling."
            f" {roll_info}\n"
            f"Sale percentage: {percentage * 100:.0f}%\n"
            f"Total sale price: {total_amount}"
        )
        return msg
