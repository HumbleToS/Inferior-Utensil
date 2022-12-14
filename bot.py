import asyncio
import json
import logging
import logging.handlers
import os
import pathlib
import sys
from typing import Union

import aiohttp
import discord
from cachetools import TTLCache
from discord.ext import commands
from tortoise import Tortoise

bot_description = "I am an Inferior Utensil <3"

cwd = pathlib.Path(__file__).parent
CONFIG_FILE_NAME = "config.json"
config_path = cwd / CONFIG_FILE_NAME

with open(config_path) as fp:
    config = json.load(fp)

db_url = config["db_url"]

if config["testing"]:
    db_url = "sqlite://:memory:"

log_fmt = logging.Formatter(
    fmt="%(asctime)s - %(name)s:%(lineno)d - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

sh = logging.StreamHandler(sys.stdout)
sh.setLevel(logging.DEBUG)
sh.setFormatter(log_fmt)

max_bytes = 4 * 1024 * 1024  # 4 MB
rfh = logging.handlers.RotatingFileHandler("logs/inferior-utensil.log", maxBytes=max_bytes, backupCount=10)
rfh.setLevel(logging.DEBUG)
rfh.setFormatter(log_fmt)

if config.get("testing"):
    HANDLER = sh
else:
    HANDLER = rfh

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(HANDLER)

_logger = logging.getLogger(__name__)


class InferiorUtensil(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents(
            emojis=True,
            guilds=True,
            invites=True,
            members=True,
            message_content=True,
            messages=True,
            presences=True,
            reactions=True,
            voice_states=True,
        )
        super().__init__(
            command_prefix=commands.when_mentioned_or("?"),
            activity=discord.Activity(type=discord.ActivityType.watching, name="my good code | ?help"),
            description=bot_description,
            intents=intents,
            case_insensitive=True,
            max_messages=5000,
        )
        self.config = config
        self._cache = TTLCache(maxsize=5, ttl=7200)

    async def fetch_team_members(self) -> Union[list[discord.TeamMember], None]:
        """Retrives the applications team members

        Returns
        -------
        Union[list[discord.TeamMember], None]
            Returns a full list of the applications team members if there is a team
        """
        key = "team_members"
        cached = self._cache.get(key)
        if cached is not None:
            return cached

        app_info = await self.application_info()
        if app_info.team:
            team_members = app_info.team.members
        else:
            team_members = None

        self._cache[key] = team_members

        return team_members

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession()
        for file in sorted(pathlib.Path("cogs").glob("**/[!_]*.py")):
            """
            Don't get (or load) any cogs starting with an underscore (AbstractUmbra's code momento <3)
            """
            ext = ".".join(file.parts).removesuffix(".py")
            try:
                await self.load_extension(ext)
                _logger.info(f"Extension {ext} was loaded successfully!")
            except Exception as err:
                _logger.exception(f"Failed to load extension {ext}")

        self.team_members = await self.fetch_team_members()

        os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
        os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
        await self.load_extension("jishaku")

    async def on_message_edit(self, _: discord.Message, after: discord.Message) -> None:
        await self.process_commands(after)

    async def close(self) -> None:
        await super().close()
        await self.session.close()


async def main() -> None:
    bot = InferiorUtensil()

    await Tortoise.init(db_url=db_url, modules={"models": ["lib.dbmodels"]})

    if config["gen_schema"]:
        await Tortoise.generate_schemas(safe=True)

    await bot.start(config.get("token"), reconnect=True)


asyncio.run(main())
