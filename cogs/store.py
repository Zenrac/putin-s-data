from discord.ext import commands

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
    
    def __str__(self):
        return [_ for _ in self.items] or 'Nothing listed at the moment.'
    
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
        await ctx.send(store)

def setup(bot):
    bot.add_cog(Store(bot))
