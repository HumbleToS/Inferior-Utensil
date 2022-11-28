"""
Copyright 2020-present fretgfr

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy,
modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software
is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT
OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""
import asyncio
import contextlib
import logging
import math
import random
from io import StringIO

import discord
from discord import embeds
from discord.ext import commands

_logger = logging.getLogger(__name__)

class PyTest(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    @commands.command(aliases=['ex', 'exec'])
    @commands.is_owner()
    async def py(self, ctx: commands.Context, *, code):
        """Runs arbitrary Python code.

        Parameters
        -----------
        code: str
            The code to run. Can be formatted without a codeblock, in a python codeblock, or in a bare codeblock.
        """
        mystdout = StringIO() #will hold the output of the code run

        async with ctx.channel.typing():
            if code.startswith("```python") and code.endswith("```"):
                code = code[10:-3]
            elif code.startswith("```py") and code.endswith("````"):
                code = code[5:-3]
            elif code.startswith("```") and code.endswith("```"):
                code = code[3:-3]
            else:
                code = code

            async def aexec(code, ctx):
                ldict = {}
                bot = self.bot

                exec(f'async def __ex(): ' + ''.join(f'\n {l}' for l in code.split('\n')), {"discord": discord, "random": random, "commands": commands, "embeds": embeds, "utils": discord.utils, "math": math, 'ctx': ctx, 'bot': bot, 'asyncio': asyncio, 'aio': asyncio}, ldict)
                return await ldict['__ex']() #await the created coro
            with contextlib.redirect_stdout(mystdout), contextlib.redirect_stderr(mystdout):
                await asyncio.wait_for(aexec(code, ctx), timeout=600) #Should time it out after 600 seconds
            await ctx.message.add_reaction("\N{WHITE HEAVY CHECK MARK}")

        if mystdout.getvalue():
            paginator = commands.Paginator(max_size=2000)
            for line in mystdout.getvalue().split("\n"):
                paginator.add_line(line)
            for page in paginator.pages:
                await ctx.send(page)

    @py.error
    async def err_handler(self, ctx, error):
        await ctx.send(f"```{error}```")
        await ctx.message.add_reaction("\N{CROSS MARK}")


async def setup(bot):
    _logger.info("Loading cog PyTest")
    await bot.add_cog(PyTest(bot))

async def teardown(bot):
    _logger.info("Unloading cog PyTest")
