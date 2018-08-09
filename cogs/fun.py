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
                print(reaction)
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
        eight_ball_embed = discord.Embed(name="", description="", colour=discord.Colour.green())
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

    # @commands.command()
    # async def meme(self, ctx):
    #     if ctx.message.author.bot: return
    #     """Displays a random meme."""
    #     memes =['https://i.imgur.com/hpB7qvi.png', 'https://i.imgur.com/vJ2TQwr.png',
    #             'https://i.imgur.com/m64uuhm.png', 'https://i.imgur.com/mMDZhos.png',
    #             'https://i.imgur.com/D2YNENN.png', 'https://media.giphy.com/media/aFTt8wvDtqKCQ/giphy.gif', 'https://cdn.discordapp.com/attachments/282515949318438922/462688857335398430/lataus.jpg', 'https://cdn.discordapp.com/attachments/282515949318438922/462688861588291584/VRdyI5E.jpg',
    #             'https://i.imgur.com/aNGHGzt.jpg', 'https://i.imgur.com/UWHgThx.jpg', 'https://cdn.discordapp.com/attachments/282515949318438922/462688863148572697/582aaf2853fa9.jpeg', 'https://cdn.discordapp.com/attachments/282515949318438922/462688863886770177/588fc19e69d58.jpeg', 'https://cdn.discordapp.com/attachments/282515949318438922/462688865325678593/aDx3G4B_700b.jpg', 'https://cdn.discordapp.com/attachments/282515949318438922/462688866189443094/b25.jpg',
    #             'https://cdn.discordapp.com/attachments/282515949318438922/462688869414862868/images_1.jpg','https://cdn.discordapp.com/attachments/282515949318438922/462688869389959169/eaf.png','https://cdn.discordapp.com/attachments/282515949318438922/462688871029932034/images.jpg',
    #             'https://media.giphy.com/media/3oKIPmlzy5iyOyOyzK/giphy.gif', 'https://media.giphy.com/media/26gs6vEzlpaxuYgso/giphy.gif','https://cdn.discordapp.com/attachments/290395754126770186/462676227858104330/IMG_20180518_193134.png']
    #     meme = random.choice(memes)
    #     try:
    #         await self.bot.delete_message(ctx.message)
    #     except:
    #         pass
    #     await ctx.send(':rofl: | Here is a meme for you {}.'.format(ctx.message.author.mention))
    #     embed = discord.Embed(title="", description='', color = discord.Color.green())
    #     embed.set_footer(text="Requested by: {}.".format(ctx.message.author), icon_url=ctx.message.author.avatar_url)
    #     embed.set_image(url=meme)
    #     await ctx.send(embed=embed)

    @commands.command()
    async def meme(self, ctx):
        """Displays a random meme from reddit."""
        async with ctx.message.channel.typing():
            accounts = ['dankmemes', 'wholesomememes', 'meirl', 'memes', 'meme', 'dank_meme']
            async with aiohttp.ClientSession(headers={'Accept': 'application/json'}) as session:
                acc = "https://api.reddit.com/r/" + random.choice(accounts)
                async with session.get(acc) as get:
                    resp = await get.json()
                    posts = resp['data']['children']
                    memes = [x['data']['url'] for x in posts if 'url' in x['data']]
                    embed = discord.Embed(colour=0xff6a00)
                    embed.set_image(url=random.choice(memes))
                    embed.set_author(name="Here is a meme for you {}.".format(ctx.message.author.name), icon_url="https://vignette.wikia.nocookie.net/chronicon/images/a/a2/Reddit-flat.png/revision/latest?cb=20170223050238")
                    embed.set_footer(text="r/{}".format(acc).replace('https://api.reddit.com/r/', '')) #thehoodmemes #https://twitter.com/search?q=thehoodmemes&src=typd
                    await ctx.send(embed=embed)

    @commands.command()
    async def coin(self, ctx):
        """Flips a coin."""
        coins = [':flag_ru: Heads', ':flag_us: Tails']
        await ctx.send(random.choice(coins))

    @commands.command()
    async def ping(self, ctx):
        """Sends a ping message."""
        if not ctx.message.author.bot:
            await ctx.send('I am not that kind of bot :smile:')

    @commands.command(hidden=True)
    async def pingg(self, ctx):
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        before = time.monotonic()
        message = await ctx.say("Pong!")
        ping = (time.monotonic() - before) * 1000
        await self.bot.edit_message(message, f"Pong!  `{int(ping)}ms`")
        print(f'Ping {int(ping)}ms')

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
        await ctx.send(':tada: | Here is a party image for you {}.'.format(ctx.message.author.mention))
        embed = discord.Embed(title="", description='', color = discord.Color.green())
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
        await ctx.send(':cry: | Here is a cry image for you {}.'.format(ctx.message.author.mention))
        embed = discord.Embed(title="", description='', color = discord.Color.green())
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
        await ctx.send(":tada: | Here is a cheer image for you {}.".format(ctx.message.author.mention))
        embed = discord.Embed(title="", description='', color = discord.Color.green())
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

    @commands.command()
    async def virus(self, ctx, *, user : discord.Member):
        """Sends a virus to someones system (this is not real)"""
        if user is None:
            await ctx.send(':exclamation: | {} you did not tell me who to install the virus.'.format(ctx.message.author.mention))
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass

        msg = await ctx.send(":warning: | Packing files")
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Packing files {}%".format(random.randint(1,33)))
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Packing files {}%".format(random.randint(33, 66)))
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Packing files {}%".format(random.randint(66, 99)))
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Packing files 100%")
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Obtaining IP address {}%".format(random.randint(1,33)))
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Obtaining IP address {}%".format(random.randint(33, 66)))
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Obtaining IP address {}%".format(random.randint(66, 99)))
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Obtaining IP address 100%")
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Initializing code {}%".format(random.randint(1,33)))
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Initializing code {}%".format(random.randint(33, 66)))
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Initializing code {}%".format(random.randint(66, 99)))
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Initializing code 100%")
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Installing virus {}%".format(random.randint(1,33)))
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Installing virus {}%".format(random.randint(33, 66)))
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Installing virus {}%".format(random.randint(66, 99)))
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Installing virus 100%")
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Finishing {}%".format(random.randint(1,33)))
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Finishing {}%".format(random.randint(33, 66)))
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Finishing {}%".format(random.randint(66, 99)))
        await asyncio.sleep(1)
        await msg.edit(content=":warning: | Finishing 100%")
        await asyncio.sleep(1)
        await msg.edit(content=":white_check_mark: | Virus Attack Success.\nVirus has been Installed to ***{}\'s*** system.".format(user))

    @commands.command(hidden=True)
    async def kys(self, ctx, user : discord.Member = None):
        """Tells someone to kill themselves."""
        if user is None:
            user = ctx.message.author
        await ctx.send("{} should kill themshelves... ***Do not take this seriously***".format(user.mention))

    @commands.command()
    async def fact(self, ctx):
        """Shows a random fact."""
        facts = [
        'If you somehow found a way to extract all of the gold from the bubbling core of our lovely little planet, you would be able to cover all of the land in a layer of gold up to your knees.',
        'McDonalds calls frequent buyers of their food “heavy users.”',
        'The average person spends 6 months of their lifetime waiting on a red light to turn green.',
        'The largest recorded snowflake was in Keogh, MT during year 1887, and was 15 inches wide.',
        'You burn more calories sleeping than you do watching television.',
        'There are more lifeforms living on your skin than there are people on the planet.',
        'Southern sea otters have flaps of skin under their forelegs that act as pockets. When diving, they use these pouches to store rocks and food.',
        'In 1386 a pig in France was executed by public hanging for the murder of a child.',
        'One in every five adults believe that aliens are hiding in our planet disguised as humans.',
        'If you believe that you’re truly one in a million, there are still approximately 7,184 more people out there just like you.',
        'A single cloud can weight more than 1 million pounds.',
        'A human will eat on average 70 assorted insects and 10 spiders while sleeping.',
        'James Buchanan, the 15th U.S. president continuously bought slaves with his own money in order to free them.',
        'There are more possible iterations of a game of chess than there are atoms in the known universe.',
        'The average person walks the equivalent of three times around the world in a lifetime.',
        'Men are 6 times more likely to be struck by lightning than women.',
        'Coca-Cola would be green if coloring wasn’t added to it.',
        'You cannot snore and dream at the same time.',
        'The world’s oldest piece of chewing gum is over 9,000 years old!',
        'A coyote can hear a mouse moving underneath a foot of snow.',
        'Bolts of lightning can shoot out of an erupting volcano.',
        'New York drifts about one inch farther away from London each year.',
        'A U.S. dollar bill can be folded approximately 4,000 times in the same place before it will tear.',
        'A sneeze travels about 100 miles per hour.',
        'Earth has traveled more than 5,000 miles in the past 5 minutes.',
        'It would take a sloth one month to travel one mile.',
        '10% of the World’s population is left handed.',
        'A broken clock is right two times every day.',
        'According to Amazon, the most highlighted books on Kindle are the Bible, the Steve Jobs biography, and The Hunger Games.',
        'Bob Marley’s last words to his son before he died were “Money can’t buy life.”',
        'A mole can dig a tunnel that is 300 feet long in only one night.',
        'A hippo’s wide open mouth is big enough to fit a 4-foot-tall child in.',
        'Chewing gum while you cut an onion will help keep you from crying.',
        'If you were to stretch a Slinky out until it’s flat, it would measure 87 feet long.',
        'Al Capone’s business card said he was a used furniture dealer',
        'There are more collect calls on Father’s Day than on any other day of the year.',
        'Banging your head against a wall burns 150 calories an hour.',
        '95% of people text things they could never say in person.',
        'A crocodile can’t poke its tongue out.',
        'It is physically impossible for pigs to look up into the sky.',
        'Guinness Book of Records holds the record for being the book most often stolen from Public Libraries.',
        'Drying fruit depletes it of 30-80% of its vitamin and antioxidant content',
        'Drying fruit depletes it of 30-80% of its vitamin and antioxidant content',
        '9 out of 10 Americans are deficient in Potassium.',
        'Blueberries will not ripen until they are picked.',
        'About 150 people per year are killed by coconuts.',
        'Ketchup was used as a medicine back in the 1930’s.',
        'Honey never spoils.',
        'About half of all Americans are on a diet on any given day.',
        'A hardboiled egg will spin, but a soft-boiled egg will not.',
        'Avocados are poisonous to birds.',
        'Chewing gum burns about 11 calories per hour.',
        'The number of animals killed for meat every hour in the U.S. is 500,000.',
        'If you try to suppress a sneeze, you can rupture a blood vessel in your head or neck and die.',
        'Celery has negative calories! It takes more calories to eat a piece of celery than the celery has in it to begin with. It’s the same with apples!'
        ,'More people are allergic to cow’s milk than any other food.',
        'Only 8% of dieters will follow a restrictive weight loss plan (such as hCG Drops diet, garcinia cambogia diet, etc.)',
        'Coconut water can be used as blood plasma.',
        'The word “gorilla” is derived from a Greek word meaning, “A tribe of hairy women.”',
        'Prisoners in Canadian war camps during WWII were treated so well, that a lot of them didn’t’ want to leave when the war was over.',
        'Gorillas burp when they are happy',
        'In New York, it is illegal to sell a haunted house without telling the buyer.',
        'In 2006 someone tried to sell New Zealand on eBay. The price got up to $3,000 before eBay shut it down.'
        'It is considered good luck in Japan when a sumo wrestler makes your baby cry.',
        'A man from Britain changed his name to Tim Pppppppppprice to make it harder for telemarketers to pronounce.',
        'A woman from California once tried to sue the makers of Cap’n Crunch, because the Crunch Berries contained “no berries of any kind.”',
        'Apple launched a clothing line in 1986. It was described as a “train wreck” by others.',
        'In Japan, crooked teeth are considered cute and attractive.',
        'A Swedish woman lost her wedding ring, and found it 16 years later- growing on a carrot in her garden.',
        'Donald duck comics were banned from Finland because he doesn’t wear pants.',
        'The chance of you dying on the way to get lottery tickets is actually greater than your chance of winning.',
        'Cherophobia is the fear of fun.',
        'The toothpaste “Colgate” in Spanish translates to “go hang yourself”',
        'Pirates wore earrings because they believed it improved their eyesight.',
        'Human thigh bones are stronger than concrete.',
        'Cockroaches can live for several weeks with their heads cut off, because their brains are located inside their body. They would eventually die from being unable to eat.',
        'Scientists have tracked butterflies that travel over 3,000 miles.',
        'To produce a single pound of honey, a single bee would have to visit 2 million flowers.',
        'The population is expected to rise to 10.8 billion by the year 2080.',
        'You breathe on average about 8,409,600 times a year',
        'More than 60,000 people are flying over the United States in an airplane right now.',
        'Hamsters run up to 8 miles at night on a wheel.',
        'A waterfall in Hawaii goes up sometimes instead of down.',
        'A church in the Czech Republic has a chandelier made entirely of human bones.',
        'Under the Code of Hammurabi, bartenders who watered down beer were punished by execution.',
        'Our eyes are always the same size from birth, but our nose and ears never stop growing.',
        'During your lifetime, you will produce enough saliva to fill two swimming pools.',
        'You are 1% shorter in the evening than in the morning',
        'The elephant is the only mammal that can’t jump!',
        'Most dust particles in your house are made from dead skin!',
        'If 33 million people held hands, they could make it all the way around the equator.',
        'Earth is the only planet that is not named after a god.',
        'The bloodhound is the only animal whose evidence is admissible in court.',
        'You are born with 300 bones, but by the time you are an adult you only have 206.',
        'A ten-gallon hat will only hold ¾ of a gallon.',
        'Just like fingerprints, everyone has different tongue prints.',
        'ATM’s were originally thought to be failures, because the only users were prostitutes and gamblers who didn’t want to deal with tellers face to face.',
        'Of all the words in the English language, the word “set” has the most definitions. The word “run” comes in close second.',
        'A “jiffy” is the scientific name for 1/100th of a second.',
        'One fourth of the bones in your body are located in your feet',
        '111,111,111 X 111,111,111 = 12,345,678,987,654,321',
        'Blue-eyed people tend to have the highest tolerance of alcohol.',
        'A traffic jam lasted for more than 10 days, with cars only moving 0.6 miles a day.',
        'The tongue is the strongest muscle in the body.',
        'Every year more than 2500 left-handed people are killed from using right-handed products.',
        'More than 50% of the people in the world have never made or received a telephone call.',
        'The cigarette lighter was invented before the match.',
        'Sea otters hold hands when they sleep so that they do not drift apart.',
        'The Golden Poison Dart Frog’s skin has enough toxins to kill 100 people.'
        ,'The male ostrich can roar just like a lion.',
        'Mountain lions can whistle.',
        'The giraffe’s tongue is so long that they can lick the inside of their own ear.',
        'Cows kill more people than sharks do.',
        'Cats have 32 muscles in each of their ears.',
        'Butterflies taste their food with their feet.',
        'A tarantula can live without food for more than two years.',
        'The tongue of a blue whale weighs more than most elephants!',
        'Ever wonder where the phrase “It’s raining cats and dogs” comes from? In the 17th century many homeless cats and dogs would drown and float down the streets of England, making it look like it literally rained cats and dogs.',
        'It takes about 3,000 cows to supply enough leather for the NFL for only one year.',
        'Male dogs lift their legs when they are urinating for a reason. They are trying to leave their mark higher so that it gives off the message that they are tall and intimidating.',
        'A hummingbird weighs less than a penny.',
        'An ostrich’s eye is bigger than its brain',
        'Dogs are capable of understanding up to 250 words and gestures and have demonstrated the ability to do simple mathematical calculations.',
        'A sheep, a duck and a rooster were the first passengers in a hot air balloon.',
        'Birds don’t urinate.',
        'A flea can jump up to 200 times its own height. That is the equivalent of a human jumping the Empire State Building.',
        'There are 5 temples in Kyoto, Japan that have blood stained ceilings. The ceilings are made from the floorboards of a castle where warriors killed themselves after a long hold-off against an army. To this day, you can still see the outlines and footprints.',
        'There is a snake, called the boomslang, whose venom causes you to bleed out from every orifice on your body. You may even turn blue from internal bleeding, and it can take up to 5 days to die from the bleeding.',
        'A ball of glass will bounce higher than a ball of rubber.',
        'Saturn’s density is low enough that the planet would float in water.',
        '68% of the universe is dark energy, and 27% is dark matter; both are invisible, even with our powerful telescopes. This means we have only seen 5% of the universe from earth.',
        'The founders of Google were willing to sell Google for $1 million to Excite in 1999, but Excite turned them down. Google is now worth $527 Billion.',
        'In the past 20 years, scientists have found over 1,000 planets outside of our solar system.',
        'There are 60,000 miles of blood vessels in the human body.',
        'If a pregnant woman has organ damage, the baby in her womb sends stem cells to help repair the organ.',
        'If you started with $0.01 and doubled your money every day, it would take 27 days to become a millionaire.',
        'Only one person in two billion will live to be 116 or older.',
        'A person can live without food for about a month, but only about a week without water. If the amount of water in your body is reduced by just 1%, you’ll feel thirsty. If it’s reduced by 10%, you’ll die.',
        'On average, 12 newborns will be given to the wrong parents daily.',
        'You can’t kill yourself by holding your breath.',
        'Human birth control pills work on gorillas.',
        'There are no clocks in Las Vegas gambling casinos.',
        'Beetles taste like apples, wasps like pine nuts, and worms like fried bacon.',
        'What is called a “French kiss” in the English-speaking world is known as an “English kiss” in France.',
        'Months that begin on a Sunday will always have a “Friday the 13th.”',
        'The placement of a donkey’s eyes in its’ heads enables it to see all four feet at all times!',
        'Some worms will eat themselves if they can’t find any food!',
        'Dolphins sleep with one eye open!',
        'It is impossible to sneeze with your eyes open.',
        'In France, it is legal to marry a dead person.',
        'Russia has a larger surface area than Pluto.',
        'There’s an opera house on the U.S.–Canada border where the stage is in one country and half the audience is in another.',
        'The harder you concentrate on falling asleep, the less likely to fall asleep.',
        'You can’t hum while holding your nose closed.',
        'Women have twice as many pain receptors on their body than men. But a much higher pain tolerance.',
        'There are more stars in space than there are grains of sand on every beach in the world.',
        'For every human on Earth there are 1.6 million ants. The total weight of all those ants, however, is about the same as all the humans.',
        'On Jupiter and Saturn it rains diamonds.'
        ]
        try:
            await self.bot.delete_message(ctx.message)
        except:
            pass
        await ctx.send('Did you know that ``{}``'.format(random.choice(facts)))
        def pred(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel

        ans = await self.bot.wait_for('message', timeout=20.0, check=pred)
        try:
            if ans.content == 'no':
                await ctx.send('Well now you do!')
        except asyncio.TimeoutError:
            pass

def setup(bot):
    f = Fun(bot)
    bot.add_cog(f)
