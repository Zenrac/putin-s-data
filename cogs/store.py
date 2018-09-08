from discord.ext import commands

class StoreConfig():
    __slots__ = ['bot', 'id', '_items']

    def __init__(self, *, guild_id, bot, record=None):
        self.id = guild_id
        self.bot = bot
        
        _items = []
        for index, _record in enumerate(record):
            # _items.append(_record['id'], _record['price'], _record['item_id'], _record['seller_id'], _record['selling_id'])
            _items.append(_record)

        self._items = _items

    @property
    def items(self):
        return self._items    
    
class Store():
    def __init__(self, bot):
        self.bot = bot

    async def get_store_items(self, guild_id, *, connection=None):
        connection = connection or self.bot.pool
        query = "SELECT * FROM store WHERE id=$1"
        records = await connection.fetchrow(query, guild_id)
        _items = []
        for _record in records:
            _items.append(str(_record['id']) + str(_record['price']) + str(_record['item_id']) + str(_record['seller_id']) + str(_record['selling_id']))
        return _items
        # return StoreConfig(guild_id=guild_id, bot=self.bot, record=record)
    
    @commands.group(hidden=True)
    async def store(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.show_help('store')

    @store.command()
    async def list(self, ctx):
        items = await self.get_store_items(ctx.guild.id)

        items = "\n".join(items)

        if store.items:
            await ctx.send(item for item in store.items)
        else:
            await ctx.send('Nothing listed at the moment.')

def setup(bot):
    bot.add_cog(Store(bot))
