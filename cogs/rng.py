from discord.ext import commands
import discord
import random as rng
import json
import aiohttp
import asyncio

class Random:
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def mur(self, ctx):
        """Gives you a mur image."""
        e = discord.Embed(title="Here is a mur image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://sheri.fun/api/v1/mur') as res:
                r = await res.json()

        yiff_url = r['url']

        e.set_image(url=yiff_url)
        await ctx.send(embed=e)

    @commands.command()
    async def number(self, ctx, minimum = 0, maximum = 100):
        """Displays a random number with optional min. and max."""
        maximum = min(maximum, 1000)
        if minimum >= maximum:
            await ctx.send(':exclamation: | Maximum is smaller than minimum.')
            return

        await ctx.send(rng.randint(minimum, maximum))

    @commands.command()
    async def lenny(self, ctx):
        """Displays a random lenny."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('http://api.lenny.today/v1/random?limit=1') as res:
                data = await res.json()
        await ctx.send(data[0]['face'])

    @commands.command()
    async def choose(self, ctx, *choices):
        """Makes a hard choice for you."""
        if len(choices) < 2:
            await ctx.send(':exclamation: | Not enough choices to pick from.')
        else:
            await ctx.send('I choose ``{}``.'.format(rng.choice(choices)))

    @commands.command()
    async def space(self, ctx):
        """Gives you a space image."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://api.chewey-bot.ga/space') as res:
                r = await res.json()
        e = discord.Embed(title="Space", color=discord.Color.blue())
        e.set_image(url=r['data'])
        e.set_footer(text="Powered by api.chewey-bot.ga")
        await ctx.send(embed=e)

    @commands.command()
    async def cat(self, ctx):
        """Gives you a cat image."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://api.chewey-bot.ga/cat') as res:
                r = await res.json()
        e = discord.Embed(title="Cat", color=discord.Color.blue())
        e.set_image(url=r['data'])
        e.set_footer(text="Powered by api.chewey-bot.ga")
        await ctx.send(embed=e)

    @commands.command()
    async def dog(self, ctx):
        """Gives you a birb image."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://api.chewey-bot.ga/dog') as res:
                r = await res.json()
        e = discord.Embed(title="Dog", color=discord.Color.blue())
        e.set_image(url=r['data'])
        e.set_footer(text="Powered by api.chewey-bot.ga")
        await ctx.send(embed=e)

    @commands.command()
    async def birb(self, ctx):
        """Gives you a birb image."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://api.chewey-bot.ga/birb') as res:
                r = await res.json()
        e = discord.Embed(title="Birb", color=discord.Color.blue())
        e.set_image(url=r['data'])
        e.set_footer(text="Powered by api.chewey-bot.ga")
        await ctx.send(embed=e)

    @commands.command()
    async def nature(self, ctx):
        """Gives you a nature image."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://api.chewey-bot.ga/nature') as res:
                r = await res.json()
        e = discord.Embed(title="Nature", color=discord.Color.blue())
        e.set_image(url=r['data'])
        e.set_footer(text="Powered by api.chewey-bot.ga")
        await ctx.send(embed=e)

    @commands.command()
    async def fantasy(self, ctx):
        """Gives you a fantasy art image."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://api.chewey-bot.ga/fantasy-art') as res:
                r = await res.json()
        e = discord.Embed(title="Fantsy art", color=discord.Color.blue())
        e.set_image(url=r['data'])
        e.set_footer(text="Powered by api.chewey-bot.ga")
        await ctx.send(embed=e)

    @commands.command()
    async def plane(self, ctx):
        """Gives you a plane image."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://api.chewey-bot.ga/plane') as res:
                r = await res.json()
        e = discord.Embed(title="Plane", color=discord.Color.blue())
        e.set_image(url=r['data'])
        e.set_footer(text="Powered by api.chewey-bot.ga")
        await ctx.send(embed=e)

    @commands.command()
    async def otter(self, ctx):
        """Gives you a otter image."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://api.chewey-bot.ga/otter') as res:
                r = await res.json()
        e = discord.Embed(title="Otter", color=discord.Color.blue())
        e.set_image(url=r['data'])
        e.set_footer(text="Powered by api.chewey-bot.ga")
        await ctx.send(embed=e)

    @commands.command()
    async def rabbit(self, ctx):
        """Gives you a rabbit image."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://api.chewey-bot.ga/rabbit') as res:
                r = await res.json()
        e = discord.Embed(title="Rabbit", color=discord.Color.blue())
        e.set_image(url=r['data'])
        e.set_footer(text="Powered by api.chewey-bot.ga")
        await ctx.send(embed=e)

    @commands.command()
    async def snake(self, ctx):
        """Gives you a snake image."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://api.chewey-bot.ga/snake') as res:
                r = await res.json()
        e = discord.Embed(title="Snake", color=discord.Color.blue())
        e.set_image(url=r['data'])
        e.set_footer(text="Powered by api.chewey-bot.ga")
        await ctx.send(embed=e)

    @commands.command()
    async def car(self, ctx):
        """Gives you a snake image."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://api.chewey-bot.ga/car') as res:
                r = await res.json()
        e = discord.Embed(title="Car", color=discord.Color.blue())
        e.set_image(url=r['data'])
        e.set_footer(text="Powered by api.chewey-bot.ga")
        await ctx.send(embed=e)

def setup(bot):
    m = Random(bot)
    bot.add_cog(m)
