from discord.ext import commands
from .utils import db

class store(db.Table):
    pass
    
class Store():
    pass
    
    
    
def setup(bot):
    bot.add_cog(Store(bot))
