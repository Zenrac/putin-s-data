from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from discord.ext import commands
from functools import partial
from io import BytesIO
from typing import Union
import discord
import re
import os
import io
import aiohttp
import asyncio
import tempfile
import unidecode
import random
import sys

COLORS = ['rgb(225,205,102)', 'rgb(144,238,144)' ,'rgb(173,216,230)','rgb(32,178,170)','rgb(255,20,147)','rgb(128,128,128)']

class Images():
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.session = aiohttp.ClientSession(loop=bot.loop)

    @commands.command()
    async def tweet(self, ctx, *, text : str=None):
        """Makes me tweet what you say."""
        if text is None:
            await self.bot.say('You didn\'t tell what I should tweet.')
            return
        async with ctx.message.channel.typing():
            image = Image.open("tweet_temp.jpg")
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype('arial.ttf', 20)

            (x, y) = (15, 70)
            (x2, y2) = (15, 90)
            (x3, y3) = (15, 110)
            if len(text) > 120:
                await self.bot.say('The message is too long.')
            else:
                message = re.findall('.{1,40}', text)
            color = 'rgb(0,0,0)'
            if message[0]:
                draw.text((x,y), message[0], fill=color, font=font)
            if len(message) == 2:
                draw.text((x2, y2), message[1], fill=color, font=font)
            if len(message) == 3:
                draw.text((x2, y2), message[1], fill=color, font=font)
                draw.text((x3, y3), message[2], fill=color, font=font)
            image.save('tweet.png', optimize=True, quality=85)
            await ctx.channel.send(file=discord.File('tweet.png'))

    @commands.command()
    async def ohno(self, ctx, *,text: str=None):
        """Makes the dog say what you say."""
        if text is None:
            await self.bot.say('You didn\'t tell what the dog should say.')
        else:
            async with ctx.message.channel.typing():
                image = Image.open("ohno_temp.png")
                draw = ImageDraw.Draw(image)
                font = ImageFont.truetype('arial.ttf', 35)

                (x, y) = (300, 25)
                (x2, y2) = (300, 62)
                (x3, y3) = (300, 100)
                if len(text) > 51:
                    await self.bot.say('The message is too long.')
                else:
                    message = re.findall('.{1,17}', text)
                color = 'rgb(0,0,0)'
                draw.text((x,y), message[0], fill=color, font=font)
                if len(message) == 2:
                    draw.text((x2, y2), message[1], fill=color, font=font)
                if len(message) == 3:
                    draw.text((x2, y2), message[1], fill=color, font=font)
                    draw.text((x3, y3), message[2], fill=color, font=font)
                image.save('ohno.png', optimize=True, quality=85)
                await ctx.channel.send(file=discord.File('ohno.png'))

    @commands.command()
    async def glitch(self, ctx, *, text: str=None):
        """Converts your text to a image."""
        if text is None:
            await self.bot.say('You didn\'t tell me what to convert.')
            return
        async with ctx.message.channel.typing():
            lenght = len(text) * 27
            img = Image.new('RGB', (lenght,40), (255, 255, 255))
            img.save('glitch.png')
            img = Image.open('glitch.png')
            img = img.convert("RGBA")
            datas = img.getdata()

            newData = []
            for item in datas:
                if item[0] == 255 and item[1] == 255 and item[2] == 255:
                    newData.append((255, 255, 255, 0))
                else:
                    newData.append(item)

            img.putdata(newData)
            img.save("glitch.png", "PNG")
            image = Image.open('glitch.png')
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype('glitch.ttf', 40)
            (x, y) = (0,0)
            color = random.choice(COLORS)
            draw.text((x,y), text, fill=color, font=font)
            image.save('glitch.png', optimize=True, quality=85)
            await ctx.channel.send(file=discord.File('glitch.png'))

    @commands.command()
    async def graffiti(self, ctx, *, text: str=None):
        """Converts your text to a image."""
        if text is None:
            await self.bot.say('You didn\'t tell me what to convert.')
            return
        async with ctx.typing():
            lenght = len(text) * 17
            img = Image.new('RGB', (lenght,40), (255, 255, 255))
            img.save('graffiti.png')
            img = Image.open('graffiti.png')
            img = img.convert("RGBA")
            datas = img.getdata()

            newData = []
            for item in datas:
                if item[0] == 255 and item[1] == 255 and item[2] == 255:
                    newData.append((255, 255, 255, 0))
                else:
                    newData.append(item)

            img.putdata(newData)
            img.save("graffiti.png", "PNG")
            image = Image.open('graffiti.png')
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype('adrip1.ttf', 40)
            (x, y) = (1,0)
            color = random.choice(COLORS)
            draw.text((x,y), text, fill=color, font=font)
            image.save('graffiti.png', optimize=True, quality=85)
            await ctx.channel.send(file=discord.File('graffiti.png'))

    @commands.command()
    async def groovy(self, ctx, *, text: str=None):
        """Converts your text to a image."""
        if text is None:
            await self.bot.say('You didn\'t tell me what to convert.')
            return
        async with ctx.typing():
            lenght = len(text) * 30
            img = Image.new('RGB', (lenght,40), (255, 255, 255))
            img.save('groovy.png')
            img = Image.open('groovy.png')
            img = img.convert("RGBA")
            datas = img.getdata()

            newData = []
            for item in datas:
                if item[0] == 255 and item[1] == 255 and item[2] == 255:
                    newData.append((255, 255, 255, 0))
                else:
                    newData.append(item)

            img.putdata(newData)
            img.save("groovy.png", "PNG")
            image = Image.open('groovy.png')
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype('Neon.ttf', 40)
            (x, y) = (1,0)
            color = random.choice(COLORS)
            draw.text((x,y), text, fill=color, font=font)
            image.save('groovy.png', optimize=True, quality=85)
            await ctx.channel.send(file=discord.File('groovy.png'))

    @commands.command()
    async def hanging(self, ctx, *, text: str=None):
        """Converts your text to a image."""
        if text is None:
            await self.bot.say('You didn\'t tell me what to convert.')
            return
        async with ctx.message.channel.typing():
            lenght = len(text) * 19
            img = Image.new('RGB', (lenght,40), (255, 255, 255))
            img.save('hanging.png')
            img = Image.open('hanging.png')
            img = img.convert("RGBA")
            datas = img.getdata()

            newData = []
            for item in datas:
                if item[0] == 255 and item[1] == 255 and item[2] == 255:
                    newData.append((255, 255, 255, 0))
                else:
                    newData.append(item)

            img.putdata(newData)
            img.save("hanging.png", "PNG")
            image = Image.open('hanging.png')
            draw = ImageDraw.Draw(image)
            font = ImageFont.truetype('KGALittleSwag.ttf', 40)
            (x, y) = (10,0)
            color = random.choice(COLORS)
            draw.text((x,y), text, fill=color, font=font)
            image.save('hanging.png', optimize=True, quality=85)
            await ctx.channel.send(file=discord.File('hanging.png'))

    # @commands.command()
    # async def test(self, ctx, *, member: discord.Member = None):
    #     await ctx.trigger_typing()
    #     member = member or ctx.author
    #     if member.is_avatar_animated():
    #         avatar_url = member.avatar_url_as(format='gif', size=1024)
    #         avatar_url_format = 'gif'
    #     else:
    #         avatar_url = member.avatar_url_as(format='png', size=1024)
    #         avatar_url_format = 'png'
    #     async with aiohttp.ClientSession() as client_session:
    #         async with client_session.get(avatar_url) as response:
    #             avatar_bytes = await response.read()
                
    #     with Image.open(BytesIO(avatar_bytes)) as my_image:
    #         output_buffer = BytesIO()
    #         my_image.save(output_buffer, avatar_url_format)
    #         output_buffer.seek(0)

    #     await ctx.send(file=discord.File(fp=output_buffer, filename="my_file."+avatar_url_format))

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def blur(self, ctx, *, member: discord.Member=None, amount: float=0.5):
        """Makes a blur version of your or someone you specify profile picture."""
        member = member or ctx.author
        if not ctx.message.attachments:
            await ctx.trigger_typing()
            async with aiohttp.ClientSession() as cs:
                async with cs.get(member.avatar_url_as(format='png', size=1024)) as image:
                    avatar_bytes = await image.read()

            with Image.open(BytesIO(avatar_bytes)) as image:
                output_buffer = BytesIO()
                image = image.filter(ImageFilter.GaussianBlur(5))
                image.save(output_buffer, 'png')
                output_buffer.seek(0)

            await ctx.send(file=discord.File(fp=output_buffer, filename='test.png'))
        else:
            try:
                attachment_bytes = BytesIO()
                file_format = ctx.message.attachments[0].filename.split('.')
                await ctx.message.attachments[0].save(attachment_bytes)
                attachment_bytes.seek(0)
                with Image.open(attachment_bytes) as image:
                    output_buffer = BytesIO()
                    image = image.filter(ImageFilter.GaussianBlur(5))
                    image.save(output_buffer, 'gif')
                    output_buffer.seek(0)
                await ctx.send(file=discord.File(fp=output_buffer, filename=ctx.message.attachments[0].filename))
            except ValueError:
                await ctx.send('That format is not supported.')

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def edge(self, ctx, *, member: discord.Member=None):
        await ctx.trigger_typing()
        member = member or ctx.author
        if not ctx.message.attachments:
            await ctx.trigger_typing()
            async with aiohttp.ClientSession() as cs:
                async with cs.get(member.avatar_url_as(format='png', size=1024)) as image:
                    avatar_bytes = await image.read()

            with Image.open(BytesIO(avatar_bytes)) as image:
                output_buffer = BytesIO()
                image = image.filter(ImageFilter.FIND_EDGES)
                image.save(output_buffer, 'png')
                output_buffer.seek(0)

            await ctx.send(file=discord.File(fp=output_buffer, filename='test.png'))

        else:
            atc = ctx.message.attachments[0]
            try:
                attachment_bytes = BytesIO()
                file_format = ctx.message.attachments[0].filename.split('.')
                await ctx.message.attachments[0].save(attachment_bytes)
                attachment_bytes.seek(0)
                with Image.open(attachment_bytes) as image:
                    output_buffer = BytesIO()
                    image = image.filter(ImageFilter.FIND_EDGES)
                    image.save(output_buffer, atc.filename.split('.')[-1])
                    output_buffer.seek(0)
                await ctx.send(file=discord.File(fp=output_buffer, filename=ctx.message.attachments[0].filename))
            except ValueError:
                await ctx.send('That format is not supported.')

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def emboss(self, ctx, *, member: discord.Member=None):
        await ctx.trigger_typing()
        member = member or ctx.author
        if not ctx.message.attachments:
            await ctx.trigger_typing()
            async with aiohttp.ClientSession() as cs:
                async with cs.get(member.avatar_url_as(format='png', size=1024)) as image:
                    avatar_bytes = await image.read()

            with Image.open(BytesIO(avatar_bytes)) as image:
                output_buffer = BytesIO()
                image = image.filter(ImageFilter.EMBOSS)
                image.save(output_buffer, 'png')
                output_buffer.seek(0)

            await ctx.send(file=discord.File(fp=output_buffer, filename='test.png'))

        else:
            atc = ctx.message.attachments[0]
            try:
                attachment_bytes = BytesIO()
                file_format = ctx.message.attachments[0].filename.split('.')
                await ctx.message.attachments[0].save(attachment_bytes)
                attachment_bytes.seek(0)
                with Image.open(attachment_bytes) as image:
                    output_buffer = BytesIO()
                    image = image.filter(ImageFilter.EMBOSS)
                    image.save(output_buffer, atc.filename.split('.')[-1])
                    output_buffer.seek(0)
                await ctx.send(file=discord.File(fp=output_buffer, filename=ctx.message.attachments[0].filename))
            except ValueError:
                await ctx.send('That format is not supported.')

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def smooth(self, ctx, *, member: discord.Member=None):
        await ctx.trigger_typing()
        member = member or ctx.author
        if not ctx.message.attachments:
            await ctx.trigger_typing()
            async with aiohttp.ClientSession() as cs:
                async with cs.get(member.avatar_url_as(format='png', size=1024)) as image:
                    avatar_bytes = await image.read()

            with Image.open(BytesIO(avatar_bytes)) as image:
                output_buffer = BytesIO()
                image = image.filter(ImageFilter.SMOOTH_MORE)
                image.save(output_buffer, 'png')
                output_buffer.seek(0)

            await ctx.send(file=discord.File(fp=output_buffer, filename='test.png'))

        else:
            atc = ctx.message.attachments[0]
            try:
                attachment_bytes = BytesIO()
                file_format = ctx.message.attachments[0].filename.split('.')
                await ctx.message.attachments[0].save(attachment_bytes)
                attachment_bytes.seek(0)
                with Image.open(attachment_bytes) as image:
                    output_buffer = BytesIO()
                    image = image.filter(ImageFilter.SMOOTH_MORE)
                    image.save(output_buffer, atc.filename.split('.')[-1])
                    output_buffer.seek(0)
                await ctx.send(file=discord.File(fp=output_buffer, filename=ctx.message.attachments[0].filename))
            except ValueError:
                await ctx.send('That format is not supported.')

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def sharpen(self, ctx, *, member: discord.Member=None):
        await ctx.trigger_typing()
        member = member or ctx.author
        if not ctx.message.attachments:
            await ctx.trigger_typing()
            async with aiohttp.ClientSession() as cs:
                async with cs.get(member.avatar_url_as(format='png', size=1024)) as image:
                    avatar_bytes = await image.read()

            with Image.open(BytesIO(avatar_bytes)) as image:
                output_buffer = BytesIO()
                image = image.filter(ImageFilter.SHARPEN)
                image.save(output_buffer, 'png')
                output_buffer.seek(0)

            await ctx.send(file=discord.File(fp=output_buffer, filename='test.png'))

        else:
            atc = ctx.message.attachments[0]
            try:
                attachment_bytes = BytesIO()
                file_format = ctx.message.attachments[0].filename.split('.')
                await ctx.message.attachments[0].save(attachment_bytes)
                attachment_bytes.seek(0)
                with Image.open(attachment_bytes) as image:
                    output_buffer = BytesIO()
                    image = image.filter(ImageFilter.SHARPEN)
                    image.save(output_buffer, atc.filename.split('.')[-1])
                    output_buffer.seek(0)
                await ctx.send(file=discord.File(fp=output_buffer, filename=ctx.message.attachments[0].filename))
            except ValueError:
                await ctx.send('That format is not supported.')

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def detail(self, ctx, *, member: discord.Member=None):
        await ctx.trigger_typing()
        member = member or ctx.author
        if not ctx.message.attachments:
            await ctx.trigger_typing()
            async with aiohttp.ClientSession() as cs:
                async with cs.get(member.avatar_url_as(format='png', size=1024)) as image:
                    avatar_bytes = await image.read()

            with Image.open(BytesIO(avatar_bytes)) as image:
                output_buffer = BytesIO()
                image = image.filter(ImageFilter.DETAIL)
                image.save(output_buffer, 'png')
                output_buffer.seek(0)

            await ctx.send(file=discord.File(fp=output_buffer, filename='test.png'))

        else:
            atc = ctx.message.attachments[0]
            try:
                attachment_bytes = BytesIO()
                file_format = ctx.message.attachments[0].filename.split('.')
                await ctx.message.attachments[0].save(attachment_bytes)
                attachment_bytes.seek(0)
                with Image.open(attachment_bytes) as image:
                    output_buffer = BytesIO()
                    image = image.filter(ImageFilter.DETAIL)
                    image.save(output_buffer, atc.filename.split('.')[-1])
                    output_buffer.seek(0)
                await ctx.send(file=discord.File(fp=output_buffer, filename=ctx.message.attachments[0].filename))
            except ValueError:
                await ctx.send('That format is not supported.')

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def upsidedown(self, ctx, *, member: discord.Member=None):
        await ctx.trigger_typing()
        member = member or ctx.author
        if not ctx.message.attachments:
            await ctx.trigger_typing()
            async with aiohttp.ClientSession() as cs:
                async with cs.get(member.avatar_url_as(format='png', size=1024)) as image:
                    avatar_bytes = await image.read()

            with Image.open(BytesIO(avatar_bytes)) as image:
                output_buffer = BytesIO()
                image = image.rotate( 180 )
                image.save(output_buffer, 'png')
                output_buffer.seek(0)

            await ctx.send(file=discord.File(fp=output_buffer, filename='test.png'))

        else:
            atc = ctx.message.attachments[0]
            try:
                attachment_bytes = BytesIO()
                file_format = ctx.message.attachments[0].filename.split('.')
                await ctx.message.attachments[0].save(attachment_bytes)
                attachment_bytes.seek(0)
                with Image.open(attachment_bytes) as image:
                    output_buffer = BytesIO()

                    image = image.rotate( 180 )

                    image.save(output_buffer, atc.filename.split('.')[-1])
                    output_buffer.seek(0)
                await ctx.send(file=discord.File(fp=output_buffer, filename=ctx.message.attachments[0].filename))
            except ValueError:
                await ctx.send('That format is not supported.')

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def rotate(self, ctx, amount: int, *, member: discord.Member=None):
        await ctx.trigger_typing()
        member = member or ctx.author
        if not ctx.message.attachments:
            await ctx.trigger_typing()
            async with aiohttp.ClientSession() as cs:
                async with cs.get(member.avatar_url_as(format='png', size=1024)) as image:
                    avatar_bytes = await image.read()

            with Image.open(BytesIO(avatar_bytes)) as image:
                output_buffer = BytesIO()

                image = image.rotate( amount, expand=True )

                image.save(output_buffer, 'png')
                output_buffer.seek(0)

            await ctx.send(file=discord.File(fp=output_buffer, filename='test.png'))

        else:
            atc = ctx.message.attachments[0]
            try:
                attachment_bytes = BytesIO()
                file_format = ctx.message.attachments[0].filename.split('.')[-1]
                await atc.save(attachment_bytes)
                attachment_bytes.seek(0)
                with Image.open(attachment_bytes) as image:
                    output_buffer = BytesIO()
                    
                    image = image.rotate( amount, expand=True )

                    image.save(output_buffer, file_format)
                    output_buffer.seek(0)
                await ctx.send(file=discord.File(fp=output_buffer, filename=ctx.message.attachments[0].filename))
            except ValueError:
                await ctx.send('That format is not supported.')

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def horisontal(self, ctx, *, member: discord.Member=None):
        await ctx.trigger_typing()
        member = member or ctx.author
        if not ctx.message.attachments:
            await ctx.trigger_typing()
            async with aiohttp.ClientSession() as cs:
                async with cs.get(member.avatar_url_as(format='png', size=1024)) as image:
                    avatar_bytes = await image.read()

            with Image.open(BytesIO(avatar_bytes)) as image:
                output_buffer = BytesIO()
                image = image.transpose(Image.FLIP_LEFT_RIGHT)
                image.save(output_buffer, 'png')
                output_buffer.seek(0)

            await ctx.send(file=discord.File(fp=output_buffer, filename='test.png'))

        else:
            atc = ctx.message.attachments[0]
            try:
                attachment_bytes = BytesIO()
                file_format = ctx.message.attachments[0].filename.split('.')
                await ctx.message.attachments[0].save(attachment_bytes)
                attachment_bytes.seek(0)
                with Image.open(attachment_bytes) as image:
                    output_buffer = BytesIO()
                    image = image.transpose(Image.FLIP_LEFT_RIGHT)
                    image.save(output_buffer, atc.filename.split('.')[-1])
                    output_buffer.seek(0)
                await ctx.send(file=discord.File(fp=output_buffer, filename=ctx.message.attachments[0].filename))
            except ValueError:
                await ctx.send('That format is not supported.')

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def vertical(self, ctx, *, member: discord.Member=None):
        await ctx.trigger_typing()
        member = member or ctx.author
        if not ctx.message.attachments:
            await ctx.trigger_typing()
            async with aiohttp.ClientSession() as cs:
                async with cs.get(member.avatar_url_as(format='png', size=1024)) as image:
                    avatar_bytes = await image.read()

            with Image.open(BytesIO(avatar_bytes)) as image:
                output_buffer = BytesIO()
                image = image.transpose(Image.FLIP_TOP_BOTTOM)
                image.save(output_buffer, 'png')
                output_buffer.seek(0)

            await ctx.send(file=discord.File(fp=output_buffer, filename='test.png'))

        else:
            atc = ctx.message.attachments[0]
            try:
                attachment_bytes = BytesIO()
                file_format = ctx.message.attachments[0].filename.split('.')
                await ctx.message.attachments[0].save(attachment_bytes)
                attachment_bytes.seek(0)
                with Image.open(attachment_bytes) as image:
                    output_buffer = BytesIO()
                    image = image.transpose(Image.FLIP_TOP_BOTTOM)
                    image.save(output_buffer, atc.filename.split('.')[-1])
                    output_buffer.seek(0)
                await ctx.send(file=discord.File(fp=output_buffer, filename=ctx.message.attachments[0].filename))
            except ValueError:
                await ctx.send('That format is not supported.')

    @commands.command(aliases = ['colour'])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def color(self, ctx, amount: float, *, member: discord.Member=None):
        if amount > 100 or amount < 1:
            return await ctx.send('The value must be between 100 and 1.')
        await ctx.trigger_typing()
        member = member or ctx.author
        if not ctx.message.attachments:
            await ctx.trigger_typing()
            async with aiohttp.ClientSession() as cs:
                async with cs.get(member.avatar_url_as(format='png', size=1024)) as image:
                    avatar_bytes = await image.read()

            with Image.open(BytesIO(avatar_bytes)) as image:
                output_buffer = BytesIO()

                enhancer = ImageEnhance.Color(image)
                image = enhancer.enhance(amount/100)

                image.save(output_buffer, 'png')
                output_buffer.seek(0)

            await ctx.send(file=discord.File(fp=output_buffer, filename='test.png'))

        else:
            atc = ctx.message.attachments[0]
            try:
                attachment_bytes = BytesIO()
                file_format = ctx.message.attachments[0].filename.split('.')
                await ctx.message.attachments[0].save(attachment_bytes)
                attachment_bytes.seek(0)
                with Image.open(attachment_bytes) as image:
                    output_buffer = BytesIO()

                    enhancer = ImageEnhance.Color(image)
                    image = enhancer.enhance(amount/100)

                    image.save(output_buffer, atc.filename.split('.')[-1])
                    output_buffer.seek(0)
                await ctx.send(file=discord.File(fp=output_buffer, filename=ctx.message.attachments[0].filename))
            except ValueError:
                await ctx.send('That format is not supported.')

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def contrast(self, ctx, amount: float, *, member: discord.Member=None):
        if amount > 200 or amount < 1:
            return await ctx.send('The value must be between 200 and 1.')
        await ctx.trigger_typing()
        member = member or ctx.author
        if not ctx.message.attachments:
            await ctx.trigger_typing()
            async with aiohttp.ClientSession() as cs:
                async with cs.get(member.avatar_url_as(format='png', size=1024)) as image:
                    avatar_bytes = await image.read()

            with Image.open(BytesIO(avatar_bytes)) as image:
                output_buffer = BytesIO()

                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(amount/100)

                image.save(output_buffer, 'png')
                output_buffer.seek(0)

            await ctx.send(file=discord.File(fp=output_buffer, filename='test.png'))

        else:
            atc = ctx.message.attachments[0]
            try:
                attachment_bytes = BytesIO()
                file_format = ctx.message.attachments[0].filename.split('.')
                await ctx.message.attachments[0].save(attachment_bytes)
                attachment_bytes.seek(0)
                with Image.open(attachment_bytes) as image:
                    output_buffer = BytesIO()

                    enhancer = ImageEnhance.Contrast(image)
                    image = enhancer.enhance(amount/100)

                    image.save(output_buffer, atc.filename.split('.')[-1])
                    output_buffer.seek(0)
                await ctx.send(file=discord.File(fp=output_buffer, filename=ctx.message.attachments[0].filename))
            except ValueError:
                await ctx.send('That format is not supported.')

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def brightness(self, ctx, amount: float, *, member: discord.Member=None):
        if amount > 100 or amount < 1:
            return await ctx.send('The value must be between 100 and 1.')
        await ctx.trigger_typing()
        member = member or ctx.author
        if not ctx.message.attachments:
            await ctx.trigger_typing()
            async with aiohttp.ClientSession() as cs:
                async with cs.get(member.avatar_url_as(format='png', size=1024)) as image:
                    avatar_bytes = await image.read()

            with Image.open(BytesIO(avatar_bytes)) as image:
                output_buffer = BytesIO()

                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(amount/100)

                image.save(output_buffer, 'png')
                output_buffer.seek(0)

            await ctx.send(file=discord.File(fp=output_buffer, filename='test.png'))

        else:
            atc = ctx.message.attachments[0]
            try:
                attachment_bytes = BytesIO()
                file_format = ctx.message.attachments[0].filename.split('.')
                await ctx.message.attachments[0].save(attachment_bytes)
                attachment_bytes.seek(0)
                with Image.open(attachment_bytes) as image:
                    output_buffer = BytesIO()

                    enhancer = ImageEnhance.Brightness(image)
                    image = enhancer.enhance(amount/100)

                    image.save(output_buffer, atc.filename.split('.')[-1])
                    output_buffer.seek(0)
                await ctx.send(file=discord.File(fp=output_buffer, filename=ctx.message.attachments[0].filename))
            except ValueError:
                await ctx.send('That format is not supported.')

    @commands.command()
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def sharpness(self, ctx, amount: float, *, member: discord.Member=None):
        if amount > 100 or amount < 1:
            return await ctx.send('The value must be between 100 and 1.')
        await ctx.trigger_typing()
        member = member or ctx.author
        if not ctx.message.attachments:
            await ctx.trigger_typing()
            async with aiohttp.ClientSession() as cs:
                async with cs.get(member.avatar_url_as(format='png', size=1024)) as image:
                    avatar_bytes = await image.read()

            with Image.open(BytesIO(avatar_bytes)) as image:
                output_buffer = BytesIO()

                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(amount/100)

                image.save(output_buffer, 'png')
                output_buffer.seek(0)

            await ctx.send(file=discord.File(fp=output_buffer, filename='test.png'))

        else:
            atc = ctx.message.attachments[0]
            try:
                attachment_bytes = BytesIO()
                file_format = ctx.message.attachments[0].filename.split('.')
                await ctx.message.attachments[0].save(attachment_bytes)
                attachment_bytes.seek(0)
                with Image.open(attachment_bytes) as image:
                    output_buffer = BytesIO()

                    enhancer = ImageEnhance.Sharpness(image)
                    image = enhancer.enhance(amount/100)

                    image.save(output_buffer, atc.filename.split('.')[-1])
                    output_buffer.seek(0)
                await ctx.send(file=discord.File(fp=output_buffer, filename=ctx.message.attachments[0].filename))
            except ValueError:
                await ctx.send('That format is not supported.')

    @commands.command()
    async def gay(self, ctx, *, member: discord.Member=None):
        await ctx.trigger_typing()
        member = member or ctx.author
        if not ctx.message.attachments:
            await ctx.trigger_typing()
            async with aiohttp.ClientSession() as cs:
                async with cs.get(member.avatar_url_as(format='png', size=1024)) as image:
                    avatar_bytes = await image.read()

            try:
                with Image.open(BytesIO(avatar_bytes)) as image:
                    output_buffer = BytesIO()
                    
                    size = width, height = image.size
                    gay_flag = Image.open('gayflag.png')
                    gay_flag = gay_flag.convert('RGB')
                    gay_flag.thumbnail(size)
                    gbytes = BytesIO()
                    gay_flag.save(gbytes, 'png')
                    gbytes.seek(0)
                    image = Image.blend(gay_flag, image, 0.5)

                    image.save(output_buffer, 'png')
                    output_buffer.seek(0)
                    del gay_flag
            except ValueError:
                return await ctx.send('I am sorry but that image format is not supported.')

            await ctx.send(file=discord.File(fp=output_buffer, filename='test.png'))

        else:
            # await ctx.send('This command does not support attachments.')
            atc = ctx.message.attachments[0]
            try:
                attachment_bytes = BytesIO()
                file_format = ctx.message.attachments[0].filename.split('.')
                await ctx.message.attachments[0].save(attachment_bytes)
                attachment_bytes.seek(0)
                with Image.open(attachment_bytes) as image:
                    output_buffer = BytesIO()
                    
                    size = width, height = image.size
                    gay_flag = Image.open('gayflag.png')
                    gay_flag = gay_flag.convert('RGB')
                    gay_flag.thumbnail(size)
                    gbytes = BytesIO()
                    gay_flag.save(gbytes, 'png')
                    gbytes.seek(0)
                    image = Image.blend(gay_flag, image, 0.5)

                    image.save(output_buffer, 'png')
                    output_buffer.seek(0)
                    del gay_flag
                await ctx.send(file=discord.File(fp=output_buffer, filename=ctx.message.attachments[0].filename))
            except ValueError:
                await ctx.send('That format is not supported.')

    #Basic image taking process
    # @commands.command()
    # async def test(self, ctx, *, member: discord.Member=None):
    #     await ctx.trigger_typing()
    #     member = member or ctx.author
    #     if not ctx.message.attachments:
    #         await ctx.trigger_typing()
    #         async with aiohttp.ClientSession() as cs:
    #             async with cs.get(member.avatar_url_as(format='png', size=1024)) as image:
    #                 avatar_bytes = await image.read()

    #         with Image.open(BytesIO(avatar_bytes)) as image:
    #             output_buffer = BytesIO()
                


    #             image.save(output_buffer, 'png')
    #             output_buffer.seek(0)

    #         await ctx.send(file=discord.File(fp=output_buffer, filename='test.png'))

    #     else:
    #         atc = ctx.message.attachments[0]
    #         try:
    #             attachment_bytes = BytesIO()
    #             file_format = ctx.message.attachments[0].filename.split('.')
    #             await ctx.message.attachments[0].save(attachment_bytes)
    #             attachment_bytes.seek(0)
    #             with Image.open(attachment_bytes) as image:
    #                 output_buffer = BytesIO()



    #                 image.save(output_buffer, atc.filename.split('.')[-1])
    #                 output_buffer.seek(0)
    #             await ctx.send(file=discord.File(fp=output_buffer, filename=ctx.message.attachments[0].filename))
    #         except ValueError:
    #             await ctx.send('That format is not supported.')

    # @commands.command()
    # async def test(self, ctx, *, member: discord.Member=None):
    #     """Makes a blur version of your or someone you specify profile picture."""
    #     await ctx.trigger_typing()
    #     member = member or ctx.author
    #     async with aiohttp.ClientSession() as cs:
    #         async with cs.get(member.avatar_url_as(format='png', size=1024)) as image:
    #             avatar_bytes = await image.read()
    #     try:
    #         with Image.open(BytesIO(avatar_bytes)) as image:
    #             output_buffer = BytesIO()
    #             gay_flag = Image.open("gayflag.png")
    #             image.save(output_buffer, 'png')
    #             image = Image.blend(image, gay_flag, 0.0)
    #             image.save(output_buffer, 'png')
    #             output_buffer.seek(0)
    #     except Exception as error:
    #         await ctx.send(error)

    #     await ctx.send(file=discord.File(fp=output_buffer, filename='test.png'))

    # @commands.command()
    # async def ship(self, ctx, member: discord.Member, second_member: discord.Member=None):
    #     await ctx.trigger_typing()
    #     async with aiohttp.ClientSession() as client_session:
    #         async with client_session.get(member.avatar_url_as(format='png', size=1024)) as response:
    #             avatar_bytes = await response.read()

    #     with Image.open(BytesIO(avatar_bytes)) as img:
    #         avatar_buffer = BytesIO()
    #         img.save(avatar_buffer, 'png')
    #         avatar_buffer.seek(0)

    #     async with aiohttp.ClientSession() as client_session:
    #         async with client_session.get(member.avatar_url_as(format='png', size=1024)) as response:
    #             avatar2_bytes = await response.read()

    #     with Image.open(BytesIO(avatar2_bytes)) as img:
    #         avatar2_buffer = BytesIO()
    #         img.save(avatar2_buffer, 'png')
    #         avatar2_buffer.seek(0)

    #     with Image.open('heart.png') as img:
    #         heart_buffer = BytesIO()
    #         img.save(heart_buffer, 'png')
    #         heart_buffer.seek(0)

    #     try:
    #         new_im = Image.new('RGB', (2304, 768))
    #         images = [avatar_buffer, heart_buffer, avatar2_buffer]
    #         x_offset = 0
    #         for im in images:
    #             new_im.paste(im, (x_offset,0))
    #             x_offset += 768

    #         new_im.save('ship.png')
    #     except Exception as e:
    #         await ctx.send('```py\n{}```'.format(e))

    #     await ctx.send(file=discord.File('ship.png'))


def setup(bot):
    bot.add_cog(Images(bot))
