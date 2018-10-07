import time
import aiohttp
import discord
import asyncio
import os
import sys

from asyncio.subprocess import PIPE
from discord.ext import commands
from io import BytesIO
from util import repo, default, http, dataIO
from util.chat_formatting import pagify, box
from ext import embedtobox

class Admin:
    def __init__(self, bot):
        self.bot = bot
        self._last_result = None
        self._last_embed = None



    @commands.command()
    @commands.check(repo.is_owner)
    async def update(self, linu):
        """do some CMD stuffs"""
        rb = "```rb\n{0}\n```"
        await linu.channel.trigger_typing()
        await asyncio.sleep(3)
        await linu.send("This may take a bit...")
        
        #input = os.popen(f'git pull {branch} --no-commit --no-edit --ff-only')
        os.execv(sys.executable, [f'git pull master --no-commit --no-edit --ff-only'])

    @commands.command(hidden=True)
    @commands.check(repo.is_owner)
    async def dm(self, linu, id: int, message: str):
        """Dm somebody"""
        user = self.bot.get_user(id)
        if user is not None:
            await user.send(message)

    @commands.command(hidden=True)
    @commands.check(repo.is_owner)
    async def df(self, linu, user: discord.Member = None, *, message: str):
        """Dm somebody"""
        if user is None:
            user = linu.author
        else:
            await user.send(message)

    @commands.command(hidden=True)
    @commands.check(repo.is_owner)
    async def obans(self, linu):
        '''See a list of banned users in the guild'''
        # m m m  g i m m i e  t h o s e  b a n s 
        try:
            bans = await linu.guild.bans()
        # no perms 
        except:
            return await linu.send('I dont have perms ;-;')

        em = discord.Embed(
            title=f'List of Banned Members ({len(bans)}):',
            color=0xFFA500)
        em.description = ', '.join([str(b.user) for b in bans])
        await linu.send(
            embed=em)

    @commands.command(hidden=True)
    @commands.check(repo.is_owner)
    async def obaninfo(self, linu, *, name_or_id):
        '''Check the reason of a ban from the audit logs.'''
        ban = await linu.get_ban(name_or_id)
        em = discord.Embed(
            color=0xFFA500)
        em.set_author(
            name=str(ban.user),
            icon_url=ban.user.avatar_url)
        em.add_field(
            name='Reason',
            value=ban.reason or 'None')
        em.set_thumbnail(
            url=ban.user.avatar_url)
        em.set_footer(
            text=f'User ID: {ban.user.id}')

        await linu.send(
            embed=em)

    @commands.command(hidden=True)
    @commands.check(repo.is_owner)
    async def cogs(self, linu):
        mod = ", ".join(list(self.bot.cogs))
        await linu.send(f"The current modules I can see are:\n{mod}")

    @commands.command(hidden=True)
    @commands.check(repo.is_owner)
    async def servers(self, linu):
        """Lists servers"""
        owner = linu.author
        guilds = sorted(list(self.bot.guilds),
                        key=lambda s: s.name.lower())
        msg = ""
        for i, guild in enumerate(guilds, 1):
            members = set(guild.members)
            bots = filter(lambda m: m.bot, members)
            bots = set(bots)
            members = len(members) - len(bots)
            msg += "`{}:` {} `{} members, {} bots` \n".format(i, guild.name, members, len(bots))

        for page in pagify(msg, ['\n']):
            await linu.send(page)


    @commands.command(hidden=True)
    @commands.check(repo.is_owner)
    async def changestats(self, linu, status: str):
        '''Changes status'''
        status = status.lower()
        if status == 'offline' or status == 'off' or status == 'invisible':
            discordStatus = discord.Status.invisible
        elif status == 'idle':
            discordStatus = discord.Status.idle
        elif status == 'dnd' or status == 'disturb':
            discordStatus = discord.Status.dnd
        elif status == 'online' or status == 'on':
            discordStatus = discord.Status.online
        await self.bot.change_presence(
            status=discordStatus)
        await linu.send(f'**:ok:** Changed status to: **{discordStatus}**')

    @commands.command(hidden=True)
    @commands.check(repo.is_owner)
    async def leaves(self, linu, guild: int):
        """leaves a server"""
        try:
            await self.bot.get_guild(guild).leave()
            await linu.send("Successfully left guild :white_check_mark: ")

        except Exception as e:
            await linu.send(e)


    @commands.command(hidden=True)
    @commands.check(repo.is_owner)
    async def guildsl(self, linu):
        """prints servers"""
        print('Servers connected to:')
        for guild in self.bot.guilds:
            print(guild.name)
            print(guild.id)

    @commands.command(hidden=True)
    async def amiadmin(self, linu):
        """ Are you admin? """
        if linu.author.id == 309025661031415809:
            return await linu.send(f"Yes **{linu.author.name}** of course your admin, your my owner :grin:")

        if linu.author.id in self.config.owners:
            return await linu.send(f"Yes **{linu.author.name}** you are admin rank! ✅")


        await linu.send(f"no, you dont have any owner/dev perms {linu.author.name}")

    @commands.command(hidden=True)
    @commands.check(repo.is_owner)
    async def reload(self, linu, name: str):
        """ Reloads an extension. """
        try:
            self.bot.unload_extension(f"cogs.{name}")
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            await linu.send(f"```\n{e}```")
            return
        await linu.send(f"Reloaded extension **{name}.linu.py**")

    @commands.command(hidden=True)
    @commands.check(repo.is_owner)
    async def reboot(self, linu):
        """ Reboot the bot """
        await linu.send('Rebooting now...')
        time.sleep(1)
        await self.bot.logout()

    @commands.command(hidden=True)
    @commands.check(repo.is_owner)
    async def load(self, linu, name: str):
        """ Reloads an extension. """
        try:
            self.bot.load_extension(f"cogs.{name}")
        except Exception as e:
            await linu.send(f"```diff\n- {e}```")
            return
        await linu.send(f"Loaded extension **{name}.linu.py**")

    @commands.command(hidden=True)
    @commands.check(repo.is_owner)
    async def unload(self, linu, name: str):
        """ Reloads an extension. """
        try:
            self.bot.unload_extension(f"cogs.{name}")
        except Exception as e:
            await linu.send(f"```diff\n- {e}```")
            return
        await linu.send(f"Unloaded extension **{name}.linu.py**")

    @commands.group(hidden=True)
    @commands.check(repo.is_owner)
    async def change(self, linu):
        if linu.invoked_subcommand is None:
            cmds = "\n".join([f"{x.name} - {x.help}" for x in self.bot.all_commands["change"].commands])

            embed = discord.Embed(
                title="Whoops, seems like you didnt use a sub command",
                description=f"To use this you gotta do (prefix) (this command) (sub command)\nSub commands:\n{cmds}",
                color=0xFFA500
            )
            embed.set_footer(
                text=f"USER={linu.message.author.name}#{linu.message.author.discriminator} ID={linu.message.author.id}")
            await linu.send(
                embed=embed)

    @change.command(name="playing")
    @commands.check(repo.is_owner)
    async def change_playing(self, linu, *, playing: str):
        """ Change playing status. """
        try:
            await self.bot.change_presence(
                activity=discord.Game(
                    type=0,
                    name=playing),
                status=discord.Status.online
            )
            await linu.send(f"Successfully changed playing status to **{playing}**")
        except discord.InvalidArgument as err:
            await linu.send(err)
        except Exception as e:
            await linu.send(e)

    @change.command(name="username")
    @commands.check(repo.is_owner)
    async def change_username(self, linu, *, name: str):
        """ Change username. """
        try:
            await self.bot.user.edit(
                username=name)
            await linu.send(f"Successfully changed username to **{name}**")
        except discord.HTTPException as err:
            await linu.send(err)

    @change.command(name="nickname")
    @commands.check(repo.is_owner)
    async def change_nickname(self, linu, *, name: str = None):
        """ Change nickname. """
        try:
            await linu.guild.me.edit(
                nick=name)
            if name:
                await linu.send(f"Successfully changed nickname to **{name}**")
            else:
                await linu.send("Successfully removed nickname")
        except Exception as err:
            await linu.send(err)

    @change.command(name="avatar")
    @commands.check(repo.is_owner)
    async def change_avatar(self, linu, url: str = None):
        """ Change avatar. """
        if url is None and len(linu.message.attachments) == 1:
            url = linu.message.attachments[0].url
        else:
            url = url.strip('<>')

        try:
            bio = await http.get(
                url,
                res_method="read")
            await self.bot.user.edit(avatar=bio)
            await linu.send(f"Successfully changed the avatar. Currently using:\n{url}")
        except aiohttp.InvalidURL:
            await linu.send("The URL is invalid...")
        except discord.InvalidArgument:
            await linu.send("This URL does not contain a useable image")
        except discord.HTTPException as err:
            await linu.send(err)


def setup(bot):
    bot.add_cog(Admin(bot))
