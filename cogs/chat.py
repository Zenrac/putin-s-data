from discord.ext import commands
import discord
from .utils import clever
import asyncio

class Chat():
    def __init__(self, bot):
        self.bot = bot
        self.client = clever.CleverBot(user='9FZVmdY47TEthPLe', key='zl3Fuk2Kx2Nis2YvbaIeMhMdoYRdKA7N', nick="Putin")

    @commands.command()
    async def chat(self, ctx, *, text: str=None):
        """Say something, and I'll answer to you."""
        if text is None:
            await ctx.send('You need to say something.')
            return
        msg = await ctx.send('Fetching the response.')
        await msg.edit(content=ctx.author.name + ', ' + await self.client.query(text))

def setup(bot):
    bot.add_cog(Chat(bot))
