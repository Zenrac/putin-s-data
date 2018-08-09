from discord.ext import commands
from googlesearch import search
import wikipedia
import urbandictionary as ud
from .utils import checks

class Search():
    """Search related commands."""
    def __init__(self, bot):
        self.bot = bot

    def search_google(self, phrase):
        query = phrase
        for j in search(query, tld="com", num=1, stop=1, pause=2):
            print(j)

    @commands.command()
    async def google(self, ctx, *, query : str = None):
        """Searches from google for a query you specify."""
        if ctx.message.channel.is_nsfw():
            found = []
            for j in search(query, tld="com", num=1, stop=1, pause=2):
                found.append(j)
            await ctx.send('Here is what I could find:\n{}'.format(found[0]))
        else:
            await ctx.send('This is not a nsfw channel.')

    @commands.command()
    async def define(self, ctx, *, string : str=None):
        """Searches from wikipedia with a string you specify."""
        if ctx.message.channel.is_nsfw():
            definition = wikipedia.summary(string, sentences=3)
            # if ' porn ' or ' dick ' or ' blowjob ' or ' hentai ' or ' sex ' in definition:
            #     await ctx.send('This definition has some nsfw content inside, and I am not allowed to show that.')
            #     return
            await ctx.send('Here\'s what I could find from wikipedia:\n```{}```'.format(definition))
        else:
            await ctx.send('This is not a nsfw channel.')

    @commands.command(hidden=True)
    async def ubdefine(self, ctx, *, string: str=None):
        if ctx.message.channel.is_nsfw():
            defs = ud.define(string)
            if defs[0]:
                await ctx.send('Here is what i found:\n```{}```'.format(defs[0]))
            else:
                await ctx.send('I could not find anything.')
        else:
            await ctx.send('This is not a nsfw channel.')

def setup(bot):
    bot.add_cog(Search(bot))
