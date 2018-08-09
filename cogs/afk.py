import discord
from discord.ext import commands
import asyncio
from .utils import checks

class ShutDown():
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @checks.is_owner()
    async def sendfiles(self, ctx):
        await self.bot.add_reaction(ctx.message, ':tickYes:315009125694177281')
        owner = await self.bot.get_user_info('282515230595219456')
        await self.bot.send_file(owner, 'logs.json')
        await self.bot.send_file(owner, 'mod.json')
        await self.bot.send_file(owner, 'prefixes.json')
        await self.bot.send_file(owner, 'profiles.json')
        await self.bot.send_file(owner, 'rooms.json')
        await self.bot.send_file(owner, 'tags.json')

def setup(bot):
    bot.add_cog(ShutDown(bot))