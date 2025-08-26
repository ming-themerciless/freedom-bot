import random, asyncio
from config import ROLL_CHANNEL_ID
from typing import Tuple
import discord

def safe_number(value, default=0.0):
    try:
        if isinstance(value, (int, float)):
            return float(value)
        s = str(value).strip().replace(",", ".")
        return float(s)
    except (ValueError, TypeError):
        return float(default)

def safe_int(value, default=0):
    try:
        if isinstance(value, (int, float)):
            return int(value)
        return int(float(str(value).strip().replace(",", ".")))
    except (ValueError, TypeError):
        return default

def col_to_index(col: str) -> int:
    index = 0
    for char in col.upper():
        index = index * 26 + (ord(char) - ord('A') + 1)
    return index - 1

def to_currency(money: float) -> Tuple[int,int,int,str]:
    total_cp = round(money * 100)
    gold   = total_cp // 100
    rem    = total_cp % 100
    silver = rem // 10
    copper = rem % 10
    msg = " ".join(
        denom for denom, amt in zip(
            [f"{gold}gp", f"{silver}sp", f"{copper}cp"], [gold, silver, copper]
        ) if amt
    ) or "0gp"
    return gold, silver, copper, msg

def roll_dice(bot: discord.Client, sides=20, rolls=1, modifier=0, roll_mode="normal", reroll=0, actor_name=None):
    results = []
    roll_details = ""
    for _ in range(rolls):
        if roll_mode == "advantage":
            a, b = random.randint(1+reroll, sides), random.randint(1+reroll, sides)
            result = max(a, b)
            roll_details = f"[{a}, {b}] (Advantage: {result})"
        elif roll_mode == "disadvantage":
            a, b = random.randint(1+reroll, sides), random.randint(1+reroll, sides)
            result = min(a, b)
            roll_details = f"[{a}, {b}] (Disadvantage: {result})"
        else:
            result = random.randint(1+reroll, sides)
            roll_details = str(result)
        results.append(result)
    total = sum(results) + modifier

    if actor_name:
        if roll_mode == "normal":
            msg = f"{actor_name}: rolls {results[0]} + {modifier} = {total}"
        else:
            msg = f"{actor_name}: rolls {roll_details} + {modifier} = {total}"
        channel = bot.get_channel(ROLL_CHANNEL_ID)
        if channel:
            asyncio.create_task(channel.send(msg))
    return results, total
