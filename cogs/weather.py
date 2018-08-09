from discord.ext import commands
import discord
import requests
import json

class Weather():
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def weather(self, ctx, *, city: str=None):
        """Gives current weather of a city you specify."""
        if city is None:
            await ctx.send('You forgot to specify a city.')
            return
        api_address = 'http://api.openweathermap.org/data/2.5/weather?appid=2dbbf6395eda172ea9aca9580b385924&q='
        units = '&units=metric'
        url = api_address + city
        data = requests.get(url).json()
        e = discord.Embed(title="Weather for {} {}:".format(data['name'], data['sys']['country']), description='{}'.format(data['weather'][0]['main'] + data['weather'][0]['description']), color=discord.Color.gold())
        e.add_field(name="Temperature now:", value="{}°C | {}°F".format(int(data['main']['temp']/17.222222), int(data['main']['temp'])), inline=True)
        e.add_field(name='Temperature max/min:', value='{}°C / {}°C | {}°F / {}°F'.format(int(data['main']['temp_max']/17.222222), int(data['main']['temp_min']/17.222222), int(data['main']['temp_max']), int(data['main']['temp_min'])))
        e.add_field(name="Air:", value="Pressure: {} | Humidity: {}".format(data['main']['pressure'], data['main']['humidity']), inline=True)
        e.add_field(name='Wind:', value='Speed: {} | Degree: {}'.format(data['wind']['speed'], data['wind']['deg']), inline=True)

        await ctx.send(embed=e)


def setup(bot):
    bot.add_cog(Weather(bot))
