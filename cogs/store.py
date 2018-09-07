from discord.ext import commands
from .utils import db

class store(db.Table):
    id = db.Column(db.Integer(big=True), primary_key=True)
    item_id = db.Column(db.Integer(big=False))
    price = db.Column(db.Integer(db.Numeric))
    seller_id = db.Column(db.Integer(big=True))

class StoreConfig():
    __slots__ = ['bot', 'id', 'items']

    def __init__(self, *, guild_id, bot, record=None):
        self.id = guild_id
        self.bot = bot

        if record:
            self.items = ((_[0],
                        _[1],
                        _[2]) for _ in (
                            record['item_id'],
                            record['price'],
                            record['seller_id'])
                            if record['id'] == self.id)
        else:
            self.items = None
        return self.items
    
class Store():
    def __init__(self, bot):
        self.bot = bot

    async def get_store(self, guild_id, *, connection=None):
        connection = connection or self.bot.pool
        query = "SELECT * FROM store WHERE id=$1"
        record = await connection.fetchrow(query, guild_id)
        return StoreConfig(guild_id=guild_id, bot=self.bot, record=record)
    
    @commands.group(hidden=True)
    async def store(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.show_help('store')

    @commands.command()
    async def list(self, ctx):
        store = self.get_store()
        await ctx.send(sotre['items'])

def setup(bot):
    bot.add_cog(Store(bot))
