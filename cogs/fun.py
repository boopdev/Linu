import random
import discord
import json
import aiohttp
import asyncio
import async_timeout

from io import BytesIO
from discord.ext import commands
from util import lists, permissions, http, default
from random import randint

class Fun_Commands:
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def hug(self, linu, user: discord.Member):
        if user is None:
            await linu.send("You need to @ someone ;-;")
            return
        isVideo = True
        while isVideo:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://api.computerfreaker.cf/v1/hug') as resp:
                    res = await resp.json()
                    res = res['url']
                    cs.close()
            if res.endswith('.mp4'):
                pass
            else:
                isVideo = False
        em = discord.Embed()
        await linu.send(content=f"**{linu.author.mention}** hugged **{user.mention}**",embed=em.set_image(url=res))

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def hit(self, linu, user: discord.Member = None):
        if user is None:
            await linu.send("You need to @ someone ;-;")
            return
        choices = ['http://s.orzzzz.com/news/b2/fa//57454a6136143.gif', 'https://i.pinimg.com/originals/8a/d3/39/8ad33953eca9fe56dcf79f57f0c04883.gif', 'https://i.pinimg.com/originals/62/b6/a6/62b6a6963250f990123ccd7f08dfbb6e.gif', 'https://i.imgur.com/nMeoCkW.gif', 'http://gifimage.net/wp-content/uploads/2017/08/one-punch-man-mosquito-gif-15.gif']

        image = random.choice(choices)

        em = discord.Embed()
        await linu.send(content=f"**{linu.author.mention}** KO'd **{user.mention}**", embed=em.set_image(url=image))

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def boop(self, linu, user: discord.Member = None):
        if user is None:
            await linu.send("You need to @ someone ;-;")
            return
        choices = ['http://i.imgur.com/fZmUTgw.gif', 'http://i.imgur.com/787H2cR.gif', 'https://media.giphy.com/media/LhIfr7B8EvToc/giphy.gif']

        image = random.choice(choices)

        em = discord.Embed()
        await linu.send(content=f"**{linu.author.mention}** booped **{user.mention}**", embed=em.set_image(url=image))

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def kiss(self, linu, user: discord.Member = None):
        if user is None:
            await linu.send("You need to @ someone ;-;")
            return
        choices = ['https://media.giphy.com/media/12VXIxKaIEarL2/giphy.gif', 'https://media1.tenor.com/images/78095c007974aceb72b91aeb7ee54a71/tenor.gif?itemid=5095865', 'https://media1.tenor.com/images/f5167c56b1cca2814f9eca99c4f4fab8/tenor.gif?itemid=6155657', 'https://orig00.deviantart.net/fda1/f/2017/339/6/c/ladynoir_kiss_gif__colored_version__by_ambarnarutofrek1-dbvk1l8.gif', 'https://media.giphy.com/media/ZRSGWtBJG4Tza/giphy.gif']

        image = random.choice(choices)

        em = discord.Embed()
        await linu.send(content=f"**{linu.author.mention}** passionately kissed **{user.mention}**", embed=em.set_image(url=image))


    @commands.command()
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def rate(self, linu, *, thing: commands.clean_content):
        """ Rates what you desire """
        n = random.randint(0, 100)
        d = random.randint(0, 9)

        if n == 100:
            d = 0

        await linu.send(f"I'd rate {thing} a **{n}.{d} / 100**")





    @commands.command(aliases=['slots', 'bet'])
    @commands.cooldown(rate=1, per=3.0, type=commands.BucketType.user)
    async def slot(self, linu):
        """ Roll the slot machine """
        emojis = "🍎🍊🍐🍋🍉🍇🍓🍒"
        a = random.choice(emojis)
        b = random.choice(emojis)
        c = random.choice(emojis)

        if (a == b == c):
            message = 'and won! 🎉'
        elif (a == b) or (a == c) or (b == c):
            message = 'and almost won (2/3)'
        else:
            message = 'and lost...'

        result = f"**{linu.author.name}** rolled the slots...\n**[ {a} {b} {c} ]**\n{message}"
        await linu.send(result)

def setup(bot):
    bot.add_cog(Fun_Commands(bot))
