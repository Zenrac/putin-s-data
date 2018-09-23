from discord.ext import commands
import discord

class Call:
	def __init__(self):
		self.self = self

class Userphone:
	def __init__(self, bot):
		self.bot = bot



def setup(bot):
	bot.add_cog(Userphone(bot))