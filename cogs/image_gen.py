import asyncio
import importlib
import random
from io import BytesIO

import PIL
import PIL.Image
import discord
import numpy as np
import wand
import wand.image
from discord.ext import commands

code = "```py\n{0}\n```"


class ImageGen:
    def __init__(self, bot):
        self.bot = bot
        self.get_images = self.bot.img_helper.get_images
        self.bytes_download = self.bot.img_helper.bytes_download
        self.wait_text = ['pls wait', 'just a sec', 'hang on', '\\*machine noises\\*', 'doing some calculations']

    def do_magik(self, scale, *imgs):
        try:
            list_imgs = []
            exif = {}
            exif_msg = ''
            count = 0
            for img in imgs:
                i = wand.image.Image(file=img)
                i.format = 'jpg'
                i.alpha_channel = True
                if i.size >= (3000, 3000):
                    return ':warning: `Image exceeds maximum resolution >= (3000, 3000).`', None
                exif.update({count: (k[5:], v) for k, v in i.metadata.items() if k.startswith('exif:')})
                count += 1
                i.transform(resize='800x800>')
                i.liquid_rescale(width=int(i.width * 0.5), height=int(i.height * 0.5),
                                 delta_x=int(0.5 * scale) if scale else 1, rigidity=0)
                i.liquid_rescale(width=int(i.width * 1.5), height=int(i.height * 1.5), delta_x=scale if scale else 2,
                                 rigidity=0)
                magikd = BytesIO()
                i.save(file=magikd)
                magikd.seek(0)
                list_imgs.append(magikd)
            if len(list_imgs) > 1:
                imgs = [PIL.Image.open(i).convert('RGBA') for i in list_imgs]
                min_shape = sorted([(np.sum(i.size), i.size) for i in imgs])[0][1]
                imgs_comb = np.hstack((np.asarray(i.resize(min_shape)) for i in imgs))
                imgs_comb = PIL.Image.fromarray(imgs_comb)
                ya = BytesIO()
                imgs_comb.save(ya, 'png')
                ya.seek(0)
            elif not len(list_imgs):
                return ':warning: **Download processor failed...**', None
            else:
                ya = list_imgs[0]
            for x in exif:
                if len(exif[x]) >= 2000:
                    continue
                exif_msg += '**Exif data for image #{0}**\n'.format(str(x + 1)) + code.format(exif[x])
            else:
                if len(exif_msg) == 0:
                    exif_msg = None
            return ya, exif_msg
        except Exception as e:
            return str(e), None

    @commands.command(description="MAGIK the image! Attach the image to the message with this "
                                  "command, add URL to the image or use a blank command to add magik to a previously "
                                  "attached image.")
    @commands.cooldown(2, 5, commands.BucketType.channel)
    async def magik(self, ctx, *, urls: str = None):
        msg = await ctx.send(f"{str(self.bot.get_emoji(432500013436764170))} {random.choice(self.wait_text)}",
                             delete_after=10)
        quality = 3
        get_images = await self.get_images(ctx, urls=urls, limit=6, scale=5)
        if not get_images:
            return
        img_urls = get_images[0]
        scale = get_images[1]
        scale_msg = get_images[2]
        if scale_msg is None:
            scale_msg = ''
        list_imgs = []
        for url in img_urls:
            b = await self.bytes_download(url)
            if b is False:
                if len(get_images) == 1:
                    await msg.edit(content=':warning: **Couldn\'t download the image ...**')
                    return
                continue
            list_imgs.append(b)
        final, content_msg = await self.bot.loop.run_in_executor(None, self.do_magik, scale, *list_imgs)
        if type(final) == str:
            await ctx.send(final)
            return
        if content_msg is None:
            content_msg = scale_msg
        else:
            content_msg = scale_msg + content_msg

        await ctx.send(content_msg, file=discord.File(final, filename='magik.jpg'))
        try:
            await msg.delete()
        except:
            pass

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reloadimggen(self, ctx):
        try:
            self.bot.img_helper = None
            p = importlib.import_module("cogs.stuffs.image_helper")
            m = importlib.reload(p)
            self.bot.img_helper = m.ImgHelper(self.bot)
            msg = await ctx.send("**IMGGEN HELPER was reloaded!**")
            await asyncio.sleep(2)
            await msg.delete()
        except ImportError:
            await ctx.send("**Something went wrong. BADLY!**")

    @commands.command(aliases=['needsmorejpeg', 'jpegify'],
                      description="Adds more JPEG to image. NEEDS MORE JPEG! Attach the image to the message with this "
                                  "command, add URL to the image or use a blank command to add jpeg to a previously "
                                  "attached image.")
    @commands.cooldown(2, 5, commands.BucketType.channel)
    async def jpeg(self, ctx, *, url: str = None):
        msg = await ctx.send(f"{str(self.bot.get_emoji(432500013436764170))} {random.choice(self.wait_text)}",
                             delete_after=10)
        quality = 3
        get_images = await self.get_images(ctx, urls=url)
        if not get_images:
            return
        for url in get_images:
            b = await self.bytes_download(url)
            if b is False:
                if len(get_images) == 1:
                    await msg.edit(content=':warning: **Couldn\'t download the image ...**')
                    return
                continue
            img = PIL.Image.open(b).convert('RGB')
            final = BytesIO()
            img.save(final, 'JPEG', quality=quality)
            final.seek(0)

            await ctx.send(file=discord.File(final, filename=f'morejpeg.jpg'))
            try:
                await msg.delete()
            except:
                pass

def setup(bot):
    bot.add_cog(ImageGen(bot))