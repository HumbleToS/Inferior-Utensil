import logging
import math

import discord
from discord import app_commands
from discord.app_commands import AppCommandError
from discord.ext import commands

_logger = logging.getLogger(__name__)


class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    def cog_load(self):
        tree = self.bot.tree
        tree.on_error = self.on_app_command_error

    def cog_unload(self):
        tree = self.bot.tree
        tree.on_error = tree.__class__.on_error

    async def on_app_command_error(self, interaction: discord.Interaction, error: AppCommandError):

        if isinstance(error, app_commands.CommandOnCooldown):
            current_cooldown = math.floor(error.retry_after * 100) / 100
            return await interaction.response.send_message(
                f"This command is on cooldown for another {current_cooldown} second{'s' * (current_cooldown != 1)}!"
            )


async def setup(bot: commands.Bot):
    await bot.add_cog(ErrorHandler(bot))


async def teardown(_):
    _logger.info("Extension: Unloading ErrorHandler")
