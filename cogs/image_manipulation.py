import functools
import io
import logging
import pathlib
from typing import Union

import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont

from utils.dynamic_cooldown_check import owner_cooldown_bypass

_logger = logging.getLogger(__name__)


class ImageManipulation(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self._slap_image_path = pathlib.Path("./cogs/base_images/slap.png")
        self._do_stuff_image_path = pathlib.Path("./cogs/base_images/do_stuff.png")

    async def get_pfp_in_bytes(self, user: Union[discord.User, discord.Member]) -> io.BytesIO:
        """Get the users avatar in bytes

        Parameters
        ----------
        user : discord.User
            The user of which will have their avatar converted to bytes

        Returns
        -------
        io.BytesIO
            A buffer containing the bytes of a User/Member's avatar
        """
        av_bytesIO = io.BytesIO(await user.display_avatar.read())
        av_bytesIO.seek(0)
        return av_bytesIO

    def generate_slap_image(self, sender: io.BytesIO, target: io.BytesIO) -> io.BytesIO:
        """Generate the slap image with the sender and target avatars

        Parameters
        ----------
        sender : io.BytesIO
            The senders avatar in BytesIO
        target : io.BytesIO
            The targets avatar in BytesIO

        Returns
        -------
        io.BytesIO
            A buffer containing a `png` with the sender and target overlayed.
        """
        template_image = Image.open(self._slap_image_path)
        sender_pfp = Image.open(sender)
        target_pfp = Image.open(target)

        if sender_pfp.mode != "RGB" or sender_pfp.mode != "RGBA":
            sender_pfp = sender_pfp.convert("RGBA")

        sender_pfp.thumbnail((128, 128))
        template_image.paste(sender_pfp, (240, 60))

        if target_pfp.mode != "RGB" or target_pfp.mode != "RGBA":
            target_pfp = target_pfp.convert("RGBA")

        target_pfp.thumbnail((128, 128))
        template_image.paste(target_pfp, (0, 105))

        # Get image into buffer and return
        buffered_image = io.BytesIO()
        template_image.save(buffered_image, "PNG")
        buffered_image.seek(0)

        return buffered_image

    def generate_do_something_image(self, avatar: io.BytesIO) -> io.BytesIO:
        """Generate the do stuff image with the users avata

        Parameters
        ----------
        avatar : io.BytesIO
            The senders avatar

        Returns
        -------
        io.BytesIO
            A buffer containing a `png` with the avatar overlayed.
        """
        template_image = Image.open(self._do_stuff_image_path)

        draw = ImageDraw.Draw(template_image)
        font = ImageFont.truetype("./cogs/fonts/OpenSans-Regular.ttf", 54)
        draw.text((140, 40), "C'mon,\ndo stuff...", 'black', font=font, align='center', stroke_width=2)

        user_avatar = Image.open(avatar)

        if user_avatar.mode != "RGB" or user_avatar.mode != "RGBA":
            user_avatar = user_avatar.convert("RGBA")

        user_avatar.thumbnail((240, 210))
        template_image.paste(user_avatar, (220, 369))

        buffered_image = io.BytesIO()
        template_image.save(buffered_image, "PNG")
        buffered_image.seek(0)

        return buffered_image

    @app_commands.command()
    @app_commands.checks.dynamic_cooldown(owner_cooldown_bypass)
    async def slap(self, interaction: discord.Interaction, target: discord.User) -> None:
        """Slap someone!

        Parameters
        ----------
        target : discord.User
            Who do you want to slap?
        """
        sender_pfp_bytes = await self.get_pfp_in_bytes(interaction.user)
        target_pfp_bytes = await self.get_pfp_in_bytes(target)
        to_run = functools.partial(self.generate_slap_image, sender_pfp_bytes, target_pfp_bytes)
        image: io.BytesIO = await self.bot.loop.run_in_executor(None, to_run)
        await interaction.response.send_message(file=discord.File(image, "slap.png"))

    @app_commands.command()
    @app_commands.checks.dynamic_cooldown(owner_cooldown_bypass)
    async def do_stuff(self, interaction: discord.Interaction, target: discord.User) -> None:
        """C'mon, do stuff...

        Parameters
        ----------
        target : discord.User
            Who do you want to do stuff?
        """
        avatar_bytes = await self.get_pfp_in_bytes(target or interaction.user)
        to_run = functools.partial(self.generate_do_something_image, avatar_bytes)
        image: io.BytesIO = await self.bot.loop.run_in_executor(None, to_run)
        await interaction.response.send_message(file=discord.File(image, "do_stuff.png"))


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ImageManipulation(bot))


async def teardown(_):
    _logger.info("Extension: Unloading ImageManipulation")
