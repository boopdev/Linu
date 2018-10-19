import sys
try:
    import discord
    from discord.ext import commands
    from discord.ext.commands import AutoShardedBot
except ImportError:
    print("Discord.py [rewrite] is not installed.\n"
          "Consult the guide for your operating system "
          "and do ALL the steps in order.\n")
    sys.exit(1)
from ext.context import CustomContext
from ext.formatter import EmbedHelp
from collections import defaultdict
from ext import embedtobox
from util import repo, default
from PIL import Image
import asyncio
import aiohttp
import datetime
import psutil
import time
import json
import os
import re
import textwrap
import io
import logging
from collections import Counter 
from pathlib import Path




class LinuClient(AutoShardedBot):
    _mentions_transforms = {
        '@everyone': '@\u200beveryone',
        '@here': '@\u200bhere'
    }

    _mention_pattern = re.compile('|'.join(_mentions_transforms.keys())) 

    def __init__(self, **attrs):
        super().__init__(
            command_prefix=self.get_pre,
            fetch_offline_members=True)
        self.formatter = EmbedHelp()
        self.process = psutil.Process()
        self._extensions = [x.replace('.py', '') for x in os.listdir('cogs') if x.endswith('.py')]
        self.last_message = None
        self.commands_used = defaultdict(int)
        self.remove_command('help')
        self.load_extensions()
        self.add_command(self.loacog)
        self.add_command(self.relcog)
        self.add_command(self.res)
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.check = default.get("data/blacklist.json")
        self.counter = Counter() # TO UPDATE COUNTERS linu evl bot.counter.update({'messages_read': 8000, 'commands_ran': 80})

    def load_extensions(self, cogs=None, path='cogs.'):
        '''Loads the default set of extensions or a seperate one if given'''
        for extension in cogs or self._extensions:
            try:
                self.load_extension(f'{path}{extension}')
                print(f'Loaded extension: {extension}')
            except Exception as e:
                print(f'LoadError: {extension}\n'
                      f'{type(e).__name__}: {e}')


    @property
    def token(self):
        '''Returns your token wherever it is'''
        with open('data/config.json') as f:
            config = json.load(f)
            if config.get('TOKEN') == "your_token_here":
                if not os.environ.get('TOKEN'):
                    self.run_wizard()
            else:
                token = config.get('TOKEN').strip('\"')
        return os.environ.get('TOKEN') or token

    @staticmethod
    async def get_pre(bot, message):
        '''Returns the prefix.'''
        with open('data/config.json') as f:
            prefix = json.load(f).get('PREFIX')
        return os.environ.get('PREFIX') or prefix or f'<@{user_id}> '

    def restart(self):
        os.execv(sys.executable, ['python3'] + sys.argv)

    @staticmethod
    def run_wizard():
        '''Wizard for first start'''
        print('------------------------------------------')
        print('First time setup')
        print('------------------------------------------')
        token = input('Enter your bots token:\n> ')
        print('------------------------------------------')
        prefix = input('Enter a prefix for linu:\n> ')
        data = {
                "TOKEN" : token,
                "PREFIX" : prefix,
            }
        with open('data/config.json','w') as f:
            f.write(json.dumps(data, indent=4))
        print('------------------------------------------')
        print('Restarting...')
        print('------------------------------------------')
        os.execv(sys.executable, ['python3'] + sys.argv)

    @classmethod
    def init(bot, token=None):
        '''Starts the actual bot'''
        linu = bot()
        safe_token = token or linu.token.strip('\"')
        try:
            linu.run(safe_token, bot=True, reconnect=True)
        except Exception as e:
            print(e)

    async def on_connect(self):
        print('---------------\n'
              'linu.py connected!')

    async def on_ready(self):
        '''Bot startup, sets uptime.'''
        if not hasattr(self, 'uptime'):
            self.uptime = datetime.datetime.utcnow()
        print(textwrap.dedent(f'''
        ---------------
        Client is ready!
        ---------------
        Logged in as: {self.user}
        User ID: {self.user.id}
        ---------------
        ---------------
        '''))
        

    async def process_commands(self, message):
        '''p r o c e s s   t h o s e     c o m m a n d s'''
        blcheck = default.get("data/blacklist.json").blacklisted
        if message.author.id in blcheck:
            return # oof get fucked
        linu = await self.get_context(message, cls=CustomContext)
        if linu.command is None:
            return
        await self.invoke(linu)

    async def on_message(self, message):
        '''Responds only to users'''
        if message.author.bot:
            return
        await self.process_commands(message)


    @commands.command(aliases=["lo"])
    @commands.check(repo.is_owner)
    async def loacog(self, linu, *, cog: str):
        """ Load an unloaded cog 
        For example: {p}load mod"""
        cog = f"cogs.{cog}"
        await linu.send(f"Preparing to load {cog}...", delete_after=10)
        try:
            self.load_extension(cog)
            await linu.send(f"{cog} cog was loaded successfully!", delete_after=10)
        except Exception as e:
            await linu.send(f"```py\nError loading {cog}:\n\n{e}\n```")


    @commands.command()
    @commands.check(repo.is_owner)
    async def res(self, linu):
        """ restarts bot """
        try:
            await linu.send("Restarting...", delete_after=2)
            await asyncio.sleep(3)
            os.execv(sys.executable, ['python3'] + sys.argv)
        except Exception as e:
            print(
                f"Error in Restarting:\n{e}")


    @commands.command(aliases=["re"])
    @commands.check(repo.is_owner)
    async def relcog(self, linu, *, cog: str): 
        """ Reload any cog """
        cog = f"cogs.{cog}"
        await linu.send(f"Preparing to reload {cog}...", delete_after=10)
        self.unload_extension(cog)
        try:
            self.load_extension(cog)
            await linu.send(f"{cog} cog was reloaded successfully!", delete_after=10)
        except Exception as e:
            await linu.send(f"```py\nError loading {cog}:\n\n{e}\n```")


if __name__ == '__main__':
    LinuClient.init()
