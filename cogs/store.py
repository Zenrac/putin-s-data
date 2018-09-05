from discord.ext import commands
from .utils import db

class store(db.Table):
    pass
    
class Store():
    def __init__(self, bot):
        self.bot = bot
    
    
def setup(bot):
    bot.add_cog(Store(bot))
