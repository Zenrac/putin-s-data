import discord
from discord.ext import commands
import random
import asyncio
import itertools
import sys
import traceback
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL
from discord import opus
from cogs.opus_loader import load_opus_lib

load_opus_lib()

ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = YoutubeDL(ytdlopts)


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')
        self.duration = data.get('duration')
        self.view_count = data.get('view_count')
        self.like_count = data.get('like_count')
        self.dislike_count = data.get('duration')
        self.thumbnail = data.get('thumbnail')
        self.msg = data.get('message')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        m, s = divmod(data['duration'], 60)
        data['duration'] = '{}m:{}s'.format(m, s)

        # await ctx.send(data)
        e = discord.Embed(title="Song added.", description=data['title'], color=discord.Color.magenta())
        e.add_field(name="Duration:", value=data['duration'], inline=True)
        e.set_footer(text="Views: {}, Likes: {}, Dis-Likes {}".format(data['view_count'], data['like_count'], data['dislike_count']))
        e.set_thumbnail(url=data['thumbnail'])
        await ctx.send(embed=e, delete_after=15)

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'message': ctx.message, 'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title'], 'duration': data['duration'], 'view_count': data['view_count'], 'like_count': data['like_count'], 'dislike_count': data['dislike_count']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

    @classmethod
    async def create_sourcee(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]
        m, s = divmod(data['duration'], 60)
        data['duration'] = '{}m:{}s'.format(m, s)

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'message': ctx.message, 'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title'], 'duration': data['duration'], 'view_count': data['view_count'], 'like_count': data['like_count'], 'dislike_count': data['dislike_count'], 'thumbnail': data['thumbnail']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)


class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume', 'stop_votes', 'skip_votes', 'progress', 'prog', 'duration', 'msg')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = .25
        self.current = None

        self.stop_votes = []
        self.skip_votes = []

        self.progress = 0
        self.prog = 0

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()
            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source

            self.progress = '0m:0s'

            m, s = divmod(source.duration, 60)
            _duration = '{}m:{}s'.format(m, s)

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            e = discord.Embed(title="Now playing:", description=source.title, color=discord.Color.magenta())
            e.add_field(name="Duration:", value="``[{}]``".format(source.duration), inline=True)
            e.set_footer(text="Views {}, Likes {}, Dis-Likes {}".format(source.view_count, source.like_count, source.dislike_count))
            e.set_thumbnail(url=source.thumbnail)
            self.np = await self._channel.send(embed=e)
            while True:
                print(source)
                if source is None:
                    break
                if self._guild.voice_client.is_playing():
                    # prog_bar_str = ''
                    # percentage = 0.0
                    # if source.duration > 0:
                    #     percentage = self.prog / source.duration
                    # progress_bar_length = 25
                    # for i in range(progress_bar_length):
                    #     if (percentage < 1 / progress_bar_length * i):
                    #         prog_bar_str += '□'
                    #     else:
                    #         prog_bar_str += '■'
                    m, s = divmod(self.prog, 60)
                    self.progress = '{}m:{}s'.format(m, s)
            #         e = discord.Embed(title="Now playing:", description=source.title, color=discord.Color.magenta())
            #         e.add_field(name="Progress:", value="``[{}/{}]``{}".format(self.progress, _duration, prog_bar_str), inline=True)
            #         e.add_field(name="Requested by:", value=source.requester, inline=True)
            #         e.set_footer(text="Views {}, Likes {}, Dis-Likes {}. If you pause the music progress will stop.".format(source.view_count, source.like_count, source.dislike_count))
            #         e.set_thumbnail(url=source.thumbnail)
            #         # await self.np.edit(content=f'**Now Playing:** `{source.title}` requested by `{source.requester}`\n`[{self.progress}/{_duration}]`')
            #         await self.np.edit(embed=e)
                    self.prog += 1
            #         if self.prog >= source.duration:
            #             break
            #         if not self._guild.voice_client.is_playing():
            #             break
                    await asyncio.sleep(1)
                else:
                    # if source is None:
                        # break
                    # await self.bot.process_commands(message)
            #         e = discord.Embed(title="Now playing:", description=source.title, color=discord.Color.magenta())
            #         e.add_field(name="Progress:", value="``[Progress stopped due to pausing.]``", inline=True)
            #         e.add_field(name="Requested by:", value=source.requester, inline=True)
            #         e.set_footer(text="Views {}, Likes {}, Dis-Likes {}. If you pause the music progress will stop.".format(source.view_count, source.like_count, source.dislike_count))
            #         e.set_thumbnail(url=source.thumbnail)
            #         await self.np.edit(embed=e)
                    break
                    # pass
            print('stopped the while loop')
            await self.next.wait()
            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None
            self.progress = 0
            self.prog = 0
            self.skip_votes = []

            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))

class Music:
    """Music related commands."""

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, commands.CommandOnCooldown):
            pass
        elif isinstance(error, commands.MissingPermissions):
            pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('Error connecting to Voice Channel. '
                           'Please make sure you are in a valid channel or provide me with one')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player

        return player

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def clear(self, ctx):
        player = self.get_player(ctx)
        player.queue.clear()
        await ctx.send('Queue cleared.')

    @commands.command(name='summon', aliases=['join', 'connect'])
    async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
        """Connect to voice.
        Parameters
        ------------
        channel: discord.VoiceChannel [Optional]
            The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
            will be made.
        This command also handles moving the bot to different channels.
        """
        if not channel:
            try:
                channel = ctx.author.voice.channel
            except AttributeError:
                raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')

        await ctx.send(f'Connected to: **{channel}**', delete_after=20)

    @commands.command(name='play', aliases=['sing', 'p', 'נגן'])
    async def play_(self, ctx, *, search: str):
        """Request a song and add it to the queue.
        This command attempts to join a valid voice channel if the bot is not already in one.
        Uses YTDL to automatically search and retrieve a song.
        Parameters
        ------------
        search: str [Required]
            The song to search and retrieve using YTDL. This could be a simple search, an ID or URL.
        """
        if not ctx.author.voice:
            await ctx.send('You are not in a voice channel. Do you think I can broadcast music to your head?')
            return
        vc = ctx.voice_client
        if not vc:
            await ctx.invoke(self.connect_)
            vc = ctx.voice_client
        if not ctx.author.voice.channel == vc.channel:
            await ctx.send('You need to be in the same channel as I am in to play music.', delete_after=20)
            return
        await ctx.trigger_typing()


        if not vc:
            await ctx.invoke(self.connect_)

        player = self.get_player(ctx)

        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=False)
        await player.queue.put(source)

    @commands.command(name='radio', aliases=['r', 'random'])
    @commands.cooldown(1, 300, commands.BucketType.guild)
    async def radio_(self, ctx, amount: int=1):
        """Adds a random song and add it to the queue.
        """
        if not ctx.author.voice:
            await ctx.send('You are not in a voice channel. Do you think I can broadcast music to your head?')
            return
        vc = ctx.voice_client
        if not vc:
            await ctx.invoke(self.connect_)
            vc = ctx.voice_client
        if not ctx.author.voice.channel == vc.channel:
            await ctx.send('You need to be in the same channel as I am in to play music.', delete_after=20)
            return
        max_radio = 10
        if amount > max_radio:
            r_cmd = self.bot.get_command('radio_')
            r_cm.reset_cooldown(ctx)
            await ctx.send('Some limits tho dude, can\'t random queue more than 10 songs.')
            return
        progress = 0
        msg = await ctx.send('Adding songs to queue {}/{}.'.format(progress, amount))
        for time in range(amount):
            progress += 1
            player = self.get_player(ctx)

            with open('autoplaylist.txt', 'r') as f:
                r_song = random.choice(f.readlines())

            # If download is False, source will be a dict which will be used later to regather the stream.
            # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
            source = await YTDLSource.create_sourcee(ctx, r_song, loop=self.bot.loop, download=False)

            await player.queue.put(source)
            await msg.edit(content='Adding songs to queue {}/{}.\n**Name:**``{}``'.format(progress, amount, source['title']))
            await asyncio.sleep(1)
        await msg.edit(content='Added {} songs to queue.'.format(amount))

    @commands.command(name='pause')
    async def pause_(self, ctx):
        """Pause the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_playing():
            return await ctx.send('I am not currently playing anything!', delete_after=20)
        elif vc.is_paused():
            return

        vc.pause()
        await ctx.send(f'**`{ctx.author}`**: Paused the song!')

    @commands.command(name='resume')
    async def resume_(self, ctx):
        """Resume the currently paused song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=20)
        elif not vc.is_paused():
            return

        vc.resume()
        await ctx.send(f'**`{ctx.author}`**: Resumed the song!')

    @commands.command(name='skip')
    async def skip_(self, ctx):
        """Skip the song."""
        vc = ctx.voice_client
        if not ctx.author.voice.channel == vc.channel:
            await ctx.send('You need to be in the same channel as I am in to vote.', delete_after=20)
            return
        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=20)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        members = 0

        for member in vc.channel.members:
            if not member.bot:
                members += 1

        player = self.get_player(ctx)

        if members == 1:
            vc.stop()
            await ctx.send(f'**`{ctx.author}`**: Skipped the song!')

        half_members = members / 2
        if members >= 2:
            if ctx.author.id in player.skip_votes:
                await ctx.send('You voted already, you need {} more votes to skip.'.format(int(half_members - len(player.skip_votes))))
                return
            player.skip_votes.append(ctx.author.id)
            if members == 2:
                vc.stop()
                await ctx.send('The vote has been passed. Skipped the song.')
                player.skip_votes = []
                return
            await ctx.send('Voted to skip, you need {} more votes to skip.'.format(int(half_members - len(player.skip_votes))))
            if len(player.skip_votes) == int(members / 2):
                vc.stop()
                await ctx.send('The vote has been passed. Skipped the song.')
                player.skip_votes = []

    @commands.command(name='forceskip', aliases=['fskip'])
    @commands.has_permissions(manage_channels=True)
    async def _skipf(self, ctx):
        vc = ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send('I am not playing anything.', delete_after=20)
        player = self.get_player(ctx)
        vc.stop()
        await ctx.send(f'**`{ctx.author}`**: Force skipped the song!')
        player.skip_votes = []

    @commands.command(name='queue', aliases=['q', 'playlist'])
    # @commands.cooldown()
    async def queue_info(self, ctx):
        """Retrieve a basic queue of upcoming songs."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!', delete_after=20)

        player = self.get_player(ctx)
        if player.queue.empty() or not player.next:
            return await ctx.send('There are currently no more queued songs.')

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, None))
        if len(upcoming) > 10:
            upcoming_len = len(upcoming)
            upcoming = upcoming[0:8]
            fmt3 = '```ini\n'
            fmt1 = '\n\n'.join(f'[{_["title"]}]\n(Requested by {_["requester"]})(Duration {_["duration"]})' for _ in upcoming) if upcoming else ''
            fmt2 = '```'
            fmt = fmt3 + fmt1 + fmt2
            end = '\nAnd {} more.'.format(upcoming_len - 10)
        else:
            fmt3 = '```ini\n'
            fmt1 = '\n\n'.join(f'[{_["title"]}]\n(Requested by {_["requester"]})(Duration {_["duration"]})' for _ in upcoming) if upcoming else ''
            fmt2 = '```'
            fmt = fmt3 + fmt1 + fmt2
            end = ''
        embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}', description=fmt + end, color=discord.Color.blue())

        await ctx.send(embed=embed)

    @commands.command(name='np', aliases=['now_playing', 'current', 'currentsong', 'playing'])
    async def now_playing_(self, ctx):
        """Display information about the currently playing song."""
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!', delete_after=20)

        player = self.get_player(ctx)
        if not player.current:
            return await ctx.send('I am not currently playing anything!')

        try:
            # Remove our previous now_playing message.
            if player.np is not None:
                await player.np.delete()
        except discord.HTTPException:
            pass
        # await ctx.send(dir(vc.source))
        m, s = divmod(vc.source.duration, 60)
        _duration = '{}m:{}s'.format(m, s)
        prog_bar_str = ''
        percentage = 0.0
        if vc.source.duration > 0:
            percentage = player.prog / vc.source.duration
        progress_bar_length = 25
        for i in range(progress_bar_length):
            if (percentage < 1 / progress_bar_length * i):
                prog_bar_str += '□'
            else:
                prog_bar_str += '■'
        e = discord.Embed(title="Now playing:", description=vc.source.title, color=discord.Color.magenta())
        e.add_field(name="Progress:", value="`[{}/{}]`{}".format(player.progress, _duration, prog_bar_str), inline=True)
        e.add_field(name="Requested by:", value=vc.source.requester, inline=True)
        e.set_footer(text="Views {}, Likes {}, Dis-Likes {}".format(vc.source.view_count, vc.source.like_count, vc.source.dislike_count))
        e.set_thumbnail(url=vc.source.thumbnail)
        # player.np = await ctx.send(f'**Now Playing:** `{vc.source.title}` '
        #                            f'requested by `{vc.source.requester}` duration `{_duration}`\n👉`{vc.source.web_url}`')
        player.np = await ctx.send(embed=e)

    @commands.command()
    async def save(self, ctx):
        vc = ctx.voice_client
        with open('autoplaylist.txt', 'r') as f:
            songs = f.readlines()
        if vc.source.web_url + '\n' in songs:
            return await ctx.send('This song is already in the random songs playlist.')
        with open('autoplaylist.txt', 'a') as f:
            f.write(vc.source.web_url + '\n')
        await ctx.send('Saved ``{}`` to the random songs playlist.\n`{}`'.format(vc.source.title, vc.source.web_url))

    @commands.command(name='volume', aliases=['vol'])
    async def change_volume(self, ctx, *, vol: float):
        """Change the player volume.
        Parameters
        ------------
        volume: float or int [Required]
            The volume to set the player to in percentage. This must be between 1 and 100.
        """
        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!', delete_after=20)

        if not 0 < vol < 101:
            return await ctx.send('Please enter a value between 1 and 100.')

        player = self.get_player(ctx)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        await ctx.send(f'**`{ctx.author}`**: Set the volume to **{vol}%**')

    @commands.command(name='stop', aliases=['leave', 'disconnect'])
    async def stop_(self, ctx):
        """Stop the currently playing song and destroy the player.
        !Warning!
            This will destroy the player assigned to your guild, also deleting any queued songs and settings.
        """
        vc = ctx.voice_client
        if not ctx.author.voice:
            return await ctx.send('You need to be in a voice channel to use this.')
        if not ctx.author.voice.channel == vc.channel:
            await ctx.send('You need to be in the same channel as I am in to vote.', delete_after=20)
            return

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=20)
        members = 0
        for user in vc.channel.members:
            if not user.bot:
                members += 1

        player = self.get_player(ctx)

        if members == 1:
            await self.cleanup(ctx.guild)
            await ctx.send('Stopped playing.')
            player.stop_votes = []
        half_members = members / 2
        if members >= 2:
            if ctx.author.id in player.stop_votes:
                await ctx.send('You voted already, you need {} more votes to stop.'.format(int(half_members - len(player.stop_votes))))
                return
            player.stop_votes.append(ctx.author.id)
            await ctx.send('Voted to stop, you need {} more votes to stop.'.format(int(half_members - len(player.stop_votes))))
            if len(player.stop_votes) == int(members / 2):
                await self.cleanup(ctx.guild)
                player.stop_votes = []

    @commands.command()
    @commands.has_permissions(manage_channels=True)
    async def stopf(self, ctx):
        vc = ctx.voice_client
        if not ctx.author.voice:
            return await ctx.send('You need to be in a voice channel to use this.')
        if not ctx.author.voice.channel == vc.channel:
            await ctx.send('You need to be in the same channel as I am in to vote.', delete_after=20)
            return

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=20)
        player = self.get_player(ctx)
        await self.cleanup(ctx.guild)
        player.stop_votes = []
        await ctx.send('Stopped playing.')

    async def on_voice_state_update(self, member, before, after):
        vc = member.guild.voice_client
        if not vc:
            return
        is_about_me = member == member.guild.me or after.channel == vc.channel or before.channel == vc.channel
        members = 0
        for member in vc.channel.members:
            if not member.bot:
                members += 1
        if is_about_me and members == 0:
            if not vc or not vc.is_playing():
                return
            elif vc.is_paused():
                return
            vc.pause()

        elif is_about_me and members >= 1:
            if not vc or not vc.is_connected():
                return
            elif not vc.is_paused():
                return
            vc.resume()

def setup(bot):
    bot.add_cog(Music(bot))
