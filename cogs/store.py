from discord.ext import commands
from .utils import db

class store(db.Table):
    pass
    
class Store():
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group(hidden=True)
    async def store(self, ctx):
        await ctx.send('xD')
    
def setup(bot):
    bot.add_cog(Store(bot))
