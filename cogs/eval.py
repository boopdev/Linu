import time
import datetime
import subprocess
from util import repo, default, http
from util.chat_formatting import pagify, box
from ext import embedtobox
from discord.ext import commands
from copy import deepcopy
import os
import asyncio
import discord
import aiohttp
from contextlib import redirect_stdout
from copy import copy
import inspect
import textwrap
import psutil
import requests
from io import BytesIO
import json
from collections import Counter as count


class evalc:
    """Eval command"""

    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self.emotes = default.get(r"emotes.json")

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

    @staticmethod
    def get_syntax_error(e):
        """Format a syntax error to send to the user.
        Returns a string representation of the error formatted as a codeblock.
        """
        if e.text is None:
            return box('{0.__class__.__name__}: {0}'.format(e), lang="py")
        return box(
            '{0.text}{1:>{0.offset}}\n{2}: {0}'
            ''.format(e, '\n^', type(e).__name__),
            lang="py")

    def get_pages(msg: str):
        """Pagify the given message for output to the user."""
        return pagify(msg, delims=["\n", " "], priority=True, shorten_by=10)

    @commands.command()
    @commands.check(repo.is_owner)
    async def evl(self, linu, *, code):
        """Retarded brother of eval
        """
        env = {
            'bot': linu.bot,
            'linu': linu,
            'ps': psutil,
            'channel': linu.channel,
            'author': linu.author,
            'guild': linu.guild,
            'message': linu.message,
            'discord': discord,
            'commands': commands,
            'os': os,
            'emote':  self.emotes,
            'counter': count,
            '_': self._last_result
        }

        code = self.cleanup_code(code)

        try:
            result = eval(code, env)
        except SyntaxError as e:
            await linu.send(self.get_syntax_error(e))
            return
        except Exception as e:
            await linu.send('{}: {!s}'.format(type(e).__name__, e))
            return

        if asyncio.iscoroutine(result):
            result = await result

        self._last_result = result
        if code == "bot.http.token":
            f = "discord.bot.http.token\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\nlmfao f in chat tard"
            memes = BytesIO(f.encode('utf-8'))
            await linu.send(content="OUtpUt too Big", file=discord.File(memes, filename="eval.txt"))

        else:
            result = str(result)
            if len(result) > 1500:
                f = result
                memes = BytesIO(f.encode('utf-8'))
                return await linu.send("Output's too big heres the file.", file=discord.File(memes, filename='eval.txt'))
            else:
                try:
                    await linu.send(result)
                except Exception as e:
                    await linu.send(f"`{e}`")


def setup(bot):
    bot.add_cog(evalc(bot))
