
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
import pip
import json
import os
import io
from util import default

class tags:
    def __init__(self, bot):
        self.bot = bot
        self.channel = default.get("data/channels.json")


    @commands.command()
    async def tags(self, linu, *, text: str=None):
        ''' Get useful bot tags & tutorials '''
        if text is None:
            return await linu.send(
                "You cant leave this blank"
                )
        with open('data/tags.json', 'r') as f:
            s = f.read()
            tags = json.loads(s)
        if text in tags:
            await linu.send(f'{tags[str(text)]}')
        else:

            e = discord.Embed()
            e.color = await linu.get_dominant_color(url=linu.message.author.avatar_url)
            e.add_field(
                name='Tag not found!',
                value=f"There is not a tag called {text}, why not request one?")
            try:
                await linu.send(
                    embed=e)
            except Exception as e:
                await linu.send(
                    f'```{e}```')

    @commands.command(aliases=['tag-add'])
    @commands.cooldown(rate=1, per=8.0, type=commands.BucketType.user)
    async def tagrequest(self, linu, *, tag: str):
        """Request a tag"""
        em = discord.Embed(
            title="Tag request",
            description=tag,
            color=0xff0000)

        author_name = f"User: {linu.message.author} ({linu.message.author.id}) "
        author_name += (f"Channel: \"{linu.channel.name}\" Guild: \"{linu.guild.name}\""
                        if linu.guild else "through DMs")

        em.set_author(
            name=author_name,
            icon_url=linu.message.author.avatar_url)

        channel=self.bot.get_channel(int(self.channel.tag)) 
        await channel.send(
            embed=em)

        em = discord.Embed(title='Tag suggestion sent!',
                           description='Your message has been delivered.',
                           color=0xff0000)
        await linu.send(
            embed=em)

def setup(bot):
    bot.add_cog(tags(bot))
