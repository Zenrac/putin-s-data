from discord.ext import commands
from discord.utils import get
from .utils import checks

class Settings:
	def __init__(self, bot, record):
		self.bot = bot
		self.blacklist = record['blacklist'] or False
		self.words = eval(record['blacklisted_wors']) or []

	async def toggle_blacklist(self, id):
		self.blacklist = not self.blacklist
		await self.bot.pool.execute(f'update settings set blacklist={self.blacklist};')

class Blacklist:
	def __init__(self, bot):
		self.bot = bot

	async def get_settings(self, id):
		record = await self.bot.pool.fetchrow(f'select * from settings where id={id}')
		return Settings(self.bot, record)

	async def check_perms(self, ctx, member):
		_perms = ctx.channel.permissions_for(member)
		return _perms.manage_messages

	async def on_message(self, message):
		if not check_perms(): return
		settings = await self.get_settings(ctx.guild.id)
		if not settings.blacklist: return

		ctx = await self.bot.get_context(message)
		words = message.content.split()
		for word in words:
			if word in settings.words:
				try:
					await message.delete()
					await message.author.send(f'You are not allowed to say {word} in {ctx.guild}!')
				except discord.Forbidden:
					pass
				break

	@commands.group()
	@checks.is_mod()
	async def blacklist(self, ctx):
		settings = await get_settings(ctx.guild.id)

		if not settings.blacklist:
			return await ctx.send(f'Blacklist is not enabled.\nUse `{ctx.prefix}blacklist toggle` to enable it.')

		if not settings.words:
			return await ctx.send(f'There is nothing in the word blaclist.\nUse `{ctx.prefix}blackist add <word>` to add a one.')

		e = discord.Embed(
			title="Blacklisted Words",
			description="\n".join(settings.words),
			color=ctx.author.top_role.color)
		await ctx.send(embed=e)

	@blacklist.command(name='toggle')
	@checks.is_mod()
	async def blacklist_toggle(self, ctx):
		settings = await self.get_settings(ctx.guild.id)

		await settings.toggle_blacklist()

		state = 'enabled' if settings.blacklist else 'disabled'

		await ctx.send(f'Blacklist is now {state}.')

	@blacklist.command(name='add')
	@checks.is_mod()
	async def blacklist_add(self, ctx, *, words:str):
		settings = await self.get_settings(ctx.guild.id)

		if not settings.blacklist:
			return await ctx.send(f'Blacklist is not enabled.\n`{ctx.prefix}blacklist toggle` to enable it.')

		words = words.split()
		changes = []

		for word in words:
			if not word in settings.words:
				settings.words.append(word)
				changes.append(f'Added `{word}`')

		await ctx.send(f'\n'.join(changes))

	@blacklist.command(name='remove')
	@checks.is_mod()
	async def blacklist_remove(self, ctx, *, words:str):
		settings = await self.get_settings(ctx.guild.id)

		if not settings.blacklist:
			return await ctx.send(f'Blacklist is not enabled.\n`{ctx.prefix}blacklist toggle` to enable it.')

		words = words.split()
		changes = []

		for word in words:
			if not word in settings.words:
				settings.words.remove(word)
				changes.append(f'Removed `{word}`')

		await ctx.send(f'\n'.join(changes))

def setup(bot):
	bot.add_cog(Blacklist(bot))