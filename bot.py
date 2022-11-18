from discord.ext import commands
import discord
import aiohttp
import asyncio
import logging
import json
import os
import pathlib

bot_description = "I am an Inferior Utensil <3"

config_path = os.path.dirname(os.path.abspath(__file__))
config = json.load(open(f"{config_path}/config.json"))

log = logging.getLogger(__name__)


class InferiorUtensil(commands.Bot):
    def __init__(self):
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
            command_prefix="?",
            description=bot_description,
            intents=intents,
            case_insensitive=True,
            max_messages=5000,
        )
        self.config = config

    async def setup_hook(self) -> None:
        self.session = aiohttp.ClientSession
        for file in sorted(pathlib.Path("cogs").glob("**/[!_]*.py")):
            """
            Don't get (or load) any cogs starting with an underscore (AbstractUmbra's code momento <3)
            """
            ext = ".".join(file.parts).removesuffix(".py")
            try:
                await self.load_extension(ext)
                log.info(f"Extension {ext} was loaded successfully!")
            except Exception as err:
                log.exception(f"Failed to load extension {ext}")

        os.environ["JISHAKU_NO_UNDERSCORE"] = "True"
        os.environ["JISHAKU_NO_DM_TRACEBACK"] = "True"
        await self.load_extension("jishaku")

    async def close(self) -> None:
        await super().close()
        await self.session.close()

    async def start(self) -> None:
        await super().start(config.get("token"), reconnect=True)

# Start and run the bot
async def main():
    bot = InferiorUtensil()
    await bot.start()

asyncio.run(main())