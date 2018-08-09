from discord.ext import commands
import discord
import asyncio
import aiohttp
import json

class Anime():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def anime(self, ctx, *, search_string: str=None):
        """Searches for anime from anilist.co"""
        query = '''
        query ($id: Int, $page: Int, $perPage: Int, $search: String) {
            Page (page: $page, perPage: $perPage) {
                pageInfo {
                    total
                    currentPage
                    lastPage
                    hasNextPage
                    perPage
                }
                media (id: $id, search: $search) {
                    id
                    title {
                        english
                    }
                    description
                    season
                    episodes
                    genres
                    duration
                    bannerImage
                    siteUrl
                }
            }
        }
        '''
        variables = {
            'search': search_string,
            'page': 1,
            'perPage': 1
        }
        url = 'https://graphql.anilist.co'


        async with aiohttp.ClientSession() as cs:
            async with cs.post(url, json={'query': query, 'variables': variables}) as res:
                response = await res.json()

        # response = requests.post(url, json={'query': query, 'variables': variables}).json()
        # await ctx.send(response)
        if not response:
            await ctx.send('I could not find that from the database.')
            return
        if not response['data']['Page']['media']:
            await ctx.send('I could not find that from the database.')
            return
        title = list(map(lambda x: x["title"]["english"], response["data"]["Page"]["media"]))
        genres = list(map(lambda x: x["genres"], response["data"]["Page"]["media"]))
        description = response["data"]["Page"]["media"][0]['description'].replace('<br>', '')
        episodes = response["data"]["Page"]["media"][0]['episodes']
        season = response["data"]["Page"]["media"][0]['season']
        duration = response["data"]["Page"]["media"][0]['duration']
        # anilist = response["data"]["Page"]["media"]['siteUrl']
        # coverImage = response["data"]["Page"]["media"][0]['coverImage']
        bannerImage = response["data"]["Page"]["media"][0]['bannerImage']
        # await ctx.send(genres[0])
        genre_string = ' | '.join(genres[0])
        e = discord.Embed(title=title[0], color=discord.Color.green())
        e.add_field(name="Description:", value="{}".format(description), inline=False)
        e.add_field(name="Season:", value="{}".format(season), inline=True)
        e.add_field(name="Episodes:", value="{}".format(episodes), inline=True)
        e.add_field(name="Duration (mintues/episode):", value="{}".format(duration), inline=True)
        e.add_field(name="Genre(s):", value="{}".format(genre_string), inline=True)
        # e.add_field(name="Link:", value="[Anilist]({})".format(streaming, anilist), inline=True)
        if bannerImage:
            e.set_image(url=bannerImage)
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(Anime(bot))
