import time
import discord
import psutil
import os
import json
import secrets

from discord.ext import commands
from datetime import datetime
from util import repo, default
from ext.formatter import EmbedHelp
from ext import context
from util.chat_formatting import pagify, box
from pathlib import Path
from util import permissions, default


class welcome:
    def __init__(self, bot):
        self.bot = bot
        self.process = psutil.Process(os.getpid())
        self.totalmembers = set({})
        self.emote = default.get("emotes.json")
        self.formatter = EmbedHelp()



    async def on_member_join(self, member):

        guild = member.guild
        welcome_path = Path(f"data/welcome/{guild.id}.json")
        if welcome_path.is_file():
            welcome_config = default.get(f'data/welcome/{guild.id}.json')
            welcome_message = welcome_config.welcome_message
            channel_dest = int(welcome_config.channel)
            channel = self.bot.get_channel(channel_dest)
            embed = discord.Embed( 
                description=welcome_message,
                color=0x36393e)
            await channel.send(embed=embed)

 
        else:
            pass



    @commands.group()
    @permissions.has_permissions(manage_server=True)
    async def welcome(self, linu):
        """Welcomer commands"""
        if linu.invoked_subcommand is None:
            cmds = "\n".join([f"{x.name} - {x.help}" for x in self.bot.all_commands["welcome"].commands])

            embed = discord.Embed(
                title="Whoops, seems like you didnt use a sub command",
                description=f"Hey there! just wanna say we cant do anything more than text (mentions and so on cant be done)\nif you want embeds just use (embed) (welcome) (embed)\nTo use this you gotta do (prefix) (this command) (sub command)\nSub commands:\n{cmds}",
                color=0xFFA500
            )
            embed.set_footer(text=f"USER={linu.message.author.name}#{linu.message.author.discriminator} ID={linu.message.author.id} GUILD={linu.guild.name} CHANNEL={linu.channel.name}")
            await linu.send(embed=embed)




    @welcome.command(name="create")
    async def start(self, linu):
        """  Creates a json welcome for you!  """
        fileopen = r"data/welcome/" + str(linu.guild.id) + ".json"
        file = open(fileopen, "w", encoding="utf-8")
        data = {}
        data["guild"] = f"NAME={linu.guild.name} ID={linu.guild.id} OWNER={linu.guild.owner}"
        data["welcome_message"] = "Not specified"
        data["channel"] = f"{linu.channel.id}"
        data["user"] = "ID: " + str(linu.message.author.id) +  " Username: " + str(linu.message.author.name) + "#" + str(linu.message.author.discriminator) + " <<< Creator"
        json.dump(data, file, ensure_ascii=False)
        file.close()
        embed = discord.Embed(
            title="Welcomer",
            description=f"Welcomer has started! Remember to use an id when editing the channel\nWelcomer has been set to {linu.channel.name} by default",
            color=0xFFA500
        )
        embed.set_footer(text=f"USER={linu.message.author.name}#{linu.message.author.discriminator} ID={linu.message.author.id}")
        await linu.send(embed=embed)

    @commands.group()
    @permissions.has_permissions(manage_server=True)
    async def editwelcome(self, linu):
        """Edit your welcome stuff"""
        if linu.invoked_subcommand is None:
            cmds = "\n".join([f"{x.name} - {x.help}" for x in self.bot.all_commands["editwelcome"].commands])

            embed = discord.Embed(
                title="Whoops, seems like you didnt use a sub command",
                description=f"To use this you gotta do (prefix) (this command) (sub command)\nSub commands:\n{cmds}",
                color=0xFFA500
            )
            embed.set_footer(text=f"USER={linu.message.author.name}#{linu.message.author.discriminator} ID={linu.message.author.id}")
            await linu.send(embed=embed)

    @editwelcome.command(name="name")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def message(self, linu, *args):
        """Sets welcome message"""
        try:
            fileopen = r"data/welcome/" + str(linu.guild.id) + ".json"
            file = open(fileopen, "r", encoding="utf-8")
            predata = json.load(file)
            prechannel = predata["channel"]
            file = open(fileopen, "w", encoding="utf-8")
            data = {}
            data["guild"] = f"NAME={linu.guild.name} ID={linu.guild.id} OWNER={linu.guild.owner}"
            data["welcome_message"] = " ".join(args).replace("/{}/g", " ")
            data["channel"] = prechannel
            data["user"] = "ID: " + str(linu.message.author.id) +  " Username: " + str(linu.message.author.name) + "#" + str(linu.message.author.discriminator) + " <<< Creator"
            json.dump(data, file, ensure_ascii=False)
            file.close()
            profilem = discord.Embed(
                title=f"The message was edited",
                description=f"Your welcome message has been edited, if any errors pop up just contact my owner.",
                color=0xFFA500)
            await linu.send(embed=profilem)
        except KeyError:
            await linu.send("There was a error editing the JSON, please contact the owner with your error. Error **'KeyError' Code: 1**")







    @editwelcome.command(name="")
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    async def channel(self, linu, *args):
        """sets channel"""
        try:
            fileopen = r"data/welcome/" + str(linu.guild.id) + ".json"
            file = open(fileopen, "r", encoding="utf-8")
            predata = json.load(file)
            prewelcome = predata["welcome_message"]
            file = open(fileopen, "w", encoding="utf-8")
            data = {}
            data["guild"] = f"NAME={linu.guild.name} ID={linu.guild.id} OWNER={linu.guild.owner}"
            data["welcome_message"] = prewelcome
            data["channel"] = " ".join(args).replace("/{}/g", " ")
            data["user"] = "ID: " + str(linu.message.author.id) +  " Username: " + str(linu.message.author.name) + "#" + str(linu.message.author.discriminator) + " <<< Creator"
            json.dump(data, file, ensure_ascii=False)
            file.close()
            profilem = discord.Embed(
                title=f"channel changed",
                description=f"Your Welcomer channel has been changed",
                color=0xFFA500)
            await linu.send(embed=profilem)
        except KeyError:
            await linu.send("There was a error editing the JSON, please contact the owner with your error. Error **'KeyError' Code: 1**")

    #@editwelcome.command(name="")
   # @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
 #   async def embedtrue(self, linu, *args):
#        """sets embed to true"""
 #       try:
 #           fileopen = r"data/welcome/" + str(linu.guild.id) + ".json"
#            file = open(fileopen, "r", encoding="utf-8")
 #           predata = json.load(file)
  #          prewelcome = predata["welcome_message"]
   #         file = open(fileopen, "w", encoding="utf-8")
    #        data = {}
     #       data["guild"] = f"NAME={linu.guild.name} ID={linu.guild.id} OWNER={linu.guild.owner}"
      #      data["welcome_message"] = prewelcome
       #     data["channel"] = " ".join(args).replace("/{}/g", " ")
        #    data["user"] = "ID: " + str(linu.message.author.id) +  " Username: " + str(linu.message.author.name) + "#" + str(linu.message.author.discriminator) + " <<< Creator"
         #   data["embed"] = "True"
          #  json.dump(data, file, ensure_ascii=False)
           # file.close()
            #profilem = discord.Embed(
           #     title=f"embed changed",
         #       description=f"Your embed has been changed to true",
       #         color=0xFFA500)
     #       await linu.send(embed=profilem)
   #     except KeyError:
 #           await linu.send("There was a error editing the JSON, please contact the owner with your error. Error **'KeyError' Code: 1**")
#
 #   @editwelcome.command(name="")
  #  @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
   # async def embedfalse(self, linu, *args):
    #    """sets channel"""
     #   try:
      #      fileopen = r"data/welcome/" + str(linu.guild.id) + ".json"
       #     file = open(fileopen, "r", encoding="utf-8")
        #    predata = json.load(file)
         #   prewelcome = predata["welcome_message"]
          #  file = open(fileopen, "w", encoding="utf-8")
           # data = {}
            #data["guild"] = f"NAME={linu.guild.name} ID={linu.guild.id} OWNER={linu.guild.owner}"
            #data["welcome_message"] = prewelcome
           # data["channel"] = " ".join(args).replace("/{}/g", " ")
          #  data["user"] = "ID: " + str(linu.message.author.id) +  " Username: " + str(linu.message.author.name) + "#" + str(linu.message.author.discriminator) + " <<< Creator"
         #   data["embed"] = "False"
        #    json.dump(data, file, ensure_ascii=False)
       #     file.close()
      #      profilem = discord.Embed(
     #           title=f"embed changed",
    #            description=f"Your embed has been changed to false",
   #             color=0xFFA500)
  #          await linu.send(embed=profilem)
 #       except KeyError:
#            await linu.send("There was a error editing the JSON, please contact the owner with your error. Error **'KeyError' Code: 1**")

def setup(bot):
    bot.add_cog(welcome(bot))
