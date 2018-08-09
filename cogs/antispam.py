from discord.ext import commands
import discord

class AntiSpam():
    def __init__(self, bot):
        self.bot = bot

    async def on_message(self, message):
        if message.author.bot: return
        if message.guild.id == 264445053596991498:
            return
        print(message.author.name + ' ' +  message.guild.name + ':' + message.content)
        counter = 0
        messages = []
        async for entry in message.channel.history(limit=6):
            if entry.author == message.author:
                if message.created_at.minute * 60 +  message.created_at.second -5 < entry.created_at.minute * 60 + entry.created_at.second:
                    counter += 1
                    messages.append(message.id)
                if counter == 5:
                    # await message.channel.send('Stop spamming.')
                    if message.guild.id == 329993146651901952:
                        for msg in messages:
                            msge = await message.channel.get_message(msg)
                            await msge.delete()
                        await message.delete()
                        await message.channel.send('Could you please stop spamming?')
                    print('lol' + str(int(message.created_at.minute * 60 +  message.created_at.second)) + '/' + str(int(entry.created_at.minute * 60 + entry.created_at.second - 2)))


def setup(bot):
    bot.add_cog(AntiSpam(bot))
