import discord
from discord.ext import commands
from discord.utils import get
from .utils import checks

class Settings:
	def __init__(self, bot, record):
		self.bot = bot
		self.id = record['id']
		self.blacklist = record['blacklist'] or False
		self._words = record['blacklisted_words'] or '[]'

	@property
	def words(self):
		__words = eval(self._words)
		return __words or []

	async def toggle_blacklist(self):
		self.blacklist = not self.blacklist
		await self.bot.pool.execute(f'update settings set blacklist={self.blacklist} where id={self.id};')

class Blacklist:
	def __init__(self, bot):
		self.bot = bot

	async def get_settings(self, id):
		record = await self.bot.pool.fetchrow(f'select * from settings where id={id}')
		if record is None:
			await self.bot.pool.execute(f'insert into settings (id) values ({id})')
			record = await self.bot.pool.fetchrow('SELECT * FROM settings WHERE id=$1;', id)
		return Settings(self.bot, record)

	async def check_perms(self, ctx, member):
		_perms = ctx.channel.permissions_for(member)
		return _perms.manage_messages

	async def on_message(self, message):
		if message.author.bot: return
		ctx = await self.bot.get_context(message)
		perms = await self.check_perms(ctx, message.author)
		if perms: return
		settings = await self.get_settings(ctx.guild.id)
		if not settings.blacklist: return

		words = message.content.split()
		for word in words:
			if word.lower() in settings.words:
				try:
					await message.delete()
					await message.author.send(f'You are not allowed to say ``{word}`` in {ctx.guild}!')
				except discord.Forbidden:
					pass
				break

	@commands.group()
	@checks.is_mod()
	async def blacklist(self, ctx):
		"""Shows the words that are currently in the blacklist."""
		if ctx.invoked_subcommand is None:
			settings = await self.get_settings(ctx.guild.id)

			if not settings.blacklist:
				return await ctx.send(f'Blacklist is not enabled.\nUse `{ctx.prefix}blacklist toggle` to enable it.')

			if not settings.words:
				return await ctx.send(f'There is nothing in the blacklist.\nUse `{ctx.prefix}blackist add <word>` to add a one.')

			e = discord.Embed(
				title="Blacklisted Words",
				description="\n".join(settings.words),
				color=ctx.author.top_role.color)
			await ctx.send(embed=e)

	@blacklist.command(name='toggle')
	@checks.is_mod()
	async def blacklist_toggle(self, ctx):
		"""Toggles backlist."""
		settings = await self.get_settings(ctx.guild.id)

		await settings.toggle_blacklist()

		state = 'enabled' if settings.blacklist else 'disabled'

		await ctx.send(f'Blacklist is now {state}.')

	@blacklist.command(name='add')
	@checks.is_mod()
	async def blacklist_add(self, ctx, *, words:str):
		"""Adds a word to the blacklist."""
		settings = await self.get_settings(ctx.guild.id)

		if not settings.blacklist:
			return await ctx.send(f'Blacklist is not enabled.\nUse `{ctx.prefix}blacklist toggle` to enable it.')

		words = words.replace("'", "\'").split()
		changes = []

		for word in words:
			if not word in settings.words:
				settings.words.append(word)
				changes.append(f'Added `{word}`')

		words = str(settings.words).replace('\'', '"')
		await ctx.db.execute(f"update settings set blacklisted_words=\'str({words})\' where id={ctx.guild.id};")
		await ctx.send(f'\n'.join(changes) or 'No changes.')

	@blacklist.command(name='remove')
	@checks.is_mod()
	async def blacklist_remove(self, ctx, *, words:str):
		"""Removes words from the blacklist."""
		settings = await self.get_settings(ctx.guild.id)

		if not settings.blacklist:
			return await ctx.send(f'Blacklist is not enabled.\nUse `{ctx.prefix}blacklist toggle` to enable it.')

		words = words.replace("'", "\'").split()
		changes = []

		for word in words:
			if word in settings.words:
				settings.words.remove(word)
				changes.append(f'Removed `{word}`')

		words = str(settings.words).replace('\'', '"')
		await ctx.db.execute(f"update settings set blacklisted_words=\'str({words})\' where id={ctx.guild.id};")
		await ctx.send(f'\n'.join(changes) or 'No changes.')

def setup(bot):
	bot.add_cog(Blacklist(bot))
