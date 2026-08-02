import logging, discord, sys
from discord.ext import commands
from config import DISCORD_TOKEN, GUILD_ID
from ext.loader import ExtensionLoadError, load_required_extensions

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
intents.voice_states = True

bot = commands.Bot(command_prefix="/", intents=intents)

# Every one of these is required: the error handler is what keeps exception text
# out of Discord, and each command is a documented game action players rely on.
# The bot refuses to start if any of them fails to load.
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
    "ext.commands.craft",
    "ext.commands.xchange",
]

@bot.event
async def on_ready():
    logging.info(f"Bot logged in as {bot.user} (ID: {bot.user.id})")
    logging.info("Guild ID: %s", GUILD_ID)

def main():
    try:
        load_required_extensions(bot, EXTENSIONS)
    except ExtensionLoadError as error:
        logging.critical("%s", error)
        return 1
    bot.run(DISCORD_TOKEN)
    return 0

if __name__ == "__main__":
    sys.exit(main())
