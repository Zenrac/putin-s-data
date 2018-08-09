import discord
from discord.ext import commands
import asyncio

class Help():
    def __init__(self, bot):
        self.bot = bot

    @commands.group(pass_context = True)
    async def help(self, ctx):
        if ctx.message.author.bot: return
        if ctx.invoked_subcommand is None:
            try:
                await ctx.message.delete()
            except:
                pass
            msg = await ctx.send('<a:dblspin:393548363879940108> Loading\.\.\.')
            await msg.add_reaction('❌')
            await msg.add_reaction('😆')
            await msg.add_reaction('✍')
            await msg.add_reaction('🛡')
            await msg.add_reaction('🔢')
            await msg.add_reaction('🎵')
            await msg.add_reaction('🔡')
            await msg.add_reaction('🔎')
            await msg.add_reaction('👫')
            await msg.add_reaction('❓')
            embed = discord.Embed(title="Prefix = \".\"", description="Use \".help (command category)\" for more information.", color=discord.Color.gold())
            embed.add_field(name=":laughing: Fun:", value="``ohno``, ``tweet``, ``bigtext``, ``cat``, ``cheer``, ``cry``, ``dog``, ``8ball``, ``fdance``, ``fdrop``, ``hug``, ``kill``, ``bigtext``, ``meme``, ``party``, ``virus``, ``poke``, ``glitch``, ``graffiti``, ``groovy``, ``hanging``, ``fact``, ``rps rock``, ``rps paper``, ``rps scisors``, ``reddit``, ``addpoke``, ``rr``, ``addrr``", inline=True)
            embed.add_field(name=":writing_hand: Meta:", value="``encode``, ``decode``, ``poll``, ``about``, ``botpermissions``, ``info``, ``invite``, ``permissions``, ``remind``, ``serverleave``, ``uptime``, ``suggest command``, ``suggest song``, ``dbl``, ``translate``, ``detect``", inline=True)
            embed.add_field(name=":shield: Mod:", value="``ban``, ``deafen``, ``ignore``, ``kick``, ``mute``, ``purge``, ``purge all``, ``purge user``, ``purge embeds``, ``purge images``, ``purge files``, ``purge contains`` , ``setnickname``, ``softban``, ``undeafen``, ``unignore``, ``unmute``, ``editchannelname``, ``setprefix``, ``enablelogging``, ``disablelogging``, ``link``, ``unlink``", inline=True)
            embed.add_field(name=":1234: RNG:", value="``choose``, ``number``, ``lenny``", inline=True)
            embed.add_field(name=":capital_abcd: Tag:", value="``tag``, ``tag create``, ``tag make``, ``tag stats``, ``tag edit``, ``tag remove``, ``tag info``, ``tag list``, ``tag search``", inline=True)
            embed.add_field(name=":musical_note: Music: (Prefix = \"-.\")", value="``summon``, ``play``, ``np``, ``resume``, ``skip``, ``queue``, ``shuffle``, ``search <yt/sc/yh>``, ``remove``, ``pldump``, ``stream``, ``lyrics``", inline=True)
            embed.add_field(name=":mag_right: Search:", value="``imgur random``, ``imgur search``, ``gif``, ``gifr``, ``define``", inline=True)
            embed.add_field(name=":couple: Profile:", value="``profile``, ``buy <pick/ring/diamond/rose/alcohol>``, ``sell <pick/ring/diamond/rose/alcohol>``, ``itemtransfer <pick/ring/diamond/rose/alcohol>``, ``moneytransfer``, ``daily``, ``loot``, ``mine``, ``slots``, ``market``, ``profile description``, ``profile birthday``, ``marry``, ``divorce``, ``drink``", inline=True)
            await msg.edit(content='DONE', embed=embed)
            def check(reaction, user):
                return user == ctx.message.author and str(reaction.emoji) in ['❌','😆','✍','🛡','🔢','🎵','🔡','🔎','👫', '❓']
            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check)
                print(reaction.emoji)
                if reaction.emoji == '❌':
                    print('added emoji')
                    await msg.delete()
                elif reaction.emoji == '😆':
                    await msg.delete()
                    await ctx.invoke(self.fun)
                elif reaction.emoji == '✍':
                    await msg.delete()
                    await ctx.invoke(self.meta)
                elif reaction.emoji == '🛡':
                    await msg.delete()
                    await ctx.invoke(self.mod)
                elif reaction.emoji == '🔢':
                    await msg.delete()
                    await ctx.invoke(self.rng)
                elif reaction.emoji == '🎵':
                    await msg.delete()
                    await ctx.invoke(self.music)
                elif reaction.emoji == '🔡':
                    await msg.delete()
                    await ctx.invoke(self.tag)
                elif reaction.emoji == '🔎':
                    await msg.delete()
                    await ctx.invoke(self.search)
                elif reaction.emoji == '👫':
                    await msg.delete()
                    await ctx.invoke(self.profile)
                elif reaction.emoji == '❓':
                    await msg.delete()
                    await ctx.invoke(self.help)
                if res is None:
                    await msg.delete()
            except:
                pass

    @help.command(pass_context = True)
    async def profile(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass
        msg = await ctx.send('<a:dblspin:393548363879940108> Loading\.\.\.')
        await msg.add_reaction('❌')
        await msg.add_reaction('😆')
        await msg.add_reaction('✍')
        await msg.add_reaction('🛡')
        await msg.add_reaction('🔢')
        await msg.add_reaction('🎵')
        await msg.add_reaction('🔡')
        await msg.add_reaction('🔎')
        await msg.add_reaction('👫')
        await msg.add_reaction('❓')
        embed = discord.Embed(title="Prefix = \".\"", description="Profile commands:", color=discord.Color.gold())
        embed.add_field(name="Commands:", value="``profile``, ``buy``, ``sell``, ``itemtransfer``, ``moneytransfer``, ``marry``, ``divorce``,``daily``, ``loot``, ``mine``, ``slots``, ``drink``", inline=True)
        embed.add_field(name=":one: profile: Shows your or a user's you mention profile or creates a profile for you.", value="Usage: ``profile [member]``", inline=False)
        embed.add_field(name=":two: buy (pick/ring/diamond): Buys a pickaxe, ring or diamond.", value="Usage: ``buy <pick/ring/diamond/rose/alcohol> [amount]``", inline=False)
        embed.add_field(name=":three: sell (pick/ring/diamond): Sells a pickaxe, ring or diamond.", value="Usage: ``sell <pick/ring/diamond/rose/alcohol> [amount]``", inline=False)
        embed.add_field(name=":four: itemtransfer: Transfers a item of your choice to a user.", value="Usage: ``itemtransfer <pick/ring/diamond/rose/alcohol> <user>``", inline=False)
        embed.add_field(name=":five: moneytransfer: Gives an amount of your choice from your money and gives to a user of you choice.", value="Usage: ``moneytransfer <amount> <user>``", inline=False)
        embed.add_field(name=":six: daily: Collects your daily cash.", value="Usage: ``daily``", inline=False)
        embed.add_field(name=":seven: loot: Collects random amount of cash", value="Usage: ``loot``", inline=False)
        embed.add_field(name=":eight: mine: Mines a random amount of cash.", value="Usage: ``mine``", inline=False)
        embed.add_field(name=":nine: slots: Plays slot machine.", value="Usage: ``daily``", inline=False)
        embed.add_field(name=":one::zero: market: Shows item buy and sell price.", value="Usage: ``market``", inline=False)
        embed.add_field(name=":one::zero: profile description: Changes your description.", value="Usage: ``profile description <text>``", inline=False)
        embed.add_field(name=":one::zero: profile birthday: Changes your birhtday.", value="Usage: ``profile birthday <DD-MM-YYYY>``", inline=False)
        embed.add_field(name=":one::one: marry: Marries a user.", value="Usage: ``marry <user>``", inline=False)
        embed.add_field(name=":one::two: divorce: Divorces with user.", value="Usage: ``divorce <user>``", inline=False)
        embed.add_field(name=":one::three: drink: Drinks alcohol.", value="Usage: ``drink``", inline=False)
        await msg.edit(content='DONE', embed=embed)
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ['❌','😆','✍','🛡','🔢','🎵','🔡','🔎','👫', '❓']
        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check)
            print(reaction.emoji)
            if reaction.emoji == '❌':
                print('added emoji')
                await msg.delete()
            elif reaction.emoji == '😆':
                await msg.delete()
                await ctx.invoke(self.fun)
            elif reaction.emoji == '✍':
                await msg.delete()
                await ctx.invoke(self.meta)
            elif reaction.emoji == '🛡':
                await msg.delete()
                await ctx.invoke(self.mod)
            elif reaction.emoji == '🔢':
                await msg.delete()
                await ctx.invoke(self.rng)
            elif reaction.emoji == '🎵':
                await msg.delete()
                await ctx.invoke(self.music)
            elif reaction.emoji == '🔡':
                await msg.delete()
                await ctx.invoke(self.tag)
            elif reaction.emoji == '🔎':
                await msg.delete()
                await ctx.invoke(self.search)
            elif reaction.emoji == '👫':
                await msg.delete()
                await ctx.invoke(self.profile)
            elif reaction.emoji == '❓':
                await msg.delete()
                await ctx.invoke(self.help)
            if res is None:
                await msg.delete()
        except:
            pass

    @help.command(pass_context = True)
    async def fun(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass
        msg = await ctx.send('<a:dblspin:393548363879940108> Loading\.\.\.')
        await msg.add_reaction('❌')
        await msg.add_reaction('😆')
        await msg.add_reaction('✍')
        await msg.add_reaction('🛡')
        await msg.add_reaction('🔢')
        await msg.add_reaction('🎵')
        await msg.add_reaction('🔡')
        await msg.add_reaction('🔎')
        await msg.add_reaction('👫')
        await msg.add_reaction('❓')
        embed = discord.Embed(title="Prefix = \".\"", description="Fun commands:", color=discord.Color.gold())
        embed.add_field(name="Commands:", value="``cat``, ``cheer``, ``cry``, ``dog``, ``8ball``, ``fdance``, ``fdrop``, ``hug``, ``kill``, ``meme``, ``party``, ``virus``", inline=True)
        embed.add_field(name=":one: cat: Displays a random cat image.", value="Usage: ``cat``", inline=False)
        embed.add_field(name=":two: tweet: Displays a tweet image of your text choice.", value="Usage: ``tweet <text max 40>``", inline=False)
        embed.add_field(name=":three: cheer: Displays a random cheer image.", value="Usage: ``cheer``", inline=False)
        embed.add_field(name=":four: cry: Displays a random cry image.", value="Usage: ``cry``", inline=False)
        embed.add_field(name=":five: dog: Displays a random dog image.", value="Usage: ``dog``", inline=False)
        embed.add_field(name=":six: 8ball: Answers from beyond.", value="Usage: ``8ball <text>``", inline=False)
        embed.add_field(name=":seven: fdance: Displays a random Fortnite dance.", value="Usage: ``fdance``", inline=False)
        embed.add_field(name=":eight: fdrop: Tells you where to drop in Fortnite.", value="Usage: ``fdrop``", inline=False)
        embed.add_field(name=":nine: hug: Hugs someone you mention.", value="Usage: ``hug [uzer]``", inline=False)
        embed.add_field(name=":one::zero: kill: Kills a member you specify.", value="Usage: ``kill <user>``", inline=False)
        embed.add_field(name=":one::one: bigtext: Try it and see!", value="Usage: ``bigtext <text>``", inline=False)
        embed.add_field(name=":one::two: meme: Displays a random meme.", value="Usage: ``meme``", inline=False)
        embed.add_field(name=":one::three: party: Displays a random party image.", value="Usage: ``party``", inline=False)
        embed.add_field(name=":one::four: virus: Sends a virus to someone\'s system. (This is not real!)", value="Usage: ``virus <user>``", inline=False)
        embed.add_field(name=":one::five: poke: Pokes a user of your choice.", value="Usage: ``poke [user]``", inline=False)
        embed.add_field(name=":one::six: ohno: Makes a dog say what you tell.", value="Usage: ``ohno <text>``", inline=False)
        embed.add_field(name=":one::seven: glitch: Makes a picture of your text with custom font.", value="Usage: ``glitch <text>``", inline=False)
        embed.add_field(name=":one::eight: graffiti:Makes a picture of your text with custom font.", value="Usage: ``graffiti <text>``", inline=False)
        embed.add_field(name=":one::nine: groovy: Makes a picture of your text with custom font.", value="Usage: ``groovy <text>``", inline=False)
        embed.add_field(name=":two::zero: hanging: Makes a picture of your text with custom font.", value="Usage: ``hanging <text>``", inline=False)
        embed.add_field(name=":two::one: fact: Tells you a random fact.", value="Usage: ``fact``", inline=False)
        embed.add_field(name=":two::two: rps rock: Plays rock paper scissors with rock.", value="Usage: ``rps rock``", inline=False)
        embed.add_field(name=":two::three: rps paper: Plays rock paper scissors with paper.", value="Usage: ``rps paper``", inline=False)
        embed.add_field(name=":two::four: rps scissors: Plays rock paper scissors with scissors.", value="Usage: ``rps scissors``", inline=False)
        embed.add_field(name=":two::five: reddit: Displays a random meme from reddit.", value="Usage: ``reddit``", inline=False)
        embed.add_field(name=":two::six: addpoke: sends a suggest to the owner.", value="Usage: ``addpoke <url>``", inline=False)
        await msg.edit(content='DONE', embed=embed)
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ['❌','😆','✍','🛡','🔢','🎵','🔡','🔎','👫', '❓']
        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check)
            print(reaction.emoji)
            if reaction.emoji == '❌':
                print('added emoji')
                await msg.delete()
            elif reaction.emoji == '😆':
                await msg.delete()
                await ctx.invoke(self.fun)
            elif reaction.emoji == '✍':
                await msg.delete()
                await ctx.invoke(self.meta)
            elif reaction.emoji == '🛡':
                await msg.delete()
                await ctx.invoke(self.mod)
            elif reaction.emoji == '🔢':
                await msg.delete()
                await ctx.invoke(self.rng)
            elif reaction.emoji == '🎵':
                await msg.delete()
                await ctx.invoke(self.music)
            elif reaction.emoji == '🔡':
                await msg.delete()
                await ctx.invoke(self.tag)
            elif reaction.emoji == '🔎':
                await msg.delete()
                await ctx.invoke(self.search)
            elif reaction.emoji == '👫':
                await msg.delete()
                await ctx.invoke(self.profile)
            elif reaction.emoji == '❓':
                await msg.delete()
                await ctx.invoke(self.help)
            if res is None:
                await msg.delete()
        except:
            pass

    @help.command(pass_context = True)
    async def meta(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass
        msg = await ctx.send('<a:dblspin:393548363879940108> Loading\.\.\.')
        await msg.add_reaction('❌')
        await msg.add_reaction('😆')
        await msg.add_reaction('✍')
        await msg.add_reaction('🛡')
        await msg.add_reaction('🔢')
        await msg.add_reaction('🎵')
        await msg.add_reaction('🔡')
        await msg.add_reaction('🔎')
        await msg.add_reaction('👫')
        await msg.add_reaction('❓')
        embed = discord.Embed(title=":writing_hand: Prefix = \".\"", description="Meta commands:", color=discord.Color.gold())
        embed.add_field(name="Commands:", value="``about``, ``botpermissions``, ``poll``, ``info``, ``invite``, ``permissions``, ``uptime``, ``suggest command``, ``suggest song``, ``rate``, ``dbl``, ``remind``, ``translate``, ``detect``", inline=True)
        embed.add_field(name=":one: about: Tells you information about the bot itself.", value="Usage: ``about``", inline=False)
        embed.add_field(name=":two: botpermissions: Shows the bot's permissions.", value="Usage: ``botpermissions``", inline=False)
        embed.add_field(name=":three: poll: Makes a poll.", value="Usage: ``poll <text>``", inline=False)
        embed.add_field(name=":four: info: Gives info about a user.", value="Usage: ``info <user>``", inline=False)
        embed.add_field(name=":five: invite: Gives you a invite link to this server.", value="Usage: ``invite``", inline=False)
        embed.add_field(name=":six: permissions: Shows a member's permissions.", value="Usage: ``permissions <user>``", inline=False)
        embed.add_field(name=":eight: uptime: Tells you how long the bot has been online.", value="Usage: ``uptime``", inline=False)
        embed.add_field(name=":nine: ``suggest command``: Sends a message to #suggestions at support server.", value="Usage: ``suggest command <text>``", inline=False)
        embed.add_field(name=":one::zero: ``suggest song``: Sends a message to #suggestions at support server.", value="Usage: ``suggest song <text>``", inline=False)
        embed.add_field(name=":one::one: rate: Makes a rate poll.", value="Usage: ``rate <reaction amount> <text>``", inline=False)
        embed.add_field(name=":one::two: dbl: Gets a bot\'s info from discordbots.org.", value="Usage: ``dbl [bot]``", inline=False)
        embed.add_field(name=":one::three: remind:Reminds you about what you want after a certain amount of time.", value="Usage: ``remmind <time e.g. 1s2m3h> [text]``", inline=False)
        embed.add_field(name=":one::four: translate: Translates text from language to another.", value="Usage: ``translate <from> <to> <text>``", inline=False)
        embed.add_field(name=":one::five: detect: Detects what language are you typing on.", value="Usage: ``detect <text>``", inline=False)
        await msg.edit(content='DONE', embed=embed)
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ['❌','😆','✍','🛡','🔢','🎵','🔡','🔎','👫', '❓']
        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check)
            print(reaction.emoji)
            if reaction.emoji == '❌':
                print('added emoji')
                await msg.delete()
            elif reaction.emoji == '😆':
                await msg.delete()
                await ctx.invoke(self.fun)
            elif reaction.emoji == '✍':
                await msg.delete()
                await ctx.invoke(self.meta)
            elif reaction.emoji == '🛡':
                await msg.delete()
                await ctx.invoke(self.mod)
            elif reaction.emoji == '🔢':
                await msg.delete()
                await ctx.invoke(self.rng)
            elif reaction.emoji == '🎵':
                await msg.delete()
                await ctx.invoke(self.music)
            elif reaction.emoji == '🔡':
                await msg.delete()
                await ctx.invoke(self.tag)
            elif reaction.emoji == '🔎':
                await msg.delete()
                await ctx.invoke(self.search)
            elif reaction.emoji == '👫':
                await msg.delete()
                await ctx.invoke(self.profile)
            elif reaction.emoji == '❓':
                await msg.delete()
                await ctx.invoke(self.help)
            if res is None:
                await msg.delete()
        except:
            pass

    @help.command(pass_context = True)
    async def mod(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass
        msg = await ctx.send('<a:dblspin:393548363879940108> Loading\.\.\.')
        await msg.add_reaction('❌')
        await msg.add_reaction('😆')
        await msg.add_reaction('✍')
        await msg.add_reaction('🛡')
        await msg.add_reaction('🔢')
        await msg.add_reaction('🎵')
        await msg.add_reaction('🔡')
        await msg.add_reaction('🔎')
        await msg.add_reaction('👫')
        await msg.add_reaction('❓')
        embed = discord.Embed(title=":shield: Prefix = \".\"", description="Mod commads:", color=discord.Color.gold())
        embed.add_field(name="Commands:", value="``Ban``, ``cleanup``, ``deafen``, ``ignore``, ``kick``, ``mute``, ``purge embeds``, ``purge files``, ``purge images``, ``purge all``, ``purge user``, ``purge contains``, ``setnickname``, ``editchannelname``, ``softban``, ``undeafen``, ``unignore``, ``setprefix``", inline=True)
        embed.add_field(name=":one: ban: Bans a member from the server.", value="Usage: ``ban <user>``", inline=False)
        embed.add_field(name=":two: cleanup: Cleans up the bot's messages from the channel.", value="Usage: ``cleanup``", inline=False)
        embed.add_field(name=":four: deafen: Deafens a user.", value="Usage: ``deafen <user>``", inline=False)
        embed.add_field(name=":five: ignore: Handles the bot's ignore lists.", value="Usage: ``ingore <channel>``", inline=False)
        embed.add_field(name=":six: kick: Kicks a member from the server.", value="Usage: ``kick <user>``", inline=False)
        embed.add_field(name=":seven: mute: Mutes a user.", value="Usage: ``mute <user>``", inline=False)
        embed.add_field(name=":nine: purge embeds: Removes messages that meet a criteria.", value="Usage: ``purge embeds``", inline=False)
        embed.add_field(name=":one::zero: purge files: Removes messages that meet a criteria.", value="Usage: ``purge files``", inline=False)
        embed.add_field(name=":one::one: purge images: Removes messages that meet a criteria.", value="Usage: ``purge images``", inline=False)
        embed.add_field(name=":one::two: purge all: Removes messages that meet a criteria.", value="Usage: ``purge all``", inline=False)
        embed.add_field(name=":one::three: purge user: Removes messages that meet a criteria.", value="Usage: ``purge user <user>``", inline=False)
        embed.add_field(name=":one::four: purge contains: Removes messages that meet a criteria.", value="Usage: ``purge contains <text>``", inline=False)
        embed.add_field(name=":one::five: setnickname: Changes the nickname of a user.", value="Usage: ``setnicname <user> <nicname>``", inline=False)
        embed.add_field(name=":one::six: editchannelname: Changes the name of current text channel.", value="Usage: ``editchannelname <channel> <name>``", inline=False)
        embed.add_field(name=":one::seven: softban: Soft bans a member from the server.", value="Usage: ``softban <user>``", inline=False)
        embed.add_field(name=":one::eight: undeafen: Undeafens a user.", value="Usage: ``undeafen <user>``", inline=False)
        embed.add_field(name=":one::nine: unignore: Unignores a specific channel from being processed.", value="Usage: ``unignore [channel]``", inline=False)
        embed.add_field(name=":two::zero: unmute: Unmutes a user.", value="Usage: ``unmute <user>``", inline=False)
        embed.add_field(name=":two::one: setprefix: Sets a server prefix. This may be resetted. If it has been resetted, assign it again.", value="Usage: ``setprefix <prefix>``", inline=False)
        embed.add_field(name=":two::two: enablelogging: Sets a channel to send all the logging from this server.", value="Usage: ``enablelogging <channel>``", inline=False)
        embed.add_field(name=":two::three: setprefix: Stops sending logging messages on this server.", value="Usage: ``disablelogging``", inline=False)
        embed.add_field(name=":two::four: link: Links a channel to another.", value="Usage: ``link <channel id>``", inline=False)
        embed.add_field(name=":two::five: unlink: Unlinks a channel from another.", value="Usage: ``unlink``", inline=False)
        await msg.edit(content='DONE', embed=embed)
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ['❌','😆','✍','🛡','🔢','🎵','🔡','🔎','👫', '❓']
        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check)
            print(reaction.emoji)
            if reaction.emoji == '❌':
                print('added emoji')
                await msg.delete()
            elif reaction.emoji == '😆':
                await msg.delete()
                await ctx.invoke(self.fun)
            elif reaction.emoji == '✍':
                await msg.delete()
                await ctx.invoke(self.meta)
            elif reaction.emoji == '🛡':
                await msg.delete()
                await ctx.invoke(self.mod)
            elif reaction.emoji == '🔢':
                await msg.delete()
                await ctx.invoke(self.rng)
            elif reaction.emoji == '🎵':
                await msg.delete()
                await ctx.invoke(self.music)
            elif reaction.emoji == '🔡':
                await msg.delete()
                await ctx.invoke(self.tag)
            elif reaction.emoji == '🔎':
                await msg.delete()
                await ctx.invoke(self.search)
            elif reaction.emoji == '👫':
                await msg.delete()
                await ctx.invoke(self.profile)
            elif reaction.emoji == '❓':
                await msg.delete()
                await ctx.invoke(self.help)
            if res is None:
                await msg.delete()
        except:
            pass

    @help.command(pass_context = True)
    async def rng(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass
        msg = await ctx.send('<a:dblspin:393548363879940108> Loading\.\.\.')
        await msg.add_reaction('❌')
        await msg.add_reaction('😆')
        await msg.add_reaction('✍')
        await msg.add_reaction('🛡')
        await msg.add_reaction('🔢')
        await msg.add_reaction('🎵')
        await msg.add_reaction('🔡')
        await msg.add_reaction('🔎')
        await msg.add_reaction('👫')
        await msg.add_reaction('❓')
        embed = discord.Embed(title=":1234: Prefix = \".\"", description="RNG commands:", color=discord.Color.gold())
        embed.add_field(name=":one: choose: Chooses between multiple choices.", value="Usage: ``choose <choices separated with spaces>``", inline=False)
        embed.add_field(name=":three: random lenny: Displays a random lenny.", value="Usage: ``random lenny``", inline=False)
        embed.add_field(name=":four: random number: Displays a random number.", value="Usage: ``random number``", inline=False)
        await msg.edit(content='DONE', embed=embed)
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ['❌','😆','✍','🛡','🔢','🎵','🔡','🔎','👫', '❓']
        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check)
            print(reaction.emoji)
            if reaction.emoji == '❌':
                print('added emoji')
                await msg.delete()
            elif reaction.emoji == '😆':
                await msg.delete()
                await ctx.invoke(self.fun)
            elif reaction.emoji == '✍':
                await msg.delete()
                await ctx.invoke(self.meta)
            elif reaction.emoji == '🛡':
                await msg.delete()
                await ctx.invoke(self.mod)
            elif reaction.emoji == '🔢':
                await msg.delete()
                await ctx.invoke(self.rng)
            elif reaction.emoji == '🎵':
                await msg.delete()
                await ctx.invoke(self.music)
            elif reaction.emoji == '🔡':
                await msg.delete()
                await ctx.invoke(self.tag)
            elif reaction.emoji == '🔎':
                await msg.delete()
                await ctx.invoke(self.search)
            elif reaction.emoji == '👫':
                await msg.delete()
                await ctx.invoke(self.profile)
            elif reaction.emoji == '❓':
                await msg.delete()
                await ctx.invoke(self.help)
            if res is None:
                await msg.delete()
        except:
            pass

    @help.command(pass_context = True)
    async def tag(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass
        msg = await ctx.send('<a:dblspin:393548363879940108> Loading\.\.\.')
        await msg.add_reaction('❌')
        await msg.add_reaction('😆')
        await msg.add_reaction('✍')
        await msg.add_reaction('🛡')
        await msg.add_reaction('🔢')
        await msg.add_reaction('🎵')
        await msg.add_reaction('🔡')
        await msg.add_reaction('🔎')
        await msg.add_reaction('👫')
        await msg.add_reaction('❓')
        embed = discord.Embed(title=":abcd: Prefix = \".\"", description="Tag commands:", color=discord.Color.gold())
        embed.add_field(name=":one: tag: Allows you to tag text for later retrieval.", value="Usage: ``tag [tag]``", inline=False)
        embed.add_field(name=":two: tag create: Creates a new tag owned by you.", value="Usage: ``tag create<name can be only one word> <content>``", inline=False)
        embed.add_field(name=":three: tag generic: Creates a new generic tag owned by you.", value="Usage: ``tag generic <name can be only one word> <content>``", inline=False)
        embed.add_field(name=":four: tag make: Interactively makes a tag for you.", value="Usage: ``tag make``", inline=False)
        embed.add_field(name=":five: tag stats: Gives stats about the tag database.", value="Usage: ``tag stats <tag>``", inline=False)
        embed.add_field(name=":six: tag edit: Modifies an existing tag that you own.", value="Usage: ``tag edit <tag> <new content>``", inline=False)
        embed.add_field(name=":seven: tag remove: Removes a tag that you own.", value="Usage: ``tag remove <tag>``", inline=False)
        embed.add_field(name=":eight: tag info: Retrieves info about a tag.", value="Usage: ``tag info <tag>``", inline=False)
        embed.add_field(name=":nine: tag list: Lists all the tags that belong to you.", value="Usage: ``tag list``", inline=False)
        embed.add_field(name=":one::zero: tag search: Searches for a tag.", value="Usage: ``tag search <text>``", inline=False)
        await msg.edit(content='DONE', embed=embed)
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ['❌','😆','✍','🛡','🔢','🎵','🔡','🔎','👫', '❓']
        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check)
            print(reaction.emoji)
            if reaction.emoji == '❌':
                print('added emoji')
                await msg.delete()
            elif reaction.emoji == '😆':
                await msg.delete()
                await ctx.invoke(self.fun)
            elif reaction.emoji == '✍':
                await msg.delete()
                await ctx.invoke(self.meta)
            elif reaction.emoji == '🛡':
                await msg.delete()
                await ctx.invoke(self.mod)
            elif reaction.emoji == '🔢':
                await msg.delete()
                await ctx.invoke(self.rng)
            elif reaction.emoji == '🎵':
                await msg.delete()
                await ctx.invoke(self.music)
            elif reaction.emoji == '🔡':
                await msg.delete()
                await ctx.invoke(self.tag)
            elif reaction.emoji == '🔎':
                await msg.delete()
                await ctx.invoke(self.search)
            elif reaction.emoji == '👫':
                await msg.delete()
                await ctx.invoke(self.profile)
            elif reaction.emoji == '❓':
                await msg.delete()
                await ctx.invoke(self.help)
            if res is None:
                await msg.delete()
        except:
            pass

    @help.command(pass_context = True)
    async def music(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass
        msg = await ctx.send('<a:dblspin:393548363879940108> Loading\.\.\.')
        await msg.add_reaction('❌')
        await msg.add_reaction('😆')
        await msg.add_reaction('✍')
        await msg.add_reaction('🛡')
        await msg.add_reaction('🔢')
        await msg.add_reaction('🎵')
        await msg.add_reaction('🔡')
        await msg.add_reaction('🔎')
        await msg.add_reaction('👫')
        await msg.add_reaction('❓')
        embed = discord.Embed(title=":musical_note: Prefix = \"-.\"", description="Music commands:", color=discord.Color.gold())
        embed.add_field(name=":one: summon: Summons the bot to the voice channel you are currently in.", value="Usage: ``summon``", inline=False)
        embed.add_field(name=":two: play: Plays or wueues a song you request.", value="Usage: ``play <song name/video name/youtube playlist url/spotify:url>``", inline=False)
        embed.add_field(name=":three: np: Shows what is playing right now on your server.", value="Usage: ``np``", inline=False)
        embed.add_field(name=":four: resume: Resues the song if the player is paused.", value="Usage: ``resume``", inline=False)
        embed.add_field(name=":five: skip: Votes to skip the song.", value="Usage: ``skip``", inline=False)
        embed.add_field(name=":six: queue: Shows the queue of songs.", value="Usage: ``queue``", inline=False)
        embed.add_field(name=":seven: shuffle: Shuffles the songs in the queue.", value="Usage: ``shuffle``", inline=False)
        embed.add_field(name=":eight: search: Searches from different services.", value="Usage: ``search <yt/sc/yh> <amount> <text to search with>``", inline=False)
        embed.add_field(name=":nine: remove: Removes an entry from queue.", value="Usage: ``remove <id in queue>``", inline=False)
        embed.add_field(name=":one::zero: pldump: Dumps a youtube playlist to txt file.", value="Usage: ``pldump <url>``", inline=False)
        embed.add_field(name=":one::one: stream: Streams from Youtube.", value="Usage: ``stream <url>``", inline=False)
        embed.add_field(name=":one::two: lyrics: Gets lyrics for the song you request.", value="Usage: ``lyrics [song name] [atrist name]``", inline=False)

        await msg.edit(content='DONE', embed=embed)
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ['❌','😆','✍','🛡','🔢','🎵','🔡','🔎','👫', '❓']
        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check)
            print(reaction.emoji)
            if reaction.emoji == '❌':
                print('added emoji')
                await msg.delete()
            elif reaction.emoji == '😆':
                await msg.delete()
                await ctx.invoke(self.fun)
            elif reaction.emoji == '✍':
                await msg.delete()
                await ctx.invoke(self.meta)
            elif reaction.emoji == '🛡':
                await msg.delete()
                await ctx.invoke(self.mod)
            elif reaction.emoji == '🔢':
                await msg.delete()
                await ctx.invoke(self.rng)
            elif reaction.emoji == '🎵':
                await msg.delete()
                await ctx.invoke(self.music)
            elif reaction.emoji == '🔡':
                await msg.delete()
                await ctx.invoke(self.tag)
            elif reaction.emoji == '🔎':
                await msg.delete()
                await ctx.invoke(self.search)
            elif reaction.emoji == '👫':
                await msg.delete()
                await ctx.invoke(self.profile)
            elif reaction.emoji == '❓':
                await msg.delete()
                await ctx.invoke(self.help)
            if res is None:
                await msg.delete()
        except:
            pass

    @help.command(pass_context=True)
    async def search(self, ctx):
        try:
            await ctx.message.delete()
        except:
            pass
        msg = await ctx.send('<a:dblspin:393548363879940108> Loading\.\.\.')
        await msg.add_reaction('❌')
        await msg.add_reaction('😆')
        await msg.add_reaction('✍')
        await msg.add_reaction('🛡')
        await msg.add_reaction('🔢')
        await msg.add_reaction('🎵')
        await msg.add_reaction('🔡')
        await msg.add_reaction('🔎')
        await msg.add_reaction('👫')
        await msg.add_reaction('❓')
        embed = discord.Embed(title=":mag_right: Search:", description="Search commands:", color=discord.Color.gold())
        embed.add_field(name=":one: imgur random: Gets a random image from imgur with a tag you specify.", value="Usage: ``imgur random <text>``", inline=False)
        embed.add_field(name=":two: imgur search: Searches from imgur with a tag you specify.", value="Usage: ``imgur search <text>``", inline=False)
        embed.add_field(name=":three: gifr: Gets a random gif from giphy with a tag you specify.", value="Usage: ``gifr <text>``", inline=False)
        embed.add_field(name=":four: gif: Gets the first search from giphy with a tag you specify.", value="Usage: ``gif <text>``", inline=False)
        embed.add_field(name=":five: define: Gets the 3 first sentences from wikipedia with a tag youi specify.", value="Usage: ``define <text>``", inline=False)
        await msg.edit(content='DONE', embed=embed)
        def check(reaction, user):
            return user == ctx.message.author and str(reaction.emoji) in ['❌','😆','✍','🛡','🔢','🎵','🔡','🔎','👫', '❓']
        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check)
            print(reaction.emoji)
            if reaction.emoji == '❌':
                print('added emoji')
                await msg.delete()
            elif reaction.emoji == '😆':
                await msg.delete()
                await ctx.invoke(self.fun)
            elif reaction.emoji == '✍':
                await msg.delete()
                await ctx.invoke(self.meta)
            elif reaction.emoji == '🛡':
                await msg.delete()
                await ctx.invoke(self.mod)
            elif reaction.emoji == '🔢':
                await msg.delete()
                await ctx.invoke(self.rng)
            elif reaction.emoji == '🎵':
                await msg.delete()
                await ctx.invoke(self.music)
            elif reaction.emoji == '🔡':
                await msg.delete()
                await ctx.invoke(self.tag)
            elif reaction.emoji == '🔎':
                await msg.delete()
                await ctx.invoke(self.search)
            elif reaction.emoji == '👫':
                await msg.delete()
                await ctx.invoke(self.profile)
            elif reaction.emoji == '❓':
                await msg.delete()
                await ctx.invoke(self.help)
            if res is None:
                await msg.delete()
        except:
            pass
def setup(bot):
    h = Help(bot)
    bot.add_cog(h)
