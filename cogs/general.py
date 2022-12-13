import logging
import re
from typing import Union

import discord
from discord.ext import commands

_logger = logging.getLogger(__name__)


class General(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener(name="on_message")
    async def mention_responder(self, message: discord.Message) -> Union[discord.Message, None]:
        guild = message.guild
        if not guild:
            return
        if re.fullmatch(rf"<@!?{guild.me.id}>", message.content):
            embed = discord.Embed(
                description=f"Hello! My prefix is `?`",
            )
            return await message.reply(embed=embed)
        return

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(1, 5.0, commands.BucketType.user)  # 1 per 5 seconds per user
    async def cleanup(self, ctx: commands.Context, amount: int = 100):
        """Purges messages from and relating to the bot.

        Parameters
        ----------
        amount : int, optional
            The number of messages to check (1-100), defaults to 100.
        """
        amount = max(min(amount, 100), 1)

        async with ctx.typing():
            can_purge_author = ctx.channel.permissions_for(ctx.guild.me).manage_messages  # type: ignore
            try:
                channel_prefixes = tuple(await self.bot.get_prefix(ctx.message))
                msgs = await ctx.channel.purge(  # type: ignore
                    limit=amount,
                    check=lambda m: (m.author == self.bot.user and len(m.components) == 0)
                    or (can_purge_author and m.author == ctx.author and m.content.startswith(channel_prefixes)),
                )
                await ctx.send(f"Removed {len(msgs)} messages.", delete_after=10.0)
            except (discord.Forbidden, discord.HTTPException):
                await ctx.send("I couldn't process this request. Please check my permissions.")


async def setup(bot: commands.Bot):
    await bot.add_cog(General(bot))


async def teardown(_):
    _logger.info("Extension: Unloading General")
