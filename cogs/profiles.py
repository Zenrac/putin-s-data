from discord.ext import commands
from .utils import db
import discord
import random
import re
import asyncio

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
            raise commands.BadArgument("Could not found this member. Note this is case sensitive.")
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
                await ctx.send('this member did not set up a profile yet')
            return


        e = discord.Embed(title="Profile of {}".format(member.nick if member.nick else member.name),color=0x19D719)
        e.set_thumbnail(url=member.avatar_url)
        keys = {
            ':writing_hand: Description': 'description',
            ':birthday: Birthday': 'bday',
            ':heart: Married with': "married",
            ':moneybag: Cash': 'cash',
            ':zap: Experience': 'experience'
        }
        for key, value in keys.items():
            e.add_field(name=key, value=str(record[value]) or 'N/A', inline=True)
        e.add_field(name=':handbag: Inventory', value=":pick:{}x :ring:{}x :diamond_shape_with_a_dot_inside:{}x :rose:{}x :champagne:{}x".format(record['picks'], record['rings'], record['diamonds'], record['roses'], record['alcohol']), inline=True)
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

    @profile.command(aliases=['תיאור'])
    async def description(self, ctx, *, DESC : str):
        """Sets a profile description."""
        await self.edit_field(ctx, description=DESC.strip('"'))
        await ctx.send('Description edited.')

    @profile.command(aliases=['יום הולדת', 'bday'])
    async def birthday(self, ctx, BDAY : str):
        """Sets a birthday to your profile."""
        bday = BDAY.upper()
        await self.edit_field(ctx, bday=bday)
        await ctx.send('Birthday edited.')


    # @profile.command()
    # async def delete(self, ctx, *fields : str):
    #     """Deletes certain fields from your profile.
    #     The valid fields that could be deleted are:
    #     - desc
    #     - bday
    #     Omitting any fields will delete your entire profile.
    #     """
    #     uid = ctx.message.author.id
    #     profile = self.config.get(uid)
    #     if profile is None:
    #         await ctx.send('You don\'t have a profile set up.')
    #         return

    #     if len(fields) == 0:
    #         await self.config.remove(uid)
    #         await ctx.send('Your profile has been deleted.')
    #         return

    #     for attr in map(str.lower, fields):
    #         if hasattr(profile, attr):
    #             setattr(profile, attr, None)

    #     await self.config.put(uid, profile)
    #     fmt = 'The fields {} have been deleted.'
    #     if len(fields) == 1:
    #         fmt = 'The field {} has been deleted'
    #     await ctx.send(fmt.format(', '.join(fields)))


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
        if desc is None:
            return
        query = "insert into profiles values ({}, '{}', '{}', 'nobody...', 0,0,0,0,0,0,0)".format(ctx.author.id, desc.clean_content, bday.clean_content)
        # await self.edit_field(ctx, bday=bday.clean_content.upper())
        # await self.edit_field(ctx, cash=int(0))
        # await self.edit_field(ctx, picks=int(0))
        # await self.edit_field(ctx, married='nobody...')
        # await self.edit_field(ctx, rings=int(0))
        # await self.edit_field(ctx, diamonds=int(0))
        # await self.edit_field(ctx, roses=int(0))
        # await self.edit_field(ctx, alcohol=int(0))
        # await self.edit_field(ctx, experience=int(0))
        # await ctx.send(query)
        await self.bot.pool.execute(query)
        await ctx.send('Alright! Your profile is all ready now.')

    @commands.command()
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def mine(self, ctx):
        """Mines with a chance of getting money and or diamond."""
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, ctx.author.id)
        # if profile is None:
        #     return await ctx.invoke(self.make)
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
                await ctx.send('{} found ${} and has now ${}\n**You can mine again in 5 minutes!**'.format(ctx.message.author.name, found, cash))
                if diamond_chance == 1:
                    await ctx.send('You lucky, you found a diamond.')
                    diamonds += 1
                    await self.edit_field(ctx, diamonds=diamonds)
    @mine.error
    async def mine_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send('You are on cooldown. Chill.', delete_after=10.0)

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
        await ctx.send('{} found ${}, and has now ${}\n**You can loot again in 3 minutes!**'.format(ctx.message.author.name, found, cash))

    @commands.command(invoke_without_command = True)
    async def market(self, ctx):
        """Shows item prices."""
        embed=discord.Embed(title=":shopping_cart: Market:", description="", color=discord.Color.green())
        embed.add_field(name=":pick: Pickaxe",value="Buy :inbox_tray:  $100, Sell :outbox_tray:  $75",inline=False)
        embed.add_field(name=":ring: Ring", value="Buy :inbox_tray:  $200, Sell :outbox_tray:  $150",inline=False)
        embed.add_field(name=":diamond_shape_with_a_dot_inside: Diamond:", value="Buy :inbox_tray:  $2000, Sell :outbox_tray:  $1500", inline=False)
        embed.add_field(name=":rose: Rose:", value="Buy :inbox_tray:  $25, Sell :outbox_tray:  $19", inline=False)
        embed.add_field(name=":champagne: Alcohol:", value="Buy :inbox_tray:  $50, Sell :outbox_tray:  $38", inline=False)
        await ctx.send(embed=embed)

    @commands.group(invoke_without_command=True)
    async def sell(self, ctx):
        """Use ``(prefix)help sell`` for more information."""
        await ctx.send('Use ``{}help sell`` for more information.'.format(ctx.prefix))

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

    @sell.command(name='alcohol')
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

    @buy.command()
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

    @commands.command()
    async def marry(self, ctx, *, member : discord.Member = None):
        """Marrys a member."""
        if member is None:
                await ctx.message.delete()
                msg = await ctx.send('You did not enter a user to propose.')
                await asyncio.sleep(10)
                await self.bot.delete_message(msg)
                return
        if member:
            if str(ctx.message.author.id) == str(member.id):
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
                if married in 'nobody...':
                    married = None
                if married is not None:
                    await ctx.send('You are already married with {}.'.format(married))
                    return
                query = """select * from profiles where id=$1"""
                member_profile = await self.bot.pool.fetchrow(query, ctx.author.id)
                if member_profile is None:
                    await ctx.send('That user does not have a profile.')
                member_married = member_profile['married']
                if member_married in 'nobody...':
                    member_married = None
                if member_married is not None:
                    await ctx.send('That user is already married with {}.'.format(member_married))
                    return
                if rings >= 2:
                    rings -= 2
                    await ctx.send('{} proposed {}.\n{} type yes or no in 60 seconds.'.format(ctx.message.author.name, member.name, member.mention))
                    def pred(m):
                        return m.author == member and m.channel == ctx.message.channel

                    answer = await self.bot.wait_for('message', timeout=60, check=pred)
                    if answer.content.lower() in 'yes':
                        await self.edit_field(ctx, rings=rings)
                        await self.edit_user_field(member, ctx, married=ctx.message.author.name)
                        await self.edit_field(ctx, married=member.name)
                        await ctx.send(':heart: | {} is now married with {}'.format(ctx.message.author.name, member.name))
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
            if married in 'nobody...':
                await ctx.send('You weren\'t married in the first place.')
                return
            query = """select * from profiles where id=$1"""
            m_profile = await self.bot.pool.fetchrow(query, ctx.author.id)

            if m_profile is None:
                await ctx.message.delete()
                msg = await ctx.send('That user does not have a profle.')
                await asyncio.sleep(10)
                await self.bot.delete_message(msg)
            m_married = m_profile['married']
            if member.name in married:
                await ctx.send('{} would like to get divorced with {}.\n{} type yes in 60 seconds if you want to get divorced.'.format(ctx.message.author.name, member.name, member.mention))
                def pred(m):
                    return m.author == member and m.channel == ctx.message.channel

                answer = await self.bot.wait_for('message', check=pred)
                if answer.content in 'yes':
                    await self.edit_user_field(member, ctx, married='nobody...')
                    await self.edit_field(ctx, married='nobody...')
                    await ctx.send(':broken_heart: | {} got divorced with {}.'.format(ctx.message.author.name, member.name))
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
            await self.bot.delete_message(msg)
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
                await ctx.send('Gave :pick: to {}.'.format(member.name))

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
            await self.bot.delete_message(msg)
        else:
            query = """select * from profiles where id=$1"""
            profile = await self.bot.pool.fetchrow(query, ctx.author.id)
            if profile is None:
                return await ctx.invoke(self.make)
            rings = profile['rings']
            if rings == 0:
                msg = await ctx.send('You don\'t have any rings.')
                await asyncio.sleep(10)
                await self.bot.delete_message(msg)
            else:
                rings -= 1
                query = """select * from profiles where id=$1"""
                member_profile = await self.bot.pool.fetchrow(query, ctx.author.id)
                if member_profile is None:
                    await ctx.send('That user does not have a profile.')
                member_rings = member_profile['rings'] + 1
                await self.edit_field(ctx, rings=rings)
                await self.edit_user_field(member, ctx, rings=member_rings)
                await ctx.send('Gave :ring: to {}.'.format(member.name))

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
            await self.bot.delete_message(msg)
        else:
            query = """select * from profiles where id=$1"""
            profile = await self.bot.pool.fetchrow(query, ctx.author.id)
            if profile is None:
                return await ctx.invoke(self.make)
            diamonds = profile['diamonds']
            if diamonds == 0:
                msg = await ctx.send('You don\'t have any diamonds.')
                await asyncio.sleep(10)
                await self.bot.delete_message(msg)
            else:
                diamonds -=1
                query = """select * from profiles where id=$1"""
                member_profile = await self.bot.pool.fetchrow(query, ctx.author.id)
                if member_profile is None:
                    await ctx.send('That user does not have a profile.')
                member_diamonds = member_profile['diamonds'] + 1
                await self.edit_field(ctx, diamonds=diamonds)
                await self.edit_user_field(member, ctx, diamonds=member_diamonds)
                await ctx.send('Gave :diamond_shape_with_a_dot_inside: to {}.'.format(member.name))

    @itemtransfer.command(name='rose')
    async def rrose(self, ctx, *, member : discord.Member = None):
        """Gives your rose to another member."""
        try:
            await ctx.message.delete()
        except:
            pass
        if member is None:
            msg = await ctx.send('You didn\'t tell who to give the item.')
            await asyncio.sleep(10)
            await self.bot.delete_message(msg)
        else:
            query = """select * from profiles where id=$1"""
            profile = await self.bot.pool.fetchrow(query, ctx.author.id)
            if profile is None:
                return await ctx.invoke(self.make)
            roses = profile['roses']
            if roses == 0:
                msg = await ctx.send('You don\'t have any roses.')
                await asyncio.sleep(10)
                await self.bot.delete_message(msg)
            else:
                roses -=1
                query = """select * from profiles where id=$1"""
                member_profile = await self.bot.pool.fetchrow(query, ctx.author.id)
                if member_profile is None:
                    await ctx.send('That user does not have a profile.')
                member_roses = member_profile['roses'] + 1
                await self.edit_field(ctx, roses=roses)
                await self.edit_user_field(member, ctx, roses=member_roses)
                await ctx.send('Gave :rose: to {}.'.format(member.name))

    @itemtransfer.command(name='alcohol')
    async def aalcohol(self, ctx, *, member : discord.Member = None):
        """Gives your alcohol to another member."""
        try:
            await ctx.message.delete()
        except:
            pass
        if member is None:
            msg = await ctx.send('You didn\'t tell who to give the item.')
            await asyncio.sleep(10)
            await self.bot.delete_message(msg)
        else:
            query = """select * from profiles where id=$1"""
            profile = await self.bot.pool.fetchrow(query, ctx.author.id)
            if profile is None:
                return await ctx.invoke(self.make)
            alcohol = profile['alcohol']
            if alcohol == 0:
                msg = await ctx.send('You don\'t have any alcohol.')
                await asyncio.sleep(10)
                await self.bot.delete_message(msg)
            else:
                alcohol -=1
                query = """select * from profiles where id=$1"""
                member_profile = await self.bot.pool.fetchrow(query, ctx.author.id)
                if member_profile is None:
                    await ctx.send('That user does not have a profile.')
                member_alcohol = member_profile['alcohol'] + 1
                await self.edit_field(ctx, alcohol=alcohol)
                await self.edit_user_field(member, ctx, alcohol=member_alcohol)
                await ctx.send('Gave :champagne: to {}.'.format(member.name))

    @commands.command(aliases=['givemoney'])
    async def moneytransfer(self, ctx, amount : int, *, member : discord.Member = None):
        """Gives the amount you specify from your money to the member you specify."""
        if ctx.author.id == member.id:
            return await ctx.send('Why\'d you give yourself money from yourself?')
        try:
            await ctx.message.delete()
        except:
            pass
        if amount < 1:
            await ctx.send('You can\'t transfer less than $1.')
            return
        if member is None:
            msg = await ctx.send('You didn\'t tell me who to give the money to.')
            await asyncio.sleep(10)
            await self.bot.delete_message(msg)
        else:
            query = """select * from profiles where id=$1"""
            profile = await self.bot.pool.fetchrow(query, ctx.author.id)
            if profile is None:
                return await ctx.invoke(self.make)
            cash = profile['cash']
            if cash <= amount:
                msg = await ctx.send('You don\'t have enough money to give.')
                await asyncio.sleep(10)
                await msg.delete()
            else:
                cash -= amount
                query = """select * from profiles where id=$1"""
                member_profile = await self.bot.pool.fetchrow(query, ctx.author.id)
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
            slot = [':four_leaf_clover:', ':moneybag:', ':cherries:', ':lemon:', ':grapes:', ':poop:', ':diamond_shape_with_a_dot_inside:', ':dollar:', ':money_with_wings:', ':slot_machine:', ':strawberry:']
            slot_machine = '╔════[SLOTS]════╗\n║  {}   ║  {}   ║  {}  ║\n>   {}   ║  {}   ║  {}  <\n║  {}   ║   {}  ║  {}  ║\n╚════[SLOTS]════╝'
            rand = random.randint(1,3)
            if rand == 1:
                winning = 'and lost everything.'
            elif rand == 2:
                win_amount = amount * 1.5
                winning = 'and won ${}'.format(win_amount)
                cash += win_amount
            else:
                win_amount = amount * 2
                winning = 'and won ${}'.format(win_amount)
                cash += win_amount


            await ctx.send(slot_machine.format(random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot))+'\n**{}** bet ${} {}'.format(ctx.message.author.name,amount, winning))
            await self.edit_field(ctx, cash=cash)

    # @commands.command()
    # @commands.is_owner()
    # async def convert(self, ctx):
    #     conn = psycopg2.connect("dbname='postgres' user='postgres' host='localhost' password='postgres'")
    #     cur = conn.cursor()
    #     with open('profiles.json') as f:
    #         data = json.load(f)
    #     # print(data)
    #     for profile in data:
    #         profilee = self.config.get(profile)
    #         desc = str(profilee.desc.replace("'", '\''))
    #         bday = str(profilee.bday)
    #         married = str(profilee.married)
    #         picks = str(profilee.picks)
    #         rings = str(profilee.rings)
    #         diamonds = str(profilee.diamonds)
    #         roses = str(profilee.roses)
    #         alcohol = str(profilee.alcohol)
    #         exp = str(profilee.experience)
    #         cash = str(profilee.cash)
    #         print(diamonds)
    #         print('got the vars')
    #         print('insert into profiles values ({}, \'{}\', \'{}\', \'{}\', {}, {}, {}, {}, {}, {}, {})'.format(profile, desc, bday, married, picks, rings, diamonds, roses, alcohol, exp, cash))
    #         cur.execute('insert into profiles values ({}, \'{}\', \'{}\', \'{}\', {}, {}, {}, {}, {}, {}, {})'.format(profile, desc, bday, married, picks, rings, diamonds, roses, alcohol, exp, cash))
    #         conn.commit()
    #         print(str(profile) + ' has been inserted.')

    @commands.command()
    async def leaderboard(self, ctx):
        query = """SELECT id as "_id", cash as "cash"
                FROM profiles
                ORDER BY "cash" DESC
                LIMIT 5;
        """
        records = await ctx.bot.pool.fetch(query)
        print(records)

        e = discord.Embed(title='Leaderboard')
        def get_name(_id):
            user = self.bot.get_user(id)
            if user is not None:
                return user.name
            else:
                return 'Undefined'

        # value = '\n'.join(f'**{await get_name(_id)}**: **${cash}**'
        #                     for (index (_id, cash)) in enumerate(records))
        # value = str(records)
        print(records)
        value = '\n'.join(f'{_id}: {cash}' for (_id, cash) in records)
        e.add_field(name="\u200b", value=value, inline=True)
        e.set_footer(text='Names can\'t be viewed here so you\'ll have to use .info <id>.')
        await ctx.send(embed=e)

    async def on_message(self, message):
        if message.author.bot: return
        query = """select * from profiles where id=$1"""
        profile = await self.bot.pool.fetchrow(query, message.author.id)
        if not profile:
            return
        if not profile['experience']:
        #     profile = self.config.get(str(message.author.id))
        #     setattr(profile, 'experience', 0)
        #     await self.config.put(str(message.author.id), profile)
            return
        exp = profile['experience']
        add = random.randint(1, 10)
        exp += add
        ctx = await self.bot.get_context(message)
        await self.edit_field(ctx, experience=exp)

    # @slots.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            m, s = divmod(error.retry_after, 60)
            h, m = divmod(m, 60)
            await ctx.send("This command is on cooldown for another {}.".format("%d hour(s) %02d minute(s) %02d second(s)" % (h, m, s)), delete_after=10.0)


def setup(bot):
    bot.add_cog(Profile(bot))
