import discord
from discord.ext import commands
import nekos
import asyncio
import aiohttp
import random, cogs.utils.eapi, cogs.utils.sfapi, os

processapi = cogs.utils.eapi.processapi
processshowapi = cogs.utils.eapi.processshowapi
search = cogs.utils.sfapi.search

class ResultNotFound(Exception):
    """Used if ResultNotFound is triggered by e* API."""
    pass

class InvalidHTTPResponse(Exception):
    """Used if non-200 HTTP Response got from server."""
    pass
class NSFW():
    """These commands work with nekos.life api."""
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def e621(self, ctx, *args):
        """Searches e621 with given queries.
        Arguments:
        `*args` : list  
        The quer(y/ies)"""
        if not ctx.channel.is_nsfw():
            return await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
        await ctx.trigger_typing()
        if not isinstance(ctx.channel, discord.DMChannel):
            if not isinstance(ctx.channel, discord.GroupChannel):
                if not ctx.channel.is_nsfw():
                    await ctx.send("Cannot be used in non-NSFW channels!")
                    return
        args = ' '.join(args)
        args = str(args)
        netloc = "e621"
        if "order:score_asc" in args:
            await ctx.send("I'm not going to fall into that one, silly~")
            return
        if "score:" in args:
            apilink = 'https://e621.net/post/index.json?tags=' + args + '&limit=320'
        else:
            apilink = 'https://e621.net/post/index.json?tags=' + args + ' score:>25&limit=320'
        try:
            await processapi(apilink)
        except ResultNotFound:
            await ctx.send("Result not found!")
            return
        except InvalidHTTPResponse:
            await ctx.send("We're getting invalid response from the API, please try again later!")
            return
        embed = discord.Embed(title="E621 Search")
        embed.set_image(url=processapi.file_link)
        await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def e926(self, ctx, *args):
        """Searches e926 with given queries.
        Arguments:
        `*args` : list  
        The quer(y/ies)"""
        await ctx.trigger_typing()
        args = ' '.join(args)
        args = str(args)
        netloc = "e926"
        if "order:score_asc" in args:
            await ctx.send("I'm not going to fall into that one, silly~")
            return
        if "score:" in args:
            apilink = 'https://e926.net/post/index.json?tags=' + args + '&limit=320'
        else:
            apilink = 'https://e926.net/post/index.json?tags=' + args + ' score:>25&limit=320'
        try:
            await processapi(apilink)
        except ResultNotFound:
            await ctx.send("Result not found!")
            return
        except InvalidHTTPResponse:
            await ctx.send("We're getting invalid response from the API, please try again later!")
            return
        embed = discord.Embed(title="E926 Search")
        embed.set_image(url=processapi.file_link)
        await ctx.send(embed=embed)

    @commands.command(pass_context=True)
    async def show(self, ctx, arg):
        """Show a post from e621/e926 with given post ID
        Arguments:
        `arg` : int  
        The post ID"""
        await ctx.trigger_typing()
        arg = str(arg)
        apilink = 'https://e621.net/post/show.json?id=' + arg
        try:
            await processshowapi(apilink)
        except ResultNotFound:
            await ctx.send("Result not found!")
            return
        except InvalidHTTPResponse:
            await ctx.send("We're getting invalid response from the API, please try again later!")
            return
        await ctx.send("""Artist: """ + processshowapi.imgartist + """\r\nSource: `""" + processshowapi.imgsource + """`\r\nRating: """ + processshowapi.imgrating + """\r\nTags: `""" + processshowapi.imgtags + """` ...and more\r\nImage link: """ + processshowapi.file_link)

    @commands.command(pass_context=True)
    async def randompick(self, ctx, *args, description="Output random result"):
        """Output random result from e621/e926.  
        If channel is NSFW, use e621, if not, then use e926."""
        await ctx.trigger_typing()
        if not isinstance(ctx.channel, discord.DMChannel):
            if not ctx.channel.is_nsfw():
                netloc = "e926"
            else:
                netloc = "e621"
        else:
            netloc = "e621"
        apilink = 'https://' + netloc + '.net/post/index.json?tags=score:>25&limit=320&page=' + str(random.randint(1,51))
        try:
            await processapi(apilink)
        except ResultNotFound:
            await ctx.send("Result not found!")
            return
        except InvalidHTTPResponse:
            await ctx.send("We're getting invalid response from the API, please try again later!")
            return
        embed = discord.Embed(title=f"{netloc.upper()} Search")
        embed.set_image(url=processapi.file_link)
        await ctx.send(embed=embed)

    @commands.command()
    async def yiff(self, ctx):
        """Gives you a yiff image."""
        if not ctx.channel.is_nsfw():
            return await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
        e = discord.Embed(title="Here is a yiff image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://sheri.fun/api/v1/yiff') as res:
                r = await res.json()

        yiff_url = r['url']

        e.set_image(url=yiff_url)
        await ctx.send(embed=e)

    @commands.command()
    async def ngif(self, ctx):
        """Gives you a neko gif."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a neko gif for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('ngif'))
        await ctx.send(embed=e)

    @commands.command()
    async def feet(self, ctx):
        """Gives you a feet image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a feet image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('feet'))
        await ctx.send(embed=e)

    @commands.command()
    async def yuri(self, ctx):
        """Gives you a yuri image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a yuri image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('yuri'))
        await ctx.send(embed=e)

    @commands.command()
    async def trap(self, ctx):
        """Gives you a trap image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a trap image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('trap'))
        await ctx.send(embed=e)

    @commands.command()
    async def futanari(self, ctx):
        """Gives you a futanari image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a futanari image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('futanari'))
        await ctx.send(embed=e)

    @commands.command()
    async def hololewd(self, ctx):
        """Gives you a hololewd image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a hololewd image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('hololewd'))
        await ctx.send(embed=e)

    @commands.command()
    async def lewdkemo(self, ctx):
        """Gives you a lewdkemo image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a lewdkemo image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('lewdkemo'))
        await ctx.send(embed=e)

    @commands.command()
    async def solog(self, ctx):
        """Gives you a solog image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a solog image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('solog'))
        await ctx.send(embed=e)

    @commands.command()
    async def feetg(self, ctx):
        """Gives you a feetg image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a feetg image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('feetg'))
        await ctx.send(embed=e)

    @commands.command()
    async def cum(self, ctx):
        """Gives you a cum image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a cum image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('cum'))
        await ctx.send(embed=e)

    @commands.command()
    async def erokemo(self, ctx):
        """Gives you a erokemo image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a erokemo image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('erokemo'))
        await ctx.send(embed=e)

    @commands.command()
    async def les(self, ctx):
        """Gives you a les image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a les image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('les'))
        await ctx.send(embed=e)

    @commands.command()
    async def lewdk(self, ctx):
        """Gives you a lewdk image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a lewdk image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('lewdk'))
        await ctx.send(embed=e)

    @commands.command()
    async def lewd(self, ctx):
        """Gives you a lewd image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a lewd image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('lewd'))
        await ctx.send(embed=e)

    @commands.command()
    async def eroyuri(self, ctx):
        """Gives you a eroyuri image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a eroyuri image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('eroyuri'))
        await ctx.send(embed=e)

    @commands.command()
    async def eron(self, ctx):
        """Gives you a eron image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a eron image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('eron'))
        await ctx.send(embed=e)

    @commands.command()
    async def cumjpg(self, ctx):
        """Gives you a cum image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a cum image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('cum_jpg'))
        await ctx.send(embed=e)

    @commands.command()
    async def bj(self, ctx):
        """Gives you a blow job image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a blow job image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('bj'))
        await ctx.send(embed=e)

    @commands.command()
    async def nsfwngif(self, ctx):
        """Gives you a nsfw neko gif."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a neko gif image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('nsfw_neko_gif'))
        await ctx.send(embed=e)

    @commands.command()
    async def nsfwavatar(self, ctx):
        """Gives you a nsfw avatar image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a avatar image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('nsfw_avatar'))
        await ctx.send(embed=e)


    @commands.command()
    async def anal(self, ctx):
        """Gives you a anal image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a anal image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('anal'))
        await ctx.send(embed=e)

    @commands.command()
    async def hentai(self, ctx):
        """Gives you a hentai image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a hentai for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('hentai'))
        await ctx.send(embed=e)

    @commands.command()
    async def erofeet(self, ctx):
        """Gives you a erofeet image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a erofeet image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('erofeet'))
        await ctx.send(embed=e)

    @commands.command()
    async def keta(self, ctx):
        """Gives you a keta image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a keta image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('keta'))
        await ctx.send(embed=e)

    @commands.command()
    async def blowjob(self, ctx):
        """Gives you a blowjob image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a blowjob image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('blowjob'))
        await ctx.send(embed=e)

    @commands.command()
    async def pussy(self, ctx):
        """Gives you a pussy image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a pussy image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('pussy'))
        await ctx.send(embed=e)

    @commands.command()
    async def tits(self, ctx):
        """Gives you a tit image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a tit image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('tits'))
        await ctx.send(embed=e)

    @commands.command()
    async def holoero(self, ctx):
        """Gives you a holoero image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a holoero image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('holoero'))
        await ctx.send(embed=e)

    @commands.command()
    async def pussyjpg(self, ctx):
        """Gives you a pussy image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a pussy image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('pussy_jpg'))
        await ctx.send(embed=e)

    @commands.command()
    async def pwankg(self, ctx):
        """Gives you a pwankg image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a pwankg image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('pwankg'))
        await ctx.send(embed=e)

    @commands.command()
    async def classic(self, ctx):
        """Gives you a classic image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a classic image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('classic'))
        await ctx.send(embed=e)

    @commands.command()
    async def erok(self, ctx):
        """Gives you a erok image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a erok image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('erok'))
        await ctx.send(embed=e)

    @commands.command()
    async def kuni(self, ctx):
        """Gives you a kuni image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a kuni image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('kuni'))
        await ctx.send(embed=e)

    @commands.command()
    async def femdom(self, ctx):
        """Gives you a femdom image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a femdom image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('femdom'))
        await ctx.send(embed=e)

    @commands.command()
    async def spank(self, ctx, member: discord.Member=None):
        """Spanks someone you mention."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        if member is None:
            await ctx.send('You need to tell who to spank.')
            return
        if member.id == ctx.author.id:
            await ctx.send('Go ahead, spank yourself!')
            return
        e = discord.Embed(title="{} has been spanked by {}.".format(member.name, ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('spank'))
        await ctx.send(embed=e)

    @commands.command()
    async def erok(self, ctx):
        """Gives you a erok image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a erok image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('erok'))
        await ctx.send(embed=e)

    @commands.command()
    async def foxgirl(self, ctx):
        """Gives you a for girl image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a fox girl image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('fox_girl'))
        await ctx.send(embed=e)

    @commands.command()
    async def boobs(self, ctx):
        """Gives you a boob image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a boob image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('boobs'))
        await ctx.send(embed=e)

    @commands.command()
    async def hentaigif(self, ctx):
        """Gives you a hentai gif."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        await ctx.send(nekos.img('Random_hentai_gif'))
        e = discord.Embed(title="Here is a hentai gif for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('Random_hentai_gif'))
        await ctx.send(embed=e)

    @commands.command()
    async def smallboobs(self, ctx):
        """Gives you a small boob image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is small boobs image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('smallboobs'))
        await ctx.send(embed=e)

    @commands.command()
    async def ero(self, ctx):
        """Gives you a ero image."""
        if not ctx.channel.is_nsfw():
            await ctx.send(':warning: These commands can only be used at nsfw marked channels. Silly :smile:')
            return
        e = discord.Embed(title="Here is a ero image for you {}.".format(ctx.author.name), color=discord.Color.magenta())
        e.set_image(url=nekos.img('ero'))
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(NSFW(bot))
