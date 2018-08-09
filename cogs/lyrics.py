import asyncio
import aiohttp
import json
from .utils.lyrics_api import *
from discord.ext import commands
from bs4 import BeautifulSoup
import re
import discord

class Lyrics():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def badlyrics(self, ctx):
        """Gives you lyrics for a song from Musixmatch which only returns 30% of the lyrics..."""
        artist_name = None
        track_name = None
        if artist_name is None:
            await ctx.send('What is the artist\'s name?\nYou have 1 minute to say it.')
            def pred(m):
                return m.author == ctx.message.author and m.channel == ctx.message.channel

            artist = await self.bot.wait_for('message', timeout=60.0, check=pred)
            try:
                artist_name = artist.content
            except asyncio.TimeoutError:
                await ctx.send('You took too long. Cya :wave:')
        if track_name is None:
            await ctx.send('Alright, what\'s the song\'s name?\nYou have 1 minute to say it.')
            def pred(m):
                return m.author == ctx.message.author and m.channel == ctx.message.channel

            track = await self.bot.wait_for('message', timeout=60.0, check=pred)
            try:
                track_name = track.content
            except asyncio.TimeoutError:
                await ctx.send('You took too long. Cya :wave:')
        async with ctx.channel.typing():
            api_call = base_url + lyrics_matcher + format_url + artist_search_parameter + artist_name + track_search_parameter + track_name + api_key
            #calls the api
            async with aiohttp.ClientSession() as cs:
                async with cs.get(api_call) as res:
                    data = await res.json()
            if data['message']['header']['status_code'] == 404:
                await ctx.send('I am sorry, but I could not find any lyrics from Musixmatch for song ``{}`` by ``{}``.'.format(track_name, artist_name))
            if data['message']['body']['lyrics']['instrumental'] == 1:
                await ctx.send('This song is instrumental, so no lyrics for it.')
                return
            if data['message']['body']['lyrics']['explicit'] == 1:
                await ctx.send('Beware these lyrics are explicit but,')
            data = data['message']['body']
            lang = data['lyrics']['lyrics_language_description']
            await ctx.send('Here\'s the lyrics for the song ``{}`` by ``{}`` from Musixmatch. It is written in ``{}``:\n```{}```'.format(track_name, artist_name, lang, data['lyrics']['lyrics_body'].replace('******* This Lyrics is NOT for Commercial use *******', '')))

    @commands.command()
    async def lyrics(self, ctx):
        """Gives you lyrics for a song from Google's Genius.com."""
        artist_name = None
        track_name = None
        if artist_name is None:
            await ctx.send('What is the artist\'s name?\nYou have 1 minute to say it.')
            def pred(m):
                return m.author == ctx.message.author and m.channel == ctx.message.channel

            artist = await self.bot.wait_for('message', timeout=60.0, check=pred)
            try:
                artist_name = artist.content
            except asyncio.TimeoutError:
                await ctx.send('You took too long. Cya :wave:')
        if track_name is None:
            await ctx.send('Alright, what\'s the song\'s name?\nYou have 1 minute to say it.')
            def pred(m):
                return m.author == ctx.message.author and m.channel == ctx.message.channel

            track = await self.bot.wait_for('message', timeout=60.0, check=pred)
            try:
                track_name = track.content
            except asyncio.TimeoutError:
                await ctx.send('You took too long. Cya :wave:')
        await ctx.trigger_typing()
        async def request_song_info(song_title, artist_name):
            base_url = 'https://api.genius.com'
            headers = {'Authorization': 'Bearer ' + 'obiZ5OI5scEi2vupO_VyKfm99Jos1-zMUrv44pXVOxy7oVlDAdCrZUR-PpPCKD0H'}
            search_url = base_url + '/search'
            data = {'q': song_title + ' ' + artist_name}
            async with aiohttp.ClientSession() as cs:
                async with cs.get(search_url, data=data, headers=headers) as res:
                    response = await res.json()

            return response
        json = await request_song_info(track_name, artist_name)
        # json = response
        remote_song_info = None

        for hit in json['response']['hits']:
            if artist_name.lower() in hit['result']['primary_artist']['name'].lower():
                remote_song_info = hit
                break
        if remote_song_info:
            song_url = remote_song_info['result']['url']
        async def scrap_song_url(url):
            async with aiohttp.ClientSession() as cs:
                async with cs.get(url) as res:
                    print(res)
                    page = await res.text()
                    print(page)
            html = BeautifulSoup(page, 'html.parser')
            lyrics = html.find('div', class_='lyrics').get_text()

            return lyrics
        print(song_url)
        lyrics = await scrap_song_url(song_url)
        e = discord.Embed(title='Lyrics', color=discord.Color.blue())
        def split_str_into_len(s, l=1000):
            """ Split a string into chunks of length l """
            return [s[i:i+l] for i in range(0, len(s), l)]
        lyrics = split_str_into_len(lyrics)
        gg = 0
        for item in lyrics:
            print(item)
            gg += 1
            e.add_field(name=str(gg), value=item, inline=True)
        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Lyrics(bot))
