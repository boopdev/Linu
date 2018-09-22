import discord
import traceback
import psutil
import os
import random
import asyncio

from collections import Counter
from datetime import datetime
from discord.ext.commands import errors
from util import default, permissions
from ext import fuzzy
from ext import embedtobox
from PIL import Image

async def send_cmd_help(linu):
    if linu.invoked_subcommand:
        _help = await linu.bot.formatter.format_help_for(linu, linu.invoked_subcommand)
    else:
        _help = await linu.bot.formatter.format_help_for(linu, linu.command)

    for page in _help:
        await linu.send(page)


class Events:
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process(os.getpid())
        self.totalmembers = set({})
        self.counter = Counter()

    def gettotalusers(self): # oof not alot of users
        for x in self.bot.guilds:
            for y in x.members:
                self.totalmembers.add(y.id)
        return len(self.totalmembers)



    async def on_command_error(self, linu, err): #  g e t   c l a p p e d   e r r o r s
        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            await send_cmd_help(linu)

        elif isinstance(err, errors.CommandInvokeError):
            err = err.original

            _traceback = traceback.format_tb(err.__traceback__)
            _traceback = ''.join(_traceback)
            error = ('```py\n{2}{0}: {3}\n```').format(
                type(err).__name__, linu.message.content, _traceback, err)
            embed = discord.Embed( # look at that sexy embed
                title="Error :(", # oof
                description=f"Please contact the owner about this.\n[Server you can get help in](https://discord.gg/KZ3vXMg)\n{error}", # totally user friendly
                color=0x36393e # l o o k   a t   t h a t 
            )
            embed.set_footer(text=f'Linu#4795') 
            await linu.send(embed=embed) # u s e r   f r i e n d l y
            self.bot.counter["errors"] += 1 # oof so many errors


        elif isinstance(err, errors.CheckFailure): # for the repo (?)
            pass

        elif isinstance(err, errors.CommandOnCooldown): # rate l i m i t
            embed = discord.Embed( # look at that sexy embed
                domcolor = await linu.get_dominant_color(linu.author.avatar_url), # look at that sexy color
                title="Ratelimit", # oof
                description=f"you can use this command in {err.retry_after:.0f} seconds.", # mission failed
                color=domcolor # we'll get em next time
            )
            embed.set_footer(text='sorry'.format(linu.author)) 
            await linu.send(embed=embed, delete_after=5) # delete after 5 seconds so it dont flood chat
            self.bot.counter["ratelimits"] += 1 # get ratelimited

        elif isinstance(err, errors.CommandNotFound):
            pass # so it dont give errors if you try to do a command thats not a command

    async def on_guild_join(self, guild): # log guild joining
        members = set(guild.members)
        bots = filter(lambda m: m.bot, members)
        bots = set(bots)
        members = len(members) - len(bots)
        try:
            to_send = sorted([chan for chan in guild.channels if chan.permissions_for(guild.me).send_messages and isinstance(chan, discord.TextChannel)], key=lambda x: x.position)[0]
            try:
                invite_chan = sorted([chan for chan in guild.channels if chan.permissions_for(guild.me).create_instant_invite and isinstance(chan, discord.TextChannel)], key=lambda x: x.position)[0]
                invite = await invite_chan.create_invite(reason="Don't mind me :eyes:")
            except:
                invite_msg = "**Invite Unavailable** ?contact owner or leave it?"
        except IndexError:
            pass
        else:
            await to_send.send("Hello! my prefix is 'linu ', to get started use 'linu help'.")
            invite_msg = f"[**Guild Invite**]({invite})"
        if len(bots) > members:
            sketchy_msg = "\n<:blobdoggothink:444122378260185088> **More Bots than users**"
        else:
            sketchy_msg = ""

        channel = self.bot.get_channel(492376070767509523) # channel ID goes here
        join = discord.Embed(title="Added to Guild ", description=f"» Name: {guild.name}\n» ID: {guild.id}\n» Reigion: {guild.region}\n» Members/Bots: `{members}:{len(bots)}`\n» Owner: {guild.owner}{sketchy_msg}\n» {invite_msg}", color=0xff00da)
        join.set_thumbnail(url=guild.icon_url)
        join.set_footer(text=f"Total Guilds: {len(self.bot.guilds)}")
        await channel.send(embed=join)
        await self.bot.change_presence(activity=discord.Game(type=0, name=f"with {self.gettotalusers()} users  | linu help"), status=discord.Status.online)


    async def on_guild_remove(self, guild): # log guild leaving
        channel = self.bot.get_channel(492376070767509523) # channel ID goes here
        members = set(guild.members)
        bots = filter(lambda m: m.bot, members)
        bots = set(bots)
        members = len(members) - len(bots)
        leave = discord.Embed(title="Removed from Guild", description=f"» Name: {guild.name}\n» ID: {guild.id}\n» Region: {guild.region}\n» Members/Bots: `{members}:{len(bots)}`\n» Owner: {guild.owner}", color=0x9905ac)
        leave.set_thumbnail(url=guild.icon_url)
        leave.set_footer(text=f"Total Guilds: {len(self.bot.guilds)}")
        await channel.send(embed=leave)
        await self.bot.change_presence(activity=discord.Game(type=0, name=f"with {self.gettotalusers()} users  | linu help"), status=discord.Status.online)

    async def on_message_edit(self, before, after):
        """Reads edited messages"""
        if not self.bot.is_ready() or after.author.bot or not permissions.can_send(after):
            return # go away bots

        await self.bot.process_commands(after) # p r o c e s   t h o s e   c o m m a n d s
        self.bot.counter["commands_ran"] += 1 # adds one to counter 

    async def on_message(self, message):
        """Every message sent (that the bot can see) adds one to the counter"""
        self.bot.counter["messages_read"] += 1 # adds one to counter

    async def on_ready(self):
        """When bot is ready it will print how many server and users it is in and set the uptime"""
        if not hasattr(self.bot, 'uptime'):
            self.bot.uptime = datetime.utcnow()
        await self.bot.change_presence(activity=discord.Game(type=0, name=f"with {self.gettotalusers()} users  | linu help"), status=discord.Status.online)

        print(f'Servers: {len(self.bot.guilds)} | Users: {len(set(self.bot.get_all_members()))}')
        print('---------------')

    async def on_command(self, linu):
        """Adds one to the counter every command its runs"""
        self.bot.counter["commands_ran"] += 1





def setup(bot):
    bot.add_cog(Events(bot))
