from discord.ext import commands
from .utils import checks, formats
import discord

from collections import OrderedDict, deque, Counter
import os, datetime
import io
import re, asyncio

import base64

import psutil
import inspect
import copy
import unicodedata
from googletrans import Translator

from fortnite_python import Fortnite
from fortnite_python.domain import Mode, Platform

from lxml import etree
from lru import LRU
translator = Translator()

def can_use_spoiler():
    def predicate(ctx):
        if ctx.guild is None:
            raise commands.BadArgument('Cannot be used in private messages.')

        my_permissions = ctx.channel.permissions_for(ctx.guild.me)
        if not (my_permissions.read_message_history and my_permissions.manage_messages and my_permissions.add_reactions):
            raise commands.BadArgument('Need Read Message History, Add Reactions and Manage Messages ' \
                                       'to permission to use this. Sorry if I spoiled you.')
        return True
    return commands.check(predicate)

SPOILER_EMOJI_ID = 463782668774146048

class SpoilerCache:
    __slots__ = ('author_id', 'channel_id', 'title', 'text', 'attachments')

    def __init__(self, data):
        self.author_id = data['author_id']
        self.channel_id = data['channel_id']
        self.title = data['title']
        self.text = data['text']
        self.attachments = data['attachments']

    def has_single_image(self):
        return self.attachments and self.attachments[0].filename.lower().endswith(('.gif', '.png', '.jpg', '.jpeg'))

    def to_embed(self, bot):
        embed = discord.Embed(title=f'{self.title} Spoiler', colour=0x01AEEE)
        if self.text:
            embed.description = self.text

        if self.has_single_image():
            if self.text is None:
                embed.title = f'{self.title} Spoiler Image'
            embed.set_image(url=self.attachments[0].url)
            attachments = self.attachments[1:]
        else:
            attachments = self.attachments

        if attachments:
            value = '\n'.join(f'[{a.filename}]({a.url})' for a in attachments)
            embed.add_field(name='Attachments', value=value, inline=False)

        user = bot.get_user(self.author_id)
        if user:
            embed.set_author(name=str(user), icon_url=user.avatar_url_as(format='png'))

        return embed

    def to_spoiler_embed(self, ctx, storage_message):
        description = 'React with <:hack_done:463782668774146048> to reveal the spoiler.'
        embed = discord.Embed(title=f'{self.title} Spoiler', description=description)
        if self.has_single_image() and self.text is None:
            embed.title = f'{self.title} Spoiler Image'

        embed.set_footer(text=storage_message.id)
        embed.colour = 0x01AEEE
        embed.set_author(name=ctx.author, icon_url=ctx.author.avatar_url_as(format='png'))
        return embed

class SpoilerCooldown(commands.CooldownMapping):
    def __init__(self):
        super().__init__(commands.Cooldown(1, 10.0, commands.BucketType.user))

    def _bucket_key(self, tup):
        return tup

    def is_rate_limited(self, message_id, user_id):
        bucket = self.get_bucket((message_id, user_id))
        return bucket.update_rate_limit() is not None

class Prefix(commands.Converter):
    async def convert(self, ctx, argument):
        user_id = ctx.bot.user.id
        if argument.startswith((f'<@{user_id}>', f'<@!{user_id}>')):
            raise commands.BadArgument('That is a reserved prefix already in use.')
        return argument

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
        self._spoiler_cache = LRU(128)
        self._spoiler_cooldown = SpoilerCooldown()

    @commands.command()
    async def charinfo(self, ctx, *, characters: str):
        """Shows you information about a number of characters.
        Only up to 25 characters at a time.
        """

        def to_string(c):
            digit = f'{ord(c):x}'
            name = unicodedata.name(c, 'Name not found.')
            return f'`\\U{digit:>08}`: {name} - {c} \N{EM DASH} <http://www.fileformat.info/info/unicode/char/{digit}>'
        msg = '\n'.join(map(to_string, characters))
        if len(msg) > 2000:
            return await ctx.send('Output too long to display.')
        await ctx.send(msg)

    @commands.group(name='prefix', invoke_without_command=True)
    async def prefix(self, ctx):
        """Manages the server's custom prefixes.
        If called without a subcommand, this will list the currently set
        prefixes.
        """

        prefixes = self.bot.get_guild_prefixes(ctx.guild)

        # we want to remove prefix #2, because it's the 2nd form of the mention
        # and to the end user, this would end up making them confused why the
        # mention is there twice
        del prefixes[1]

        e = discord.Embed(title='Prefixes:', colour=discord.Colour.blurple())
        e.set_footer(text=f'{len(prefixes)} prefixes on this server.')
        e.description = '\n'.join(f'{index}. {elem}' for index, elem in enumerate(prefixes, 1))
        await ctx.send(embed=e)

    @prefix.command(name='add', ignore_extra=False)
    @checks.is_mod()
    async def prefix_add(self, ctx, prefix: Prefix):
        """Appends a prefix to the list of custom prefixes.
        Previously set prefixes are not overridden.
        To have a word prefix, you should quote it and end it with
        a space, e.g. "hello " to set the prefix to "hello ". This
        is because Discord removes spaces when sending messages so
        the spaces are not preserved.
        Multi-word prefixes must be quoted also.
        You must have Manage Server permission to use this command.
        """

        current_prefixes = self.bot.get_raw_guild_prefixes(ctx.guild.id)
        current_prefixes.append(prefix)
        try:
            await self.bot.set_guild_prefixes(ctx.guild, current_prefixes)
        except Exception as e:
            await ctx.send(f'{ctx.tick(False)} {e}')
        else:
            await ctx.send(ctx.tick(True))

    @prefix_add.error
    async def prefix_add_error(self, ctx, error):
        if isinstance(error, commands.TooManyArguments):
            await ctx.send("You've given too many prefixes. Either quote it or only do it one by one.")

    @prefix.command(name='remove', aliases=['delete'], ignore_extra=False)
    @checks.is_mod()
    async def prefix_remove(self, ctx, prefix: Prefix):
        """Removes a prefix from the list of custom prefixes.
        This is the inverse of the 'prefix add' command. You can
        use this to remove prefixes from the default set as well.
        You must have Manage Server permission to use this command.
        """

        current_prefixes = self.bot.get_raw_guild_prefixes(ctx.guild.id)

        try:
            current_prefixes.remove(prefix)
        except ValueError:
            return await ctx.send('I do not have this prefix registered.')

        try:
            await self.bot.set_guild_prefixes(ctx.guild, current_prefixes)
        except Exception as e:
            await ctx.send(f'{ctx.tick(False)} {e}')
        else:
            await ctx.send(ctx.tick(True))

    async def redirect_post(self, ctx, title, text):
        storage = self.bot.get_guild(329993146651901952).get_channel(480429414166036500)

        supported_attachments = ('.png', '.jpg', '.jpeg', '.webm', '.gif', '.mp4', '.txt')
        if not all(attach.filename.lower().endswith(supported_attachments) for attach in ctx.message.attachments):
            raise RuntimeError(f'Unsupported file in attachments. Only {", ".join(supported_attachments)} supported.')

        files = []
        total_bytes = 0
        eight_mib = 8 * 1024 * 1024
        for attach in ctx.message.attachments:
            async with ctx.session.get(attach.url) as resp:
                if resp.status != 200:
                    continue

                content_length = int(resp.headers.get('Content-Length'))

                # file too big, skip it
                if (total_bytes + content_length) > eight_mib:
                    continue

                total_bytes += content_length
                fp = io.BytesIO(await resp.read())
                files.append(discord.File(fp, filename=attach.filename))

            if total_bytes >= eight_mib:
                break

        await ctx.message.delete()
        data = discord.Embed(title=title)
        if text:
            data.description = text

        data.set_author(name=ctx.author.id)
        data.set_footer(text=ctx.channel.id)

        try:
            message = await storage.send(embed=data, files=files)
        except discord.HTTPException as e:
            raise RuntimeError(f'Sorry. Could not store message due to {e.__class__.__name__}: {e}.') from e

        to_dict = {
            'author_id': ctx.author.id,
            'channel_id': ctx.channel.id,
            'attachments': message.attachments,
            'title': title,
            'text': text
        }

        cache = SpoilerCache(to_dict)
        return message, cache

    async def get_spoiler_cache(self, channel_id, message_id):
        try:
            return self._spoiler_cache[message_id]
        except KeyError:
            pass

        storage = self.bot.get_guild(329993146651901952).get_channel(480429414166036500)

        # slow path requires 2 lookups
        # first is looking up the message_id of the original post
        # to get the embed footer information which points to the storage message ID
        # the second is getting the storage message ID and extracting the information from it
        channel = self.bot.get_channel(channel_id)
        if not channel:
            return None

        try:
            original_message = await channel.get_message(message_id)
            storage_message_id = int(original_message.embeds[0].footer.text)
            message = await storage.get_message(storage_message_id)
        except:
            # this message is probably not the proper format or the storage died
            return None

        data = message.embeds[0]
        to_dict = {
            'author_id': int(data.author.name),
            'channel_id': int(data.footer.text),
            'attachments': message.attachments,
            'title': data.title,
            'text': None if not data.description else data.description
        }
        cache = SpoilerCache(to_dict)
        self._spoiler_cache[message_id] = cache
        return cache

    async def on_raw_reaction_add(self, payload):
        if payload.emoji.id != SPOILER_EMOJI_ID:
            return

        user = self.bot.get_user(payload.user_id)
        if not user or user.bot:
            return

        if self._spoiler_cooldown.is_rate_limited(payload.message_id, payload.user_id):
            return

        cache = await self.get_spoiler_cache(payload.channel_id, payload.message_id)
        embed = cache.to_embed(self.bot)
        await user.send(embed=embed)

    @commands.command()
    @can_use_spoiler()
    async def spoiler(self, ctx, title, *, text=None):
        """Marks your post a spoiler with a title.
        Once your post is marked as a spoiler it will be
        automatically deleted and the bot will DM those who
        opt-in to view the spoiler.
        The only media types supported are png, gif, jpeg, mp4,
        and webm.
        Only 8MiB of total media can be uploaded at once.
        Sorry, Discord limitation.
        To opt-in to a post's spoiler you must click the reaction.
        """

        if len(title) > 100:
            return await ctx.send('Sorry. Title has to be shorter than 100 characters.')

        try:
            storage_message, cache = await self.redirect_post(ctx, title, text)
        except Exception as e:
            return await ctx.send(str(e))

        spoiler_message = await ctx.send(embed=cache.to_spoiler_embed(ctx, storage_message))
        self._spoiler_cache[spoiler_message.id] = cache
        await spoiler_message.add_reaction(':hack_done:463782668774146048')


    @prefix.command(name='clear')
    @checks.is_mod()
    async def prefix_clear(self, ctx):
        """Removes all custom prefixes.
        After this, the bot will listen to only mention prefixes.
        You must have Manage Server permission to use this command.
        """

        await self.bot.set_guild_prefixes(ctx.guild, [])
        await ctx.send(ctx.tick(True))

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
            encodeddd = str(stringToBase64(text))
            encodedd = encodeddd.replace('b\'', '')
            encoded = encodedd.replace('\'', '')
            await ctx.send(':closed_lock_with_key: Here is you encoded data:\n```{}```'.format(encoded))

    @commands.command()
    async def decode(self, ctx, *, text):
        """Decodes text from base64."""
        if text is None:
            await ctx.send('You did not tell me what to decode. Try again.')
        else:
            def base64ToString(b):
                return base64.b64decode(b).decode('utf-8')
            decoded = str(base64ToString(text))
            await ctx.send(':lock: :key: Here is your decoded data:\n```{}```'.format(decoded))

    @commands.command(hidden=True)
    async def reactions(self, ctx):
        """Adds thumbs up reaction."""
        if ctx.message.author.bot: return
        await ctx.message.add_reaction('👍')

    @commands.group(invoke_without_command=True)
    @commands.guild_only()
    async def info(self, ctx, *, member: discord.Member = None):
        """Shows info about a member.
        This cannot be used in private messages. If you don't specify
        a member then the info returned will be yours.
        """

        if member is None:
            member = ctx.author

        e = discord.Embed()
        roles = [role.name.replace('@', '@\u200b') for role in member.roles]
        shared = sum(1 for m in self.bot.get_all_members() if m.id == member.id)
        voice = member.voice
        if voice is not None:
            vc = voice.channel
            other_people = len(vc.members) - 1
            voice = f'{vc.name} with {other_people} others' if other_people else f'{vc.name} by themselves'
        else:
            voice = 'Not connected.'

        e.set_author(name=str(member))
        e.set_footer(text='Member since').timestamp = member.joined_at
        e.add_field(name='ID', value=member.id)
        e.add_field(name='Servers', value=f'{shared} shared')
        e.add_field(name='Created', value=member.created_at)
        e.add_field(name='Voice', value=voice)
        e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles')
        e.colour = member.colour

        if member.avatar:
            e.set_thumbnail(url=member.avatar_url)

        await ctx.send(embed=e)

    @info.command(name='server', aliases=['guild'])
    @commands.guild_only()
    async def server_info(self, ctx):
        """Shows info about the current server."""

        guild = ctx.guild
        roles = [role.name.replace('@', '@\u200b') for role in guild.roles]

        # we're going to duck type our way here
        class Secret:
            pass

        secret_member = Secret()
        secret_member.id = 0
        secret_member.roles = [guild.default_role]

        # figure out what channels are 'secret'
        secret_channels = 0
        secret_voice = 0
        text_channels = 0
        for channel in guild.channels:
            perms = channel.permissions_for(secret_member)
            is_text = isinstance(channel, discord.TextChannel)
            text_channels += is_text
            if is_text and not perms.read_messages:
                secret_channels += 1
            elif not is_text and (not perms.connect or not perms.speak):
                secret_voice += 1

        regular_channels = len(guild.channels) - secret_channels
        voice_channels = len(guild.channels) - text_channels
        member_by_status = Counter(str(m.status) for m in guild.members)

        e = discord.Embed()
        e.title = 'Info for ' + guild.name
        e.add_field(name='ID', value=guild.id)
        e.add_field(name='Owner', value=guild.owner)
        if guild.icon:
            e.set_thumbnail(url=guild.icon_url)

        if guild.splash:
            e.set_image(url=guild.splash_url)

        info = []
        info.append(ctx.tick(len(guild.features) >= 3, 'Partnered'))

        sfw = guild.explicit_content_filter is not discord.ContentFilter.disabled
        info.append(ctx.tick(sfw, 'Scanning Images'))
        info.append(ctx.tick(guild.member_count > 100, 'Large'))

        e.add_field(name='Info', value='\n'.join(map(str, info)))

        fmt = f'Text {text_channels} ({secret_channels} secret)\nVoice {voice_channels} ({secret_voice} locked)'
        e.add_field(name='Channels', value=fmt)

        fmt = f'<:online:316856575413321728> {member_by_status["online"]} ' \
              f'<:idle:316856575098880002> {member_by_status["idle"]} ' \
              f'<:dnd:316856574868193281> {member_by_status["dnd"]} ' \
              f'<:offline:316856575501402112> {member_by_status["offline"]}\n' \
              f'Total: {guild.member_count}'

        e.add_field(name='Members', value=fmt)
        e.add_field(name='Roles', value=', '.join(roles) if len(roles) < 10 else f'{len(roles)} roles')
        e.set_footer(text='Created').timestamp = guild.created_at
        await ctx.send(embed=e)

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
