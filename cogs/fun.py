import aiohttp
import aiohttp
import async_timeout
import asyncio
import asyncio
import cv2
import discord
import io
import json
import numpy as np
import pytesseract
import qrcode
import random
import random
import re
import tempfile
import unidecode

import datetime
import json
import time
import urllib.request

from PIL import Image
from PIL import Image
from PIL import ImageDraw
from PIL import ImageEnhance
from PIL import ImageFilter
from PIL import ImageFont
from PIL import ImageOps
from discord.ext import commands
from ext import embedtobox
from ext import fuzzy
from functools import partial
from io import BytesIO
from pathlib import Path
from pokedex import pokedex
from random import randint
from typing import Union
from util import default
from util import http
from util import lists
from util import permissions


class Fun_Commands:
    def __init__(self, bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=self.bot.loop)

    @commands.command()
    @commands.cooldown(rate=1, per=12, type=commands.BucketType.user)
    async def shit(self, linu, user: discord.Member = None):
        ''': Show em how shitty they are'''
        x = Image.open("SHIT.png")
        async with aiohttp.ClientSession() as cs:
            async with cs.get(user.avatar_url_as(format='png')) as r:
                b = io.BytesIO(await r.read())
        # open the pic and give it an alpha channel so it's transparent
        im1 = Image.open(b).convert('RGBA')
        im4 = im1.resize((120, 200))
        # rotate it and expand it's canvas so the corners don't get cut off:
        im2 = im4.rotate(-45, expand=1)

        # note the second appearance of im2, that's necessary to paste without a bg
        x.paste(im2, (200, 655), im2)
        x.save("SHIT_tmp.png")
        await linu.send(file=discord.File("SHIT_tmp.png"))

    @commands.command()
    @commands.cooldown(rate=1, per=15, type=commands.BucketType.guild)
    async def meme(self, linu):
        # Returns a dictonary with the title, content and url to the post
        # This will error if it gets any http code other than 200

        req = urllib.request.Request(
            'https://old.reddit.com/r/dank_meme/random.json',
            data=None,
            headers={
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            }
        )

        f = urllib.request.urlopen(req)
        response = json.loads(f.read().decode('utf-8'))
        post = response[0]["data"]["children"][0]["data"]
        embed = discord.Embed(
            description="[" + post["title"] + "](" + post["url"] + ")"
        )
        #start = datetime.timedelta()
        #PERIOD_OF_TIME = 10
        i = 0
        isVideo = True
        while isVideo is True:
            if i == 25:
                await linu.send("Cant find a meme (25 attempt loop break)")
                break

            # if datetime.timedelta() > start + PERIOD_OF_TIME:
            #    await linu.send("Cant find a meme (10s loop break)")
            #    isVideo = True
            #    break
            #    break

            if post["url"].startswith("https://i."):
                isVideo = False
            elif post["url"].startswith("https://v."):
                isVideo = True
                i += 1
            else:
                isVideo = True
            await asyncio.sleep(0.7)

        if isVideo is False:
            try:
                embed.set_image(url=post["url"])
                await linu.send(embed=embed)
            except Exception:
                await linu.send("Cant send the content, heres the link\n" + post["url"])
        else:
            return

    @commands.command()
    @commands.cooldown(rate=1, per=8, type=commands.BucketType.guild)
    async def copypasta(self, linu):
        # Returns a dictonary with the title, content and url to the post
        # This will error if it gets any http code other than 200
        if linu.channel.is_nsfw():
            req = urllib.request.Request(
                'https://old.reddit.com/r/copypasta/random.json',
                data=None,
                headers={
                    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
                }
            )

            f = urllib.request.urlopen(req)
            response = json.loads(f.read().decode('utf-8'))
            post = response[0]["data"]["children"][0]["data"]
            embed = discord.Embed(
                title=post["title"],
                description=post["selftext"]
            )
            embed.set_footer(text=post["url"])
            try:
                await linu.send(embed=embed)
            except Exception:
                await linu.send("Cant send the content, heres the link\n" + post["url"])

        else:
            await linu.send("Nope, gotta be nsfw channel my guy")

    @commands.command()
    @commands.cooldown(rate=1, per=12, type=commands.BucketType.user)
    async def shrug(self, linu, user: discord.Member = None):
        if user is None:
            user = linu.author

        img1 = Image.open(fp=open("shrug.png", "rb"))
        async with aiohttp.ClientSession() as session:
            avatar = await session.get(user.avatar_url_as(format="png"))
            data = await avatar.read()
            av_bytes = BytesIO(data)
            avatar = Image.open(av_bytes)
            dest = (155, 70)
        size = avatar.size
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        av = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
        av.putalpha(mask)

        face_1 = av.resize((78, 78), Image.LANCZOS)
        face_1 = face_1.rotate(15, expand=True)

        img1.paste(face_1, dest, face_1)

        dest = (351, 43)
        size = avatar.size
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        av = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
        av.putalpha(mask)

        face_2 = av.resize((36, 36), Image.LANCZOS)
        face_2 = face_2.rotate(-4, expand=True)

        img1.paste(face_2, dest, face_2)

        dest = (350, 225)
        size = avatar.size
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        av = ImageOps.fit(avatar, mask.size, centering=(0.5, 0.5))
        av.putalpha(mask)

        face_3 = av.resize((40, 40), Image.LANCZOS)
        face_3 = face_3.rotate(5, expand=True)

        img1.paste(face_3, dest, face_3)

        processed = BytesIO()
        img1.save(processed, format="PNG")
        await linu.send(file=discord.File(fp=processed.getvalue(), filename="shrugged.png"))

    @commands.command()
    @commands.cooldown(rate=1, per=12, type=commands.BucketType.user)
    async def qr(self, linu, *, text: str=None):
        if not text:
            return await linu.send("You forgot to include text.")
        img = qrcode.make(text)
        output = BytesIO()
        img.save('qr.png', optimize=True, quality=85)
        output.seek(0)
        await linu.channel.send(file=discord.File('qr.png'))

    @commands.command()
    async def trumptweet(self, linu, *, text: str=None):
        """Makes trump tweet what you say."""
        if text is None:
            await linu.send('You didn\'t tell what I should tweet.')
            return

        image = Image.open("trump_tweet_temp.jpg")
        draw = ImageDraw.Draw(image)
        #font = ImageFont.truetype('arial.ttf', 17)

        (x, y) = (15, 60)
        (x2, y2) = (15, 90)
        (x3, y3) = (15, 110)
        if len(text) > 120:
            await linu.send('The message is too long.')
        else:
            message = re.findall('.{1,40}', text)
        color = 'rgb(0,0,0)'
        if message[0]:
            draw.text((x, y), message[0], fill=color)
        if len(message) == 2:
            draw.text((x2, y2), message[1], fill=color)
        if len(message) == 3:
            draw.text((x2, y2), message[1], fill=color)
            draw.text((x3, y3), message[2], fill=color)
        image.save('tweet.png', optimize=True, quality=85)
        await linu.channel.send(file=discord.File('tweet.png'))

    @commands.command()
    @commands.cooldown(rate=1, per=12, type=commands.BucketType.user)
    async def ohno(self, linu, *, text: str=None):
        """Makes the dog say what you say."""
        if text is None:
            await linu.send('what should the dog should say.')
        else:
            image = Image.open("ohno_temp.png")
            draw = ImageDraw.Draw(image)
            #font = ImageFont.truetype('arial.ttf', 25)

            (x, y) = (320, 50)
            (x2, y2) = (320, 72)
            (x3, y3) = (320, 100)
            if len(text) > 51:
                await linu.send('The message is too long.')
            else:
                message = re.findall('.{1,17}', text)
                color = 'rgb(0,0,0)'

                draw.text((x, y), message[0], fill=color, font=font)
                if len(message) == 2:
                    draw.text((x2, y2), message[1], fill=color)
                if len(message) == 3:
                    draw.text((x2, y2), message[1], fill=color)
                    draw.text((x3, y3), message[2], fill=color)
                image.save('ohno.png', optimize=True, quality=85)
                await linu.channel.send(file=discord.File('ohno.png'))

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def linu(self, kit):
        """linu's! floofy linu"""
        isVideo = True
        while isVideo:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://randomlinu.ca/floof/') as resp:
                    res = await resp.json()
                    res = res['image']
                    cs.close()
            if res.endswith('.mp4'):
                pass
            else:
                isVideo = False
        em = discord.Embed()
        await kit.send(embed=em.set_image(url=res))

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def anime(self, kit):
        """Weeb shit"""
        isVideo = True
        while isVideo:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://api.computerfreaker.cf/v1/anime') as resp:
                    res = await resp.json()
                    res = res['url']
                    cs.close()
            if res.endswith('.mp4'):
                pass
            else:
                isVideo = False
        em = discord.Embed()
        await kit.send(embed=em.set_image(url=res))

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def neko(self, kit):
        """some cat girls"""
        isVideo = True
        while isVideo:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://nekos.life/api/neko') as resp:
                    res = await resp.json()
                    res = res['neko']
                    cs.close()
            if res.endswith('.mp4'):
                pass
            else:
                isVideo = False
        em = discord.Embed()
        await kit.send(embed=em.set_image(url=res))

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def duck(self, kit):
        """QUACK"""
        isVideo = True
        while isVideo:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://random-d.uk/api/v1/random') as resp:
                    res = await resp.json()
                    res = res['url']
                    cs.close()
            if res.endswith('.mp4'):
                pass
            else:
                isVideo = False
        em = discord.Embed()
        await kit.send(embed=em.set_image(url=res))

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def dog(self, kit):
        """Only the goodest boys"""
        isVideo = True
        while isVideo:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://random.dog/woof.json') as resp:
                    res = await resp.json()
                    res = res['url']
                    cs.close()
            if res.endswith('.mp4'):
                pass
            else:
                isVideo = False
        em = discord.Embed()
        await kit.send(embed=em.set_image(url=res))

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def cat(self, kit):
        """The little satans"""
        isVideo = True
        while isVideo:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://nekos.life/api/v2/img/meow') as resp:
                    res = await resp.json()
                    res = res['url']
                    cs.close()
            if res.endswith('.mp4'):
                pass
            else:
                isVideo = False
        em = discord.Embed()
        await kit.send(embed=em.set_image(url=res))

    @commands.command()
    @commands.cooldown(rate=1, per=12, type=commands.BucketType.user)
    async def pokemon(self, linu, *, pokemon):
        """: Check info about pokemon"""
        pokedex1 = pokedex.Pokedex(
            version='v1',
            user_agent='ExampleApp (https://example.com, v2.0.1)')
        x = pokedex1.get_pokemon_by_name(f'''{pokemon}''')
        embed = discord.Embed(
            title=f'''{x[0]['name']}''',
            description=f'''Discovered in generation {x[0]['gen']}''',
            color=0xFFFFFF)
        embed.add_field(
            name='Species', value=f'''{x[0]['species']}''', inline=False)
        if not x[0]['gender']:
            embed.add_field(name='Gender', value="No Gender", inline=False)
        else:
            embed.add_field(
                name='Gender',
                value=f'''Male:  {x[0]['gender'][0]}%\nFemale:  {x[0]['gender'][1]}%''',
                inline=False)
        embed.add_field(
            name='Type',
            value=f'''{', '.join(str(i) for i in x[0]['types'])}''',
            inline=False)
        embed.set_image(url=f'''{x[0]['sprite']}''')
        embed.add_field(
            name='Abilities',
            value=f'''{', '.join(str(i)for i in x[0]['abilities']['normal'])}''',
            inline=False)
        if not x[0]['abilities']['hidden']:
            embed.add_field(
                name='Hidden Abilities',
                value="No hidden talents like me",
                inline=False)
        else:
            embed.add_field(
                name='Hidden Abilities',
                value=f'''{', '.join(str(i)for i in x[0]['abilities']['hidden'])}''',
                inline=False)
        embed.add_field(
            name='Egg Groups',
            value=f'''{', '.join(str(i)for i in x[0]['eggGroups'])}''',
            inline=False)
        embed.add_field(
            name='Evolution',
            value=f'''{' => '.join(str(i)for i in x[0]['family']['evolutionLine'])}''',
            inline=False)
        embed.add_field(name='Height', value=x[0]['height'], inline=False)
        embed.add_field(name='Weight', value=x[0]['weight'], inline=False)
        if x[0]['legendary']:
            a = 'Legendary'
        elif x[0]['starter']:
            a = 'Starter'
        elif x[0]['mythical']:
            a = 'Mythical'
        elif x[0]['ultraBeast']:
            a = 'Ultra Beast'
        elif x[0]['mega']:
            a = 'Mega'
        else:
            a = '-'
        embed.add_field(name='Notes', value=a, inline=False)
        await linu.send(embed=embed)

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
        await linu.send(content=f"**{linu.author.mention}** hugged **{user.mention}**", embed=em.set_image(url=res))

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def hit(self, linu, user: discord.Member = None):
        if user is None:
            await linu.send("You try to hit the air, the air hits back. Be afraid....")
            return

        choices = ['http://s.orzzzz.com/news/b2/fa//57454a6136143.gif', 'https://i.pinimg.com/originals/8a/d3/39/8ad33953eca9fe56dcf79f57f0c04883.gif',
                   'https://i.pinimg.com/originals/62/b6/a6/62b6a6963250f990123ccd7f08dfbb6e.gif', 'https://i.imgur.com/nMeoCkW.gif', 'http://gifimage.net/wp-content/uploads/2017/08/one-punch-man-mosquito-gif-15.gif']

        image = random.choice(choices)

        em = discord.Embed()
        await linu.send(content=f"**{linu.author.mention}** KO'd **{user.mention}**", embed=em.set_image(url=image))

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def boop(self, linu, user: discord.Member = None):
        if user is None:
            await linu.send("You try to boop the air, the air boops back. Be afraid....")
            return

        choices = ['http://i.imgur.com/fZmUTgw.gif', 'http://i.imgur.com/787H2cR.gif',
                   'https://media.giphy.com/media/LhIfr7B8EvToc/giphy.gif']

        image = random.choice(choices)

        em = discord.Embed()
        await linu.send(content=f"**{linu.author.mention}** booped **{user.mention}**", embed=em.set_image(url=image))

    @commands.command(pass_context=True)
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def kiss(self, linu, user: discord.Member = None):
        if user is None:
            await linu.send("You need to @ someone ;-;")
            return

        choices = ['https://media.giphy.com/media/12VXIxKaIEarL2/giphy.gif', 'https://media1.tenor.com/images/78095c007974aceb72b91aeb7ee54a71/tenor.gif?itemid=5095865', 'https://media1.tenor.com/images/f5167c56b1cca2814f9eca99c4f4fab8/tenor.gif?itemid=6155657',
                   'https://orig00.deviantart.net/fda1/f/2017/339/6/c/ladynoir_kiss_gif__colored_version__by_ambarnarutofrek1-dbvk1l8.gif', 'https://media.giphy.com/media/ZRSGWtBJG4Tza/giphy.gif']

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
