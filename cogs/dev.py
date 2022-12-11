import logging
import typing

import discord
from discord.ext import commands

from lib.dbmodels import ErrorLog
from lib import utils

_logger = logging.getLogger(__name__)

class DevTools(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def sync(
        self,
        ctx: commands.Context,
        guilds: commands.Greedy[discord.Object],
        spec: typing.Optional[typing.Literal["~", "*", "^"]] = None,
    ) -> None:
        """Syncs command tree.

        Parameters
        -----------
        guilds: list[int]
            The guilds to sync to
        spec: str
            The spec to sync.
            ~ -> Current Guild
            * -> Globals to current guild
            ^ -> Clear globals copied to current guild.
        """
        if not guilds:
            if spec == "~":
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "*":
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == "^":
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                synced = await ctx.bot.tree.sync()
            await ctx.send(f"Synced {len(synced)} commands {'globally' if spec is None else 'to the current guild.'}")
            return
        ret = 0
        for guild in guilds:
            try:
                await ctx.bot.tree.sync(guild=guild)
            except discord.HTTPException:
                pass
            else:
                ret += 1
        await ctx.send(f"Synced the tree to {ret}/{len(guilds)}.")

    @commands.command(aliases=('e', ))
    @commands.is_owner()
    async def error(self, ctx: commands.Context, error_id: int, raw: bool = False) -> None:
        """Sends an error from the database.

        Parameters
        ----------
        error_id : int
            The error id to send.
        raw : bool
            Whether to send the error in raw form, defaults to False
        """
        err = await ErrorLog.get_or_none(id=error_id)
        if not err:
            await ctx.send(f"I could not find an error with that id. (ID: {error_id})")
            return
        if raw:
            await ctx.send(file=discord.File(err.raw_bytes, filename=f"{err.id} raw.txt"))
        else:
            await ctx.send(embed=err.embed)

    @commands.command(aliases=('re',))
    @commands.is_owner()
    async def recenterrors(self, ctx: commands.Context) -> None:
        """Returns the 20 most recently logged errors."""
        errs = await ErrorLog.filter().order_by("-id").limit(20)
        embed = discord.Embed(color=utils.randpastel_color(), description="")
        if errs:
            for err in errs:
                embed.description += f"{err.id:0>5}: (Item: {err.item}) {err.timestamp:%m-%d-%Y} at {err.timestamp:%I:%M:%M %p} UTC\n\n"
            await ctx.send(embed=embed)
        else:
            await ctx.send("No errors logged yet.")

    @commands.command()
    @commands.is_owner()
    async def clearerrors(self, ctx: commands.Context) -> None:
        """Deletes all errors logged in the database except for the most recent."""
        await ctx.send(f"Are you sure you want to clear all of the logged errors? The most recent one will be kept. (y/N)")
        msg = await self.bot.wait_for("message", check=lambda m: m.author.id == self.bot.owner_id)

        if msg.clean_content.lower().strip() == "y":
            max_id = (await ErrorLog.all().order_by("-id").first()).id
            deleted = await ErrorLog.filter(id__lt=max_id).delete()

            await ctx.send(f"Deleted {deleted} logged errors.")
        else:
            await ctx.send("Aborted....")


async def setup(bot):
    _logger.info("Loading DevTools cog")
    await bot.add_cog(DevTools(bot))

async def teardown(_):
    _logger.info("Extension: Unloading DevTools")
