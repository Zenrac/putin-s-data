from discord.ext import commands
import discord
from fortnite_python import Fortnite

class Fortnite():
    def __init__(self, bot):
        self.bot = bot
        self.fortnite = Fortnite('274e0176-875b-400a-a7b4-fa2567990fda')

    @commands.command
    async def fn(self, ctx, player: str=None):
        if player is None:
            return await ctx.send('You forgot to insert a player name.')
        player = fortnite.player(player)
        await ctx.send(dir(player))

def setup(bot):
    bot.add_cog(Fortnite(bot))
