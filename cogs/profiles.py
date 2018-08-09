from discord.ext import commands
import discord.utils
from .utils import config, formats
import json, re
from collections import Counter
import asyncio
import random

class DefaultProfileType:
    def __str__(self):
        return 'me'

MyOwnProfile = DefaultProfileType()

class MemberParser:
    """
    Lazily fetches an argument and then when asked attempts to get the data.
    """

    def __init__(self, argument):
        self.argument = argument.strip()
        self.regex = re.compile(r'<@([0-9]+)>')

    def member_entry(self, tup):
        index = tup[0]
        member = tup[1]
        return '{0}. {1.name}#{1.discriminator} from {1.guild.name}'.format(index, member)

    async def get(self, ctx):
        """Given an invocation context, gets a user."""
        guild = ctx.guild
        bot = ctx.me
        members = guild.members if guild is not None else bot.get_all_members()
        # check if the argument is a mention
        m = self.regex.match(self.argument)
        if m:
            user_id = m.group(1)
            await ctx.send(user_id)
            return discord.utils.get(members, id=user_id)

        # it isn't, so search by name
        results = {m for m in members if m.name == self.argument}
        results = list(results)
        if len(results) == 0:
            # we have no matches... so we must return None
            return None


        if len(results) == 1:
            # we have an exact match.
            return results[0]

        # no exact match
        msg = ctx.message
        member = await formats.too_many_matches(bot, msg, results, self.member_entry)
        return member

class ProfileInfo:
    def __init__(self, **kwargs):
        self.desc = kwargs.get('desc')
        self.bday = kwargs.get('bday')
        self.married = kwargs.get('married')
        self.cash = kwargs.get('cash')
        self.inventory = kwargs.get('inventory')
        self.picks = kwargs.get('picks')
        self.rings = kwargs.get('rings')
        self.diamonds = kwargs.get('diamonds')
        self.roses = kwargs.get('roses')
        self.alcohol = kwargs.get('alcohol')
        self.experience = kwargs.get('experience')

    def __str__(self):
        output = []
        output.append('Description: {0.desc}'.format(self))
        output.append('Birthday: {0.bday}'.format(self))
        output.append('Married with: {0.married}'.format(self))
        output.append('Cash: {0.cash}'.format(self))
        output.append('Inventory: {o.inventory}'.format(self))
        output.append('Picks: {0.picks}'.format(self))
        output.append('Rings: {0.rings}'.format(self))
        output.append('Diamonds: {0.diamonds}'.format(self))
        output.append('Roses: {0.roses}'.format(self))
        output.append('Alcohol: {0.alcohol}'.format(self))
        output.append('Experience: {0.experience}'.format(self))
        return '\n'.join(output)


class ProfileEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ProfileInfo):
            payload = obj.__dict__.copy()
            payload['__profile__'] = True
            return payload
        return json.JSONEncoder.default(self, obj)

def profile_decoder(obj):
    if '__profile__' in obj:
        return ProfileInfo(**obj)
    return obj

class Profile:
    """Profile related commands."""

    def __init__(self, bot):
        self.bot = bot
        self.config = config.Config('profiles.json', encoder=ProfileEncoder, object_hook=profile_decoder)

    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return

        ignored = (commands.CommandNotFound, commands.UserInputError)
        error = getattr(error, 'original', error)

        if isinstance(error, ignored):
            return

        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list':
                return await ctx.send('I could not find that member. Please try again.')

    async def get_profile(self, ctx, parser):
        try:
            if parser is MyOwnProfile:
                member = ctx.message.author
            else:
                member = await parser.get(ctx)
        except commands.CommandError as e:
            await ctx.send(e)
            return
        if member.bot:
            await ctx.send('Bots can\'t have profiles.')
            return

        if member is None:
            await ctx.send('Member not found. Note that this is case sensitive. You can use a mention instead.')
            return

        profile = self.config.get(str(member.id))
        if profile is None:
            if parser is not MyOwnProfile:
                await ctx.send('This member did not set up a profile.')
            else:
                await ctx.send('You did not set up a profile. One is being created for you.')
                await self.config.put(str(member.id), ProfileInfo())
                await ctx.invoke(self.make)
        else:
            if ctx.guild.id == 418801915162263574:
                # if not profile.alcohol in profile:
                #     profile = self.config.get(member.id)
                #     setattr(profile, 'alcohol', 0)
                #     await self.config.put(member.id, profile)
                embed = discord.Embed(title="**{0.name}#{0.discriminator}**:פרופיל על".format(member), description="", color=discord.Color.magenta())
                embed.add_field(name=":writing_hand: תיאור:", value="{}".format(profile.desc), inline=False)
                embed.add_field(name=":birthday: יום הולדת:", value="{}".format(profile.bday), inline=True)
                embed.add_field(name=":heart: התחתן עם:", value="{}".format(profile.married), inline=True)
                embed.add_field(name=":moneybag: כסף:", value="${}".format(profile.cash), inline=True)
                embed.add_field(name=":zap: פרופיל על:", value="{}".format(profile.experience), inline=True)
                embed.add_field(name=":medal: רמה:", value="{}".format(int(profile.experience / 1000)), inline=True)
                embed.add_field(name=":handbag: מלאי:", value=":pick:{}x :ring:{}x :diamond_shape_with_a_dot_inside:{}x :rose:{}x :champagne:{}x".format(profile.picks, profile.rings, profile.diamonds, profile.roses, profile.alcohol), inline=True)
                # embed.add_field(name="", value=":pick:{}x".format(profile.picks), inline=Falses)
                embed.set_thumbnail(url=member.avatar_url)
                profile_menu = await ctx.send(embed=embed)
                await profile_menu.add_reaction('❌')
                def check(reaction, user):
                    return user == ctx.message.author and reaction.emoji in '❌'
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', check=check)
                except:
                    pass
                if reaction:
                    await profile_menu.delete()
                    await ctx.message.delete()
            else:
                # if not profile.alcohol in profile:
                #     profile = self.config.get(member.id)
                #     setattr(profile, 'alcohol', 0)
                #     await self.config.put(member.id, profile)
                embed = discord.Embed(title="Profile of **{0.name}#{0.discriminator}**:".format(member), description="", color=discord.Color.magenta())
                embed.add_field(name=":writing_hand: Description:", value="{}".format(profile.desc), inline=False)
                embed.add_field(name=":birthday: Birthday:", value="{}".format(profile.bday), inline=True)
                embed.add_field(name=":heart: Married with:", value="{}".format(profile.married), inline=True)
                embed.add_field(name=":moneybag: Cash:", value="${}".format(profile.cash), inline=True)
                embed.add_field(name=":zap: Experience:", value="{}".format(profile.experience), inline=True)
                embed.add_field(name=":medal: Level:", value="{}".format(int(profile.experience / 1000)), inline=True)
                embed.add_field(name=":handbag: Inventory:", value=":pick:{}x :ring:{}x :diamond_shape_with_a_dot_inside:{}x :rose:{}x :champagne:{}x".format(profile.picks, profile.rings, profile.diamonds, profile.roses, profile.alcohol), inline=True)
                # embed.add_field(name="", value=":pick:{}x".format(profile.picks), inline=Falses)
                embed.set_thumbnail(url=member.avatar_url)
                profile_menu = await ctx.send(embed=embed)
                await profile_menu.add_reaction('❌')
                def check(reaction, user):
                    return user == ctx.message.author and reaction.emoji in '❌'
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', check=check)
                except:
                    pass
                if reaction:
                    await profile_menu.delete()
                    await ctx.message.delete()

    @commands.group(invoke_without_command=True, aliases=['פרופיל'])
    async def profile(self, ctx, *, member : MemberParser = MyOwnProfile):
        """Shows your or another member's profile."""
        await self.get_profile(ctx, member)

    @profile.command()
    async def get(self, ctx, *, member : MemberParser):
        """Gets a profile of another member."""
        await self.get_profile(ctx, member)

    async def edit_field(self, attr, ctx, data):
        user_id = str(ctx.message.author.id)
        profile = self.config.get(user_id, ProfileInfo())
        setattr(profile, attr, data)
        await self.config.put(user_id, profile)
        # await ctx.send('Field {} set to {}.'.format(attr, data))

    async def edit_user_field(self, member, attr, ctx, data):
        user_id = str(member.id)
        profile = self.config.get(user_id, ProfileInfo())
        setattr(profile, attr, data)
        await self.config.put(user_id, profile)


    @profile.command(aliases=['תיאור'])
    async def description(self, ctx, *, DESC : str):
        """Sets a profile description."""
        await self.edit_field('desc', ctx, DESC.strip('"'))
        await ctx.send('Description edited.')

    @profile.command(aliases=['יום הולדת'])
    async def birthday(self, ctx, BDAY : str):
        """Sets a birthday to your profile."""
        bday = BDAY.upper()
        await self.edit_field('bday', ctx, bday)
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
        await ctx.invoke(self.description, DESC=desc.content)
        await ctx.send('Now tell me, what is your birthday? Format is DD-MM-YYYY.\nYou can also say none if you don\'t want to expose your birthday.\nSay ``cancel`` to cancel.')
        def pred(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel

        bday = await self.bot.wait_for('message', check=pred)
        if bday.content.lower() == 'cancel':
            return await ctx.send('Cancelled profile creation.')
        if desc is None:
            return

        await self.edit_field('bday', ctx, bday.clean_content.upper())
        await self.edit_field('cash', ctx, int(0))
        await self.edit_field('picks', ctx, int(0))
        await self.edit_field('married', ctx, 'nobody...')
        await self.edit_field('inventory', ctx, ':pick:0x :ring:0x :diamond_shape_with_a_dot_inside:0x')
        await self.edit_field('rings', ctx, int(0))
        await self.edit_field('diamonds', ctx, int(0))
        await self.edit_field('roses', ctx, int(0))
        await self.edit_field('alcohol', ctx, int(0))
        await self.edit_field('experience', ctx, int(0))
        await ctx.send('Alright! Your profile is all ready now.')

    @commands.command()
    @commands.cooldown(1, 300, commands.BucketType.user)
    async def mine(self, ctx):
        """Mines with a chance of getting money and or diamond."""
        profile = self.config.get(str(ctx.message.author.id))
        if profile is None:
            await ctx.invoke(self.make)
        picks = profile.picks
        cash = profile.cash
        diamonds = profile.diamonds
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
            await self.edit_field('picks', ctx, picks)
            mining_chance = random.randint(1, 3)
            diamond_chance = random.randint(1, 25)
            if mining_chance == 1:
                await ctx.send('You broke your pickaxe.\n**You can mine again in 5 minutes!**')
                if diamond_chance == 1:
                    await ctx.send('But you found a diamond lying on the ground.')
                    diamonds += 1
                    await self.edit_field('diamonds', ctx, diamonds)
            else:
                found = random.randint(40, 200)
                cash += found
                await self.edit_field('cash', ctx, cash)
                await self.edit_field('picks', ctx, picks)
                await ctx.send('{} found ${} and has now ${}\n**You can mine again in 5 minutes!**'.format(ctx.message.author.name, found, cash))
                if diamond_chance == 1:
                    await ctx.send('You lucky, you found a diamond.')
                    diamonds += 1
                    await self.edit_field('diamonds', ctx, diamonds)
    @mine.error
    async def mine_handler(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send('You are on cooldown. Chill.', delete_after=10.0)

    @commands.command()
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def daily(self, ctx):
        """Gets your daily money."""
        profile = self.config.get(str(ctx.message.author.id))
        if profile is None:
            await ctx.invoke(self.make)
        cash = profile.cash
        found = random.randint(100,150)
        cash += found
        await self.edit_field('cash', ctx, cash)
        await ctx.send('You got ${} from daily and you have ${} in total.\n**Come get your daily again after 24h.**'.format(found, cash))

    @commands.command(aliases=['balance', 'כסף', 'בנק'])
    async def money(self, ctx):
        """Shows your money amount."""
        profile = self.config.get(str(ctx.author.id))
        if profile is None:
            await ctx.invoke(self.make)
        cash = profile.cash
        await ctx.send('You have ${}'.format(cash))

    @commands.command()
    @commands.cooldown(1, 180, commands.BucketType.user)
    async def loot(self, ctx):
        """Loots money from messages."""
        profile = self.config.get(str(ctx.message.author.id))
        if profile is None:
            await ctx.invoke(self.make)
        cash = profile.cash
        found = random.randint(20,50)
        cash = cash + found
        await self.edit_field('cash', ctx, cash)
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

    @sell.command(name='pick')
    async def pic(self, ctx, amount : int = None):
        """Sells a pickaxe."""
        profile = self.config.get(str(ctx.message.author.id))
        if profile is None:
            await ctx.invoke(self.make)
        cash = profile.cash
        picks = profile.picks
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
            await self.edit_field('cash', ctx, cash)
            await self.edit_field('picks', ctx, picks)
            await ctx.send('Sold {}x :pick:'.format(amount))

    @sell.command(name='ring')
    async def rin(self, ctx, amount : int = None):
        profile = self.config.get(str(ctx.message.author.id))
        if profile is None:
            await ctx.invoke(self.make)
        cash = profile.cash
        rings = profile.rings
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
            await self.edit_field('cash', ctx, cash)
            await self.edit_field('rings', ctx, rings)
            await ctx.send('Sold {}x :ring:'.format(amount))

    @sell.command(name='diamond')
    async def diamon(self, ctx, amount : int = None):
        """Sells a diamond."""
        profile = self.config.get(str(ctx.message.author.id))
        if profile is None:
            await ctx.invoke(self.make)
        diamonds = profile.diamonds
        cash = profile.cash
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
            await self.edit_field('diamonds', ctx, diamonds)
            await self.edit_field('cash', ctx, cash)
            await ctx.send('Sold {}x :diamond_shape_with_a_dot_inside:'.format(amount))

    @sell.command(name='rose')
    async def ros(self, ctx, amount : int = None):
        """Sells a rose."""
        profile = self.config.get(str(ctx.message.author.id))
        if profile is None:
            await ctx.invoke(self.make)
        roses = profile.roses
        cash = profile.cash
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
            await self.edit_field('roses', ctx, roses)
            await self.edit_field('cash', ctx, cash)
            await ctx.send('Sold {}x :rose:'.format(amount))

    @sell.command(name='alcohol')
    async def alcoho(self, ctx, amount : int = None):
        """Sells alcohol."""
        profile = self.config.get(str(ctx.message.author.id))
        if profile is None:
            await ctx.invoke(self.make)
        alcohol = profile.alcohol
        cash = profile.cash
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
            await self.edit_field('alcohol', ctx, alcohol)
            await self.edit_field('cash', ctx, cash)
            await ctx.send('Sold {}x :champagne:'.format(amount))

    @commands.command()
    async def drink(self, ctx):
        """Drinks alcohol."""
        profile = self.config.get(str(ctx.message.author.id))
        if profile is None:
            await ctx.invoke(self.make)
            return
        alcohol = profile.alcohol
        if alcohol == 0:
            await ctx.send('You don\'t have any alcohol.')
        else:
            alcohol -= 1
            await self.edit_field('alcohol', ctx, alcohol)
            await ctx.send('You drank :champagne: and got drunk.')

    @commands.group(invoke_without_command=True)
    async def buy(self, ctx):
        """Use ``(prefix)help buy`` for more information."""
        print("buying")

    @buy.command()
    async def pick(self, ctx, amount : int = None):
        """Buys a pickaxe."""
        profile = self.config.get(str(ctx.message.author.id))
        if profile is None:
            await ctx.invoke(self.make)
        if amount is None:
            amount =1
        cash = profile.cash
        picks = profile.picks
        if amount*100 > cash:
            await ctx.send('You don\'t have enough money.')
            return
        if cash >= 100:
            cash -= amount * 100
            picks += amount
            if amount is None:
                amount = 1
            await ctx.send('Bought {}x :pick:'.format(amount))
            await self.edit_field('cash', ctx, cash)
            await self.edit_field('picks', ctx, picks)
        else:
            await ctx.send('You don\'t have enough cash.')

    @buy.command()
    async def ring(self, ctx, amount : int = None):
        """Buys a ring."""
        profile = self.config.get(str(ctx.message.author.id))
        if profile is None:
            await ctx.invoke(self.make)
        rings = profile.rings
        cash = profile.cash
        if amount is None:
            amount = 1
        if amount*200 > cash:
            await ctx.send('You don\'t have enough money.')
            return
        if cash >= 200:
            cash -= amount * 200
            rings += amount
            await ctx.send('Bought {}x :ring:'.format(amount))
            await self.edit_field('cash', ctx, cash)
            await self.edit_field('rings', ctx, rings)
        else:
            await ctx.send('You don\'t have enough cash.')

    @buy.command()
    async def diamond(self, ctx, amount : int = None):
        """Buys a diamond."""
        profile = self.config.get(str(ctx.message.author.id))
        if profile is None:
            await ctx.invoke(self.make)
        cash = profile.cash
        diamonds = profile.diamonds
        if amount is None:
            amount = 1
        if amount*2000 > cash:
            await ctx.send('You don\'t have enough money.')
            return
        if cash >= amount*2000:
            cash -= amount * 2000
            diamonds += amount
            await self.edit_field('cash', ctx, cash)
            await self.edit_field('diamonds', ctx, diamonds)
            await ctx.send('Bought {}x :diamond_shape_with_a_dot_inside:'.format(amount))
        else:
            await ctx.send('You don\'t have enough cash.')

    @buy.command()
    async def rose(self, ctx, amount : int = None):
        """Buys a rose."""
        profile = self.config.get(str(ctx.message.author.id))
        if profile is None:
            await ctx.invoke(self.make)
        cash = profile.cash
        roses = profile.roses
        if amount is None:
            amount = 1
        if amount*25 > cash:
            await ctx.send('You don\'t have enough money.')
            return
        if cash >= 25:
            cash -= amount * 25
            roses += amount
            await self.edit_field('cash', ctx, cash)
            await self.edit_field('roses', ctx, roses)
            await ctx.send('Bought {}x :rose:'.format(amount))
        else:
            await ctx.send('You don\'t have enough cash.')

    @buy.command()
    async def alcohol(self, ctx, amount : int = None):
        """Buys alcohol."""
        profile = self.config.get(str(ctx.message.author.id))
        if profile is None:
            await ctx.invoke(self.make)
        cash = profile.cash
        alcohol = profile.alcohol
        if amount is None:
            amount = 1
        if amount*50 > cash:
            await ctx.send('You don\'t have enough money.')
            return
        if cash >= 50:
            cash -= amount * 50
            alcohol += amount
            await self.edit_field('cash', ctx, cash)
            await self.edit_field('alcohol', ctx, alcohol)
            await ctx.send('Bought {}x :champagne:'.format(amount))
        else:
            await ctx.send('You don\'t have enough cash.')

    @commands.command()
    async def marry(self, ctx, *, member : discord.Member = None):
        """Marrys a member."""
        if member is None:
                await self.bot.delete_message(ctx.message)
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
                profile = self.config.get(str(ctx.message.author.id))
                if profile is None:
                    await ctx.invoke(self.make)
                rings = profile.rings
                married = profile.married
                if married in 'nobody...':
                    married = None
                if married is not None:
                    await ctx.send('You are already married with {}.'.format(married))
                    return
                member_profile = self.config.get(str(member.id))
                if member_profile is None:
                    await ctx.send('That user does not have a profile.')
                member_married = member_profile.married
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
                        await self.edit_field('rings', ctx, rings)
                        await self.edit_user_field(member, 'married', ctx, ctx.message.author.name)
                        await self.edit_field('married', ctx, member.name)
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
            profile = self.config.get(str(ctx.message.author.id))
            if profile is None:
                await ctx.invoke(self.make)
            married = profile.married
            if married in 'nobody...':
                await ctx.send('You weren\'t married in the first place.')
                return
            m_profile = self.config.get(str(member.id))

            if m_profile is None:
                await self.bot.delete_message(ctx.message)
                msg = await ctx.send('That user does not have a profle.')
                await asyncio.sleep(10)
                await self.bot.delete_message(msg)
            m_married = m_profile.married
            if member.name in married:
                await ctx.send('{} would like to get divorced with {}.\n{} type yes in 60 seconds if you want to get divorced.'.format(ctx.message.author.name, member.name, member.mention))
                def pred(m):
                    return m.author == member and m.channel == ctx.message.channel

                answer = await self.bot.wait_for('message', check=pred)
                if answer.content in 'yes':
                    await self.edit_user_field(member, 'married', ctx, 'nobody...')
                    await self.edit_field('married', ctx, 'nobody...')
                    await ctx.send(':broken_heart: | {} got divorced with {}.'.format(ctx.message.author.name, member.name))
                else:
                    await ctx.send('I\'ll take that as no.')
            else:
                await ctx.send('You are not married with that user.')

    @commands.group(aliases=['giveitem'])
    async def itemtransfer(self, ctx):
        """Use ``(prefix)help itemtransfer`` for more information."""
        print("it")

    @itemtransfer.command(name='pick')
    async def ppick(self, ctx, member : discord.Member = None):
        """Gives your pickaxe to another member."""
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        if member is None:
            msg = await ctx.send('You didn\'t tell who to give the item.')
            await asyncio.sleep(10)
            await self.bot.delete_message(msg)
        else:
            profile = self.config.get(str(ctx.message.author.id))
            if profile is None:
                await ctx.invoke(self.make)
            picks = profile.picks
            if picks == 0:
                await ctx.send('You don\'t have any pickaxes.')
            else:
                picks -= 1
                member_profile = self.config.get(str(member.id))
                if member_profile is None:
                    await ctx.send('That user does not have a profile.')
                member_picks = member_profile.picks + 1
                await self.edit_field('picks', ctx, picks)
                await self.edit_user_field(member, 'picks', ctx, member_picks)
                await ctx.send('Gave :pick: to {}.'.format(member.name))

    @itemtransfer.command(name='ring')
    async def rring(self, ctx, *, member : discord.Member = None):
        """Gives your ring to another member."""
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        if member is None:
            msg = await ctx.send('You didn\'t tell who to give the item.')
            await asyncio.sleep(10)
            await self.bot.delete_message(msg)
        else:
            profile = self.config.get(str(ctx.message.author.id))
            if profile is None:
                await ctx.invoke(self.make)
            rings = profile.rings
            if rings == 0:
                msg = await ctx.send('You don\'t have any rings.')
                await asyncio.sleep(10)
                await self.bot.delete_message(msg)
            else:
                rings -= 1
                member_profile = self.config.get(str(member.id))
                if member_profile is None:
                    await ctx.send('That user does not have a profile.')
                member_rings = member_profile.rings + 1
                await self.edit_field('rings', ctx, rings)
                await self.edit_user_field(member, 'rings', ctx, member_rings)
                await ctx.send('Gave :ring: to {}.'.format(member.name))

    @itemtransfer.command(name='diamond')
    async def ddiamond(self, ctx, *, member : discord.Member = None):
        """Gives your diamond to another member."""
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        if member is None:
            msg = await ctx.send('You didn\'t tell who to give the item.')
            await asyncio.sleep(10)
            await self.bot.delete_message(msg)
        else:
            profile = self.config.get(str(ctx.message.author.id))
            if profile is None:
                await ctx.invoke(self.make)
            diamonds = profile.diamonds
            if diamonds == 0:
                msg = await ctx.send('You don\'t have any diamonds.')
                await asyncio.sleep(10)
                await self.bot.delete_message(msg)
            else:
                diamonds -=1
                member_profile = self.config.get(str(member.id))
                if member_profile is None:
                    await ctx.send('That user does not have a profile.')
                member_diamonds = member_profile.diamonds + 1
                await self.edit_field('diamonds', ctx, diamonds)
                await self.edit_user_field(member, 'diamonds', ctx, member_diamonds)
                await ctx.send('Gave :diamond_shape_with_a_dot_inside: to {}.'.format(member.name))

    @itemtransfer.command(name='rose')
    async def rrose(self, ctx, *, member : discord.Member = None):
        """Gives your rose to another member."""
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        if member is None:
            msg = await ctx.send('You didn\'t tell who to give the item.')
            await asyncio.sleep(10)
            await self.bot.delete_message(msg)
        else:
            profile = self.config.get(str(ctx.message.author.id))
            if profile is None:
                await ctx.invoke(self.make)
            roses = profile.roses
            if roses == 0:
                msg = await ctx.send('You don\'t have any roses.')
                await asyncio.sleep(10)
                await self.bot.delete_message(msg)
            else:
                roses -=1
                member_profile = self.config.get(str(member.id))
                if member_profile is None:
                    await ctx.send('That user does not have a profile.')
                member_roses = member_profile.roses + 1
                await self.edit_field('roses', ctx, roses)
                await self.edit_user_field(member, 'roses', ctx, member_roses)
                await ctx.send('Gave :rose: to {}.'.format(member.name))

    @itemtransfer.command(name='alcohol')
    async def aalcohol(self, ctx, *, member : discord.Member = None):
        """Gives your alcohol to another member."""
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        if member is None:
            msg = await ctx.send('You didn\'t tell who to give the item.')
            await asyncio.sleep(10)
            await self.bot.delete_message(msg)
        else:
            profile = self.config.get(str(ctx.message.author.id))
            if profile is None:
                await ctx.invoke(self.make)
            alcohol = profile.alcohol
            if alcohol == 0:
                msg = await ctx.send('You don\'t have any alcohol.')
                await asyncio.sleep(10)
                await self.bot.delete_message(msg)
            else:
                alcohol -=1
                member_profile = self.config.get(str(member.id))
                if member_profile is None:
                    await ctx.send('That user does not have a profile.')
                member_alcohol = member_profile.alcohol + 1
                await self.edit_field('alcohol', ctx, alcohol)
                await self.edit_user_field(member, 'alcohol', ctx, member_alcohol)
                await ctx.send('Gave :champagne: to {}.'.format(member.name))

    @commands.command(aliases=['givemoney'])
    async def moneytransfer(self, ctx, amount : int, *, member : discord.Member = None):
        """Gives the amount you specify from your money to the member you specify."""
        if ctx.author.id == member.id:
            return await ctx.send('Why\'d you give yourself money from yourself?')
        try:
            await self.bot.delete_message(ctx.message)
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
            profile = self.config.get(str(ctx.message.author.id))
            if profile is None:
                await ctx.invoke(self.make)
            cash = profile.cash
            if cash <= amount:
                msg = await ctx.send('You don\'t have enough money to give.')
                await asyncio.sleep(10)
                await self.bot.delete_message(msg)
            else:
                cash -= amount
                member_profile = self.config.get(str(member.id))
                if member_profile is None:
                    await ctx.send('That user does not have a profile.')
                member_cash = member_profile.cash
                member_cash += amount
                await self.edit_field('cash', ctx, cash)
                await self.edit_user_field(member, 'cash', ctx, member_cash)
                await ctx.send('Gave ${} to {}.'.format(amount, member.name))

    @commands.group(aliases=['סלוט'])
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def slots(self, ctx, amount: int = 10):
        """Plays slots default bet is 10$"""
        # if ctx.subcommand_invoked is None:
        if amount < 10:
            await ctx.send('You can\'t bet less than 10$.')
            return
        profile = self.config.get(str(ctx.message.author.id))
        if profile is None:
            await ctx.invoke(self.make)
        cash = profile.cash
        if cash < amount:
            await ctx.send('You don\'t have enough cash.')
        else:
            cash -= amount
            slot = [':four_leaf_clover:', ':moneybag:', ':cherries:', ':lemon:', ':grapes:', ':poop:', ':diamond_shape_with_a_dot_inside:', ':dollar:', ':money_with_wings:', ':slot_machine:', ':strawberry:']
            slot_machine = '╔════[SLOTS]════╗\n║  {}   ║  {}   ║  {}  ║\n>   {}   ║  {}   ║  {}  <\n║  {}   ║   {}  ║  {}  ║\n╚════[SLOTS]════╝'
            msg = await ctx.send(slot_machine.format(random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot)))
            await asyncio.sleep(1)
            await msg.edit(content=slot_machine.format(random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot)))
            await asyncio.sleep(1)
            await msg.edit(content=slot_machine.format(random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot)))
            await asyncio.sleep(1)
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


            await msg.edit(content=slot_machine.format(random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot))+'\n**{}** bet ${} {}'.format(ctx.message.author.name,amount, winning))
            await self.edit_field('cash', ctx, cash)

    @slots.command()
    async def all(self, ctx):
        profile = self.config.get(str(ctx.message.author.id))
        if profile is None:
            await ctx.invoke(self.make)
        bet = profile.cash
        cash = profile.cash
        if cash < 1:
            await ctx.send('You don\'t have any cash.')
        else:
            cash = 0
            slot = [':four_leaf_clover:', ':moneybag:', ':cherries:', ':lemon:', ':grapes:', ':poop:', ':diamond_shape_with_a_dot_inside:', ':dollar:', ':money_with_wings:', ':slot_machine:', ':strawberry:']
            slot_machine = '╔════[SLOTS]════╗\n║  {}   ║  {}   ║  {}  ║\n>   {}   ║  {}   ║  {}  <\n║  {}   ║   {}  ║  {}  ║\n╚════[SLOTS]════╝'
            msg = await ctx.send(slot_machine.format(random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot)))
            await asyncio.sleep(1)
            await msg.edit(content=slot_machine.format(random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot)))
            await asyncio.sleep(1)
            await msg.edit(content=slot_machine.format(random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot)))
            await asyncio.sleep(1)
            rand = random.randint(1,3)
            if rand == 1:
                winning = 'and lost everything.'
            elif rand == 2:
                win_amount = bet * 1.5
                winning = 'and won ${}'.format(win_amount)
                cash += bet
            else:
                win_amount = bet * 2
                winning = 'and won ${}'.format(win_amount)
                cash += bet


            await msg.edit(content=slot_machine.format(random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot),random.choice(slot))+'\n**{}** bet ${} {}'.format(ctx.message.author.name, bet, winning))
            await self.edit_field('cash', ctx, cash)

    async def on_message(self, message):
        if message.author.bot: return
        profile = self.config.get(str(message.author.id))
        if not profile:
            return
        if not profile.experience:
        #     profile = self.config.get(str(message.author.id))
        #     setattr(profile, 'experience', 0)
        #     await self.config.put(str(message.author.id), profile)
            return
        exp = profile.experience
        add = random.randint(1, 10)
        exp += add
        ctx = await self.bot.get_context(message)
        await self.edit_field('experience', ctx, exp)

    # @slots.error
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            m, s = divmod(error.retry_after, 60)
            h, m = divmod(m, 60)
            await ctx.send("This command is on cooldown for another {}.".format("%d hour(s) %02d minute(s) %02d second(s)" % (h, m, s)), delete_after=10.0)

def setup(bot):
    bot.add_cog(Profile(bot))
