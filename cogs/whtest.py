from discord.ext import commands
from discord import Embed, Webhook, AsyncWebhookAdapter, PermissionOverwrite, TextChannel
import asyncio
import aiohttp

from .utils import checks

class SuggestionConfig:
	def __init__(self, bot, record):
		self.bot = bot
		self.id = ['id']
		self.wh_url = record['wh_url']

	async def send(self, ctx, suggestion):
		async with aiohttp.ClientSession() as cs:
			webhook = Webhook.from_url(self.wh_url, adapter=AsyncWebhookAdapter(cs))
			e = Embed(title="Suggestion", description=suggestion)
			await webhook.send(embed=e, username=ctx.author.display_name, avatar_url=ctx.author.avatar_url)

		# _ch = self.bot.get_guild(self.id).get_channel(self.channel)
		# self._webhook = await _ch.create_webhook('suggestion-webhook')


class Suggestion:
	def __init__(self, bot):
		self.bot = bot

	async def get_config(self, guild_id):
		record = await self.bot.pool.fetchrow('SELECT * FROM suggestions WHERE id=$1;', id)
		if not record:
			return None
		return SuggestionConfig(self.bot, record)

	@commands.group()
	async def suggest(self, ctx, *, text:str=None):
		config = await self.get_config(ctx.guild.id)
		if not config:
			return await ctx.send(f'{ctx.tick(False)} This server does not have suggestions enabled.')

		if not text:
			return await ctx.send(f'{ctx.tick(False)} You forgot the actual suggestion.')

		await config.send(ctx, text)

		await ctx.send(f'{ctx.tick(True)} Suggestion sent.')

	@suggest.command(name='enable')
	@checks.is_mod()
	async def suggest_enable(self, ctx, discord.TextChannel=None):
		if not channel:
			overwrites = {
			guild.default_role: PermissionOverwrite(send_messages=False)
			}
			channel = await ctx.guild.create_text_channel('suggestions', overwrites=overwrites)

		webhook = await channel.create_webhook('suggestion-webhook')
		await ctx.db.execute('INSERT INTO suggestions VALUES ($1)', webhook.url)

		await ctx.send(f'{ctx.tick(True)} Suggestions are now enabled.')

def setup(bot):
	bot.add_cog(Suggestion(bot))