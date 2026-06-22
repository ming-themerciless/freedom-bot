import logging, discord, os
from discord.ext import commands
from config import DISCORD_TOKEN, GUILD_ID
# from music import attach_music

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="/", intents=intents)

EXTENSIONS = [
    "ext.error_handler",
    "ext.commands.info",
    "ext.commands.lc",
    "ext.commands.trade",
    "ext.commands.mine",
    "ext.commands.work",
    "ext.commands.bastion",
    "ext.commands.sale",
    "ext.commands.learn",
]

@bot.event
async def on_ready():
    logging.info(f"Bot logged in as {bot.user} (ID: {bot.user.id})")
    logging.info("Guild ID: %s", GUILD_ID)

def main():
    for ext in EXTENSIONS:
        try:
            bot.load_extension(ext)
        except Exception:
            logging.exception("Failed loading extension: %s", ext)
    try:
        if os.getenv("ENABLE_MUSIC", "0") == "1":
            from music import attach_music
            attach_music(bot, guild_ids=[GUILD_ID])
    except Exception:
        logging.exception("Music attach failed (stub or custom module missing).")
    bot.run(DISCORD_TOKEN)

if __name__ == "__main__":
    main()
