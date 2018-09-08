from discord.ext import commands

class StoreConfig():
    __slots__ = ['bot', 'id', '_items']

    def __init__(self, *, guild_id, bot, record=None):
        self.id = guild_id
        self.bot = bot
        
        _items = []
        for (id, price, item_id, seller_id, selling_id) in record['id'], record['price'], record['item_id'], record['seller_id'], record['selling_id']:
            _items.append(id, price, item_id, seller_id, selling_id)
        self._items = _items

    @property
    def items(self):
        return self._items    
    
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

    @store.command()
    async def list(self, ctx):
        store = await self.get_store(ctx.guild.id)

        if store.items:
            await ctx.send(item for item in store.items)
        else:
            await ctx.send('Nothing listed at the moment.')

def setup(bot):
    bot.add_cog(Store(bot))
