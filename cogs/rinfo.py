import time
import discord
import psutil
import os
import sys
import asyncio
import aiohttp
import unicodedata
import traceback
import textwrap
import inspect
import time
import re
import io
import os
import random
import json
import base64

from ext import embedtobox
from util.chat_formatting import pagify, box
from discord.ext import commands
from datetime import datetime
from util import repo, default
from discord import Webhook, AsyncWebhookAdapter
from collections import Counter


class Information2:
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process(os.getpid())
        self.totalmembers = set({})
        self.counter = Counter()

    def gettotalusers(self):
        for x in self.bot.guilds:
            for y in x.members:
                self.totalmembers.add(y.id)
        return len(self.totalmembers)

    def get_bot_uptime(self, *, brief=False):
        now = datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        if not brief:
            if days:
                fmt = '{d} days, {h} hours, {m} minutes, and {s} seconds'
            else:
                fmt = '{h} hours, {m} minutes, and {s} seconds'
        else:
            fmt = '{h}h {m}m {s}s'
            if days:
                fmt = '{d}d ' + fmt

        return fmt.format(d=days, h=hours, m=minutes, s=seconds)

    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def ping(self, linu):
        """ ping? """
        before = time.monotonic()
        message = await linu.send("pat?")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"""
The message round-trip took {int(ping)}ms 
The heartbeat ping {round(self.bot.latency * 1000)}ms 
""")

    @commands.command(aliases=['stats', 'status'])
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def botstats(self, linu):
        """ About the bot """
        ramUsage = self.process.memory_full_info().rss / 1024**2
        cpu_usage = round(self.process.cpu_percent() / psutil.cpu_count(), 2)
        embed = discord.Embed(
            colour=0xFFA500)
        embed.set_thumbnail(
            url=linu.bot.user.avatar_url)
        embed.add_field(
            name="Commands",
            value=len([x.name for x in self.bot.commands]), inline=True)
        embed.add_field(
            name="Some counter stats",
            value=f"People ratelimited(Since last restart) " + str(self.bot.counter["ratelimits"]) + "\nCommands ran(since last restart) " + str(self.bot.counter["commands_ran"]) + "\nMessages read(Since last restart) " + str(self.bot.counter["messages_read"]) + " ", inline=False)
        embed.add_field(
            name="Library",
            value="discord.py [rewrite]", inline=True)
        embed.add_field(
            name="Servers",
            value=len(linu.bot.guilds), inline=True)
        embed.add_field(
            name='Total Users',
            value=self.gettotalusers())
        embed.add_field(
            name="Platform",
            value='Linux Ubuntu 18.04 LTS', inline=True)
        embed.add_field(
            name="CPU Percentage",
            value=f"{cpu_usage}%", inline=True)
        embed.add_field(
            name="RAM Currently using",
            value=f"{ramUsage:.2f} MB", inline=True)
        embed.add_field(
            name="Total RAM",
            value=f"3.8 GB", inline=True)

        embed.add_field(
            name="Uptime",
            value=self.get_bot_uptime(), inline=False)

        await linu.send(
            embed=embed)

    @commands.command()
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def about(self, linu):
        """info about the bot"""
        embed = discord.Embed(
            colour=0xFFA500)
        embed.set_thumbnail(
            url=linu.bot.user.avatar_url)
        embed.add_field(
            name="Hello!",
            value="im linu *the small fox from your pocket*\n[no creativity left think somthing later]",
            inline=False)
        embed.add_field(
            name="Dev[s]",
            value="wolfirik#4041",
            inline=False)
        embed.add_field(
            name="Admin[s]",
            value="""
            wolfirik#4041
            Syntax#0666
            """,
            inline=True)
        embed.add_field(
            name="Im using",
            value="discord.py [rewrite]",
            inline=True)
        embed.set_footer(
            text='linu')
        await linu.send(
            embed=embed)


def setup(bot):
    bot.add_cog(Information2(bot))
