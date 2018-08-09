import discord
from discord.ext import commands
import nekos

class NSFW():
    """These commands work with nekos.life api."""
    def __init__(self, bot):
        self.bot = bot

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
