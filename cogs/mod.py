'''
MIT License

Copyright (c) 2017 Grok

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import discord
import re

from io import BytesIO
from discord.ext import commands
from util import permissions, default
from ext import embedtobox


# Source: https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/mod.py
class MemberID(commands.Converter):
    async def convert(self, linu, argument):
        try:
            m = await commands.MemberConverter().convert(linu, argument)
        except commands.BadArgument:
            try:
                return int(argument, base=10)
            except ValueError:
                raise commands.BadArgument(f"{argument} is not a valid member or member ID.") from None
        else:
            can_execute = linu.author.id == linu.bot.owner_id or \
                          linu.author == linu.guild.owner or \
                          linu.author.top_role > m.top_role

            if not can_execute:
                raise commands.BadArgument('You cannot do this action on this user due to role hierarchy.')
            return m.id


class ActionReason(commands.Converter):
    async def convert(self, linu, argument):
        ret = argument

        if len(ret) > 512:
            reason_max = 512 - len(ret) - len(argument)
            raise commands.BadArgument(f'reason is too long ({len(argument)}/{reason_max})')
        return ret


class Moderator:
    def __init__(self, bot):
        self.bot = bot



    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(kick_members=True)
    async def kick(self, linu, member: discord.Member, *, reason: str = None):
        """ Kicks a user from the current server. """
        try:
            await member.kick(reason=default.responsible(linu.author, reason))
            await linu.send(default.actionmessage("kicked"))
        except Exception as e:
            await linu.send(e)



    @commands.command(aliases=["nick"])
    @commands.guild_only()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    @permissions.has_permissions(manage_nicknames=True)
    async def nickname(self, linu, member: discord.Member, *, name: str = None):
        """ Nicknames a user from the current server. """
        try:
            await member.edit(nick=name, reason=default.responsible(linu.author, "Changed by command"))
            message = f"Changed **{member.name}'s** nickname to **{name}**"
            if name is None:
                message = f"Reset **{member.name}'s** nickname"
            await linu.send(message)
        except Exception as e:
            await linu.send(e)

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(ban_members=True)
    async def ban(self, linu, member: MemberID = None, *, reason: str = None):
        """ Bans a user from the current server. """
        if member is None:
            await linu.send("You didnt mention someone...?")
            pass
        try:
            await linu.guild.ban(discord.Object(id=member), reason=default.responsible(linu.author, reason))
            await linu.send(default.actionmessage("banned"))
        except Exception as e:
            await linu.send(e)

    @commands.command()
    @commands.guild_only()
    @commands.cooldown(rate=1, per=10.0, type=commands.BucketType.user)
    @permissions.has_permissions(ban_members=True)
    async def massban(self, linu, reason: ActionReason, *members: MemberID):
        """ Mass bans multiple members from the server. """

        try:
            for member_id in members:
                await linu.guild.ban(discord.Object(id=member_id), reason=default.responsible(linu.author, reason))
            await linu.send(default.actionmessage("massbanned", mass=True))
        except Exception as e:
            await linu.send(e)

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(ban_members=True)
    async def unban(self, linu, member: MemberID, *, reason: str = None):
        """ Bans a user from the current server. """
        if member is None:
            await linu.send("You didnt mention someone...?")
            pass
        try:
            await linu.guild.unban(discord.Object(id=member), reason=default.responsible(linu.author, reason))
            await linu.send(default.actionmessage("unbanned"))
        except Exception as e:
            await linu.send(e)

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def mute(self, linu, member: discord.Member, *, reason: str = None):
        """ Mutes a user from the current server. """
        message = []
        for role in linu.guild.roles:
            if role.name == "Muted":
                message.append(role.id)
        try:
            therole = discord.Object(id=message[0])
        except IndexError:
            return await linu.send("Are you sure you've made a role called **Muted**? Remember that it's case sensetive too...")

        try:
            await member.add_roles(therole, reason=default.responsible(linu.author, reason))
            await linu.send(default.actionmessage("muted"))
        except Exception as e:
            await linu.send(e)

    @commands.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def unmute(self, linu, member: discord.Member, *, reason: str = None):
        """ Mutes a user from the current server. """
        message = []
        for role in linu.guild.roles:
            if role.name == "Muted":
                message.append(role.id)
        try:
            therole = discord.Object(id=message[0])
        except IndexError:
            return await linu.send("Are you sure you've made a role called **Muted**? Remember that it's case sensetive too...")

        try:
            await member.remove_roles(therole, reason=default.responsible(linu.author, reason))
            await linu.send(default.actionmessage("unmuted"))
        except Exception as e:
            await linu.send(e)

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def role(self, linu):
        """Roles commands"""
        if linu.invoked_subcommand is None:
            cmds = "\n".join([f"{x.name} - {x.help}" for x in self.bot.all_commands["role"].commands])

            embed = discord.Embed(
                title="Whoops, seems like you didnt use a sub command",
                description=f"To use this you gotta do (prefix) (this command) (sub command)\nSub commands:\n{cmds}",
                color=0xFFA500
            )
            embed.set_footer(text=f"USER={linu.message.author.name}#{linu.message.author.discriminator} ID={linu.message.author.id}")
            await linu.send(embed=embed)


    @role.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def addrole(self, linu, member: discord.Member, *, rolename: str):
        '''Add a role to someone else.'''
        if member is None:
            linu.send("Mention someone please")

        if rolename is None:
            linu.send("Give a role please")

        role = discord.utils.find(lambda m: rolename.lower() in m.name.lower(), linu.message.guild.roles)
        if not role:
            return await linu.send('That role does not exist.')
        try:
            await member.add_roles(role)
            await linu.send(f'Added: `{role.name}`')
        except:
            await linu.send("I don't have the perms to add that role.")


    @role.command()
    @commands.guild_only()
    @permissions.has_permissions(manage_roles=True)
    async def removerole(self, linu, member: discord.Member, *, rolename: str):
        '''Remove a role from someone else.'''
        role = discord.utils.find(lambda m: rolename.lower() in m.name.lower(), linu.message.guild.roles)
        if not role:
            return await linu.send('That role does not exist.')
        try:
            await member.remove_roles(role)
            await linu.send(f'Removed: `{role.name}`')
        except:
            await linu.send("I don't have the perms to remove that role.")


    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    @permissions.has_permissions(manage_server=True)
    async def lockdown(self, linu):
        """Server/Channel lockdown"""
        if linu.invoked_subcommand is None:
            cmds = "\n".join([f"{x.name} - {x.help}" for x in self.bot.all_commands["lockdown"].commands])

            embed = discord.Embed(
                title="Whoops, seems like you didnt use a sub command",
                description=f"To use this you gotta do (prefix) (this command) (sub command)\nSub commands:\n{cmds}",
                color=0xFFA500
            )
            embed.set_footer(text=f"USER={linu.message.author.name}#{linu.message.author.discriminator} ID={linu.message.author.id}")
            await linu.send(embed=embed)

    @lockdown.command(aliases=['channel'])
    async def chan(self, linu, channel = None,  *, reason = None):
        if channel is None: channel = linu.channel
        try:
            await channel.set_permissions(linu.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages = False), reason=reason)
            await linu.send("Done")
        except Exception as e:
            await linu.send(e)
    @lockdown.command()
    async def server(self, linu, server:discord.Guild = None, *, reason=None):
        if server is None: server = linu.guild
        try:
            for channel in server.channels:
                await channel.set_permissions(linu.guild.default_role, overwrite=discord.PermissionOverwrite(send_messages = False), reason=reason)
                await linu.send("Done")
        except Exception as e:
            await linu.send(e)



def setup(bot):
    bot.add_cog(Moderator(bot))
