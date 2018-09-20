from discord.ext import commands
from .utils import db
import discord
import random
import re
import asyncio
from .utils.paginator import Pages
import datetime
from datetime import datetime as dtime
from datetime import timedelta
from .utils import context

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

class ProfileConfig:
    def __init__(self, ctx, record):
        self.ctx = ctx
        self.id = record['id'] or None
        self.xp = record['experience']
        self.description = record['description']
        self.level = record['level']
        self.last_xp_time = record['last_xp_time'] or False
        self.married = record['married'] or 'Nobody...'
        self.cash = record['cash'] or 0
        self.picks = record['picks'] or 0
        self.rings = record['rings'] or 0
        self.diamonds = record['diamonds'] or 0
        self.roses = record['roses'] or 0
        self.alcohol = record['roses'] or 0
        self.banner = record['banner'] or 0
        self.pet = record['pet'] or 'No pet'
        self.name = record['name']
        self.announce_level = record['announce_level']
        self.bday = record['bday'] or '`.profile birthday <DD-MM-YYYY>`'

    def __str__(self):
        return f'Profile of {self.name}'
    
    @property
    def is_ratelimited(self):
        return eval(self.last_xp_time) + timedelta(minutes=1) >= dtime.utcnow()

    async def edit_field(self, ctx, **fields):
        keys = ', '.join(fields)
        values = ', '.join(f'${2 + i}' for i in range(len(fields)))

        query = f"""update profiles
                    SET {keys} = {values}
                    where id=$1;
                 """

        await self.ctx.db.execute(query, self.id, *fields.values())
        av = ctx.author.avatar_url_as(format='png', size=1024)
        await ctx.db.execute(f'update profiles set name=\'{ctx.author.name}#{ctx.author.discriminator}\','\
                               f'pfp=\'{av}\' where id={ctx.author.id}')

    async def increase_xp(self, ctx):
        try:
            if self.is_ratelimited:
                return
            if not self.last_xp_time:
                _now = dtime.utcnow()
                await self.edit_field(ctx, last_xp_time=repr(_now))
            else:
                last_xp_time = dtime.utcnow()
                await self.edit_field(ctx, last_xp_time=repr(last_xp_time))
            new_xp = self.xp  + random.randint(15, 25)
            await self.edit_field(self.ctx, experience=new_xp)
            lvl = self.level
            new_lvl = Profile._get_level_from_xp(self.xp)
            await self.edit_field(ctx, level=new_lvl)
            if new_lvl != lvl:
                if self.announce_level and not ctx.guild.id == 264445053596991498:
                    await ctx.send(f'Good job {ctx.author.display_name} you just leveled up to level {new_lvl}!')
        except Exception as e:
            if ctx.channel.id == 482188217400033280:
                await ctx.send(e)

class Profile():
    def __init__(self, bot):
        self.bot = bot

    @staticmethod
    def _get_level_xp(n):
        return 5*(n**2)+50*n+100

    @staticmethod
    def _get_level_from_xp(xp):
        remaining_xp = int(xp)
        level = 0
        while remaining_xp >= Profile._get_level_xp(level):
            remaining_xp -= Profile._get_level_xp(level)
            level += 1
        return level

    async def get_profile(self, ctx, id):
        record = await self.bot.pool.fetchrow(f'select * from profiles where id={id}')
        return ProfileConfig(ctx, record) or None

    @commands.group(invoke_without_command=True)
    async def profile(self, ctx, *, member: DisambiguateMember = None):
        member = member or ctx.author
        av = member.avatar_url_as(format='png', size=1024)
        await self.bot.pool.execute(f'update profiles set name=\'{member.name}#{member.discriminator}\', pfp=\'{av}\' where id={member.id}')
        query = """select * from profiles where id=$1"""
        record = await self.bot.pool.fetchrow(query, member.id)

        if record is None:
            if member == ctx.author:
                return await ctx.invoke(self.make)
            else:
                await ctx.send(f'{ctx.tick(False)} This member did not set up a profile yet.')
            return

        profile = await self.get_profile(ctx, member.id)

        if not profile:
            return await ctx.invoke(self.make)

        if isinstance(member, discord.Member):
            color = member.top_role.color
        else:
            color = 0xcc205c

        e = discord.Embed(title="Profile of {}".format(member.display_name), color=color)
        e.set_thumbnail(url=member.avatar_url)
        
        e.add_field(name=':writing_hand: Description', value=profile.description)
        e.add_field(name=':birthday: Birthday', value=profile.bday)
        e.add_field(name=':moneybag: Cash', value='$' + str(profile.cash))
        e.add_field(name=':zap: Experience', value=str(profile.xp))
        e.add_field(name=':medal: Level', value=str(profile.level))
        
        picks = f':pick:{str(profile.picks)}' if profile.picks else ''
        rings = f':ring:{str(profile.rings)}' if profile.rings else ''
        diamonds = f':diamond_shape_with_a_dot_inside:{str(profile.diamonds)}' if profile.diamonds else ''
        roses = f':rose:{str(profile.roses)}' if profile.roses else ''
        alcohol = f':champagne:{str(profile.alcohol)}' if profile.alcohol else ''
        inventory = picks + rings + diamonds + roses + alcohol
        inventory = inventory or 'Nothing in inventory'
        e.add_field(name=':handbag: Inventory', value=inventory)
        
        e.add_field(name='Pet', value=profile.pet)

        if not profile.married == 'Nobody...':
            married = ctx.guild.get_member(profile.married) or await self.bot.get_user_info(profile.married)
            e.add_field(name=':heart: Married with', value=married.display_name)
        else:
            e.add_field(name=':heart: Married with', value=profile.married)        
        banner = profile.banner
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
        e.add_field(name="Links", value=f"[Website](https://w-bot.ml/profile/?uid={member.id})")
        
        await ctx.send(embed=e)

    async def edit_field(self, ctx, **fields):
        keys = ', '.join(fields)
        values = ', '.join(f'${2 + i}' for i in range(len(fields)))

        query = f"""update profiles
                    SET {keys} = {values}
                    where id=$1;
                 """

        await self.bot.pool.execute(query, ctx.author.id, *fields.values())
        av = ctx.author.avatar_url_as(format='png', size=1024)
        await self.bot.pool.execute(f'update profiles set name=\'{ctx.author.name}#{ctx.author.discriminator}\', pfp=\'{av}\' where id={ctx.author.id}')

    async def edit_user_field(self, member, ctx, **fields):
        keys = ', '.join(fields)
        values = ', '.join(f'${2 + i}' for i in range(len(fields)))

        query = f"""update profiles
                    SET {keys} = {values}
                    where id=$1;
                 """

        await self.bot.pool.fetchrow(query, member.id, *fields.values())
        av = member.avatar_url_as(format='png', size=1024)
        await self.bot.pool.execute(f'update profiles set name=\'{member.name}#{member.discriminator}\', pfp=\'{av}\' where id={member.id}')

    @commands.command(hidden=True)
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
        """Changes your profile's banner.
        User banners command to view the available banners."""
        if banner is None:
            return await ctx.invoke(self.banners)
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
        profile = await self.get_profile(ctx, ctx.author.id)
        await profile.edit_field(ctx, description=DESC.strip('"'))
        await ctx.send(f'{ctx.tick(True)} Description edited.')

    @profile.command(aliases=['יום הולדת', 'bday'])
    async def birthday(self, ctx, BDAY : str):
        """Sets a birthday to your profile."""
        bday = re.search(r'(\d+-\d+-\d+)', BDAY)
        if not bday:
            return await ctx.send('Invalid birthday inserted. The format is `DD-MM-YYYY`')
        else:
            bday = bday.group(1)
        profile = await self.get_profile(ctx, ctx.author.id)
        await profile.edit_field(ctx, bday=bday)
        await ctx.send('Birthday edited.')

    @profile.command(aliases=['level'])
    async def announce(self, ctx):
        """Toggles level messages."""
        profile = await self.get_profile(ctx, ctx.author.id)
        announce_level = not profile.announce_level
        await profile.edit_field(ctx, announce_level=announce_level)
        state = 'enabled' if announce_level else 'disabled'
        await ctx.send(f'Level messages are now {state} for you.')

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
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.picks == 0:
            mine_cmd = self.bot.get_command('mine')
            mine_cmd.reset_cooldown(ctx)
            if profile.cash >= 100:
                await ctx.send(f'{ctx.tick(False)} You don\'t have any pickaxes.\nType yes in 20 seconds if you want to buy a pickaxe.')
                def pred(m):
                    return m.author == ctx.message.author and m.channel == ctx.message.channel

                answer = await self.bot.wait_for('message', check=pred)
                if answer.content.lower() in 'yes':
                    await ctx.invoke(self.pick)
                else:
                    await ctx.send('I\'ll take that as no.')
                    return
            else:
                await ctx.send(f'{ctx.tick(False)} You don\'t have any pickaxes.')
        else:
            await profile.edit_field(ctx, picks=profile.picks - 1)
            mining_chance = random.randint(1, 3)
            diamond_chance = random.randint(1, 10)
            if mining_chance == 1:
                await ctx.send(
                    'You broke your pickaxe.\n'\
                    '**You can mine again in 5 minutes!**')
                if diamond_chance == 1:
                    await ctx.send('But you found a diamond lying on the ground.')
                    diamonds += 1
                    await self.edit_field(ctx, diamonds=diamonds)
            else:
                found = random.randint(40, 200)
                await self.edit_field(ctx, cash=profile.cash + found)
                await ctx.send(
                    f'{ctx.author.display_name} found ${found} and has now ${cash}\n'\
                    f'**You can mine again in 5 minutes!**')
                if diamond_chance == 1:
                    await ctx.send('You lucky, you found a diamond.')
                    diamonds += 1
                    await profile.edit_field(ctx, diamonds=diamonds)

    @commands.command()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        """Gets your daily money."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        found = random.randint(100,150)
        await profile.edit_field(ctx, cash=profile.cash + found)
        await ctx.send(
            f'You got ${found} from daily and you have ${profile.cash} in total.\n'\
            f'**Come get your daily again after 24h.**')

    @commands.command(aliases=['balance', 'כסף', 'בנק'])
    async def money(self, ctx):
        """Shows your money amount."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        await ctx.send(f'You have ${profile.cash}')

    @commands.command()
    @commands.cooldown(1, 180, commands.BucketType.user)
    async def loot(self, ctx):
        """Loots money from messages."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        found = random.randint(20,50)
        await profile.edit_field(ctx, cash=profile.cash + found)
        await ctx.send(
            f'{ctx.author.display_name} found ${found}, and has now ${profile.cash}\n'\
            '**You can loot again in 3 minutes!**')

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
        f"""Use ``{ctx.prefix}help sell`` for more information."""
        await ctx.show_help('sell')

    @sell.command(name='dog')
    async def _dog(self, ctx):
        """Sells a dog."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.pet == 'No pet':
            return await ctx.send(f'{ctx.tick(False)} You don\'t have a pet.')
        if profile.pet != ':dog: Dog':
            await ctx.send(f'{ctx.tick(False)} You do not have this pet.' \
                           f'Your pet is {profile.pet}.')
        else:
            await profile.edit_field(ctx, cash=profile.cash + 7500)            
            await profile.edit_field(ctx, pet=None)            
            await ctx.send(f'{ctx.tick(True)} Sold :dog:')

    @sell.command(name='cat')
    async def _cat(self, ctx):
        """Sells a dog."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.pet == 'No pet':
            return await ctx.send(f'{ctx.tick(False)} You don\'t have a pet.')
        if profile.pet != ':cat2: Cat':
            await ctx.send(f'{ctx.tick(False)} You do not have this pet.' \
                           f'Your pet is {profile.pet}.')
        else:
            await profile.edit_field(ctx, cash=profile.cash + 15000)
            await profile.edit_field(ctx, pet=None)
            await ctx.send(f'{ctx.tick(True)} Sold :cat2:')

    @sell.command(name='mouse')
    async def _mouse(self, ctx):
        """Sells a mouse."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.pet == 'No pet':
            return await ctx.send(f'{ctx.tick(False)} You don\'t have a pet.')
        if profile.pet != ':mouse: Mouse':
            await ctx.send(f'{ctx.tick(False)} You do not have this pet.' \
                           f'Your pet is {profile.pet}.')
        else:
            await profile.edit_field(ctx, cash=profile.cash + 4500)            
            await profile.edit_field(ctx, pet=None)            
            await ctx.send(f'{ctx.tick(True)} Sold :mouse:')

    @sell.command(name='hamster')
    async def _hamster(self, ctx):
        """Sells a mouse."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.pet == 'No pet':
            return await ctx.send(f'{ctx.tick(False)} You don\'t have a pet.')
        if profile.pet != ':hamster: Hamster':
            await ctx.send(f'{ctx.tick(False)} You do not have this pet.' \
                           f'Your pet is {profile.pet}.')
        else:
            await profile.edit_field(ctx, cash=profile.cash + 4500)            
            await profile.edit_field(ctx, pet=None)            
            await ctx.send(f'{ctx.tick(True)} Sold :hamster:')

    @sell.command(name='rabbit')
    async def _rabbit(self, ctx):
        """Sells a mouse."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.pet == 'No pet':
            return await ctx.send(f'{ctx.tick(False)} You don\'t have a pet.')
        if profile.pet != ':rabbit: Rabbit':
            await ctx.send(f'{ctx.tick(False)} You do not have this pet.' \
                           f'Your pet is {profile.pet}.')
        else:
            await profile.edit_field(ctx, cash=profile.cash + 7500)            
            await profile.edit_field(ctx, pet=None)            
            await ctx.send(f'{ctx.tick(True)} Sold :rabbit:')

    @sell.command(name='dragon')
    async def _dragon(self, ctx):
        """Sells a dragon."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.pet == 'No pet':
            return await ctx.send(f'{ctx.tick(False)} You don\'t have a pet.')
        if profile.pet != ':dragon: Dragon':
            await ctx.send(f'{ctx.tick(False)} You do not have this pet.' \
                           f'Your pet is {profile.pet}.')
        else:
            await profile.edit_field(ctx, cash=profile.cash + 75000000000000)            
            await profile.edit_field(ctx, pet=None)            
            await ctx.send(f'{ctx.tick(True)} Sold :dragon:')

    @sell.command(name='bear')
    async def _bear(self, ctx):
        """Sells a mouse."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.pet == 'No pet':
            return await ctx.send(f'{ctx.tick(False)} You don\'t have a pet.')
        if profile.pet != ':bear: Bear':
            await ctx.send(f'{ctx.tick(False)} You do not have this pet.' \
                           f'Your pet is {profile.pet}.')
        else:
            await profile.edit_field(ctx, cash=profile.cash + 75000)            
            await profile.edit_field(ctx, pet=None)            
            await ctx.send(f'{ctx.tick(True)} Sold :bear:')

    @sell.command(name='pig')
    async def _pig(self, ctx):
        """Sells a mouse."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.pet == 'No pet':
            return await ctx.send(f'{ctx.tick(False)} You don\'t have a pet.')
        if profile.pet != ':pig2: Pig':
            await ctx.send(f'{ctx.tick(False)} You do not have this pet.' \
                           f'Your pet is {profile.pet}.')
        else:
            await profile.edit_field(ctx, cash=profile.cash + 37500)            
            await profile.edit_field(ctx, pet=None)            
            await ctx.send(f'{ctx.tick(True)} Sold :pig2:')

    @sell.command(name='pick')
    async def pic(self, ctx, amount : int = None):
        """Sells a pickaxe."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if amount is None or amount < 0:
            amount = 1
        if profile.picks == 0:
            await ctx.send(f'{ctx.tick(False)} You don\'t have any pickaxes.')
        else:
            if amount > profile.picks:
                return await ctx.send(f'{ctx.tick(False)} You don\'t have that many pickaxes.')
            await profile.edit_field(ctx, cash=profile.cash + amount * 75)
            await profile.edit_field(ctx, picks=profile.picks - amount)
            await ctx.send(f'{ctx.tick(True)} Sold {amount}x :pick:')

    @sell.command(name='ring')
    async def sell_ring(self, ctx, amount:int=None):
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if amount is None or amount < 0:
            amount = 1
        if profile.rings == 0:
            await ctx.send(f'{ctx.tick(False)} You don\'t have any rings.')
        else:
            if amount > profile.rings:
                return await ctx.send(f'{ctx.tick(False)} You don\'t have that many rings.')
            await profile.edit_field(ctx, cash=profile.cash + amount * 150)
            await profile.edit_field(ctx, rings=profile.rings - amount)
            await ctx.send(f'{ctx.tick(True)} Sold {amount}x :ring:')

    @sell.command(name='diamond')
    async def diamon(self, ctx, amount : int = None):
        """Sells a diamond."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if amount is None or amount < 0:
            amount = 1
        if profile.diamonds == 0:
            await ctx.send(f'{ctx.tick(False)} You don\'t have any diamonds.')
        else:
            if amount > profile.diamonds:
                return await ctx.send(f'{ctx.tick(False)} You don\'t have that many diamonds.')
            await profile.edit_field(ctx, cash=profile.cash + amount * 1500)
            await profile.edit_field(ctx, diamonds=profile.diamonds - amount)
            await ctx.send(f'{ctx.tick(True)} Sold {amount}x :diamond_shape_with_a_dot_inside:')

    @sell.command(name='rose')
    async def ros(self, ctx, amount : int = None):
        """Sells a rose."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if amount is None or amount < 0:
            amount = 1
        if profile.roses == 0:
            await ctx.send(f'{ctx.tick(False)} You don\'t have any roses.')
        else:
            if amount > profile.roses:
                return await ctx.send(f'{ctx.tick(False)} You don\'t have that many roses.')
            await profile.edit_field(ctx, cash=profile.cash + amount * 19)
            await profile.edit_field(ctx, roses=profile.roses - amount)
            await ctx.send(f'{ctx.tick(True)} Sold {amount}x :rose:')

    @sell.command(name='alcohol', aliases=['vodka'])
    async def alcoho(self, ctx, amount : int = None):
        """Sells alcohol."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if amount is None or amount < 0:
            amount = 1
        if profile.alcohol == 0:
            await ctx.send(f'{ctx.tick(False)} You don\'t have any alcohol.')
        else:
            if amount > profile.alcohol:
                return await ctx.send(f'{ctx.tick(False)} You don\'t have that much alcohol.')
            await profile.edit_field(ctx, cash=profile.cash + amount * 38)
            await profile.edit_field(ctx, alcohol=profile.alcohol - amount)
            await ctx.send(f'{ctx.tick(True)} Sold {amount}x :champagne:')

    @commands.command()
    async def drink(self, ctx):
        """Drinks alcohol."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.alcohol == 0:
            await ctx.send(f'{ctx.tick(False)} You don\'t have any alcohol.')
        else:
            await profile.edit_field(ctx, alcohol=profile.alcohol - 1)
            await ctx.send('You drank :champagne: and got drunk.')

    @commands.group(invoke_without_command=True)
    async def buy(self, ctx):
        """Use ``(prefix)help buy`` for more information."""
        if ctx.invoked_subcommand is None:
            await ctx.show_help('buy')

    @buy.command()
    async def dog(self, ctx):
        """Buys a dog."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.pet:
            return await ctx.send(f'{ctx.tick(False)} You have a {profile.pet} already.')
        if profile.cash < 10000:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        await profile.edit_field(ctx, cash=profile.cash - 10000)
        await profile.edit_field(ctx, pet=':dog: Dog')
        await ctx.send(f'{ctx.tick(True)} Bought :dog:')

    @buy.command()
    async def cat(self, ctx):
        """Buys a cat."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.pet:
            return await ctx.send(f'{ctx.tick(False)} You have a {pet} already.')
        if profile.cash < 20000:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        await profile.edit_field(ctx, cash=profile.cash - 20000)
        await profile.edit_field(ctx, pet=':cat2: Cat')
        await ctx.send(f'{ctx.tick(True)} Bought :cat2:')

    @buy.command()
    async def mouse(self, ctx):
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.pet:
            return await ctx.send(f'{ctx.tick(False)} You have a {pet} already.')
        if profile.cash < 5000:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        await profile.edit_field(ctx, cash=profile.cash - 5000)
        await profile.edit_field(ctx, pet=':mouse: Mouse')
        await ctx.send(f'{ctx.tick(True)} Bought :mouse:')

    @buy.command()
    async def hamster(self, ctx):
        """Buys a hamster."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.pet:
            return await ctx.send(f'{ctx.tick(False)} You have a {pet} already.')
        if profile.cash < 15000:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        await profile.edit_field(ctx, cash=profile.cash - 15000)
        await profile.edit_field(ctx, pet=':hamster: Hamster')
        await ctx.send(f'{ctx.tick(True)} Bought :hamster:')

    @buy.command()
    async def rabbit(self, ctx):
        """Buys a rabbit."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.pet:
            return await ctx.send(f'{ctx.tick(False)} You have a {pet} already.')
        if profile.cash < 10000:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        await profile.edit_field(ctx, cash=profile.cash - 10000)
        await profile.edit_field(ctx, pet=':rabbit: Rabbit')
        await ctx.send(f'{ctx.tick(True)} Bought :rabbit:')

    @buy.command()
    async def bear(self, ctx):
        """Buys a bear."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.pet:
            return await ctx.send(f'{ctx.tick(False)} You have a {pet} already.')
        if profile.cash < 100000:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        await profile.edit_field(ctx, cash=profile.cash - 100000)
        await profile.edit_field(ctx, pet=':bear: Bear')
        await ctx.send(f'{ctx.tick(True)} Bought :bear:')

    @buy.command()
    async def dragon(self, ctx):
        """Buys a dragon."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.pet:
            return await ctx.send(f'{ctx.tick(False)} You have a {pet} already.')
        if profile.cash < 100000000000000:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        await profile.edit_field(ctx, cash=profile.cash - 100000000000000)
        await profile.edit_field(ctx, pet=':dragon: Dragon')
        await ctx.send(f'{ctx.tick(True)} Bought :dragon:')

    @buy.command()
    async def pig(self, ctx):
        """Buys a pig."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.pet:
            return await ctx.send(f'{ctx.tick(False)} You have a {pet} already.')
        if profile.cash < 50000:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        await profile.edit_field(ctx, cash=profile.cash - 50000)
        await profile.edit_field(ctx, pet=':pig2: Pig')
        await ctx.send(f'{ctx.tick(True)} Bought :pig2:')

    @buy.command()
    async def pick(self, ctx, amount : int = None):
        """Buys a pickaxe."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if amount is None or amount < 0:
            amount = 1
        if profile.cash < amount * 100:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        await ctx.send(f'{ctx.tick(True)} Bought {amount}x :pick:')
        await profile.edit_field(ctx, cash=profile.cash + amount * 100)
        await profile.edit_field(ctx, picks=profile.picks + amount)

    @buy.command()
    async def ring(self, ctx, amount : int = None):
        """Buys a ring."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if amount is None or amount < 0:
            amount = 1
        if profile.cash < amount*200:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        await ctx.send(f'{ctx.tick(True)} Bought {amount}x :ring:')
        await profile.edit_field(ctx, cash=profile.cash - amount * 200)
        await profile.edit_field(ctx, rings=profile.rings + amount)

    @buy.command()
    async def diamond(self, ctx, amount : int = None):
        """Buys a diamond."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if amount is None or amount < 0:
            amount = 1
        if profile.cash < amount * 2000:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        await profile.edit_field(ctx, cash=profile.cash - amount * 2000)
        await profile.edit_field(ctx, diamonds=profile.diamonds + amount)
        await ctx.send(f'{ctx.tick(True)} Bought {amount}x :diamond_shape_with_a_dot_inside:')

    @buy.command()
    async def rose(self, ctx, amount : int = None):
        """Buys a rose."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if amount is None or amount < 0:
            amount = 1
        if profile.cash < amount * 25:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        await profile.edit_field(ctx, cash=profile.cash - amount * 25)
        await profile.edit_field(ctx, roses=profile.roses + amount)
        await ctx.send(f'{ctx.tick(True)} Bought {amount}x :rose:')

    @buy.command(aliases=['vodka'])
    async def alcohol(self, ctx, amount : int = None):
        """Buys alcohol."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if amount is None or amount < 0:
            amount = 1
        if profile.cash < amount*50:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        await profile.edit_field(ctx, cash=profile.cash - amount * 50)
        await profile.edit_field(ctx, alcohol=profile.alcohol + amount)
        await ctx.send(f'{ctx.tick(True)} Bought {amount}x :champagne:')

    @buy.command()
    async def bronze(self, ctx):
        """Buys a W.Bot market Bronze role. You can not sell this after buying."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.cash < 10000:
            return await ctx.send(f'{ctx.tick(False)} You do not have enough money to buy this role.')
        for role in ctx.author.roles:
            if role.name == 'W.Bot Bronze':
                return await ctx.send(f'{ctx.tick(False)} Why\'d you buy this role again?')
        data = await self.bot.pool.fetchrow(f'select buy_roles from settings where id={ctx.guild.id}')
        if not data: return await ctx.send(f'{ctx.tick(False)} This guild hasn\'t enabled role buying.')
        try:
            role = discord.utils.get(ctx.guild.roles, name='W.Bot Bronze')
            if not role:
                try:
                    role = await ctx.guild.create_role(
                        name='W.Bot Bronze',
                        color=discord.Color.from_rgb(145, 44, 7),
                        reason='W.Bot Market Buyable role.',
                        mentionable=False)
                    await ctx.author.add_roles(role, reason='W.Bot Market Buyable role.')
                    return await ctx.send(f'{ctx.tick(True)} Bought W.Bot Bronze role.')
                except discord.Forbidden:
                    return await ctx.send(
                        f'{ctx.tick(False)} It seems that buyable roles are enabled.\n'\
                        'But I could not create it or I couldn\'t add it to you.')
                except Exception as e:
                    print(e)
            role = discord.utils.get(ctx.guild.roles, name='W.Bot Bronze')
            await ctx.author.add_roles(role, reason='W.Bot Market Buyable role.')
            await ctx.send(f'{ctx.tick(True)} Bought W.Bot Bronze role.')
        except discord.Forbidden:
            return await ctx.send(f'{ctx.tick(False)} I couldn\'t add the role to you.')
        except Exception as e:
            print(e)
        await profile.edit_field(ctx, cash=profile.cash - 10000)

    @buy.command()
    async def silver(self, ctx):
        """Buys a W.Bot market Silver role. You can not sell this after buying."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.cash < 10000:
            return await ctx.send(f'{ctx.tick(False)} You do not have enough money to buy this role.')
        for role in ctx.author.roles:
            if role.name == 'W.Bot Silver':
                return await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        data = await self.bot.pool.fetchrow(f'select buy_roles from settings where id={ctx.guild.id}')
        if not data: return await ctx.send(f'{ctx.tick(False)} This guild hasn\'t enabled role buying.')
        try:
            role = discord.utils.get(ctx.guild.roles, name='W.Bot Silver')
            if not role:
                try:
                    role = await ctx.guild.create_role(
                        name='W.Bot Silver',
                        color=discord.Color.from_rgb(144, 159, 165),
                        reason='W.Bot Market Buyable role.',
                        mentionable=False)
                    await ctx.author.add_roles(role, reason='W.Bot Market Buyable role.')
                    return await ctx.send(f'{ctx.tick(True)} Bought W.Bot Silver role.')
                except discord.Forbidden:
                    return await ctx.send(
                        f'{ctx.tick(False)} It seems that buyable roles are enabled.\n'\
                        'But I could not create it or I couldn\'t add it to you.')
                except Exception as e:
                    print(e)
            role = discord.utils.get(ctx.guild.roles, name='W.Bot Silver')
            await ctx.author.add_roles(role, reason='W.Bot Market Buyable role.')
            await ctx.send(f'{ctx.tick(True)} Bought W.Bot Silver role.')
        except discord.Forbidden:
            return await ctx.send(f'{ctx.tick(False)} I couldn\'t add the role to you.')
        except Exception as e:
            print(e)
        await self.edit_field(ctx, cash=profile.cash - 10000)

    @buy.command()
    async def gold(self, ctx):
        """Buys a W.Bot market Gold role. You can not sell this after buying."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.cash < 10000:
            return await ctx.send(f'{ctx.tick(False)} You do not have enough money to buy this role.')
        for role in ctx.author.roles:
            if role.name == 'W.Bot Gold':
                return await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        data = await self.bot.pool.fetchrow(f'select buy_roles from settings where id={ctx.guild.id}')
        if not data: return await ctx.send(f'{ctx.tick(False)} This guild hasn\'t enabled role buying.')
        try:
            role = discord.utils.get(ctx.guild.roles, name='W.Bot Gold')
            if not role:
                try:
                    role = await ctx.guild.create_role(
                        name='W.Bot Gold',
                        color=discord.Color.from_rgb(209, 150, 33),
                        reason='W.Bot Market Buyable role.',
                        mentionable=False)
                    await ctx.author.add_roles(role, reason='W.Bot Market Buyable role.')
                    return await ctx.send(f'{ctx.tick(True)} Bought W.Bot Gold role.')
                except discord.Forbidden:
                    return await ctx.send(
                        f'{ctx.tick(False)} It seems that buyable roles are enabled.\n'\
                        'But I could not create it or I couldn\'t add it to you.')
                except Exception as e:
                    print(e)
            role = discord.utils.get(ctx.guild.roles, name='W.Bot Gold')
            await ctx.author.add_roles(role, reason='W.Bot Market Buyable role.')
            await ctx.send(f'{ctx.tick(True)} Bought W.Bot Gold role.')
        except discord.Forbidden:
            return await ctx.send(f'{ctx.tick(False)} I couldn\'t add the role to you.')
        except Exception as e:
            print(e)
        await self.edit_field(ctx, cash=profile.cash - 10000)


    @buy.command()
    async def blue(self, ctx):
        """Buys a W.Bot market Blue role. You can not sell this after buying."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.cash < 10000:
            return await ctx.send(f'{ctx.tick(False)} You do not have enough money to buy this role.')
        for role in ctx.author.roles:
            if role.name == 'W.Bot Blue':
                return await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        data = await self.bot.pool.fetchrow(f'select buy_roles from settings where id={ctx.guild.id}')
        if not data: return await ctx.send(f'{ctx.tick(False)} This guild hasn\'t enabled role buying.')
        try:
            role = discord.utils.get(ctx.guild.roles, name='W.Bot Blue')
            if not role:
                try:
                    role = await ctx.guild.create_role(
                        name='W.Bot Blue',
                        color=discord.Color.from_rgb(66, 134, 244),
                        reason='W.Bot Market Buyable role.',
                        mentionable=False)
                    await ctx.author.add_roles(role, reason='W.Bot Market Buyable role.')
                    return await ctx.send(f'{ctx.tick(True)} Bought W.Bot Blue role.')
                except discord.Forbidden:
                    return await ctx.send(
                        f'{ctx.tick(False)} It seems that buyable roles are enabled.\n'\
                        'But I could not create it or I couldn\'t add it to you.')
                except Exception as e:
                    print(e)
            role = discord.utils.get(ctx.guild.roles, name='W.Bot Blue')
            await ctx.author.add_roles(role, reason='W.Bot Market Buyable role.')
            await ctx.send(f'{ctx.tick(True)} Bought W.Bot Blue role.')
        except discord.Forbidden:
            return await ctx.send(f'{ctx.tick(False)} I couldn\'t add the role to you.')
        except Exception as e:
            print(e)
        await self.edit_field(ctx, cash=profile.cash - 10000)

    @buy.command()
    async def red(self, ctx):
        """Buys a W.Bot market Red role. You can not sell this after buying."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.cash < 10000:
            return await ctx.send(f'{ctx.tick(False)} You do not have enough money to buy this role.')
        for role in ctx.author.roles:
            if role.name == 'W.Bot Red':
                return await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        data = await self.bot.pool.fetchrow(f'select buy_roles from settings where id={ctx.guild.id}')
        if not data: return await ctx.send(f'{ctx.tick(False)} This guild hasn\'t enabled role buying.')
        try:
            role = discord.utils.get(ctx.guild.roles, name='W.Bot Red')
            if not role:
                try:
                    role = await ctx.guild.create_role(
                        name='W.Bot Red',
                        color=discord.Color.from_rgb(183, 14, 14),
                        reason='W.Bot Market Buyable role.',
                        mentionable=False)
                    await ctx.author.add_roles(role, reason='W.Bot Market Buyable role.')
                    return await ctx.send(f'{ctx.tick(True)} Bought W.Bot Red role.')
                except discord.Forbidden:
                    return await ctx.send(
                        f'{ctx.tick(False)} It seems that buyable roles are enabled.\n'\
                        'But I could not create it or I couldn\'t add it to you.')
                except Exception as e:
                    print(e)
            role = discord.utils.get(ctx.guild.roles, name='W.Bot Red')
            await ctx.author.add_roles(role, reason='W.Bot Market Buyable role.')
            await ctx.send(f'{ctx.tick(True)} Bought W.Bot Red role.')
        except discord.Forbidden:
            return await ctx.send(f'{ctx.tick(False)} I couldn\'t add the role to you.')
        except Exception as e:
            print(e)
        await self.edit_field(ctx, cash=profile.cash - 10000)

    @buy.command()
    async def black(self, ctx):
        """Buys a W.Bot market Black role. You can not sell this after buying."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.cash < 10000:
            return await ctx.send(f'{ctx.tick(False)} You do not have enough money to buy this role.')
        for role in ctx.author.roles:
            if role.name == 'W.Bot Black':
                return await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        data = await self.bot.pool.fetchrow(f'select buy_roles from settings where id={ctx.guild.id}')
        if not data: return await ctx.send(f'{ctx.tick(False)} This guild hasn\'t enabled role buying.')
        if not data[0]: return await ctx.send(f'{ctx.tick(False)} This guild hasn\'t enabled role buying.')
        try:
            role = discord.utils.get(ctx.guild.roles, name='W.Bot Black')
            if not role:
                try:
                    role = await ctx.guild.create_role(
                        name='W.Bot Black',
                        color=discord.Color.from_rgb(22, 22, 22), 
                        reason='W.Bot Market Buyable role.',
                        mentionable=False)
                    await ctx.author.add_roles(role, reason='W.Bot Market Buyable role.')
                    return await ctx.send(f'{ctx.tick(True)} Bought W.Bot Black role.')
                except discord.Forbidden:
                    return await ctx.send(
                        f'{ctx.tick(False)} It seems that buyable roles are enabled.\n'\
                        'But I could not create it or I couldn\'t add it to you.')
                except Exception as e:
                    print(e)
            role = discord.utils.get(ctx.guild.roles, name='W.Bot Black')
            await ctx.author.add_roles(role, reason='W.Bot Market Buyable role.')
            await ctx.send(f'{ctx.tick(True)} Bought W.Bot Black role.')
        except discord.Forbidden:
            return await ctx.send(f'{ctx.tick(False)} I couldn\'t add the role to you.')
        except Exception as e:
            print(e)
        await self.edit_field(ctx, cash=profile.cash - 10000)

    @buy.command()
    async def green(self, ctx):
        """Buys a W.Bot market Green role. You can not sell this after buying."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.cash < 10000:
            return await ctx.send(f'{ctx.tick(False)} You do not have enough money to buy this role.')
        for role in ctx.author.roles:
            if role.name == 'W.Bot Green':
                return await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        data = await self.bot.pool.fetchrow(f'select buy_roles from settings where id={ctx.guild.id}')
        if not data: return await ctx.send(f'{ctx.tick(False)} This guild hasn\'t enabled role buying.')
        try:
            role = discord.utils.get(ctx.guild.roles, name='W.Bot Green')
            if not role:
                try:
                    role = await ctx.guild.create_role(
                        name='W.Bot Green',
                        color=discord.Color.from_rgb(101, 206, 41),
                        reason='W.Bot Market Buyable role.',
                        mentionable=False)
                    await ctx.author.add_roles(role, reason='W.Bot Market Buyable role.')
                    return await ctx.send(f'{ctx.tick(True)} Bought W.Bot Green role.')
                except discord.Forbidden:
                    return await ctx.send(
                        f'{ctx.tick(False)} It seems that buyable roles are enabled.\n'\
                        'But I could not create it or I couldn\'t add it to you.')
                except Exception as e:
                    print(e)
            role = discord.utils.get(ctx.guild.roles, name='W.Bot Green')
            await ctx.author.add_roles(role, reason='W.Bot Market Buyable role.')
            await ctx.send(f'{ctx.tick(True)} Bought W.Bot Green role.')
        except discord.Forbidden:
            return await ctx.send(f'{ctx.tick(False)} I couldn\'t add the role to you.')
        except Exception as e:
            print(e)
        await self.edit_field(ctx, cash=profile.cash - 10000)

    @commands.command()
    async def marry(self, ctx, *, member : discord.Member = None):
        """Marrys a member."""
        if member is None:
            return await ctx.send(f'{ctx.tick(False)} You did not enter a user to propose.')
        if ctx.author.id == member.id:
            return await ctx.send(f'{ctx.tick(False)} You can\'t marry yourself.')
        if member.bot:
            return await ctx.send(f'{ctx.tick(False)} You can\'t marry a bot.')

        profile = await self.get_profile(ctx, ctx.author.id)

        if not profile:
            return await ctx.invoke(self.make)
        if profile.married == 'Nobody...':
            return await ctx.send(f'{ctx.tick(False)} You\'re already married with {profile.married}.')
        m_profile = await self.get_profile(ctx, ctx.author.id)
        if m_profile is None:
            await ctx.send(f'{ctx.tick(False)} That user does not have a profile.')
        if m_profile.married == 'Nobody...':
            member_married_name = ctx.guild.get_member(m_profile.married) or await self.bot.get_user_info(member_married)
            return await ctx.send(f'That user is already married with {member_married_name}.')
        if not rings >= 2:
            return await ctx.send(f'{ctx.tick(False)} You need 2 rings to propose.')
        await ctx.send(f'{ctx.author.display_name} proposed {member.display_name}.\n'\
                       f'{member.display_name} type yes or no in 60 seconds.')
        def pred(m):
            return m.author == member and m.channel == ctx.message.channel
        try:
            answer = await self.bot.wait_for('message', timeout=60, check=pred)
        except asyncio.TimeoutError:
            return await ctx.send('No answer.')
        if answer.content.lower() in 'yes':
            await profile.edit_field(ctx, rings=profile.rings - 2)
            await profile.edit_field(ctx, married=member.id)
            await m_profile.edit_field(ctx, married=ctx.message.author.id)
            await ctx.send(f':heart: {ctx.author.display_name} is now married with {member.display_name}')
        else:
            await ctx.send('I\'ll take that as a no.')

    @commands.command()
    async def divorce(self, ctx):
        """Divorces with a member."""
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if married == 'Nobody...':
            return await ctx.send(f'{ctx.tick(False)} You weren\'t married in the first place.')
        married = ctx.guild.get_member(profile.married)
        if not married:
            return await ctx.send(f'{ctx.tick(False)} The member you are married with is not in this server.')
        m_profile = await self.get_profile(ctx, profile.married)

        await ctx.send(f'{ctx.message.author.display_name} would like to get divorced with {member.display_name}.\n'\
                       f'{member.display_name} type yes in 60 seconds if you want to get divorced.')
        def pred(m):
            return m.author == member and m.channel == ctx.message.channel

        try:
            answer = await self.bot.wait_for('message', timeout=60, check=pred)
        except asyncio.TimeoutError:
            return await ctx.send('No answer.')
        if answer.content in 'yes':
            await profile.edit_field(ctx, married=None)
            await m_profile.edit_field(member, ctx, married=None)
            await ctx.send(f':broken_heart: {ctx.author.display_name} got divorced with {member.display_name}.')
        else:
            await ctx.send('I\'ll take that as no.')

    @commands.group(aliases=['giveitem'])
    async def itemtransfer(self, ctx):
        """Use ``(prefix)help itemtransfer`` for more information."""
        if ctx.invoked_subcommand is None:
            await ctx.show_help('giveitem')

    @itemtransfer.command(name='pick')
    async def give_pick(self, ctx, member:discord.Member=None, amount:int=None):
        """Gives your pickaxe to another member."""
        if member is None:
            msg = await ctx.send(f'{ctx.tick(False)} You didn\'t tell who to give the item.')
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if not amount or amount < 0:
            amount = 1
        if profile.picks < amount:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have enough pickaxes.')
        m_profile = await self.get_profile(ctx, member.id)
        if m_profile is None:
            return await ctx.send(f'{ctx.tick(False)} That user does not have a profile.')
        await profile.edit_field(ctx, picks=profile.picks - amount)
        await m_profile.edit_field(ctx, picks=m_profile.picks + amount)
        await ctx.send(f'{ctx.tick(True)} Gave {amount}x :pick: to {member.display_name}.')

    @itemtransfer.command(name='ring')
    async def give_ring(self, ctx, member : discord.Member = None, amount:int=None):
        """Gives your ring to another member."""
        if member is None:
            return await ctx.send(f'{ctx.tick(False)} You didn\'t tell who to give the item.')
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if not amount or amount < 0:
            amount = 1
        if profile.rings < amount:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have enough rings.')
        m_profile = await self.get_profile(ctx, member.id)
        if m_profile is None:
            return await ctx.send(f'{ctx.tick(False)} That user does not have a profile.')
        await profile.edit_field(ctx, rings=profile.rings - amount)
        await m_profile.edit_field(ctx, rings=m_profile.rings + amount)
        await ctx.send(f'{ctx.tick(True)} Gave {amount}x :ring: to {member.display_name}.')

    @itemtransfer.command(name='diamond')
    async def give_diamond(self, ctx, member : discord.Member = None, amount:int=None):
        """Gives your diamond to another member."""
        if member is None:
            return await ctx.send(f'{ctx.tick(False)} You didn\'t tell who to give the item.')
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if not amount or amount < 0:
            amount = 1
        if profile.diamonds < amount:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have enough diamonds.')
        m_profile = await self.get_profile(ctx, member.id)
        if m_profile is None:
            return await ctx.send(f'{ctx.tick(False)} That user does not have a profile.')
        await profile.edit_field(ctx, diamonds=profile.diamonds - amount)
        await m_profile.edit_field(ctx, diamonds=m_profile.diamonds + amount)
        await ctx.send(f'{ctx.tick(True)} Gave {amount}x :diamond_shape_with_a_dot_inside: to {member.display_name}.')

    @itemtransfer.command(name='rose')
    async def give_rose(self, ctx, member : discord.Member = None, amount:int=None):
        """Gives your rose to another member."""
        if member is None:
            return await ctx.send(f'{ctx.tick(False)} You didn\'t tell who to give the item.')
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if not amount or amount < 0:
            amount = 1
        if roses < amount:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have enough roses.')
        m_profile = await self.get_profile(ctx, member.id)
        if m_profile is None:
            return await ctx.send(f'{ctx.tick(False)} That user does not have a profile.')
        await profile.edit_field(ctx, roses=profile.roses - amount)
        await m_profile.edit_field(ctx, roses=m_profile.roses + amount)
        await ctx.send(f'{ctx.tick(True)} Gave {amount}x :rose: to {member.display_name}.')

    @itemtransfer.command(name='alcohol', aliases=['vodka'])
    async def give_alcohol(self, ctx, member : discord.Member = None, amount:int=None):
        """Gives your alcohol to another member."""
        if member is None:
            return await ctx.send(f'{ctx.tick(False)} You didn\'t tell who to give the item.')
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if not amount or amount < 0:
            amount = 1
        if alcohol == 0:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have enough alcohol.')
        m_profile = await self.get_profile(ctx, member.id)
        if m_profile is None:
            return await ctx.send(f'{ctx.tick(False)} That user does not have a profile.')
        await profile.edit_field(ctx, alcohol=profile.alcohol - amount)
        await m_profile.edit_field(ctx, alcohol=m_profile.alcohol + amount)
        await ctx.send(f'{ctx.tick(True)} Gave :champagne: to {member.display_name}.')

    @commands.command(aliases=['moneytransfer'])
    async def givemoney(self, ctx, member:discord.Member=None, amount:int=None):
        """Gives the amount you specify from your money to the member you specify."""      
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)        
        if ctx.author.id == member.id:
            return await ctx.send('Na ah..')
        if not amount or amount < 0:
            amount = 1      
        if not member:
            return await ctx.send(f'{ctx.tick(False)} You didn\'t tell me who to give the money to.')
        if not profile:
            return await ctx.invoke(self.make)
        if profile.cash <= amount:
            return await ctx.send(f'{ctx.tick(False)} You don\'t have enough money to give.')
        m_profile = await self.get_profile(ctx, member.id)
        if m_profile is None:
            return await ctx.send(f'{ctx.tick(False)} That user does not have a profile.')
        await profile.edit_field(ctx, cash=profile.cash - amount)
        await m_profile.edit_field(ctx, cash=m_profile.cash + amount)
        await ctx.send(f'{ctx.tick(True)} {ctx.author.display_name} gave ${amount} to {member.display_name}.')

    @commands.group(aliases=['סלוט'])
    @commands.cooldown(1, 2, commands.BucketType.user)
    async def slots(self, ctx, amount: int = 10):
        """Plays slots default bet is $10"""
        # if ctx.subcommand_invoked is None:
        if amount < 10:
            await ctx.send('You can\'t bet less than $10.')
            return
        profile = await self.get_profile(ctx, ctx.author.id)
        if not profile:
            return await ctx.invoke(self.make)
        if profile.cash < amount:
            await ctx.send(f'{ctx.tick(False)} You don\'t have enough cash.')
        else:
            slot = ['\U0001f352', '\U0001f347', '\U0001f353']
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
            chance = random.randint(1, 2)
            if chance is not 2:
                winning_times = 1
            else:
                winning_times = 0

            await ctx.send(f'{slot_machine}\n**{ctx.message.author.display_name}** bet ${amount} and won ${round(amount*int(winning_times/0.5))}')
            await profile.edit_field(ctx, cash=profile.cash+round(amount*int(winning_times/0.5)))

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

        await self.edit_field(ctx, cash=profile.cash[0]-100)
        await self.edit_user_field(member, ctx, cash=profile.cash[0]-100)

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
        e.add_field(name="Top global profiles by cash", value=value)

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
        e.add_field(name="Top global profiles by experience", value=value)
        await ctx.send(embed=e)

    @commands.command(aliases=['rank'])
    async def level(self, ctx, *, member:discord.Member=None):
        if not member:
            member = ctx.author

        profile = await self.get_profile(ctx, member.id)

        if not profile:
            return await ctx.invoke(self.make)

        await ctx.send(f'{member.display_name} is on level {profile.level} and has {profile.xp} experience.')

    async def on_message(self, message):
        if message.author.bot: return
        ctx = await self.bot.get_context(message, cls=context.Context)

        async with ctx.acquire():
            profile = await self.get_profile(ctx, message.author.id)
            if not profile:
                return

            await profile.increase_xp(ctx)

    @commands.command()
    async def howgay(self, ctx, *, member:discord.Member=None):
        """Tells you how gay you or someone else is."""
        if not member:
            member = ctx.author

        profile = await self.get_profile(ctx, member.id)
        if profile.gay:
            e = discord.Embed(title="How gay?", color=member.top_role.color)
            e.description=f"{member.display_name} is {profile.gay}% gay."
        else
            gay = random.randint(0,100)
            
            if member.id == 285042740738392064:
                gay = 100
            
            e = discord.Embed(title="How gay?", color=member.top_role.color)
            e.description=f"{member.display_name} is {gay}% gay."
            await profile.edit_field(ctx, gay=gay)
        
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(Profile(bot))
