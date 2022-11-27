import discord
from discord import app_commands

from typing import Optional

def owner_cooldown_bypass(interaction: discord.Interaction) -> Optional[app_commands.Cooldown]:
    """Uses the applications team members to indicate whether the command should return a cooldown or not

    Parameters
    ----------
    interaction : discord.Interaction
        The interaction provided from the the slash command

    Returns
    -------
    Optional[app_commands.Cooldown]
        Returns None based on the members id and whether it is in team_members
    """
    if interaction.user.id in [member.id for member in interaction.client.team_members]:
        return None
    return app_commands.Cooldown(1, 10)