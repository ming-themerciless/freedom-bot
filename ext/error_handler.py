import logging

import discord
from discord.ext import commands

logger = logging.getLogger(__name__)

SAFE_ERROR_MESSAGE = (
    "Something went wrong while processing that command. "
    "Please try again or contact a bot administrator."
)


class GlobalErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: Exception):
        interaction_id = getattr(getattr(ctx, "interaction", None), "id", "unknown")
        logger.error(
            "Unhandled application command error command=%s interaction_id=%s",
            getattr(ctx.command, "name", "?"),
            interaction_id,
            exc_info=(type(error), error, error.__traceback__),
        )
        try:
            if ctx.response.is_done():
                await ctx.followup.send(SAFE_ERROR_MESSAGE, ephemeral=True)
            else:
                await ctx.respond(SAFE_ERROR_MESSAGE, ephemeral=True)
        except discord.HTTPException:
            pass

def setup(bot):
    bot.add_cog(GlobalErrorHandler(bot))
