import requests
from io import BytesIO
import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import aiohttp

class Avatar():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def avatar(self, ctx, member: discord.Member=None):

        async with aiohttp.ClientSession() as client_session:
            async with client_session.get(ctx.message.member.avatar_url) as response:
                image_bytes = await response.read()

# in an executor

        with Image.open(BytesIO(image_bytes)) as my_image:
    # do whatever with your image
            output_buffer = BytesIO()
            my_image.save(output_buffer, "my_file.png")  # or whatever format
            output_buffer.seek(0)

# back in your async function
        await self.bot.send_file(fp=output_buffer, filename="my_file.png")

def setup(bot):
    bot.add_cog(Avatar(bot))
