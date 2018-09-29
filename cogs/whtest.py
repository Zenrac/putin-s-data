from discord.ext import commands
from discord import Embed, Webhook, AsyncWebhookAdapter
import asyncio
import aiohttp

from .utils import checks

class WHTest:
	def __init__(self, bot):
		self.bot = bot

	async def whsend(self, _url, _msg, _username, _avatar_url):
		async with aiohttp.ClientSession() as cs:
			webhook = Webhook.from_url(_url, adapter=AsyncWebhookAdapter(cs))
			await webhook.send(_msg, username=_username, avatar_url=_avatar_url)

	@commands.command()
	@checks.is_mod()
	async def wh(self, ctx):
		await self.whsend(
			'https://discordapp.com/api/webhooks/495654255470968842/gJge2raRFT6AKa1jInJCliZPJ1RwxdqR20XRogM_LK-VByZUQYywvcKiWOenzn3a35n0',
			ctx.author.display_name,
			ctx.message.clean_content,
			ctx.author.avatar_url)

def setup(bot):
	bot.add_cog(WHTest(bot))