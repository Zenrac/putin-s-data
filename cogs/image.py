from PIL import Image, ImageDraw, ImageFont
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

    async def get_avatar(self, user: Union[discord.User, discord.Member]) -> bytes:

        # generally an avatar will be 1024x1024, but we shouldn't rely on this
        avatar_url = user.avatar_url_as(format="png")

        async with self.session.get(avatar_url) as response:
            # this gives us our response object, and now we can read the bytes from it.
            avatar_bytes = await response.read()

        return avatar_bytes

    @staticmethod
    def processing(avatar_bytes: bytes, colour: tuple) -> BytesIO:

        # we must use BytesIO to load the image here as PIL expects a stream instead of
        # just raw bytes.
        with Image.open(BytesIO(avatar_bytes)) as im:

            # this creates a new image the same size as the user's avatar, with the
            # background colour being the user's colour.
            with Image.new("RGB", im.size, colour) as background:

                # this ensures that the user's avatar lacks an alpha channel, as we're
                # going to be substituting our own here.
                rgb_avatar = im.convert("RGB")

                # this is the mask image we will be using to create the circle cutout
                # effect on the avatar.
                with Image.new("L", im.size, 0) as mask:

                    # ImageDraw lets us draw on the image, in this instance, we will be
                    # using it to draw a white circle on the mask image.
                    mask_draw = ImageDraw.Draw(mask)

                    # draw the white circle from 0, 0 to the bottom right corner of the image
                    mask_draw.ellipse([(0, 0), im.size], fill=255)

                    # paste the alpha-less avatar on the background using the new circle mask
                    # we just created.
                    background.paste(rgb_avatar, (0, 0), mask=mask)

                # prepare the stream to save this image into
                final_buffer = BytesIO()

                # save into the stream, using png format.
                background.save(final_buffer, "png")

        # seek back to the start of the stream
        final_buffer.seek(0)

        return final_buffer

    @commands.command()
    async def circle(self, ctx, *, member: discord.Member = None):
        """Display the user's avatar on their colour."""

        # this means that if the user does not supply a member, it will default to the
        # author of the message.
        member = member or ctx.author

        async with ctx.typing():
            # this means the bot will type while it is processing and uploading the image

            if isinstance(member, discord.Member):
                # get the user's colour, pretty self explanatory
                member_colour = member.colour.to_rgb()
            else:
                # if this is in a DM or something went seriously wrong
                member_colour = (0, 0, 0)

            # grab the user's avatar as bytes
            avatar_bytes = await self.get_avatar(member)

            # create partial function so we don't have to stack the args in run_in_executor
            fn = partial(self.processing, avatar_bytes)
            # this runs our processing in an executor, stopping it from blocking the thread loop.
            # as we already seeked back the buffer in the other thread, we're good to go
            final_buffer = await self.bot.loop.run_in_executor(None, fn)

            # prepare the file
            file = discord.File(filename="circle.png", fp=final_buffer)

            # send it
            await ctx.send(file=file)

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
