import asyncio
from discord.ext import commands
import pychromecast

class Chromecast():
    def __init__(self, bot):
        self.bot = bot

        casts = pychromecast.get_chromecasts()

        self.active = False
        self.cast = next(cc for cc in casts if cc.device.friendly_name == 'Chromecast')
        self.mc = None

    @commands.group(aliases=['chromecast'], hidden=True)
    @commands.is_owner()
    async def cc(self, ctx):
        pass

    @cc.command(hidden=True)
    async def play(self, ctx, format: str, *, url: str):
        self.mc = cast.media_controller
        mc.play_media(url, format)
        mc.block_until_active()
        self.active = True
        await ctx.send('Started playing.')

    @cc.command(hidden=True)
    async def pause(self, ctx):
        if self.active:
            self.mc.pause()
        else:
            await ctx.send('Not palying anything.')

def setup(bot):
    bot.add_cog(Chromecast(bot))
