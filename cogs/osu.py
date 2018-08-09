from discord.ext import commands
import discord
from osuapi import OsuApi, AHConnector
import aiohttp
import asyncio

class OSU():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def osu(self, ctx, player: str=None):
        # if ctx.subcommand_invoked is None:
        # await ctx.send(player)
        async def get_user():
            api = OsuApi("d372f888679a27536cc2a6732a0d5c83f4db489a", connector=AHConnector())
            results = await api.get_user(player)
            return results[0]

        results = await get_user()
        e = discord.Embed(title="Osu stats for {} {}:".format(results.username, results.country), description="User id: {}".format(results.user_id), color=discord.Color.green())
        e.add_field(name="Level:", value=results.level, inline=True)
        e.add_field(name="Total score:", value=results.total_score, inline=True)
        e.add_field(name="Total hits:", value=results.total_hits, inline=True)
        e.add_field(name="Accuracy:", value=results.accuracy, inline=True)
        e.add_field(name="300 hits:", value=results.count300, inline=True)
        e.add_field(name="100 hits:", value=results.count100, inline=True)
        e.add_field(name="50 hits:", value=results.count50, inline=True)
        e.add_field(name="Play count:", value=results.playcount, inline=True)
        e.add_field(name="Ranked score:", value=results.ranked_score, inline=True)
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(OSU(bot))
