import discord
from discord.ext import commands
from .utils.paginator import Pages
import datetime

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

        self.items = {
            'pick': 1,
            'pickaxe': 1,
            'ring': 2,
            'diamond': 3,
            'rose': 4,
            'alcohol': 5,
            'vodka': 5
        }

        self._items = {
            1: 'picks',
            2: 'rings',
            3: 'diamonds',
            4: 'roses',
            5: 'alcohol'
        }

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
                _seller = ctx.guild.get_member(record['seller_id']) or self.bot.get_user(record['seller_id'])
                seller = _seller.display_name

                price = record['price']

                items = {
                    1: ':pick: Pickaxe',
                    2: ':ring: Ring',
                    3: ':diamond_shape_with_a_dot_inside: Diamond',
                    4: ':rose: Rose',
                    5: ':champagne: Alcohol'
                }
                item = items[record['item_id']]

                quantity = record['quantity']

                selling_id = record['selling_id']

                listings.append(f'{selling_id}: {quantity}x {item} ${price} {seller}')
            
            try:
                p = Pages(ctx, entries=listings, per_page=10, show_entry_count=False)
                # p.embed.title = str(base)
                p.embed.timestamp = datetime.datetime.utcnow()
                p.embed.title=f'{len(listings)} items listed now.'
                await p.paginate()
            except Exception as e:
                await ctx.send(e)
        else:
            await ctx.send('Nothing listed at the moment.')

    @store.command()
    async def sell(self, ctx, price: int=None, item:str=None, quantity:int=1):
        """Adds a listing to the store."""
        if price is None:
            return await ctx.show_help('store sell')

        if item is None:
            return await ctx.send('Valid items are ``pickaxe``, ``ring``, ``diamond``, ``rose``, ``alcohol``.')

        if quantity <= 0:
            return await ctx.send(f'{ctx.tick(False)} You can\'t sell negative amounts.')

        item = item.lower()

        

        await ctx.db.execute(f'insert into store(id, price, item_id, seller_id, quantity) values ({ctx.guild.id}, {price}, {self.items[item]}, {ctx.author.id}, {quantity});')

        
        item_name = self._items[self.items[item]]

        item_quantity = await ctx.db.fetchrow(f'select {item_name} from profiles where id={ctx.author.id};')

        if not item_quantity[0]:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have any {item_name}s.')

        if item_quantity[0] < quantity:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have that much.')

        await ctx.db.execute(f'update profiles set {item_name}={item_name} - {quantity} where id={ctx.author.id}')

        await ctx.send(f'{ctx.tick(True)} Added listing.')

    @store.command()
    async def buy(self, ctx, selling_id:int=None, quantity:int=1):
        if selling_id is None:
            return await ctx.send('You forgot to add the selling id of the item you want to buy.')

        listing = await ctx.db.fetchrow(f'select * from store where selling_id={selling_id};')

        if listing is None:
            return await ctx.send(f'{ctx.tick(False)} This listing was not found.')

        listing_quantity = listing['quantity']
        price = listing['price']
        item_id = listing['item_id']
        seller_id = listing['seller_id']

        cash = await ctx.db.fetchrow(f'select cash from profiles where id={ctx.author.id}')

        if cash[0] < price*quantity:
            return await ctx.send(f'{ctx.tick(False)} You can\'t afford to buy that many.')

        if quantity > listing_quantity:
            return await ctx.send(f'{ctx.tick(False)} There is not that many for sale.')
        elif quantity < 1:
            return await ctx.send(f'{ctx.tick(False)} You can\'t buy negative amounts.')
        elif quantity == listing_quantity:
            await ctx.db.execute(f'delete from store where selling_id={selling_id}')
        else:
            await ctx.db.execute(f'update store set quantity=quantity-{quantity} where selling_id={selling_id}')

        await ctx.db.execute(f'update profiles set cash=cash-{price*quantity} where id={ctx.author.id}')

        await ctx.db.execute(f'update profiles set cash=cash+{price*quantity} where id={seller_id}')

        item_name = self._items[item_id]

        await ctx.db.execute(f'update profiles set {item_name}={item_name}+{quantity} where id={ctx.author.id}')

        # await ctx.send(f'update profiles set {item_name}={item_name}+{quantity} where id={ctx.author.id}')

        items = {
                    1: ':pick: Pickaxe',
                    2: ':ring: Ring',
                    3: ':diamond_shape_with_a_dot_inside: Diamond',
                    4: ':rose: Rose',
                    5: ':champagne: Alcohol'
                }

        await ctx.send(f'{ctx.tick(True)} Bought {quantity}x {items[item_id]} for ${price*quantity}.')

def setup(bot):
    bot.add_cog(Store(bot))
