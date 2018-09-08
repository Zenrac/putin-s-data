from discord.ext import commands
from .utils import db
import discord
import random
import re
import asyncio
from .utils.paginator import Pages
import datetime

class DisambiguateMember(commands.IDConverter):
    async def convert(self, ctx, argument):
        # check if it's a user ID or mention
        match = self._get_id_match(argument) or re.match(r'<@!?([0-9]+)>$', argument)
 
        if match is not None:
            # exact matches, like user ID + mention should search
            # for every member we can see rather than just this guild.
            user_id = int(match.group(1))
            result = ctx.bot.get_user(user_id)
            if result is None:
                raise commands.BadArgument("Could not find this member.")
            return result

        # check if we have a discriminator:
        if len(argument) > 5 and argument[-5] == '#':
            # note: the above is true for name#discrim as well
            name, _, discriminator = argument.rpartition('#')
            pred = lambda u: u.name == name and u.discriminator == discriminator
            result = discord.utils.find(pred, ctx.bot.users)
        else:
            # disambiguate I guess
            if ctx.guild is None:
                matches = [
                    user for user in ctx.bot.users
                    if user.name == argument
                ]
                entry = str
            else:
                matches = [
                    member for member in ctx.guild.members
                    if member.name == argument
                    or (member.nick and member.nick == argument)
                ]

                def to_str(m):
                    if m.nick:
                        return f'{m} (a.k.a {m.nick})'
                    else:
                        return str(m)

                entry = to_str

            try:
                result = await ctx.disambiguate(matches, entry)
            except Exception as e:
                raise commands.BadArgument(f'Could not find this member. {e}') from None

        if result is None:
            raise commands.BadArgument("Could not find this member. Note this is case sensitive.")
        return result

class Profile():
    def __init__(self, bot):
        self.bot = bot

    @commands.group(invoke_without_command=True)
    async def profile(self, ctx, *, member: DisambiguateMember = None):
        member = member or ctx.author

        query = """select * from profiles where id=$1"""
        record = await self.bot.pool.fetchrow(query, member.id)

        if record is None:
            if member == ctx.author:
                await ctx.send('You didnt set up a profile yet.')
                return await ctx.invoke(self.make)
            else:
                await ctx.send('This member did not set up a profile yet.')
            return

        if isinstance(member, discord.Member):
            name = member.display_name
            color = member.top_role.color
        else:
            name = member.name
            color = 0xcc205c

        e = discord.Embed(title="Profile of {}".format(name),color=color)
        e.set_thumbnail(url=member.avatar_url)
        keys = {
            ':writing_hand: Description': 'description',
            ':birthday: Birthday': 'bday',
            ':moneybag: Cash': 'cash',
            ':zap: Experience': 'experience'
        }
        for key, value in keys.items():
            e.add_field(name=key, value=str(record[value]) or 'N/A', inline=True)
        if record['married']:
            married = await self.bot.get_user_info(record['married'])
            married = married.name
        else:
            married = 'nobody...'
        e.add_field(name=':heart: Married with', value=married, inline=True)
        picks = ':pick:{}'.format(record['picks']) if record['picks'] else ''
        rings = ':ring:{}'.format(record['rings']) if record['rings'] else ''
        diamonds = ':diamond_shape_with_a_dot_inside:{}'.format(record['diamonds']) if record['diamonds'] else ''
        roses = ':rose:{}'.format(record['roses']) if record['roses'] else ''
        alcohol = ':champagne:{}'.format(record['alcohol']) if record['alcohol'] else ''
        inventory = picks + rings + diamonds + roses + alcohol
        inventory = inventory if inventory else 'Nothing in inventory'
        e.add_field(name=':handbag: Inventory', value=inventory, inline=True)
        pet = record['pet'] if record['pet'] else 'No pet'
        pet_title = 'Pet'
        e.add_field(name=pet_title, value=pet, inline=True)
        banner = record['banner'] or 0
        banners = {
            0: 'https://cdn.pixabay.com/photo/2016/08/03/09/03/universe-1566159_960_720.jpg',
            1: 'https://cdn.pixabay.com/photo/2018/08/18/18/42/emotions-3615255_960_720.jpg',
            2: 'https://cdn.pixabay.com/photo/2014/08/26/20/08/eye-428390_960_720.jpg',
            3: 'https://cdn.pixabay.com/photo/2016/09/04/20/14/sunset-1645103_960_720.jpg', 
            4: 'https://cdn.pixabay.com/photo/2018/08/30/13/21/travel-3642167_960_720.jpg',
            5: 'https://cdn.pixabay.com/photo/2016/09/04/20/14/sunset-1645105_960_720.jpg',
            6: 'https://cdn.pixabay.com/photo/2016/02/03/08/32/banner-1176676_960_720.jpg',
            7: 'https://cdn.pixabay.com/photo/2015/12/13/09/40/banner-1090830_960_720.jpg',
            8: 'https://cdn.pixabay.com/photo/2017/09/19/08/54/eyes-2764597_960_720.jpg',
            9: 'https://cdn.pixabay.com/photo/2015/10/11/11/20/banner-982162_960_720.jpg',
            10: 'https://cdn.pixabay.com/photo/2016/08/03/09/04/universe-1566161_960_720.jpg',
            11: 'https://cdn.pixabay.com/photo/2017/03/06/20/48/water-lily-2122505_960_720.jpg',
            12: 'https://cdn.pixabay.com/photo/2015/11/10/08/31/banner-1036483_960_720.jpg',
            13: 'https://cdn.pixabay.com/photo/2018/07/28/11/08/guitar-3567767_960_720.jpg',
            14: 'https://cdn.pixabay.com/photo/2018/02/06/18/54/travel-3135436_960_720.jpg'
        }
        e.set_image(url=banners[banner])
        await ctx.send(embed=e)

    async def edit_field(self, ctx, **fields):
        keys = ', '.join(fields)
        values = ', '.join(f'${2 + i}' for i in range(len(fields)))

        query = f"""update profiles
                    SET {keys} = {values}
                    where id=$1;
                 """

        await self.bot.pool.execute(query, ctx.author.id, *fields.values())

    async def edit_user_field(self, member, ctx, **fields):
        keys = ', '.join(fields)
        values = ', '.join(f'${2 + i}' for i in range(len(fields)))

        query = f"""update profiles
                    SET {keys} = {values}
                    where id=$1;
                 """

        await self.bot.pool.fetchrow(query, member.id, *fields.values())

    @commands.command()
    async def banners(self, ctx):
        if True:
            e = discord.Embed(color=discord.Color(0x1083a3))
            e.add_field(name="Valid banners are", value=
                '1: default\n'\
                '2: Air balloons\n'\
                '3: Blue eye\n'\
                '4: Sunset\n'\
                '5: Airplane\n'\
                '6: Sunset 2\n'\
                '7: Stars\n'\
                '8: Questions\n'\
                '9: Eyes\n'\
                '10: Matrix\n'\
                '11: Blue wave\n'\
                '12: Purple flower\n'\
                '13: Blue wave 2\n'\
                '14: Guitar\n'\
                '15: River\n',
                inline=False
                )
        await ctx.send(embed=e)

    @commands.command()
    async def banner(self, ctx, banner: int):
        if banner < 0 or banner > 15:
            e = discord.Embed(title="Invalid banner", color=discord.Color(0x1083a3))
            e.add_field(name="Valid banners are", value=
                '1: default\n'\
                '2: Air balloons\n'\
                '3: Blue eye\n'\
                '4: Sunset\n'\
                '5: Airplane\n'\
                '6: Sunset 2\n'\
                '7: Stars\n'\
                '8: Questions\n'\
                '9: Eyes\n'\
                '10: Matrix\n'\
                '11: Blue wave\n'\
                '12: Purple flower\n'\
                '13: Blue wave 2\n'\
                '14: Guitar\n'\
                '15: River\n',
                inline=False
                )
            return await ctx.send(embed=e)
        await self.edit_field(ctx, banner=banner - 1)
        await ctx.send('Banner changed.')

    @profile.command(aliases=['תיאור'])
    async def description(self, ctx, *, DESC : str):
        """Sets a profile description."""
        await self.edit_field(ctx, description=DESC.strip('"'))
        await ctx.send('Description edited.')

    @profile.command(aliases=['יום הולדת', 'bday'])
    async def birthday(self, ctx, BDAY : str):
        """Sets a birthday to your profile."""
        bday = re.search(r'(\d+-\d+-\d+)', BDAY)
        if not bday:
            return await ctx.send('Invalid birthday inserted. The format is `DD-MM-YYYY`')
        else:
            bday = bday.group(1)
        await self.edit_field(ctx, bday=bday)
        await ctx.send('Birthday edited.')

    @profile.command()
    async def make(self, ctx):
        """Interactively set up a profile.
        This command will walk you through the steps required to create
        a profile. Note that it only goes through the basics of a profile.
        """
    
        message = ctx.message
        await ctx.send('Hello. Let\'s walk you through making a profile!\nWhat do you want your description to be?\nSay ``cancel`` to cancel.')
        def pred(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel
    
        desc = await self.bot.wait_for('message', check=pred)
        if desc.content.lower() == 'cancel':
            return await ctx.send('Cancelled profile creation.')
        if desc is None:
            return
        await ctx.send('Now tell me, what is your birthday? Format is DD-MM-YYYY.\nYou can also say none if you don\'t want to expose your birthday.\nSay ``cancel`` to cancel.')
        def pred(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel
    
        bday = await self.bot.wait_for('message', check=pred)
        if bday.content.lower() == 'cancel':
            return await ctx.send('Cancelled profile creation.')
        if not desc:
            return
        bday = re.search(r'(\d+-\d+-\d+)', bday.clean_content)
        if not bday:
            bday = '`.profile birthday <DD-MM-YYY>`'
        else:
            bday = bday.group(1)
        query = "insert into profiles values ({}, '{}', '{}', 0, 0, 0, 0, 0, 0, 0, null, null)".format(ctx.author.id, desc.clean_content, bday)
        await self.bot.pool.execute(query)
        await ctx.send('Alright! Your profile is all ready now.')

    @commands.command()
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def mine(self, ctx):
        """Mines with a chance of getting money and or diamond."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        picks = profile['picks']
        cash = profile['cash']
        diamonds = profile['diamonds']
        if picks == 0:
            mine_cmd = self.bot.get_command('mine')
            mine_cmd.reset_cooldown(ctx)
            if cash >= 100:
                await ctx.send('You don\'t have any pickaxes.\nType yes in 20 seconds if you want to buy a pickaxe.')
                def pred(m):
                    return m.author == ctx.message.author and m.channel == ctx.message.channel

                answer = await self.bot.wait_for('message', check=pred)
                if answer.content.lower() in 'yes':
                    await ctx.invoke(self.pick)
                else:
                    await ctx.send('I\'ll take that as no.')
                    return
            else:
                await ctx.send('You don\'t have any pickaxes.')
        else:
            picks -= 1
            await self.edit_field(ctx, picks=picks)
            mining_chance = random.randint(1, 3)
            diamond_chance = random.randint(1, 25)
            if mining_chance == 1:
                await ctx.send('You broke your pickaxe.\n**You can mine again in 5 minutes!**')
                if diamond_chance == 1:
                    await ctx.send('But you found a diamond lying on the ground.')
                    diamonds += 1
                    await self.edit_field(ctx, diamonds=diamonds)
            else:
                found = random.randint(40, 200)
                cash += found
                await self.edit_field(ctx, cash=cash)
                await self.edit_field(ctx, picks=picks)
                await ctx.send('{} found ${} and has now ${}\n**You can mine again in 5 minutes!**'.format(ctx.message.author.display_name, found, cash))
                if diamond_chance == 1:
                    await ctx.send('You lucky, you found a diamond.')
                    diamonds += 1
                    await self.edit_field(ctx, diamonds=diamonds)

    @commands.command()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        """Gets your daily money."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        found = random.randint(100,150)
        cash += found
        await self.edit_field(ctx, cash=cash)
        await ctx.send('You got ${} from daily and you have ${} in total.\n**Come get your daily again after 24h.**'.format(found, cash))

    @commands.command(aliases=['balance', 'כסף', 'בנק'])
    async def money(self, ctx):
        """Shows your money amount."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        await ctx.send('You have ${}'.format(cash))

    @commands.command()
    @commands.cooldown(1, 180, commands.BucketType.user)
    async def loot(self, ctx):
        """Loots money from messages."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        found = random.randint(20,50)
        cash = cash + found
        await self.edit_field(ctx, cash=cash)
        await ctx.send('{} found ${}, and has now ${}\n**You can loot again in 3 minutes!**'.format(ctx.message.author.display_name, found, cash))

    @commands.command(aliases=['shop'])
    async def market(self, ctx):
        """Shows item prices."""
        pages=[':pick: Pickaxe: Buy :inbox_tray:  $100, Sell :outbox_tray:  $75',
              ':ring: Ring: Buy :inbox_tray:  $200, Sell :outbox_tray:  $150',
              ':diamond_shape_with_a_dot_inside: Diamond: Buy :inbox_tray:  $2000, Sell :outbox_tray:  $1500',
              ':rose: Rose: Buy :inbox_tray:  $25, Sell :outbox_tray:  $19',
              ':champagne: Alcohol: Buy :inbox_tray:  $50, Sell :outbox_tray:  $38',
              ':medal: Bronze role: Buy :inbox_tray:  $10000, Sell :outbox_tray: Can not sell.',
              ':medal: Silver role: Buy :inbox_tray:  $10000, Sell :outbox_tray: Can not sell.',
              ':medal: Gold role: Buy :inbox_tray:  $10000, Sell :outbox_tray: Can not sell.',
              ':medal: Blue role: Buy :inbox_tray:  $10000, Sell :outbox_tray: Can not sell.',
              ':third_place: Red role: Buy :inbox_tray:  $10000, Sell :outbox_tray: Can not sell.',
              ':second_place: Black role: Buy :inbox_tray:  $10000, Sell :outbox_tray: Can not sell.',
              ':first_place: Green role: Buy :inbox_tray:  $10000, Sell :outbox_tray: Can not sell.',
              ':dog: Dog: Buy :inbox_tray:  $10000, Sell :outbox_tray:  $7500',
              ':cat2: Cat: Buy :inbox_tray:  $20000, Sell :outbox_tray:  $15000',
              ':mouse: Mouse: Buy :inbox_tray:  $5000, Sell :outbox_tray:  $4500',
              ':hamster: Hamster: Buy :inbox_tray:  $15000, Sell :outbox_tray:  $11250',
              ':rabbit: Rabbit: Buy :inbox_tray:  $10000, Sell :outbox_tray:  $7500',
              ':pig2: Pig: Buy :inbox_tray:  $50000, Sell :outbox_tray:  $37500',
              ':bear: Bear: Buy :inbox_tray:  $100000, Sell :outbox_tray:  $75000',
              ':dragon: Dragon: Buy :inbox_tray:  $100000000000000, Sell :outbox_tray:  $75000000000000',
              ]
        try:
            p = Pages(ctx, entries=pages, per_page=10)
            # p.embed.title = str(base)
            p.embed.timestamp = datetime.datetime.utcnow()
            p.embed.title=":shopping_cart: Market:"
            await p.paginate()
        except Exception as e:
            await ctx.send(e)

    @commands.group(invoke_without_command=True)
    async def sell(self, ctx):
        """Use ``(prefix)help sell`` for more information."""
        await ctx.send('Use ``{}help sell`` for more information.'.format(ctx.prefix))

    @sell.command(name='dog')
    async def _dog(self, ctx):
        """Sells a dog."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        pet = profile['pet']
        if not pet:
            return await ctx.send('You don\'t have a pet.')
        if pet != ':dog: Dog':
            await ctx.send('You do not have this pet.' \
                           f'Your pet is {pet}.')
        else:
            cash += 7500
            pet = None
            await self.edit_field(ctx, cash=cash)            
            await self.edit_field(ctx, pet=pet)            
            await ctx.send('Sold :dog:')

    @sell.command(name='cat')
    async def _cat(self, ctx):
        """Sells a dog."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        pet = profile['pet']
        if not pet:
            return await ctx.send('You don\'t have a pet.')
        if pet != ':cat2: Cat':
            await ctx.send('You do not have this pet.' \
                           f'Your pet is {pet}.')
        else:
            cash += 15000
            pet = None
            await self.edit_field(ctx, cash=cash)
            await self.edit_field(ctx, pet=pet)
            await ctx.send('Sold :cat2:')

    @sell.command(name='mouse')
    async def _mouse(self, ctx):
        """Sells a mouse."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        pet = profile['pet']
        if not pet:
            return await ctx.send('You don\'t have a pet.')
        if pet != ':mouse: Mouse':
            await ctx.send('You do not have this pet.' \
                           f'Your pet is {pet}.')
        else:
            cash += 4500
            pet = None
            await self.edit_field(ctx, cash=cash)            
            await self.edit_field(ctx, pet=pet)            
            await ctx.send('Sold :mouse:')

    @sell.command(name='hamster')
    async def _hamster(self, ctx):
        """Sells a mouse."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        pet = profile['pet']
        if not pet:
            return await ctx.send('You don\'t have a pet.')
        if pet != ':hamster: Hamster':
            await ctx.send('You do not have this pet.' \
                           f'Your pet is {pet}.')
        else:
            cash += 4500
            pet = None
            await self.edit_field(ctx, cash=cash)            
            await self.edit_field(ctx, pet=pet)            
            await ctx.send('Sold :hamster:')

    @sell.command(name='rabbit')
    async def _rabbit(self, ctx):
        """Sells a mouse."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        pet = profile['pet']
        if not pet:
            return await ctx.send('You don\'t have a pet.')
        if pet != ':rabbit: Rabbit':
            await ctx.send('You do not have this pet.' \
                           f'Your pet is {pet}.')
        else:
            cash += 7500
            pet = None
            await self.edit_field(ctx, cash=cash)            
            await self.edit_field(ctx, pet=pet)            
            await ctx.send('Sold :rabbit:')

    @sell.command(name='dragon')
    async def _dragon(self, ctx):
        """Sells a dragon."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        pet = profile['pet']
        if not pet:
            return await ctx.send('You don\'t have a pet.')
        if pet != ':dragon: Dragon':
            await ctx.send('You do not have this pet.' \
                           f'Your pet is {pet}.')
        else:
            cash += 75000000000000
            pet = None
            await self.edit_field(ctx, cash=cash)            
            await self.edit_field(ctx, pet=pet)            
            await ctx.send('Sold :dragon:')

    @sell.command(name='bear')
    async def _bear(self, ctx):
        """Sells a mouse."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        pet = profile['pet']
        if not pet:
            return await ctx.send('You don\'t have a pet.')
        if pet != ':bear: Bear':
            await ctx.send('You do not have this pet.' \
                           f'Your pet is {pet}.')
        else:
            cash += 75000
            pet = None
            await self.edit_field(ctx, cash=cash)            
            await self.edit_field(ctx, pet=pet)            
            await ctx.send('Sold :bear:')

    @sell.command(name='pig')
    async def _pig(self, ctx):
        """Sells a mouse."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        pet = profile['pet']
        if not pet:
            return await ctx.send('You don\'t have a pet.')
        if pet != ':pig2: Pig':
            await ctx.send('You do not have this pet.' \
                           f'Your pet is {pet}.')
        else:
            cash += 37500
            pet = None
            await self.edit_field(ctx, cash=cash)            
            await self.edit_field(ctx, pet=pet)            
            await ctx.send('Sold :pig2:')

    @sell.command(name='pick')
    async def pic(self, ctx, amount : int = None):
        """Sells a pickaxe."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        picks = profile['picks']
        if amount is None:
            amount = 1
        if picks == 0:
            await ctx.send('You don\'t have any pickaxes.')
        else:
            if amount > picks:
                await ctx.send('You don\'t have that many pickaxes.')
                return
            cash += amount * 75
            picks -= amount
            await self.edit_field(ctx, cash=cash)
            await self.edit_field(ctx, picks=picks)
            await ctx.send('Sold {}x :pick:'.format(amount))

    @sell.command(name='ring')
    async def rin(self, ctx, amount : int = None):
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        rings = profile['rings']
        if amount is None:
            amout = 1
        if rings == 0:
            await ctx.send('You don\'t have any rings.')
        else:
            if amount > rings:
                await ctx.send('You don\'t have that many rings.')
                return
            cash += amount * 150
            rings -= amount
            await self.edit_field(ctx, cash=cash)
            await self.edit_field(ctx, rings=rings)
            await ctx.send('Sold {}x :ring:'.format(amount))

    @sell.command(name='diamond')
    async def diamon(self, ctx, amount : int = None):
        """Sells a diamond."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        diamonds = profile['diamonds']
        cash = profile['cash']
        if amount is None:
            amount = 1
        if diamonds == 0:
            await ctx.send('You don\'t have any diamonds.')
        else:
            if amount > diamonds:
                await ctx.send('You don\'t have that many diamonds.')
                return
            cash += amount * 1500
            diamonds -= amount
            await self.edit_field(ctx, diamonds=diamonds)
            await self.edit_field(ctx, cash=cash)
            await ctx.send('Sold {}x :diamond_shape_with_a_dot_inside:'.format(amount))

    @sell.command(name='rose')
    async def ros(self, ctx, amount : int = None):
        """Sells a rose."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        roses = profile['roses']
        cash = profile['cash']
        if amount is None:
            amount = 1
        if roses == 0:
            await ctx.send('You don\'t have any roses.')
        else:
            if amount > roses:
                await ctx.send('You don\'t have that many roses.')
                return
            cash += amount * 19
            roses -= amount
            await self.edit_field(ctx, roses=roses)
            await self.edit_field(ctx, cash=cash)
            await ctx.send('Sold {}x :rose:'.format(amount))

    @sell.command(name='alcohol', aliases=['vodka'])
    async def alcoho(self, ctx, amount : int = None):
        """Sells alcohol."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        alcohol = profile['alcohol']
        cash = profile['cash']
        if amount is None:
            amount = 1
        if alcohol == 0:
            await ctx.send('You don\'t have any alcohol.')
        else:
            if amount > alcohol:
                await ctx.send('You don\'t have that much alcohol.')
                return
            cash += amount * 38
            alcohol -= amount
            await self.edit_field(ctx, alcohol=alcohol)
            await self.edit_field(ctx, cash=cash)
            await ctx.send('Sold {}x :champagne:'.format(amount))

    @commands.command()
    async def drink(self, ctx):
        """Drinks alcohol."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
            return
        alcohol = profile['alcohol']
        if alcohol == 0:
            await ctx.send('You don\'t have any alcohol.')
        else:
            alcohol -= 1
            await self.edit_field(ctx, alcohol=alcohol)
            await ctx.send('You drank :champagne: and got drunk.')

    @commands.group(invoke_without_command=True)
    async def buy(self, ctx):
        """Use ``(prefix)help buy`` for more information."""
        print("buying")

    @buy.command()
    async def dog(self, ctx):
        """Buys a dog."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        pet = profile['pet']
        if pet:
            return await ctx.send(f'You have a {pet} already.')
        if 10000 > cash:
            return await ctx.send('You don\'t have enough money.')
        cash -= 10000
        pet = ':dog: Dog'
        await self.edit_field(ctx, cash=cash)
        await self.edit_field(ctx, pet=pet)
        await ctx.send('Bought :dog:')

    @buy.command()
    async def cat(self, ctx):
        """Buys a cat."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        pet = profile['pet']
        if pet:
            return await ctx.send(f'You have a {pet} already.')
        if 20000 > cash:
            return await ctx.send('You don\'t have enough money.')
        cash -= 20000
        pet = ':cat2: Cat'
        await self.edit_field(ctx, cash=cash)
        await self.edit_field(ctx, pet=pet)
        await ctx.send('Bought :cat2:')

    @buy.command()
    async def mouse(self, ctx):
        """Buys a mouse."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        pet = profile['pet']
        if pet:
            return await ctx.send(f'You have a {pet} already.')
        if 5000 > cash:
            return await ctx.send('You don\'t have enough money.')
        cash -= 5000
        pet = ':mouse: Mouse'
        await self.edit_field(ctx, cash=cash)
        await self.edit_field(ctx, pet=pet)
        await ctx.send('Bought :mouse:')

    @buy.command()
    async def hamster(self, ctx):
        """Buys a hamster."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        pet = profile['pet']
        if pet:
            return await ctx.send(f'You have a {pet} already.')
        if 15000 > cash:
            return await ctx.send('You don\'t have enough money.')
        cash -= 11250
        pet = ':hamster: Hamster'
        await self.edit_field(ctx, cash=cash)
        await self.edit_field(ctx, pet=pet)
        await ctx.send('Bought :hamster:')

    @buy.command()
    async def rabbit(self, ctx):
        """Buys a rabbit."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        pet = profile['pet']
        if pet:
            return await ctx.send(f'You have a {pet} already.')
        if 10000 > cash:
            return await ctx.send('You don\'t have enough money.')
        cash -= 10000
        pet = ':rabbit: Rabbit'
        await self.edit_field(ctx, cash=cash)
        await self.edit_field(ctx, pet=pet)
        await ctx.send('Bought :rabbit:')

    @buy.command()
    async def bear(self, ctx):
        """Buys a bear."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        pet = profile['pet']
        if pet:
            return await ctx.send(f'You have a {pet} already.')
        if 100000 > cash:
            return await ctx.send('You don\'t have enough money.')
        cash -= 100000
        pet = ':bear: Bear'
        await self.edit_field(ctx, cash=cash)
        await self.edit_field(ctx, pet=pet)
        await ctx.send('Bought :bear:')

    @buy.command()
    async def dragon(self, ctx):
        """Buys a dragon."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        pet = profile['pet']
        if pet:
            return await ctx.send(f'You have a {pet} already.')
        if 100000000000000 > cash:
            return await ctx.send('You don\'t have enough money.')
        cash -= 100000000000000
        pet = ':dragon: Dragon'
        await self.edit_field(ctx, cash=cash)
        await self.edit_field(ctx, pet=pet)
        await ctx.send('Bought :dragon:')

    @buy.command()
    async def pig(self, ctx):
        """Buys a pig."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        pet = profile['pet']
        if pet:
            return await ctx.send(f'You have a {pet} already.')
        if 50000 > cash:
            return await ctx.send('You don\'t have enough money.')
        cash -= 50000
        pet = ':pig2: Pig'
        await self.edit_field(ctx, cash=cash)
        await self.edit_field(ctx, pet=pet)
        await ctx.send('Bought :pig2:')

    @buy.command()
    async def pick(self, ctx, amount : int = None):
        """Buys a pickaxe."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        if amount is None:
            amount =1
        cash = profile['cash']
        picks = profile['picks']
        if amount*100 > cash:
            await ctx.send('You don\'t have enough money.')
            return
        if cash >= 100:
            cash -= amount * 100
            picks += amount
            if amount is None:
                amount = 1
            await ctx.send('Bought {}x :pick:'.format(amount))
            await self.edit_field(ctx, cash=cash)
            await self.edit_field(ctx, picks=picks)
        else:
            await ctx.send('You don\'t have enough cash.')

    @buy.command()
    async def ring(self, ctx, amount : int = None):
        """Buys a ring."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        rings = profile['rings']
        cash = profile['cash']
        if amount is None:
            amount = 1
        if amount*200 > cash:
            await ctx.send('You don\'t have enough money.')
            return
        if cash >= 200:
            cash -= amount * 200
            rings += amount
            await ctx.send('Bought {}x :ring:'.format(amount))
            await self.edit_field(ctx, cash=cash)
            await self.edit_field(ctx, rings=rings)
        else:
            await ctx.send('You don\'t have enough cash.')

    @buy.command()
    async def diamond(self, ctx, amount : int = None):
        """Buys a diamond."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        diamonds = profile['diamonds']
        if amount is None:
            amount = 1
        if amount*2000 > cash:
            await ctx.send('You don\'t have enough money.')
            return
        if cash >= amount*2000:
            cash -= amount * 2000
            diamonds += amount
            await self.edit_field(ctx, cash=cash)
            await self.edit_field(ctx, diamonds=diamonds)
            await ctx.send('Bought {}x :diamond_shape_with_a_dot_inside:'.format(amount))
        else:
            await ctx.send('You don\'t have enough cash.')

    @buy.command()
    async def rose(self, ctx, amount : int = None):
        """Buys a rose."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        roses = profile['roses']
        if amount is None:
            amount = 1
        if amount*25 > cash:
            await ctx.send('You don\'t have enough money.')
            return
        if cash >= 25:
            cash -= amount * 25
            roses += amount
            await self.edit_field(ctx, cash=cash)
            await self.edit_field(ctx, roses=roses)
            await ctx.send('Bought {}x :rose:'.format(amount))
        else:
            await ctx.send('You don\'t have enough cash.')

    @buy.command(aliases=['vodka'])
    async def alcohol(self, ctx, amount : int = None):
        """Buys alcohol."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        alcohol = profile['alcohol']
        if amount is None:
            amount = 1
        if amount*50 > cash:
            await ctx.send('You don\'t have enough money.')
            return
        if cash >= 50:
            cash -= amount * 50
            alcohol += amount
            await self.edit_field(ctx, cash=cash)
            await self.edit_field(ctx, alcohol=alcohol)
            await ctx.send('Bought {}x :champagne:'.format(amount))
        else:
            await ctx.send('You don\'t have enough cash.')

    @buy.command()
    async def bronze(self, ctx):
        """Buys a Putin market Bronze role. You can not sell this after buying."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        if cash < 10000:
            return await ctx.send('You do not have enough money to buy this role.')
        for role in ctx.author.roles:
            if role.name == 'Putin Bronze':
                return await ctx.send('Why\'d you buy this role again?')
        data = await self.bot.pool.fetchrow(f'select buy_roles from settings where id={ctx.guild.id}')
        if not data: return await ctx.send('This guild hasn\'t enabled role buying.')
        if not data[0]: return await ctx.send('This guild hasn\'t enabled role buying.')
        try:
            role = discord.utils.get(ctx.guild.roles, name='Putin Bronze')
            if not role:
                try:
                    role = await ctx.guild.create_role(name='Putin Bronze', color=discord.Color.from_rgb(145, 44, 7), reason='Putin Market Buyable role.', mentionable=False)
                    await ctx.author.add_roles(role, reason='Putin Market Buyable role.')
                    return await ctx.send('Bought Putin Bronze role.')
                except discord.Forbidden:
                    return await ctx.send('It seems that buyable roles are enable but I could not create it or I couldn\'t add it to you.')
                except Exception as e:
                    print(e)
            role = discord.utils.get(ctx.guild.roles, name='Putin Bronze')
            await ctx.author.add_roles(role, reason='Putin Market Buyable role.')
            await ctx.send('Bought Putin Bronze role.')
        except discord.Forbidden:
            return await ctx.send('I couldn\'t add the role to you.')
        except Exception as e:
            print(e)
        cash -= 10000
        await self.edit_field(ctx, cash=cash)

    @buy.command()
    async def silver(self, ctx):
        """Buys a Putin market Silver role. You can not sell this after buying."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        if cash < 10000:
            return await ctx.send('You do not have enough money to buy this role.')
        for role in ctx.author.roles:
            if role.name == 'Putin Silver':
                return await ctx.send('Why\'d you buy this role again?')
        data = await self.bot.pool.fetchrow(f'select buy_roles from settings where id={ctx.guild.id}')
        if not data: return await ctx.send('This guild hasn\'t enabled role buying.')
        if not data[0]: return await ctx.send('This guild hasn\'t enabled role buying.')
        try:
            role = discord.utils.get(ctx.guild.roles, name='Putin Silver')
            if not role:
                try:
                    role = await ctx.guild.create_role(name='Putin Silver', color=discord.Color.from_rgb(144, 159, 165), reason='Putin Market Buyable role.', mentionable=False)
                    await ctx.author.add_roles(role, reason='Putin Market Buyable role.')
                    return await ctx.send('Bought Putin Silver role.')
                except discord.Forbidden:
                    return await ctx.send('It seems that buyable roles are enable but I could not create it or I couldn\'t add it to you.')
                except Exception as e:
                    print(e)
            role = discord.utils.get(ctx.guild.roles, name='Putin Silver')
            await ctx.author.add_roles(role, reason='Putin Market Buyable role.')
            await ctx.send('Bought Putin Silver role.')
        except discord.Forbidden:
            return await ctx.send('I couldn\'t add the role to you.')
        except Exception as e:
            print(e)
        cash -= 10000
        await self.edit_field(ctx, cash=cash)

    @buy.command()
    async def gold(self, ctx):
        """Buys a Putin market Gold role. You can not sell this after buying."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        if cash < 10000:
            return await ctx.send('You do not have enough money to buy this role.')
        for role in ctx.author.roles:
            if role.name == 'Putin Gold':
                return await ctx.send('Why\'d you buy this role again?')
        data = await self.bot.pool.fetchrow(f'select buy_roles from settings where id={ctx.guild.id}')
        if not data: return await ctx.send('This guild hasn\'t enabled role buying.')
        if not data[0]: return await ctx.send('This guild hasn\'t enabled role buying.')
        try:
            role = discord.utils.get(ctx.guild.roles, name='Putin Gold')
            if not role:
                try:
                    role = await ctx.guild.create_role(name='Putin Gold', color=discord.Color.from_rgb(209, 150, 33), reason='Putin Market Buyable role.', mentionable=False)
                    await ctx.author.add_roles(role, reason='Putin Market Buyable role.')
                    return await ctx.send('Bought Putin Gold role.')
                except discord.Forbidden:
                    return await ctx.send('It seems that buyable roles are enable but I could not create it or I couldn\'t add it to you.')
                except Exception as e:
                    print(e)
            role = discord.utils.get(ctx.guild.roles, name='Putin Gold')
            await ctx.author.add_roles(role, reason='Putin Market Buyable role.')
            await ctx.send('Bought Putin Gold role.')
        except discord.Forbidden:
            return await ctx.send('I couldn\'t add the role to you.')
        except Exception as e:
            print(e)
        cash -= 10000
        await self.edit_field(ctx, cash=cash)


    @buy.command()
    async def blue(self, ctx):
        """Buys a Putin market Blue role. You can not sell this after buying."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        if cash < 10000:
            return await ctx.send('You do not have enough money to buy this role.')
        for role in ctx.author.roles:
            if role.name == 'Putin Blue':
                return await ctx.send('Why\'d you buy this role again?')
        data = await self.bot.pool.fetchrow(f'select buy_roles from settings where id={ctx.guild.id}')
        if not data: return await ctx.send('This guild hasn\'t enabled role buying.')
        if not data[0]: return await ctx.send('This guild hasn\'t enabled role buying.')
        try:
            role = discord.utils.get(ctx.guild.roles, name='Putin Blue')
            if not role:
                try:
                    role = await ctx.guild.create_role(name='Putin Blue', color=discord.Color.from_rgb(66, 134, 244), reason='Putin Market Buyable role.', mentionable=False)
                    await ctx.author.add_roles(role, reason='Putin Market Buyable role.')
                    return await ctx.send('Bought Putin Blue role.')
                except discord.Forbidden:
                    return await ctx.send('It seems that buyable roles are enable but I could not create it or I couldn\'t add it to you.')
                except Exception as e:
                    print(e)
            role = discord.utils.get(ctx.guild.roles, name='Putin Blue')
            await ctx.author.add_roles(role, reason='Putin Market Buyable role.')
            await ctx.send('Bought Putin Blue role.')
        except discord.Forbidden:
            return await ctx.send('I couldn\'t add the role to you.')
        except Exception as e:
            print(e)
        cash -= 10000
        await self.edit_field(ctx, cash=cash)

    @buy.command()
    async def red(self, ctx):
        """Buys a Putin market Red role. You can not sell this after buying."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        if cash < 10000:
            return await ctx.send('You do not have enough money to buy this role.')
        for role in ctx.author.roles:
            if role.name == 'Putin Red':
                return await ctx.send('Why\'d you buy this role again?')
        data = await self.bot.pool.fetchrow(f'select buy_roles from settings where id={ctx.guild.id}')
        if not data: return await ctx.send('This guild hasn\'t enabled role buying.')
        if not data[0]: return await ctx.send('This guild hasn\'t enabled role buying.')
        try:
            role = discord.utils.get(ctx.guild.roles, name='Putin Red')
            if not role:
                try:
                    role = await ctx.guild.create_role(name='Putin Red', color=discord.Color.from_rgb(183, 14, 14), reason='Putin Market Buyable role.', mentionable=False)
                    await ctx.author.add_roles(role, reason='Putin Market Buyable role.')
                    return await ctx.send('Bought Putin Red role.')
                except discord.Forbidden:
                    return await ctx.send('It seems that buyable roles are enable but I could not create it or I couldn\'t add it to you.')
                except Exception as e:
                    print(e)
            role = discord.utils.get(ctx.guild.roles, name='Putin Red')
            await ctx.author.add_roles(role, reason='Putin Market Buyable role.')
            await ctx.send('Bought Putin Red role.')
        except discord.Forbidden:
            return await ctx.send('I couldn\'t add the role to you.')
        except Exception as e:
            print(e)
        cash -= 10000
        await self.edit_field(ctx, cash=cash)

    @buy.command()
    async def black(self, ctx):
        """Buys a Putin market Black role. You can not sell this after buying."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        if cash < 10000:
            return await ctx.send('You do not have enough money to buy this role.')
        for role in ctx.author.roles:
            if role.name == 'Putin Black':
                return await ctx.send('Why\'d you buy this role again?')
        data = await self.bot.pool.fetchrow(f'select buy_roles from settings where id={ctx.guild.id}')
        if not data: return await ctx.send('This guild hasn\'t enabled role buying.')
        if not data[0]: return await ctx.send('This guild hasn\'t enabled role buying.')
        try:
            role = discord.utils.get(ctx.guild.roles, name='Putin Black')
            if not role:
                try:
                    role = await ctx.guild.create_role(name='Putin Black', color=discord.Color.from_rgb(22, 22, 22), reason='Putin Market Buyable role.', mentionable=False)
                    await ctx.author.add_roles(role, reason='Putin Market Buyable role.')
                    return await ctx.send('Bought Putin Black role.')
                except discord.Forbidden:
                    return await ctx.send('It seems that buyable roles are enable but I could not create it or I couldn\'t add it to you.')
                except Exception as e:
                    print(e)
            role = discord.utils.get(ctx.guild.roles, name='Putin Black')
            await ctx.author.add_roles(role, reason='Putin Market Buyable role.')
            await ctx.send('Bought Putin Black role.')
        except discord.Forbidden:
            return await ctx.send('I couldn\'t add the role to you.')
        except Exception as e:
            print(e)
        cash -= 10000
        await self.edit_field(ctx, cash=cash)

    @buy.command()
    async def green(self, ctx):
        """Buys a Putin market Green role. You can not sell this after buying."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        if cash < 10000:
            return await ctx.send('You do not have enough money to buy this role.')
        for role in ctx.author.roles:
            if role.name == 'Putin Green':
                return await ctx.send('Why\'d you buy this role again?')
        data = await self.bot.pool.fetchrow(f'select buy_roles from settings where id={ctx.guild.id}')
        if not data: return await ctx.send('This guild hasn\'t enabled role buying.')
        if not data[0]: return await ctx.send('This guild hasn\'t enabled role buying.')
        try:
            role = discord.utils.get(ctx.guild.roles, name='Putin Green')
            if not role:
                try:
                    role = await ctx.guild.create_role(name='Putin Green', color=discord.Color.from_rgb(101, 206, 41), reason='Putin Market Buyable role.', mentionable=False)
                    await ctx.author.add_roles(role, reason='Putin Market Buyable role.')
                    return await ctx.send('Bought Putin Green role.')
                except discord.Forbidden:
                    return await ctx.send('It seems that buyable roles are enable but I could not create it or I couldn\'t add it to you.')
                except Exception as e:
                    print(e)
            role = discord.utils.get(ctx.guild.roles, name='Putin Green')
            await ctx.author.add_roles(role, reason='Putin Market Buyable role.')
            await ctx.send('Bought Putin Green role.')
        except discord.Forbidden:
            return await ctx.send('I couldn\'t add the role to you.')
        except Exception as e:
            print(e)
        cash -= 10000
        await self.edit_field(ctx, cash=cash)

    @commands.command()
    async def marry(self, ctx, *, member : discord.Member = None):
        """Marrys a member."""
        if member is None:
                await ctx.message.delete()
                msg = await ctx.send('You did not enter a user to propose.')
                await asyncio.sleep(10)
                await msg.delete()
                return
        if member:
            if ctx.message.author.id == member.id:
                await ctx.send('You can\'t marry yourself.')
                return
            if member.bot:
                await ctx.send('You can\'t marry a bot.')
                return
            else:
                query = """select * from profiles where id=$1"""
                profile = await self.bot.pool.fetchrow(query, ctx.author.id)
                if profile is None:
                    return await ctx.invoke(self.make)
                rings = profile['rings']
                married = profile['married']
                if married:
                    await ctx.send('You are already married with {}.'.format(married))
                    return
                query = """select * from profiles where id=$1"""
                member_profile = await self.bot.pool.fetchrow(query, ctx.author.id)
                if member_profile is None:
                    await ctx.send('That user does not have a profile.')
                member_married = member_profile['married']
                if member_married:
                    member_married_name = await self.bot.get_user_info(member_married)
                    await ctx.send('That user is already married with {}.'.format(member_married_name))
                    return
                if rings >= 2:
                    rings -= 2
                    await ctx.send('{} proposed {}.\n{} type yes or no in 60 seconds.'.format(ctx.message.author.display_name, member.display_name, member.mention))
                    def pred(m):
                        return m.author == member and m.channel == ctx.message.channel
                    try:
                        answer = await self.bot.wait_for('message', timeout=60, check=pred)
                    except asyncio.TimeoutError:
                        return await ctx.send('No answer.')
                    if answer.content.lower() in 'yes':
                        await self.edit_field(ctx, rings=rings)
                        await self.edit_user_field(member, ctx, married=ctx.message.author.id)
                        await self.edit_field(ctx, married=member.id)
                        await ctx.send(':heart: | {} is now married with {}'.format(ctx.message.author.display_name, member.name))
                    elif answer.content.lower() in 'no':
                        await ctx.send('Proposing denied..')
                    else:
                        await ctx.send('I\'ll take that as a no.')
                else:
                    await ctx.send('You need 2 rings to propose.')
        else:
            await ctx.send('User not found.')

    @commands.command()
    async def divorce(self, ctx, *, member : discord.Member = None):
        """Divorces with a member."""
        if member is None:
            return await ctx.send('You didn\'t tell me who you want to divorce with.')
        else:
            query = """select * from profiles where id=$1"""
            profile = await self.bot.pool.fetchrow(query, ctx.author.id)
            if profile is None:
                return await ctx.invoke(self.make)
            married = profile['married']
            if not married:
                await ctx.send('You weren\'t married in the first place.')
                return
            query = """select * from profiles where id=$1"""
            m_profile = await self.bot.pool.fetchrow(query, ctx.author.id)

            if m_profile is None:
                msg = await ctx.send('That user does not have a profle.')
            m_married = m_profile['married']
            if member.id == married:
                await ctx.send('{} would like to get divorced with {}.\n{} type yes in 60 seconds if you want to get divorced.'.format(ctx.message.author.display_name, member.display_name, member.mention))
                def pred(m):
                    return m.author == member and m.channel == ctx.message.channel

                try:
                    answer = await self.bot.wait_for('message', timeout=60, check=pred)
                except asyncio.TimeoutError:
                    return await ctx.send('No answer.')
                if answer.content in 'yes':
                    await self.edit_user_field(member, ctx, married=None)
                    await self.edit_field(ctx, married=None)
                    await ctx.send(':broken_heart: | {} got divorced with {}.'.format(ctx.message.author.display_name, member.display_name))
                else:
                    await ctx.send('I\'ll take that as no.')
            else:
                await ctx.send('You are not married with that user.')

    @commands.group(aliases=['giveitem'])
    async def itemtransfer(self, ctx):
        """Use ``(prefix)help itemtransfer`` for more information."""

    @itemtransfer.command(name='pick')
    async def ppick(self, ctx, member : discord.Member = None):
        """Gives your pickaxe to another member."""
        try:
            await ctx.message.delete()
        except:
            pass
        if member is None:
            msg = await ctx.send('You didn\'t tell who to give the item.')
            await asyncio.sleep(10)
            await msg.delete()
        else:
            query = """select * from profiles where id=$1"""
            profile = await self.bot.pool.fetchrow(query, ctx.author.id)
            if profile is None:
                return await ctx.invoke(self.make)
            picks = profile['picks']
            if picks == 0:
                await ctx.send('You don\'t have any pickaxes.')
            else:
                picks -= 1
                query = """select * from profiles where id=$1"""
                member_profile = await self.bot.pool.fetchrow(query, ctx.author.id)
                if member_profile is None:
                    await ctx.send('That user does not have a profile.')
                member_picks = member_profile['picks'] + 1
                await self.edit_field(ctx, picks=picks)
                await self.edit_user_field(member, ctx, picks=member_picks)
                await ctx.send('Gave :pick: to {}.'.format(member.display_name))

    @itemtransfer.command(name='ring')
    async def rring(self, ctx, *, member : discord.Member = None):
        """Gives your ring to another member."""
        try:
            await ctx.message.delete()
        except:
            pass
        if member is None:
            msg = await ctx.send('You didn\'t tell who to give the item.')
            await asyncio.sleep(10)
            await msg.delete()
        else:
            query = """select * from profiles where id=$1"""
            profile = await self.bot.pool.fetchrow(query, ctx.author.id)
            if profile is None:
                return await ctx.invoke(self.make)
            rings = profile['rings']
            if rings == 0:
                msg = await ctx.send('You don\'t have any rings.')
                await asyncio.sleep(10)
                await msg.delete()
            else:
                rings -= 1
                query = """select * from profiles where id=$1"""
                member_profile = await self.bot.pool.fetchrow(query, ctx.author.id)
                if member_profile is None:
                    await ctx.send('That user does not have a profile.')
                member_rings = member_profile['rings'] + 1
                await self.edit_field(ctx, rings=rings)
                await self.edit_user_field(member, ctx, rings=member_rings)
                await ctx.send('Gave :ring: to {}.'.format(member.display_name))

    @itemtransfer.command(name='diamond')
    async def ddiamond(self, ctx, *, member : discord.Member = None):
        """Gives your diamond to another member."""
        try:
            await ctx.message.delete()
        except:
            pass
        if member is None:
            msg = await ctx.send('You didn\'t tell who to give the item.')
            await asyncio.sleep(10)
            await msg.delete()
        else:
            query = """select * from profiles where id=$1"""
            profile = await self.bot.pool.fetchrow(query, ctx.author.id)
            if profile is None:
                return await ctx.invoke(self.make)
            diamonds = profile['diamonds']
            if diamonds == 0:
                msg = await ctx.send('You don\'t have any diamonds.')
                await asyncio.sleep(10)
                await msg.delete()
            else:
                diamonds -=1
                query = """select * from profiles where id=$1"""
                member_profile = await self.bot.pool.fetchrow(query, ctx.author.id)
                if member_profile is None:
                    await ctx.send('That user does not have a profile.')
                member_diamonds = member_profile['diamonds'] + 1
                await self.edit_field(ctx, diamonds=diamonds)
                await self.edit_user_field(member, ctx, diamonds=member_diamonds)
                await ctx.send('Gave :diamond_shape_with_a_dot_inside: to {}.'.format(member.display_name))

    @itemtransfer.command(name='rose')
    async def rrose(self, ctx, *, member : discord.Member = None):
        """Gives your rose to another member."""
        try:
            await ctx.message.delete()
        except:
            pass
        if member is None:
            msg = await ctx.send('You didn\'t tell who to give the item.')
        else:
            query = """select * from profiles where id=$1"""
            profile = await self.bot.pool.fetchrow(query, ctx.author.id)
            if profile is None:
                return await ctx.invoke(self.make)
            roses = profile['roses']
            if roses == 0:
                msg = await ctx.send('You don\'t have any roses.')
            else:
                roses -=1
                query = """select * from profiles where id=$1"""
                member_profile = await self.bot.pool.fetchrow(query, ctx.author.id)
                if member_profile is None:
                    await ctx.send('That user does not have a profile.')
                member_roses = member_profile['roses'] + 1
                await self.edit_field(ctx, roses=roses)
                await self.edit_user_field(member, ctx, roses=member_roses)
                await ctx.send('Gave :rose: to {}.'.format(member.display_name))

    @itemtransfer.command(name='alcohol')
    async def aalcohol(self, ctx, *, member : discord.Member = None):
        """Gives your alcohol to another member."""
        try:
            await ctx.message.delete()
        except:
            pass
        if member is None:
            msg = await ctx.send('You didn\'t tell who to give the item.')
        else:
            query = """select * from profiles where id=$1"""
            profile = await self.bot.pool.fetchrow(query, ctx.author.id)
            if profile is None:
                return await ctx.invoke(self.make)
            alcohol = profile['alcohol']
            if alcohol == 0:
                msg = await ctx.send('You don\'t have any alcohol.')
            else:
                alcohol -=1
                query = """select * from profiles where id=$1"""
                member_profile = await self.bot.pool.fetchrow(query, ctx.author.id)
                if member_profile is None:
                    await ctx.send('That user does not have a profile.')
                member_alcohol = member_profile['alcohol'] + 1
                await self.edit_field(ctx, alcohol=alcohol)
                await self.edit_user_field(member, ctx, alcohol=member_alcohol)
                await ctx.send('Gave :champagne: to {}.'.format(member.display_name))

    @commands.command(aliases=['givemoney'])
    # @commands.is_owner()
    async def moneytransfer(self, ctx, amount : int, *, member : discord.Member = None):
        """Gives the amount you specify from your money to the member you specify."""
        if ctx.author.id == member.id:
            return await ctx.send('Why\'d you give yourself money from yourself?')
        if amount < 1:
            await ctx.send('You can\'t transfer less than $1.')
            return
        if not member:
            return await ctx.send('You didn\'t tell me who to give the money to.')
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = profile['cash']
        if cash <= amount:
            msg = await ctx.send('You don\'t have enough money to give.')
        else:
            cash -= amount
            query = """select * from profiles where id=$1"""
            member_profile = await self.bot.pool.fetchrow(query, member.id)
            if member_profile is None:
                return await ctx.send('That user does not have a profile.')
            member_cash = member_profile['cash']
            member_cash += amount
            await self.edit_field(ctx, cash=cash)
            await self.edit_user_field(member, ctx, cash=member_cash)
            await ctx.send('{} gave ${} to {}.'.format(ctx.author.display_name, amount, member.display_name))

    @commands.group(aliases=['סלוט'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def slots(self, ctx, amount: int = 10):
        """Plays slots default bet is $10"""
        # if ctx.subcommand_invoked is None:
        if amount < 10:
            await ctx.send('You can\'t bet less than $10.')
            return
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        if profile is None:
            return await ctx.invoke(self.make)
        cash = int(profile['cash'])
        if cash < amount:
            await ctx.send('You don\'t have enough cash.')
        else:
            cash -= amount
            slot = ['\U0001f4b0', '\U0001f347', '\U0001f353']
            slot1 = random.choice(slot)
            slot2 = random.choice(slot)
            slot3 = random.choice(slot)
            slot4 = random.choice(slot)
            slot5 = random.choice(slot)
            slot6 = random.choice(slot)
            slot7 = random.choice(slot)
            slot8 = random.choice(slot)
            slot9 = random.choice(slot)
            slot_machine = f'```╔════[SLOTS]════╗\n║ {slot1} ║ {slot2} ║ {slot3} ║\n> {slot4} ║ {slot5} ║ {slot6} <\n║ {slot7} ║ {slot8} ║ {slot9} ║\n╚════[SLOTS]════╝```'
            winning_times = 0
            if slot4 == slot5 and slot4 == slot6:
                winning_times += 1
            if slot1 == slot5 and slot1 == slot9:
                winning_times += 1
            if slot7 == slot5 and slot7 == slot3:
                winning_times += 1
            if slot1 == slot2 and slot1 == slot3:
                winning_times += 1
            if slot7 == slot8 and slot7 == slot9:
                winning_times += 1

            await ctx.send(f'{slot_machine}\n**{ctx.message.author.display_name}** bet ${amount} and won ${round(amount*int(winning_times/0.5))}')
            await self.edit_field(ctx, cash=cash+round(amount*int(winning_times/0.5)))

    @commands.command()
    async def challenge(self, ctx, *, member:discord.Member=None):
        """Challenges another member to a shooting fight.
        When you challenge someone you bet $100.
        The winner gets the money back and the opponent's bet too.
        So basically the winner get $200."""
        if member is None:
            return await ctx.send('You need to tell who to challenge.')

        if member.bot:
            return await ctx.send('You can\'t challenge a bot.')

        query = """select cash from profiles where id=$1"""
        cash = await self.bot.pool.fetchrow(query, ctx.author.id)

        if not cash:
            return await ctx.send('You don\'t have a profile yet.')

        if cash[0] is None or cash is None:
            return await ctx.send('You don\'t have a profile yet.')

        if cash[0] < 100:
            return await ctx.send('You need $100 to challenge someone.')

        def pred(m):
            return m.author == member and m.channel == ctx.message.channel

        await ctx.send(f'{ctx.author.display_name} would like to callenge {member.display_name}.\n'\
                       f'{member.display_name} type `yes` in 20 seconds to accept the challenge.')

        try:
            answer = await self.bot.wait_for('message', timeout=20, check=pred)
        except asyncio.TimeoutError:
            return await ctx.send('No answer.')
        if not answer.content.lower() in 'yes':
            return await ctx.send('I\'ll take that as no.')

        query = """select cash from profiles where id=$1"""
        _cash = await self.bot.pool.fetchrow(query, member.id)

        if _cash is None or _cash[0] is None:
            return await ctx.send('You don\'t have a profile yet.')

        if _cash[0] < 100:
            return await ctx.send('You need $100 to accept the callenge.')

        await self.edit_field(ctx, cash=cash[0]-100)
        await self.edit_user_field(member, ctx, cash=cash[0]-100)

        times = random.randint(1, 5)

        for i in range(times):
            await ctx.send(f'Wait' + '.'*i)
            if not i == times:
                await ctx.trigger_typing()
            wait = random.randint(2, 7)
            await asyncio.sleep(wait)

        words = ['fire', 'shoot', 'now', 'boom']

        word = random.choice(words)

        await ctx.send(f'Now quickly say ``{word}``')

        def pred(m):
            return m.author == member or ctx.author and m.channel == ctx.channel

        answer = await self.bot.wait_for('message', check=pred)

        if str(answer.clean_content.lower()) == str(word):
            if answer.author is ctx.author:
                winner = ctx.author
            else:
                winner = answer.author
        else:
            await ctx.send(f'Wrong word {answer.author.display_name}.')
            if answer.author is ctx.author:
                winner = member
            else:
                winner = ctx.author

        query = """select cash from profiles where id=$1"""
        winner_cash = await self.bot.pool.fetchrow(query, winner.id)

        await self.edit_user_field(winner, ctx, cash=winner_cash[0]+200)
        await ctx.send(f'Congrats {winner} you won $200.')

    @commands.command(aliases=['lb', 'leaderboards'])
    async def leaderboard(self, ctx):

        await ctx.trigger_typing()

        lookup = (
            '\N{FIRST PLACE MEDAL}',
            '\N{SECOND PLACE MEDAL}',
            '\N{THIRD PLACE MEDAL}',
            '\N{SPORTS MEDAL}',
            '\N{SPORTS MEDAL}'
        )

        query = """SELECT id as "_id", cash as "cash"
                FROM profiles
                ORDER BY "cash" DESC
                LIMIT 5;
        """
        records = await ctx.bot.pool.fetch(query)

        e = discord.Embed(title='Leaderboard')

        async def get_name(_id):
            user = await self.bot.get_user_info(_id)
            if user is not None:
                return user.name
            else:
                return 'Undefined'

        lb = []

        for record in records:
            try:
                name = await get_name(record['_id'])
            except:
                name = 'Undefined'
            if not record['cash']:
                continue
            lb.append((name, record['cash']))

        value = '\n'.join(f'{lookup[index]} **{_id}**: ``${cash}``' for (index, (_id, cash)) in enumerate(lb))
        e.color = discord.Color.from_rgb(75, 38, 168)
        e.add_field(name="Top global profiles by cash", value=value, inline=True)

        query = """SELECT id as "_id", experience as "exp"
                FROM profiles
                ORDER BY "exp" DESC
                LIMIT 5;
        """
        exps = await ctx.bot.pool.fetch(query)

        lb = []

        for record in exps:
            try:
                name = await get_name(record['_id'])
            except:
                name = 'Undefined'
            if not record['exp']:
                print(record)
                continue
            lb.append((name, record['exp']))

        value = '\n'.join(f'{lookup[index]} **{_id}**: ``{exp}``' for (index, (_id, exp)) in enumerate(lb))
        e.add_field(name="Top global profiles by experience", value=value, inline=True)
        await ctx.send(embed=e)

    async def on_message(self, message):
        if message.author.bot: return
        query = """select experience from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, message.author.id)
        ctx = await self.bot.get_context(message)
        if not profile:
            return
        if profile[0] == 0 or not profile[0]:
            return await self.edit_field(ctx, experience=10)
        exp = profile[0]
        add = random.randint(1, 10)
        exp += add
        await self.edit_field(ctx, experience=exp)

def setup(bot):
    bot.add_cog(Profile(bot))
