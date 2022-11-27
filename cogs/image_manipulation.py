import functools
import pathlib
import io

import discord
from discord import app_commands
from discord.ext import commands
from PIL import Image


class ImageManipulation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.slap_image_path = pathlib.Path("./cogs/base_images/slap.png")

    async def get_pfp_in_bytes(self, user: discord.User) -> bytes:
        av_bytesIO = io.BytesIO(await user.display_avatar.read())
        av_bytesIO.seek(0)
        return av_bytesIO

    def generate_slap_image(self, sender: io.BytesIO, target: io.BytesIO) -> io.BytesIO:
        template_image: Image = Image.open(self.slap_image_path)
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

    @app_commands.command()
    async def slap(self, interaction: discord.Interaction, target: discord.User):
        sender_pfp_bytes = await self.get_pfp_in_bytes(interaction.user)
        target_pfp_bytes = await self.get_pfp_in_bytes(target)
        to_run = functools.partial(self.generate_slap_image, sender_pfp_bytes, target_pfp_bytes)
        image: io.BytesIO = await self.bot.loop.run_in_executor(None, to_run)
        await interaction.response.send_message(file=discord.File(image, "slap.png"))


async def setup(bot):
    await bot.add_cog(ImageManipulation(bot))
