import logging, discord
from discord.ext import commands

class GlobalErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_application_command_error(self, ctx: discord.ApplicationContext, error: Exception):
        logging.error("Unhandled error in /%s", getattr(ctx.command, "name", "?"),
                      exc_info=(type(error), error, error.__traceback__))
        try:
            if ctx.response.is_done():
                await ctx.followup.send(f"Error: {error}", ephemeral=True)
            else:
                await ctx.respond(f"Error: {error}", ephemeral=True)
        except discord.HTTPException:
            pass

def setup(bot):
    bot.add_cog(GlobalErrorHandler(bot))
