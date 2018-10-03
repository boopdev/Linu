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
from discord.ext import commands
from urllib.parse import urlparse
from ext import embedtobox
import datetime
import asyncio
import psutil
import random
import json
import os
import io


class Information:
    def __init__(self, bot):
        self.bot = bot


    @commands.command(aliases=['server','si','svi'], no_pm=True)
    @commands.guild_only()
    async def serverinfo(self, linu, server_id : int=None):
        '''See information about the server.'''
        server = self.bot.get_guild(id=server_id) or linu.guild
        total_users = len(server.members)
        online = len([m for m in server.members if m.status != discord.Status.offline])
        text_channels = len([x for x in server.channels if isinstance(x, discord.TextChannel)])
        voice_channels = len([x for x in server.channels if isinstance(x, discord.VoiceChannel)])
        categories = len(server.channels) - text_channels - voice_channels
        passed = (linu.message.created_at - server.created_at).days
        created_at = "Since {}. That's over {} days ago!".format(server.created_at.strftime("%d %b %Y %H:%M"), passed)

        colour = await linu.get_dominant_color(server.icon_url)

        data = discord.Embed(
            description=created_at,
            colour=colour)
        data.add_field(
            name="Region",
            value=str(server.region))
        data.add_field(
            name="Users",
            value="Online:{} Total:{}".format(online, total_users))
        data.add_field(
            name="Text Channels",
            value=text_channels)
        data.add_field(
            name="Voice Channels",
            value=voice_channels)
        data.add_field(
            name="Categories",
            value=categories)
        data.add_field(
            name="Roles",
            value=len(server.roles))
        data.add_field(
            name="Owner",
            value=str(server.owner))
        data.set_footer(
            text="Server ID: " + str(server.id))
        data.set_author(
            name=server.name,
            icon_url=None or server.icon_url)
        data.set_thumbnail(
            url=None or server.icon_url)
        try:
            await linu.send(
                embed=data)
        except discord.HTTPException:
            em_list = await embedtobox.etb(data)
            for page in em_list:
                await linu.send(page)

    @commands.command()
    @commands.guild_only() 
    async def baninfo(self, linu, *, name_or_id):
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

    @commands.command()
    @commands.guild_only() 
    async def bans(self, linu):
        '''See a list of banned users in the guild'''
        try:
            bans = await linu.guild.bans()
        except:
            return await linu.send('i dont have the perms to see bans.')

        em = discord.Embed(
            title=f'List of Banned Members ({len(bans)}):',
            color=0xFFA500)
        em.description = ', '.join([str(b.user) for b in bans])

        await linu.send(embed=em)

    @commands.command(aliases=['ui', 'user'], no_pm=True)
    @commands.guild_only()
    async def userinfo(self, linu, *, member : discord.Member=None):
        '''Get information about a member of a server'''
        server = linu.guild
        user = member or linu.message.author
        avi = user.avatar_url
        roles = sorted(user.roles, key=lambda c: c.position)

        for role in roles:
            if str(role.color) != "#000000":
                color = role.color
        if 'color' not in locals():
            color = 0

        rolenames = ', '.join([r.name for r in roles if r.name != "@everyone"]) or 'None'
        time = linu.message.created_at
        desc = '{0} is chilling in {1} mode.'.format(user.name, user.status)
        member_number = sorted(server.members, key=lambda m: m.joined_at).index(user) + 1

        if user.activity is None:
            playing = f'{user.name} is not playing anything, or it is not a Rich Presence'

        elif user.activity.type == discord.ActivityType.listening and user.activity.name == "Spotify":                       #Duration: {user.activity.dururation[3:].split(".", 1)[0]} 
            playing = f'{user.name} is listening to spotify! Artists: {user.activity.artists}  Album: {user.activity.album} Track: [HERE](https://open.spotify.com/track/{user.activity.track_id}) '

        elif user.activity.state and user.activity.state is None:
            playing = f'{user.name} is playing {user.activity.name}'

        elif user.activity is None:
            playing = f'{user.name} is not playing anything, or it is not a Rich Presence'

        else:
            playing = f'{user.name} is playing `{user.activity.name}` `{user.activity.details}` `{user.activity.state}`'
        em = discord.Embed(
            colour=color,
            description=desc,
            timestamp=time)
        em.add_field(
            name='Playing',
            value=playing,
            inline=True)
        em.add_field(
            name='Nick',
            value=user.nick,
            inline=True)
        em.add_field(
            name='Member No.',
            value=str(member_number),
            inline = True) 
        passed = (linu.message.created_at - user.created_at).days
        em.add_field(
            name='Account Created',
            value="{} thats over {} days ago".format(user.created_at.__format__('%A, %d. %B %Y'), passed))
        em.add_field(
            name='Join Date',
            value=user.joined_at.__format__('%A, %d. %B %Y'))
        em.add_field(
            name='Roles',
            value=rolenames, 
            inline=True)
        em.set_footer(
            text='User ID: '+str(user.id))
        em.set_thumbnail(
            url=avi)
        em.set_author(
            name=user,
            icon_url=avi)

        try:
            await linu.send(
                embed=em)
        except discord.HTTPException:
            em_list = await embedtobox.etb(em)
            for page in em_list:
                await linu.send(page)



def setup(bot):
	bot.add_cog(Information(bot))
