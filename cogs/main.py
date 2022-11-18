from discord.ext import commands
import discord

class Main(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if self.bot.user.mention == message.content or f'<@!{self.bot.user.id}>' == message.content:
            em = discord.Embed(
                description=f'Hello! My prefix is `?`',
                color=discord.Color.random(),
            )
            await message.reply(embed=em)
        else:
            return

async def setup(bot):
    await bot.add_cog(Main(bot))