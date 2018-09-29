import discord
from discord.ext import commands
import random
import time
import asyncio
from unidecode import unidecode
import aiohttp
import aiohttp
import json
import datetime

class Fun():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gayify(self, ctx, member:discord.Member=None, member2:discord.Member=None):
        if not member:
            return await ctx.send(f'{ctx.tick(False)} You need to specify at least one member to gayify.')

        if not member2:
            member2 = ctx.author

        e = discord.Embed()
        e.set_image(url=f'https://kaan.ga/iWeeti/gayify/{member2.id}/{member2.avatar}/{member.id}/{member.avatar}/')

        await ctx.send(embed=e)

    @commands.command()
    async def ship(self, ctx, member:discord.Member=None, member2:discord.Member=None):
        if not member:
            return await ctx.send(f'{ctx.tick(False)} You need to specify at least one member to ship with.')

        if not member2:
            member2 = ctx.author

        if len(member.display_name.split()) == 1:
            name_1 = member.display_name[0:len(member.display_name) / 2]
        else:
            name_1 = member.display_name.split()[0]

        if len(member2.display_name.split()) == 1:
            name_2 = member2.display_name[len(member2.display_name) / 2:len(member2.display_name)]
        else:
            name_2 = member2.display_name.split()[1]

        e = discord.Embed(title=name_1 + name_2)
        e.set_image(url=f'https://kaan.ga/iWeeti/loveify/{member2.id}/{member2.avatar}/{member.id}/{member.avatar}/')

        await ctx.send(embed=e)
        
    @commands.command(hidden=False, aliases=['reee'])
    async def ree(self, ctx):
        await ctx.send('**FUCKING NORMIES** ***REEEEEEEEEEEEEEEEEEEEEEEEEEE***')

    @commands.command()
    async def nmeme(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://w-bot.ml/api/meme') as r:
                r = await r.json()

        e = discord.Embed(title='Meme by Community', color=ctx.me.top_role.color)
        e.set_image(url=r['meme'])
        e.set_footer(text='Mostly by NoahVN')
        await ctx.send(embed=e)

    @commands.command()
    async def jumbo(self, ctx, emoji: discord.Emoji):
        e = discord.Embed(title=emoji.name)
        e.set_image(url=emoji.url)
        await ctx.send(embed=e)

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def eat(self, ctx, member: discord.Member):
        if not member:
            return await ctx.send('You didn\'t specify a member.')
        await ctx.send(f'ням, {member.display_name} tastes like finest vodka')

    @commands.command()
    async def wyr(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('http://www.rrrather.com/botapi') as res:
                data = await res.json()
        # data = r.json()
        e = discord.Embed(title="{}".format(data['title']), color=discord.Color.red())
        e.add_field(name="Choices", value=":red_circle: ``{}``\n:large_blue_circle: ``{}``".format(data['choicea'], data['choiceb']), inline=False)
        # e.set_footer(text="Vote below.")
        msg = await ctx.send(embed=e)
        await msg.add_reaction('🔴')
        await msg.add_reaction('🔵')

    @commands.command()
    async def joke(self, ctx):
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://icanhazdadjoke.com/slack') as res:
                data = await res.json()
        # data = json.loads(r.text)


        jokeString = ""
        for element in data['attachments']:
            for item in element['fallback']:
                jokeString += item

        await ctx.send(jokeString)
    @commands.command(aliases=['type'])
    async def typing(self, ctx):
        """Sends typing to the current channel."""
        async with ctx.channel.typing():
            await asyncio.sleep(10)
            await ctx.send('I typed as you told me to.')
    #claps command
    @commands.command()
    async def claps(self, ctx, *, text : str = None):
        """Adds :clap: to the start and the end of the message."""
        if text is None:
            await ctx.send('You did not input any text.')
            return
        await ctx.send(':clap: {} :clap:'.format(text))

    @commands.command()
    async def paper(self, ctx):
        """Plays rock, paper and scissors with paper."""
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        msg = await ctx.send('3')
        await asyncio.sleep(1)
        await msg.edit(content='2')
        await asyncio.sleep(1)
        await msg.edit(content='1')
        await asyncio.sleep(1)
        rps = random.randint(1,3)
        if rps == 1:
            await msg.edit(content='You chose paper. I chose rock. You won!')
        if rps == 2:
            await msg.edit(content='We both chose paper ._.')
        if rps == 3:
            await msg.edit(content='You chose paper. I chose scissors. I won!')

    @commands.command()
    async def rock(self, ctx):
        """Plays rock, paper and scissors with rock."""
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        msg = await ctx.send('3')
        await asyncio.sleep(1)
        await msg.edit(content='2')
        await asyncio.sleep(1)
        await msg.edit(content='1')
        await asyncio.sleep(1)
        rps = random.randint(1,3)
        if rps == 1:
            await msg.edit(content='We both chose rock :smile:')
        if rps == 2:
            await msg.edit(content='You chose rock. I chose paper. I won!')
        if rps == 3:
            await msg.edit(content='You chose rock. I chose scissors. You won!')

    @commands.command()
    async def scissors(self, ctx):
        """Plays rock, paper and scissors with scissors."""
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        msg = await ctx.send('3')
        await asyncio.sleep(1)
        await msg.edit(content='2')
        await asyncio.sleep(1)
        await msg.edit(content='1')
        await asyncio.sleep(1)
        rps = random.randint(1,3)
        if rps == 1:
            await msg.edit(content='You chose scissors. I chose rock. I won!')
        if rps == 2:
            await msg.edit(content='You chose scissors. I chose paper. You cut me in half...')
        if rps == 3:
            await msg.edit(content='We both chose scissors ._.')

    # @commands.command()
    # async def sendfile(self, ctx, *, filename: str):
    #     async with ctx.channel.typing():
    #         await ctx.send('Here you go:', file=discord.File(filename), delete_after=5.0)

    @commands.command()
    async def rr(self, ctx):
        """Gives you a random response."""
        with open('rr.txt', 'r') as f:
            r = f.readlines()
        await ctx.send(random.choice(r))

    @commands.command()
    async def addrr(self, ctx, *, text: str = None):
        """Sends a random response suggestion to the support guild."""
        if text is None:
            await ctx.send('You need to tell me what random response to add.')
            return
        if str(ctx.message.author.id) not in '282515230595219456':
            suggestions = self.bot.get_channel(468710780867575809)
            if suggestions is None:
                return
            approving = await suggestions.send('{} asked to add this to random responses:\n{}'.format(ctx.message.author.name, text))
            await approving.add_reaction('✅')
            await approving.add_reaction('❌')
            await ctx.send('I have sent a suggestion to the support guild now just wait for the owner to approve or decline.\nYou will get notified in DMs if and when it gets approved.')
            owner = await self.bot.get_user_info(282515230595219456)

            def check(reaction, user):
                return user == owner and str(reaction.emoji) in ['✅','❌']

            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check)
                if reaction.emoji == '✅':
                    with open('rr.txt', 'a+') as f:
                        f.write('\n' + text)
                        await ctx.message.author.send('Your random response got approved.')
                elif reaction.emoji == '❌':
                    await ctx.message.author.send('Sadly your random response was not approved.')
            except:
                pass
            await self.bot.delete_message(approving)
        else:
            with open('rr.txt', 'a+') as f:
                f.write('\n' + text)
            await ctx.message.add_reaction('✅')

    #bigtext command
    @commands.command()
    async def emojify(self, ctx, *, text : str = None):
        """Makes your text to emojis."""
        if ctx.message.author.bot: return
        if text is None:
            await ctx.send('You did not tell me what to convert!')
        else:
            try:
                await self.bot.delete_message(ctx.message)
            except:
                pass
            phrase = unidecode(text.lower())
            emophrase = str()
            for letter in phrase:
                if letter == '?':
                    emophrase += ':question:'
                elif letter == '!':
                    emophrase += ':exclamation:'
                elif letter == '1':
                    emophrase += ':one:'
                elif letter == '2':
                    emophrase += ':two:'
                elif letter == '3':
                    emophrase += ':three:'
                elif letter == '4':
                    emophrase += ':four:'
                elif letter == '5':
                    emophrase += ':five:'
                elif letter == '6':
                    emophrase += ':six:'
                elif letter == '7':
                    emophrase += ':seven:'
                elif letter == '8':
                    emophrase += ':eight:'
                elif letter == '9':
                    emophrase += ':nine:'
                elif letter == '0':
                    emophrase += ':zero:'
                else:
                    emophrase += letter.isalpha() and f":regional_indicator_{letter}:" or letter
            await ctx.send(emophrase)

    #Kill command
    @commands.command(no_pm = True,)
    async def kill(self, ctx, *, member: discord.Member = None):
        """Kills another member."""
        if ctx.message.author.bot: return
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        """Kills a member you specify."""
        killResponses = ["%s fell in a ditch, 'accidentally', RIP >:)", "I poisoned the food of %s... This should be fun to watch!", "I shot %s to head :gun:", "%s fell from the sky, don\'t know how :D", "%s ate soap and was toren apart from inside.", "%s disappeared. :O", "Ugh, %s is so cute I don\'t want to kill him/her."]
        if member is None:
            await ctx.send(ctx.message.author.mention + ": I can't kill someone unless you tell me who do you want me to kill!")
            return

        elif member.id == "460846291300122635":
            await ctx.send(ctx.message.author.mention + ": You can't kill me if I kill you first! :knife:")
        elif member.id == "282515230595219456":
            await ctx.send(ctx.message.author.mention + ": Why do you want me to kill my master?")
        elif member.id == ctx.message.author.id:
            await ctx.send(ctx.message.author.mention + ": Why do you want me to kill you?")
        else:
            random.seed(time.time())
            chosenResponse = killResponses[random.randrange(len(killResponses))] % member.name
            await ctx.send(ctx.message.author.mention + ": " + chosenResponse)

    #8ball command
    @commands.command(no_pm = True, aliases=['8ball', 'eightball'])
    async def eight_ball(self, ctx,*, question : str):
        """Asks a question from the magical 8ball."""
        if ctx.message.author.bot: return
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        """Answers from beyond.

        Answers to a question you put after .8ball
        """
        possible_responses = [
            'That is a resounding no',
            'It is not looking likely',
            'Too hard to tell',
            'It is quite possible',
            'Definitely',
            'Maybe',
            'It is impossible',
            'It is so scray that even the 8ball does not want to answer'
            ]
        eight_ball_embed = discord.Embed(name="", description="", colour=discord.me.top_role.color)
        eight_ball_embed.add_field(name="Question:", value="\"{}\", by {}.".format(question, ctx.message.author.nick), inline=True)
        eight_ball_embed.add_field(name="The 8-ball answers: ", value=random.choice(possible_responses) + ", " + ctx.message.author.nick, inline=True)
        await ctx.send(embed=eight_ball_embed)

    #unhug command
    @commands.command(no_pm = True)
    async def unhug(self, ctx, *, member : discord.Member = None):
        """Unhugs another member."""
        if ctx.message.author.bot: return
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        if member is None:
            await ctx.send("{} has definetely **NOT** hugged ever.".format(ctx.message.author.mention))
        elif member.id == ctx.message.author.id:
            await ctx.send("{} has definetely **NOT** hugged themselves ever.".format(ctx.message.author.mention))
        else:
            await ctx.send("{} has definetely **NOT** hugged {} ever.".format(ctx.message.author.mention, member.mention))

    @commands.command()
    async def meme(self, ctx):
        """Displays a random meme from reddit."""
        async with ctx.message.channel.typing():
            accounts = ['dankmemes', 'wholesomememes', 'meirl', 'memes', 'meme', 'dank_meme']
            async with aiohttp.ClientSession(headers={'Accept': 'application/json'}) as session:
                acc = "https://api.reddit.com/r/" + random.choice(accounts)
                async with session.get(acc) as get:
                    resp = await get.json()
                    if get.status == 404:
                        return await ctx.send(f'{ctx.tick(False)} I couldn\'t get a meme try again...')
                    posts = resp['data']['children']
                    memes = [x['data']['url'] for x in posts if 'url' in x['data']]
                    embed = discord.Embed(colour=ctx.me.top_role.color)
                    embed.set_image(url=random.choice(memes))
                    embed.set_author(name="Here is a meme for you {}.".format(ctx.message.author.name), icon_url="https://vignette.wikia.nocookie.net/chronicon/images/a/a2/Reddit-flat.png/revision/latest?cb=20170223050238")
                    embed.set_footer(text="r/{}".format(acc).replace('https://api.reddit.com/r/', '')) #thehoodmemes #https://twitter.com/search?q=thehoodmemes&src=typd
                    await ctx.send(embed=embed)

    @commands.command()
    async def coin(self, ctx):
        """Flips a coin."""
        coins = [f'{ctx.tick(True)} Heads', f'{ctx.tick(False)} Tails']
        await ctx.send(random.choice(coins))

    @commands.command()
    async def party(self, ctx):
        """Display a random party image."""
        partys =['https://media.giphy.com/media/3rgXBQIDHkFNniTNRu/giphy.gif', 'https://media.giphy.com/media/l0MYt5jPR6QX5pnqM/giphy.gif',
                'https://media.giphy.com/media/MS3XuWjQV1FiU/giphy.gif', 'https://media.giphy.com/media/xT8qAY7e9If38xkrIY/giphy.gif',
                'https://media.giphy.com/media/s2qXK8wAvkHTO/giphy.gif', 'https://media.giphy.com/media/l4pTfx2qLszoacZRS/giphy.gif',
                'https://media.giphy.com/media/YTbZzCkRQCEJa/giphy.gif', 'https://media.giphy.com/media/7vQZanyufdRe0/giphy.gif',
                'https://media.giphy.com/media/3KC2jD2QcBOSc/giphy.gif', 'https://media.giphy.com/media/10hO3rDNqqg2Xe/giphy.gif',
                'https://media.giphy.com/media/l41Yy2XyXWlSvupl6/giphy.gif', 'https://media.giphy.com/media/xUNd9HAossTNDyUUbS/giphy.gif',
                'https://media.giphy.com/media/bj09BK2BzLLQk/giphy.gif', 'https://media.giphy.com/media/AuMt534EY2Ahy/giphy.gif',
                'https://media.giphy.com/media/j3gsT2RsH9K0w/giphy.gif','https://media.giphy.com/media/jzaZ23z45UxK8/giphy.gif',
                'https://media.giphy.com/media/K9MPm9A3CaSkw/giphy.gif','https://media.giphy.com/media/XyAGm96eUIPsc/giphy.gif',
                'https://media.giphy.com/media/K9MPm9A3CaSkw/giphy.gif','https://media.giphy.com/media/Pjs1kqtH1KTaU/giphy.gif',
                'https://media.giphy.com/media/LLHkw7UnvY3Kw/giphy.gif','https://media.giphy.com/media/8rEjxb8U8XG4XmjKhY/giphy.gif']
        party = random.choice(partys)
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        embed = discord.Embed(description=':tada: Here is a party image for you {}.'.format(ctx.author.display_name), color = ctx.me.top_role.color)
        embed.set_footer(text="Requested by: {}.".format(ctx.message.author), icon_url=ctx.message.author.avatar_url)
        embed.set_image(url=party)
        await ctx.send(embed=embed)

    @commands.command()
    async def cry(self, ctx):
        """Display a random cry image."""
        cries =['https://media.giphy.com/media/OPU6wzx8JrHna/giphy.gif', 'https://media.giphy.com/media/L95W4wv8nnb9K/giphy.gif',
                'https://media.giphy.com/media/5WmyaeDDlmb1m/giphy.gif', 'https://media.giphy.com/media/4bBLOhnMb0vHG/giphy.gif',
                'https://media.giphy.com/media/MSgJnzNSMGBc6BpGIc/giphy.gif', 'https://media.giphy.com/media/Ph8OWoJA2M3eM/giphy.gif']
        cry = random.choice(cries)
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        await ctx.send()
        embed = discord.Embed(description=':cry: Here is a cry image for you {}.'.format(ctx.author.display_name), color = ctx.me.top_role.color)
        embed.set_footer(text="Requested by: {}.".format(ctx.message.author), icon_url=ctx.message.author.avatar_url)
        embed.set_image(url=cry)
        await ctx.send(embed=embed)

    @commands.command()
    async def cheer(self, ctx):
        """Displays a random cheer image."""
        cheers =['https://media.giphy.com/media/TPkLd5oec1SzS/giphy.gif', 'https://media.giphy.com/media/m8Z2UqDYU20SY/giphy.gif',
                'https://media.giphy.com/media/xUPGcFeJiX8IImdEsw/giphy.gif', 'https://media.giphy.com/media/9DnHPHLhcgEVb3981r/giphy.gif',
                'https://media.giphy.com/media/xWDomsFyDpfy2G7rpx/giphy.gif', 'https://media.giphy.com/media/3oz8xEXgWWnUXIQI4o/giphy.gif',
                'https://media.giphy.com/media/9EoQM8QF6asUg/giphy.gif', 'https://media.giphy.com/media/8Fy7FayJ6Cjja/giphy.gif',
                'https://media.giphy.com/media/3fmRTfVIKMRiM/giphy.gif','https://media.giphy.com/media/2rtQMJvhzOnRe/giphy.gif',
                'https://media.giphy.com/media/qQdL532ZANbjy/giphy.gif','https://media.giphy.com/media/KDRv3QggAjyo/giphy.gif',
                'https://media.giphy.com/media/3fmRTfVIKMRiM/giphy.gif','https://media.giphy.com/media/ldC94BvZwmiIw/giphy.gif',
                'https://media.giphy.com/media/DITaUdrnjzw4g/giphy.gif','https://media.giphy.com/media/jSfiX3lj42RDG/giphy.gif',
                'https://media.giphy.com/media/tKGFfFcHjKT9m/giphy.gif','https://media.giphy.com/media/5GoVLqeAOo6PK/giphy.gif',
                'https://media.giphy.com/media/JltOMwYmi0VrO/giphy.gif','https://media.giphy.com/media/BlVnrxJgTGsUw/giphy.gif',
                'https://media.giphy.com/media/3o8doSQ5eYzwEgaPVS/giphy.gif','https://media.giphy.com/media/14udF3WUwwGMaA/giphy.gif',
                'https://media.giphy.com/media/26vUGmwloJ19PFBkc/giphy.gif','https://media.giphy.com/media/3o7btLPD9OZCxRbiIU/giphy.gif']
        cheer = random.choice(cheers)
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        embed = discord.Embed(description=":tada: | Here is a cheer image for you {}.".format(ctx.author.display_name), color=ctx.me.top_role.color)
        embed.set_footer(text="Requested by: {}.".format(ctx.message.author), icon_url=ctx.message.author.avatar_url)
        embed.set_image(url=cheer)
        await ctx.send(embed=embed)

    @commands.command()
    async def fdance(self, ctx):
        """Displays a random fortnite dance."""
        fortnite_dances = ['https://media.giphy.com/media/1lwSiygGzLuk8cynYS/giphy.gif', 'https://media.giphy.com/media/4TrJMNlfxyg2H2nhx0/giphy.gif',
                            'https://media.giphy.com/media/pzKRxS42FLK81ZPz5C/giphy.gif', 'https://media.giphy.com/media/SG5paY6WxH6Ki2lWys/giphy.gif',
                            'https://media.giphy.com/media/fs6gcc4CxMTY5bAGyn/giphy.gif', 'https://media.giphy.com/media/1fmA4DHlleNG016sLE/giphy.gif',
                            'https://media.giphy.com/media/cNDb41n8Xv7C5j6hOO/giphy.gif', 'https://media.giphy.com/media/AhXOqQ7ts5J8Ri6V6P/giphy.gif']
        fortnite_dance = random.choice(fortnite_dances)
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        await ctx.send(":tada: | Here is a cheer Fortnite dance for you {}.".format(ctx.message.author.mention))
        embed = discord.Embed(title="", description='', color = discord.Color.green())
        embed.set_footer(text="Requested by: {}.".format(ctx.message.author), icon_url=ctx.message.author.avatar_url)
        embed.set_image(url=fortnite_dance)
        await ctx.send(embed=embed)

    @commands.command()
    async def fdrop(self, ctx):
        """Tells you where to drop in Fortnite."""
        fortnite_locations = ['Lazy Links','Dusty Divot','Fatal Fields','Flush Factory','Greasy Grove','Haunted Hills','Junk Junktion','Paradise Palms',
                            'Loot Lake','Lucky Landing','Pleasant Park','Retail Row','Risky Reels','Salty Springs','Shifty Shafts','Snobby Shores',
                            'Tilted Towers','Tomato Town','Wailing Woods']
        fortnite_location = random.choice(fortnite_locations)
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        await ctx.send(':point_right: | {} you should drop to {}.'.format(ctx.message.author.mention, fortnite_location))

    @commands.command(hidden=True)
    async def kys(self, ctx, user : discord.Member = None):
        """Tells someone to kill themselves."""
        if user is None:
            user = ctx.message.author
        await ctx.send("{}, you should kill yourself... ***Do not take this seriously***".format(user.display_name))

    @commands.command()
    async def fact(self, ctx):
        """Shows a random fact."""
        async with aiohttp.ClientSession() as cs:
            async with cs.get('https://w-bot.ml/api/fact') as r:
                r = await r.json()
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        await ctx.send('Did you know that ``{}``'.format(r['fact']))

def setup(bot):
    f = Fun(bot)
    bot.add_cog(f)
