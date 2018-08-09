from discord.ext import commands
from .utils import checks, formats
import discord
from collections import OrderedDict, deque, Counter
import os, datetime
import re, asyncio
import base64
import psutil
from googletrans import Translator
from fortnite_python import Fortnite
from fortnite_python.domain import Mode, Platform
translator = Translator()

class TimeParser:
    def __init__(self, argument):
        compiled = re.compile(r"(?:(?P<hours>\d+)h)?(?:(?P<minutes>\d+)m)?(?:(?P<seconds>\d+)s)?")
        self.original = argument
        try:
            self.seconds = int(argument)
        except ValueError as e:
            match = compiled.match(argument)
            if match is None or not match.group(0):
                raise commands.BadArgument('Failed to parse time.') from e

            self.seconds = 0
            hours = match.group('hours')
            if hours is not None:
                self.seconds += int(hours) * 3600
            minutes = match.group('minutes')
            if minutes is not None:
                self.seconds += int(minutes) * 60
            seconds = match.group('seconds')
            if seconds is not None:
                self.seconds += int(seconds)

class Meta:
    """Commands for utilities realted to Discord or Bot itself."""

    def __init__(self, bot):
        self.bot = bot
        self.fortnite = Fortnite('274e0176-875b-400a-a7b4-fa2567990fda')

    @commands.group(aliases=['fortnite'])
    async def fn(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('You need to tell me what mode you want. ``solo, duo, squad``')

    @fn.command()
    async def solo(self, ctx, player: str=None):
        if player is None:
            return await ctx.send('You need to insert a player name. Usage ``fn solo <player>``')
        try:
            player = self.fortnite.player(player)
        except:
            return await ctx.send('I think that is not the correct player.')
        if player is None:
            return await ctx.send('Could not find that player.')
        stats = player.getStats(Mode.SOLO)
        e = discord.Embed(title="Info of {}:".format(player.username), description="User id: {}".format(player.id), color=discord.Color.green())
        e.add_field(name="Kills:", value=stats.kills, inline=True)
        e.add_field(name="Wins:", value=stats.wins, inline=True)
        e.add_field(name="KD:", value=stats.kd, inline=True)
        e.add_field(name="Top3:", value=stats.top3, inline=True)
        e.add_field(name="Top5:", value=stats.top5, inline=True)
        e.add_field(name="Top6:", value=stats.top6, inline=True)
        e.add_field(name="Top10:", value=stats.top10, inline=True)
        e.add_field(name="Top12:", value=stats.top12, inline=True)
        e.add_field(name="Top25:", value=stats.top25, inline=True)
        e.add_field(name="Score:", value=stats.score, inline=True)
        e.add_field(name="Winratio:", value=stats.winratio, inline=True)
        e.add_field(name="Total:", value=stats.total, inline=True)

        await ctx.send(embed=e)


    @fn.command()
    async def duo(self, ctx, player: str=None):
        if player is None:
            return await ctx.send('You need to insert a player name. Usage ``fn duo <player>``')
        try:
            player = self.fortnite.player(player)
        except:
            return await ctx.send('I think that is not the correct player.')
        if player is None:
            return await ctx.send('Could not find that player.')
        stats = player.getStats(Mode.DUO)
        e = discord.Embed(title="Info of {}:".format(player.username), description="User id: {}".format(player.id), color=discord.Color.green())
        e.add_field(name="Kills:", value=stats.kills, inline=True)
        e.add_field(name="Wins:", value=stats.wins, inline=True)
        e.add_field(name="KD:", value=stats.kd, inline=True)
        e.add_field(name="Top3:", value=stats.top3, inline=True)
        e.add_field(name="Top5:", value=stats.top5, inline=True)
        e.add_field(name="Top6:", value=stats.top6, inline=True)
        e.add_field(name="Top10:", value=stats.top10, inline=True)
        e.add_field(name="Top12:", value=stats.top12, inline=True)
        e.add_field(name="Top25:", value=stats.top25, inline=True)
        e.add_field(name="Score:", value=stats.score, inline=True)
        e.add_field(name="Winratio:", value=stats.winratio, inline=True)
        e.add_field(name="Total:", value=stats.total, inline=True)

        await ctx.send(embed=e)

    @fn.command(aliases=['sq'])
    async def squad(self, ctx, player: str=None):
        if player is None:
            return await ctx.send('You need to insert a player name. Usage ``fn squad <player>``')
        try:
            player = self.fortnite.player(player)
        except:
            return await ctx.send('I think that is not the correct player.')
        if player is None:
            return await ctx.send('Could not find that player.')
        stats = player.getStats(Mode.SQUAD)
        e = discord.Embed(title="Info of {}:".format(player.username), description="User id: {}".format(player.id), color=discord.Color.green())
        e.add_field(name="Kills:", value=stats.kills, inline=True)
        e.add_field(name="Wins:", value=stats.wins, inline=True)
        e.add_field(name="KD:", value=stats.kd, inline=True)
        e.add_field(name="Top3:", value=stats.top3, inline=True)
        e.add_field(name="Top5:", value=stats.top5, inline=True)
        e.add_field(name="Top6:", value=stats.top6, inline=True)
        e.add_field(name="Top10:", value=stats.top10, inline=True)
        e.add_field(name="Top12:", value=stats.top12, inline=True)
        e.add_field(name="Top25:", value=stats.top25, inline=True)
        e.add_field(name="Score:", value=stats.score, inline=True)
        e.add_field(name="Winratio:", value=stats.winratio, inline=True)
        e.add_field(name="Total:", value=stats.total, inline=True)

        await ctx.send(embed=e)

    @commands.command()
    async def translate(self, ctx, src: str=None, dest: str=None, *, text: str=None):
        """Translates text from language to another."""
        LANGUAGES = {
            'af': 'afrikaans',
            'sq': 'albanian',
            'am': 'amharic',
            'ar': 'arabic',
            'hy': 'armenian',
            'az': 'azerbaijani',
            'eu': 'basque',
            'be': 'belarusian',
            'bn': 'bengali',
            'bs': 'bosnian',
            'bg': 'bulgarian',
            'ca': 'catalan',
            'ceb': 'cebuano',
            'ny': 'chichewa',
            'zh-cn': 'chinese (simplified)',
            'co': 'corsican',
            'hr': 'croatian',
            'cs': 'czech',
            'da': 'danish',
            'nl': 'dutch',
            'en': 'english',
            'eo': 'esperanto',
            'et': 'estonian',
            'tl': 'filipino',
            'fi': 'finnish',
            'fr': 'french',
            'fy': 'frisian',
            'gl': 'galician',
            'ka': 'georgian',
            'de': 'german',
            'el': 'greek',
            'gu': 'gujarati',
            'ht': 'haitian creole',
            'ha': 'hausa',
            'haw': 'hawaiian',
            'iw': 'hebrew',
            'hi': 'hindi',
            'hmn': 'hmong',
            'hu': 'hungarian',
            'is': 'icelandic',
            'ig': 'igbo',
            'id': 'indonesian',
            'ga': 'irish',
            'it': 'italian',
            'ja': 'japanese',
            'jw': 'javanese',
            'kn': 'kannada',
            'kk': 'kazakh',
            'km': 'khmer',
            'ko': 'korean',
            'ku': 'kurdish (kurmanji)',
            'ky': 'kyrgyz',
            'lo': 'lao',
            'la': 'latin',
            'lv': 'latvian',
            'lt': 'lithuanian',
            'lb': 'luxembourgish',
            'mk': 'macedonian',
            'mg': 'malagasy',
            'ms': 'malay',
            'ml': 'malayalam',
            'mt': 'maltese',
            'mi': 'maori',
            'mr': 'marathi',
            'mn': 'mongolian',
            'my': 'myanmar (burmese)',
            'ne': 'nepali',
            'no': 'norwegian',
            'ps': 'pashto',
            'fa': 'persian',
            'pl': 'polish',
            'pt': 'portuguese',
            'pa': 'punjabi',
            'ro': 'romanian',
            'ru': 'russian',
            'sm': 'samoan',
            'gd': 'scots gaelic',
            'sr': 'serbian',
            'st': 'sesotho',
            'sn': 'shona',
            'sd': 'sindhi',
            'si': 'sinhala',
            'sk': 'slovak',
            'sl': 'slovenian',
            'so': 'somali',
            'es': 'spanish',
            'su': 'sundanese',
            'sw': 'swahili',
            'sv': 'swedish',
            'tg': 'tajik',
            'ta': 'tamil',
            'te': 'telugu',
            'th': 'thai',
            'tr': 'turkish',
            'uk': 'ukrainian',
            'ur': 'urdu',
            'uz': 'uzbek',
            'vi': 'vietnamese',
            'cy': 'welsh',
            'xh': 'xhosa',
            'yi': 'yiddish',
            'yo': 'yoruba',
            'zu': 'zulu',
            'fil': 'Filipino',
            'he': 'Hebrew'
        }
        if src is None:
            await ctx.send('You forgot to tell from what laguage you want to translate from. The format is e.g. ``en``.')
            return
        if dest is None:
            await ctx.send('You forgot to tell from what laguage you want to translate to. The format is e.g. ``en``.')
            return
        if text is None:
            await ctx.send('You forgot to tell what to translate.')
            return
        if src not in LANGUAGES:
            await ctx.send('That language is not supported.\nUse ``detect <text>`` to get the correct format.')
            return
        if dest not in LANGUAGES:
            await ctx.send('That language is not supported.\nUse ``detect <text>`` to get the correct format.')
            return

        translated = translator.translate(text, src=src, dest=dest)
        if translated is None:
            await ctx.send('Could not translate that.')
            return
        if translated.text is not None:
            await ctx.send('Translated from {} to {}:\n```{}```'.format(LANGUAGES[src], LANGUAGES[dest], translated.text))

    @commands.command()
    async def detect(self, ctx, text: str=None):
        """Detects the language you are writing."""
        LANGUAGES = {
            'af': 'afrikaans',
            'sq': 'albanian',
            'am': 'amharic',
            'ar': 'arabic',
            'hy': 'armenian',
            'az': 'azerbaijani',
            'eu': 'basque',
            'be': 'belarusian',
            'bn': 'bengali',
            'bs': 'bosnian',
            'bg': 'bulgarian',
            'ca': 'catalan',
            'ceb': 'cebuano',
            'ny': 'chichewa',
            'zh-cn': 'chinese (simplified)',
            'zh-tw': 'chinese (traditional)',
            'co': 'corsican',
            'hr': 'croatian',
            'cs': 'czech',
            'da': 'danish',
            'nl': 'dutch',
            'en': 'english',
            'eo': 'esperanto',
            'et': 'estonian',
            'tl': 'filipino',
            'fi': 'finnish',
            'fr': 'french',
            'fy': 'frisian',
            'gl': 'galician',
            'ka': 'georgian',
            'de': 'german',
            'el': 'greek',
            'gu': 'gujarati',
            'ht': 'haitian creole',
            'ha': 'hausa',
            'haw': 'hawaiian',
            'iw': 'hebrew',
            'hi': 'hindi',
            'hmn': 'hmong',
            'hu': 'hungarian',
            'is': 'icelandic',
            'ig': 'igbo',
            'id': 'indonesian',
            'ga': 'irish',
            'it': 'italian',
            'ja': 'japanese',
            'jw': 'javanese',
            'kn': 'kannada',
            'kk': 'kazakh',
            'km': 'khmer',
            'ko': 'korean',
            'ku': 'kurdish (kurmanji)',
            'ky': 'kyrgyz',
            'lo': 'lao',
            'la': 'latin',
            'lv': 'latvian',
            'lt': 'lithuanian',
            'lb': 'luxembourgish',
            'mk': 'macedonian',
            'mg': 'malagasy',
            'ms': 'malay',
            'ml': 'malayalam',
            'mt': 'maltese',
            'mi': 'maori',
            'mr': 'marathi',
            'mn': 'mongolian',
            'my': 'myanmar (burmese)',
            'ne': 'nepali',
            'no': 'norwegian',
            'ps': 'pashto',
            'fa': 'persian',
            'pl': 'polish',
            'pt': 'portuguese',
            'pa': 'punjabi',
            'ro': 'romanian',
            'ru': 'russian',
            'sm': 'samoan',
            'gd': 'scots gaelic',
            'sr': 'serbian',
            'st': 'sesotho',
            'sn': 'shona',
            'sd': 'sindhi',
            'si': 'sinhala',
            'sk': 'slovak',
            'sl': 'slovenian',
            'so': 'somali',
            'es': 'spanish',
            'su': 'sundanese',
            'sw': 'swahili',
            'sv': 'swedish',
            'tg': 'tajik',
            'ta': 'tamil',
            'te': 'telugu',
            'th': 'thai',
            'tr': 'turkish',
            'uk': 'ukrainian',
            'ur': 'urdu',
            'uz': 'uzbek',
            'vi': 'vietnamese',
            'cy': 'welsh',
            'xh': 'xhosa',
            'yi': 'yiddish',
            'yo': 'yoruba',
            'zu': 'zulu',
            'fil': 'Filipino',
            'he': 'Hebrew'
        }
        dlang = translator.detect(text)
        if dlang.lang not in LANGUAGES:
            await ctx.send('I am sorry but this language is not supported.')
            return
        dlangcode = dlang.lang
        await ctx.send('That sentence is written in ``{}`` and it\'s code is ``{}``.'.format(LANGUAGES[dlangcode], dlang.lang))

    @commands.command()
    async def vote(self, ctx):
        """Gives you the discordbots.org vote link."""
        await ctx.send('You can upvote me here: https://discordbots.org/bot/460846291300122635/vote')

    @commands.group(hidden=True)
    async def suggest(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('You didn\'t tell what to suggest.\nUsage is ``suggest <commands/song>``')

    @suggest.command()
    async def song(self, ctx, *, text : str = None):
        """Sends a song suggestion to the support guild."""
        try:
            await ctx.message.delete()
        except:
            pass
        if text is None:
            msg = await ctx.send('You didn\'t tell me what song to suggest.')
            await asyncio.sleep(10)
            await msg.delete()
        else:
            msg = text
            author = ctx.message.author
            suggestion = self.bot.get_channel(468710780867575809)
            embed = discord.Embed(title='Suggestion from: ', description='{}'.format(author.name), color=discord.Color.green())
            embed.add_field(name="Song name:", value="{}".format(text), inline=True)
            await suggestion.send(embed=embed)
            msg = await ctx.send('Song suggestion sent.', delete_after=10.0)

    @suggest.command()
    async def command(self, ctx, *, text: str=None):
        """Sends a command suggestion to the support guild."""
        try:
            await ctx.message.delete()
        except:
            pass
        if text is None:
            msg = await ctx.send('You didn\'t tell me what to suggest.')
            await asyncio.sleep(10)
            await msg.delete()
        else:
            msg = text
            author = ctx.message.author
            suggestion = self.bot.get_channel(468710780867575809)
            embed = discord.Embed(title='Suggestion from: ', description='{}'.format(author.name), color=discord.Color.blue())
            embed.add_field(name="Command suggestion:", value="{}".format(text), inline=True)
            await suggestion.send(embed=embed)
            msg = await ctx.send('Command suggestion sent.')
            await asyncio.sleep(10)
            await msg.delete()

    @commands.command()
    async def encode(self, ctx, *, text = None):
        """Encodes text to base64."""
        if text is None:
            await ctx.send('You did not tell me what to encode. Try again.')
        else:
            def stringToBase64(s):
                return base64.b64encode(s.encode('utf-8'))
            encoded = stringToBase64(text)
            await ctx.send(':closed_lock_with_key: Here is you encoded data:\n```{}```\nIf you want to convert it back remove the ``b\'`` and ``\'``.'.format(encoded))

    @commands.command()
    async def decode(self, ctx, *, text):
        """Decodes text from base64."""
        if text is None:
            await ctx.send('You did not tell me what to decode. Try again.')
        else:
            def base64ToString(b):
                return base64.b64decode(b).decode('utf-8')
            decoded = base64ToString(text)
            await ctx.send(':lock: :key: Here is your decoded data:\n```{}```'.format(decoded))

    @commands.command(hidden=True)
    async def reactions(self, ctx):
        """Adds thumbs up reaction."""
        if ctx.message.author.bot: return
        await ctx.message.add_reaction('👍')

    @commands.group()
    async def poll(self, ctx,*, poll : str):
        """Makes a poll from what you say."""
        if ctx.message.author.bot: return
        try:
            await ctx.message.delete()
        except:
            pass
        message = await ctx.send('{} asked you about:\n```{}```\n**Add your reactions.**'.format(ctx.message.author.nick, poll))
        await message.add_reaction('👍')
        await message.add_reaction('👎')
        await message.add_reaction('✅')
        await message.add_reaction('❌')

    @commands.command()
    async def rate(self, ctx, amount: int = None, *,poll: str = None):
        """Makes a rate poll from what you say with the reaction amount you provide."""
        if ctx.message.author.bot: return
        if str(amount) not in '123456789':
            amount = 5
        if amount is None:
            amount = 5
        if amount == 0:
            await ctx.send('The amont of reactions can\'t be 0.')
            return
        if amount > 9:
            await ctx.send('The amount of reactions can\'t be more than 9')
            return
        if poll is None:
            await ctx.send('You forgot to add a thing to rate. Or it is not a valid one.')
            return
        try:
            await ctx.message.delete()
        except:
            pass
        msg = await ctx.send('{} asked you to rate about:\n```{}```\n**Rate it**'.format(ctx.message.author.name, poll))
        for number in range(amount):
            emoji= str(number + 1) + '⃣'
            await msg.add_reaction(emoji)
        # await self.bot.add_reaction(msg, emoji)

    @commands.command()
    async def remind(self, ctx, time : TimeParser, *, message=''):
        """Reminds you of something after a certain amount of time.

        The time can optionally be specified with units such as 'h'
        for hours, 'm' for minutes and 's' for seconds. If no unit
        is given then it is assumed to be seconds. You can also combine
        multiple units together, e.g. 3h2m1s.
        """

        author = ctx.message.author
        reminder = None
        completed = None

        if not message:
            reminder = 'Okay {0.mention}, I\'ll remind you in {1.seconds} seconds.'
            completed = 'Time is up {0.mention}! You asked to be reminded about something.'
        else:
            reminder = 'Okay {0.mention}, I\'ll remind you about "{2}" in {1.seconds} seconds.'
            completed = 'Time is up {0.mention}! You asked to be reminded about "{1}".'

        await ctx.send(reminder.format(author, time, message))
        await asyncio.sleep(time.seconds)
        await ctx.send(completed.format(author, message))


    @commands.command()
    async def info(self, ctx, *, member : discord.Member = None):
        if ctx.message.author.bot: return
        """Shows info about a member.

        This cannot be used in private messages. If you don't specify
        a member then info returned will be yours.
        """
        channel = ctx.message.channel
        if channel.is_private:
            await ctx.send('You cannot use this in PMs.')
            return

        if member is None:
            member = ctx.message.author

        roles = [role.name.replace('@', '@\u200b') for role in member.roles]
        shared = sum(1 for m in self.bot.get_all_members() if m.id == member.id)
        voice = member.voice_channel
        if voice is not None:
            voice = '{} with {} people'.format(voice, len(voice.voice_members))
        else:
            voice = 'Not connected.'

        entries = [
            ('Name', member.name),
            ('User ID', member.id),
            ('Joined', member.joined_at),
            ('Roles', ', '.join(roles)),
            ('guilds', '{} shared'.format(shared)),
            ('Channel', channel.name),
            ('Voice Channel', voice),
            ('Channel ID', channel.id)
        ]

        await formats.entry_to_code(self.bot, entries)

    async def say_permissions(self, member, channel):
        permissions = channel.permissions_for(member)
        entries = []
        for attr in dir(permissions):
            is_property = isinstance(getattr(type(permissions), attr), property)
            if is_property:
                entries.append((attr.replace('_', ' ').title(), getattr(permissions, attr)))

        await formats.entry_to_code(self.bot, entries)

    @commands.command(no_pm=True)
    async def permissions(self, ctx, *, member : discord.Member = None):
        if ctx.message.author.bot: return
        """Shows a member's permissions.

        You cannot use this in private messages. If no member is given then
        the info returned will be yours.
        """
        channel = ctx.message.channel
        if member is None:
            member = ctx.message.author

        await self.say_permissions(member, channel)

    @commands.command(no_pm=True)
    async def botpermissions(self, ctx):
        """Shows the bot's permissions.
        This is a good way of checking if the bot has the permissions needed
        to execute the commands it wants to execute.
        To execute this command you must have Manage Roles permissions or
        have the Bot Admin role. You cannot use this in private messages.
        """
        channel = ctx.message.channel
        member = ctx.message.guild.me
        await self.say_permissions(member, channel)

    def get_bot_uptime(self):
        now = datetime.datetime.utcnow()
        delta = now - self.bot.uptime
        hours, remainder = divmod(int(delta.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)
        if days:
            fmt = '{d} days, {h} hours, {m} minutes, and {s} seconds'
        else:
            fmt = '{h} hours, {m} minutes, and {s} seconds'

        return fmt.format(d=days, h=hours, m=minutes, s=seconds)

    @commands.command()
    async def invite(self, ctx):
        if ctx.message.author.bot: return
        """Gives you a invite link to this guild."""
        invite  = await guild.create_invite(ctx.guild)
        await ctx.send(':ballot_box_with_check: | I created a invite "{}" to this guild.'.format(invite))

    @commands.command(hidden=True)
    async def guildjoin(self, ctx, invite : discord.Invite):
        """Joins a guild via invite."""
        await self.bot.accept_invite(invite)
        await ctx.send('\U0001f44c')

    @commands.command(no_pm=True)
    @checks.has_permissions(manage_guild=True)
    async def guildleave(self, ctx):
        if ctx.message.author.bot: return
        """Leaves the guild.

        To use this command you must have Manage guild permissions.
        """
        guild = ctx.message.guild
        try:
            await self.bot.leave_guild(guild)
        except:
            await ctx.send(':exclamation:{} I could not leave...'.format(ctx.message.author.mention))

    @commands.command()
    async def uptime(self, ctx):
        """Tells you how long the bot has been online."""
        await ctx.send('Uptime: **{}**'.format(self.get_bot_uptime()))

    def format_message(self, message):
        return 'On {0.timestamp}, {0.author} said {0.content}'.format(message)

    @commands.command(hidden=True)
    async def mentions(self, ctx, channel : discord.TextChannel = None, context : int = 3):
        if ctx.message.author.bot: return
        """Tells you when you were mentioned in a channel.
        If a channel is not given, then it tells you when you were mentioned in a
        the current channel. The context is an integer that tells you how many messages
        before should be shown. The context cannot be greater than 5 or lower than 0.
        """
        if channel is None:
            channel = ctx.message.channel

        context = min(5, max(0, context))

        author = ctx.message.author
        previous = deque(maxlen=context)
        async for message in self.bot.logs_from(channel, limit=100):
            previous.append(message)
            if author in message.mentions or message.mention_everyone:
                # we're mentioned so..
                try:
                    await self.bot.whisper('\n'.join(map(self.format_message, previous)))
                except discord.HTTPException:
                    await self.bot.whisper('An error happened while fetching mentions.')

    @commands.command()
    async def about(self, ctx):
        """Tells you information about the bot itself."""
        e = discord.Embed(title="About Me:", color=discord.Color.dark_green())
        e.add_field(name="Creator:", value="iWeeti#4990 (Discord ID: 282515230595219456)", inline=False)
        e.add_field(name="Library:", value="discord.py rewrite (Python)", inline=False)
        e.add_field(name="Uptime:", value=self.get_bot_uptime(), inline=False)
        e.add_field(name="Guilds:", value=len(self.bot.guilds), inline=False)
        e.add_field(name="Commands Run:", value=self.bot.commands_executed, inline=False)
        # # statistics
        total_members = sum(len(s.members) for s in self.bot.guilds)
        total_online  = sum(1 for m in self.bot.get_all_members() if m.status != discord.Status.offline)
        # unique_members = set(self.bot.get_all_members())
        # unique_online = sum(1 for m in unique_members if m.status != discord.Status.offline)
        # # channel_types = Counter(c.type for c in self.bot.get_all_channels())
        # # voice = channel_types[discord.VoiceChannel]
        # # text = channel_types[discord.TextChannel]
        e.add_field(name="Total Members / Online:", value="{} / {}".format(total_members, total_online), inline=False)
        e.set_thumbnail(url=ctx.me.avatar_url)
        await ctx.send(embed=e)

    @commands.command(rest_is_raw=True, hidden=True)
    @commands.is_owner()
    async def echo(self, ctx, *, content):
        """Says what you say."""
        if ctx.message.author.bot: return
        try:
            await ctx.message.delete()
        except discord.Forbidden:
            pass
        await ctx.send(content)

def setup(bot):
    bot.add_cog(Meta(bot))
