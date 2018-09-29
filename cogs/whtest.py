from discord.ext import commands
from discord import Embed, Webhook, AsyncWebhookAdapter
import asyncio
import aiohttp

from .utils import checks

class WHTest:
	def __init__(self, bot):
		self.bot = bot

	async def whsend(self, _url, _username, _msg, _avatar_url):
		async with aiohttp.ClientSession() as cs:
			webhook = Webhook.from_url(_url, adapter=AsyncWebhookAdapter(cs))
			await webhook.send(_msg, username=_username, avatar_url=_avatar_url)

	@commands.command()
	@checks.is_mod()
	async def wh(self, ctx, *, text:str):
		user = await self.bot.get_user_info(257262778602094593)
		await self.whsend(
			'https://discordapp.com/api/webhooks/495658670693154816/7XrwT81R5BXGKn2IUIafEi795fXUBs19YY_1VAylzudcIvqBKZr_5HS7sE8ywuKBZsO3',
			user.display_name,
			text,
			user.avatar_url)

def setup(bot):
	bot.add_cog(WHTest(bot))