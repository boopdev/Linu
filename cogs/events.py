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

#sync def send_cmd_help(self):
 #   '''Sends command help'''
  #  if self.invoked_subcommand:
   #     pages = self.formatter.format_help_for(self, self.invoked_subcommand)
    #    for page in pages:
     #       await self.send_message(self.message.channel, page)
    #else:
     #   pages = self.formatter.format_help_for(self, self.command)
      #  for page in pages:
       #     await self.send_message(self.message.channel, page)


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
        if isinstance(err, errors.MissingRequiredArgument):
            embed = discord.Embed( # look at that sexy embed
                title="Error :(", # oof
                description=f"You didnt give any args.... Usage (prefix) (command) (args)!", # totally user friendly
                color=0x36393e # l o o k   a t   t h a t 
            )
            embed.set_footer(text=f'Linu#4795') 
            await linu.send(embed=embed) # u s e r   f r i e n d l y

        if isinstance(err, errors.BadArgument):

            _traceback = traceback.format_tb(err.__traceback__)
            _traceback = ''.join(_traceback)
            error = ('```py\n{0}\n```').format(err)
            embed = discord.Embed( # look at that sexy embed
                title="Error :(", # oof
                description=f"BadArgument\n{error}\n\n[Server you can get help in](https://discord.gg/KZ3vXMg)", # totally user friendly
                color=0x36393e # l o o k   a t   t h a t 
            )
            embed.set_footer(text=f'Linu#4795') 
            await linu.send(embed=embed) # u s e r   f r i e n d l y

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
            embed = discord.Embed( # look at that sexy embed
                title="Error :(", # oof
                description=f"Seems you tried to use a command that requires either more permissions or owner\n\nthis incident will be reported and looked at shortly", # totally user friendly
                color=0x36393e # l o o k   a t   t h a t 
            )
            embed.set_footer(text=f'Linu#4795') 
            await linu.send(embed=embed) # u s e r   f r i e n d l y

        elif isinstance(err, errors.CommandOnCooldown): # rate l i m i t
            embed = discord.Embed( # look at that sexy embed
                domcolor = await linu.get_dominant_color(linu.author.avatar_url), # look at that sexy color
                title="Ratelimit", # oof
                description=f"you can use this command in {err.retry_after:.0f} seconds.", # mission failed
                color=0x36393e # we'll get em next time
            )
            embed.set_footer(text='sorry'.format(linu.author)) 
            await linu.send(embed=embed, delete_after=5) # delete after 5 seconds so it dont flood chat
            self.bot.counter["ratelimits"] += 1 # get ratelimited

        elif isinstance(err, errors.CommandNotFound):
            pass # so it dont give errors if you try to do a command thats not a command

    async def on_guild_join(self, guild):
        members = set(guild.members)
        bots = filter(lambda m: m.bot, members)
        bots = set(bots)
        members = len(members) - len(bots)
        try:
            to_send = sorted([chan for chan in guild.channels if chan.permissions_for(guild.me).send_messages and isinstance(chan, discord.TextChannel)], key=lambda x: x.position)[0]
            await to_send.send("Hello! my prefix is 'linu ', to get started use 'linu help'.\n`NOTE\nby using this bot and adding it to your server you agree that this bot can make invites for this server(whether your server is private or public(only the owners can see or use the invite)) **we are required to state this** TO SEE THE FULL STATEMENT DO 'linu tos'`")
            try:
                invite_chan = sorted([chan for chan in guild.channels if chan.permissions_for(guild.me).create_instant_invite and isinstance(chan, discord.TextChannel)], key=lambda x: x.position)[0]
                invite = await invite_chan.create_invite(reason="Invite for devs(do not delete)")
            except:
                invite_msg = "**Invite Unavailable**"
        except IndexError:
            pass
        else:
            pass
         #   invite_msg = f"[**Guild Invite**]({invite})"
        if len(bots) > members:
            sketchy_msg = "\nBot farm alert <@!309025661031415809> <@320576655620046860>"
        else:
            sketchy_msg = ""

        join = discord.Embed(title="Added to Guild", description=f"» Name: {guild.name}\n» ID: {guild.id}\n» Reigion: {guild.region}\n» Members/Bots: `{members}:{len(bots)}`\n» Owner: {guild.owner}{sketchy_msg}\n", color=discord.Color.dark_green())
        join.set_thumbnail(url=guild.icon_url)
        join.set_footer(text=f"Total Guilds: {len(self.bot.guilds)}")
        await self.bot.change_presence(activity=discord.Game(type=0, name=f"with {self.gettotalusers()} users  | linu help"), status=discord.Status.online)
        try:
            channel = self.bot.get_channel(492376070767509523)
            await channel.send(embed=leave)
        except Exception as e:
            print(e)

    async def on_guild_remove(self, guild):
        members = set(guild.members)
        bots = filter(lambda m: m.bot, members)
        bots = set(bots)
        members = len(members) - len(bots)
        leave = discord.Embed(title="Removed from Guild", description=f"» Name: {guild.name}\n» ID: {guild.id}\n» Region: {guild.region}\n» Members/Bots: `{members}:{len(bots)}`\n» Owner: {guild.owner}", color=discord.Color.dark_red())
        leave.set_thumbnail(url=guild.icon_url)
        leave.set_footer(text=f"Total Guilds: {len(self.bot.guilds)}")
        await self.bot.change_presence(activity=discord.Game(type=0, name=f"with {self.gettotalusers()} users  | linu help"), status=discord.Status.online)
        try:
            channel = self.bot.get_channel(492376070767509523)
            await channel.send(embed=leave)
        except Exception as e:
            print(e)

 



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
