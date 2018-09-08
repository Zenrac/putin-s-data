from discord.ext import commands

class StoreConfig():
    __slots__ = ['bot', 'id', '_items']

    def __init__(self, *, guild_id, bot, records=None):
        self.id = guild_id
        self.bot = bot
        
        def _items():
            for _record in records:
                yield _record

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
        records = await connection.fetch(query, guild_id)
        return StoreConfig(guild_id=guild_id, bot=self.bot, records=records)
    
    @commands.group(hidden=True)
    async def store(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.show_help('store')

    @store.command()
    async def list(self, ctx):
        store = await self.get_store(ctx.guild.id)

        if store.items:
            listings = []
            for _item in store.items():
                _seller = await ctx.guild.get_member(record['seller_id'])
                seller = _seller.display_name

                price = record['price']

                items = {
                    1: ':pick: Pickaxe',
                    2: ':rign: Ring',
                    3: ':diamond_shape_with_a_dot_inside: Diamond',
                    4: ':rose: Rose',
                    5: ':champagne: Alcohol'
                }
                item = items[record['item_id']]

                quantity = record['quantity']

                listings.append(f'{quantity} {item} {price} {seller}')

            e = discord.Embed(title=f"Listings for {ctx.guild.name}")

            e.description = "\n".join(listings)

            await ctx.send(embed=e)
        else:
            await ctx.send('Nothing listed at the moment.')

def setup(bot):
    bot.add_cog(Store(bot))
