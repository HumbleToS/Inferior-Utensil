from __future__ import annotations

import io
import logging

import discord
from tortoise import fields
from tortoise.models import Model

from . import utils

_logger = logging.getLogger(__name__)

class ErrorLog(Model):
    """Represents a logged error."""
    id = fields.BigIntField(pk=True, generated=True)
    timestamp = fields.DatetimeField(auto_now_add=True)
    traceback = fields.TextField(null=False)
    item = fields.TextField(null=True)

    @property
    def embed(self) -> discord.Embed:
        """Generates an Embed that represents this Error.

        Returns
        -------
        discord.Embed
            The generated Embed.
        """
        embed = discord.Embed(title=f"Error #{self.id}{f' (Item/Command: {self.item})' if self.item is not None else ''}", color=utils.randpastel_color())
        embed.description = f"```{self.traceback[:5500]}```"
        embed.set_footer(text=f"Occurred On: {self.timestamp:%m-%d-%Y} at {self.timestamp:%I:%M:%M %p} UTC")

        return embed

    @property
    def pub_embed(self) -> discord.Embed:
        """Returns the public embed message for this error.

        Returns
        -------
        discord.Embed
            The generated Embed.
        """
        return discord.Embed(title=f"An unexpected error occured (ID: {self.id})", description=f"My developers are aware of the issue.\n\nIf you want to discuss this error with my developer, join the [support server](https://discord.gg/f64pfnqbJJ \"Support Server Invite URL\") and refer to the error by it's id. (ID: {self.id})", color=utils.randpastel_color())

    @property
    def raw_text(self) -> str:
        """Returns the error in a raw text buffer."""
        output = (
            f"Error #{self.id}{f' (Item/Command: {self.item})' if self.item is not None else ''}\n"
            f"Occurred On: {self.timestamp:%m-%d-%Y} at {self.timestamp:%I:%M:%M %p} UTC\n"
            f"{self.traceback}\n"
        )
        return output

    @property
    def raw_bytes(self) -> io.BytesIO:
        """Returns the error as raw UTF-8 encoded bytes buffer."""
        output = io.BytesIO(self.raw_text.encode("UTF-8"))
        output.seek(0)

        return output
