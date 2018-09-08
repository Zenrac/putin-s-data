import discord
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
        """Store commands."""
        if ctx.invoked_subcommand is None:
            await ctx.show_help('store')

    @store.command()
    async def list(self, ctx):
        """Shows all the current listings for the server."""
        store = await self.get_store(ctx.guild.id)

        if store.items:
            listings = []
            for record in store.items():
                _seller = ctx.guild.get_member(record['seller_id'])
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

                selling_id = record['selling_id']

                listings.append(f'{selling_id}: {quantity}x {item} ${price} {seller}')

            e = discord.Embed(title=f"Listings for {ctx.guild.name}")

            e.description = "\n".join(listings)

            await ctx.send(embed=e)
        else:
            await ctx.send('Nothing listed at the moment.')

    @store.command()
    async def sell(self, ctx, price: int=None, item:str=None, quantity:int=1):
        """Adds a listing to the store."""
        if price is None:
            return await ctx.show_help('store sell')

        if item is None:
            return await ctx.send('Valid items are ``pickaxe``, ``ring``, ``diamond``, ``rose``, ``alcohol``.')

        item = item.lower()

        items = {
            'pick': 1,
            'pickaxe': 1,
            'ring': 2,
            'diamond': 3,
            'rose': 4,
            'alcohol': 5,
            'vodka': 5
        }

        await ctx.db.execute(f'insert into store(id, price, item_id, seller_id, quantity) values ({ctx.guild.id}, {price}, {items[item]}, {ctx.author.id}, {quantity});')

        _items = {
            'picks': 1,
            'rings': 2,
            'diamonds': 3,
            'roses': 4,
            'alcohol': 5
        }

        await ctx.db.execute(f'update profiles set {_items[items[item]]}={_items[items[item]]}-{quantity}')

        await ctx.send('Added listing.')

def setup(bot):
    bot.add_cog(Store(bot))
