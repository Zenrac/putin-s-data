from .utils import checks

from discord.ext import commands
from datetime import datetime
import discord
import base64

class Warn:
	def __init__(self, bot, ctx, record):
		self.bot = bot
		self.ctx = ctx
		self.record = record
		self.id = record['id']
		self.guild_id = record['guild_id']
		self.member_id = record['member_id']
		self.warner_id = record['warner_id']
		self.warn = record['warn']

	async def delete(self):
		await self.bot.pool.execute('DELETE FROM warns WHERE id=$;', self.id)

	async def edit_reason(self, reason):
		await self.bot.pool.execute('UPDATE warns SET reason=$1 where id=$2;', reason, self.id)

class Warns:
	def __init__(self, bot):
		self.bot = bot

	async def get_warn(self, ctx, id):
		record = self.bot.pool.fetchrow('SELECT * FROM warns WHERE id=$1;', id)
		if not record:
			return None
		return Warn(self.bot, ctx, record)

	async def create_warn(self, ctx, member, reason):
		now = datetime.utcnow()
		id_int = now.year + now.second + now.minute + now.hour + member.id
		id = base64.b64encode(str(id_int).encode('utf-8'))
		id = str(id).replace('b\'', '', 1)
		id = id.strip("'")
		query = """
				INSERT INTO warns (id, guild_id, member_id, warner_id, warn)
				VALUES ($1, $2, $3, $4, $5);
				"""
		await self.bot.pool.execute(query, id, ctx.guild.id, member.id, ctx.author.id, reason)

		record = await self.bot.pool.fetchrow('SELECT * FROM warns WHERE id=$1;', str(id))
		return Warn(self.bot, ctx, record)

	@commands.group()
	@checks.is_mod()
	async def warn(self, ctx, member:discord.Member=None, *, warn:str=None):
		if ctx.invoked_subcommand is None:
			if not member:
				return await ctx.send(f'{ctx.tick(False)} You forgot to tell me who to warn.')
			if not warn:
				warn = f'{member.display_name} (ID:{member.id}) warned by {ctx.author.display_name} (ID:{ctx.author.id})'

			warn = await self.create_warn(ctx, member, warn)

			await ctx.send(f'{ctx.tick(True)} Warned {member.display_name}. Incident ``#{warn.id}``')

	@warn.command()
	async def warn_show(self, ctx, id:str=None):
		await ctx.send('gg')
		warn = await self.get_warn(ctx, id)

		if not warn:
			return await ctx.send(f'{ctx.tick(False)} Warn not found.')

		warned = ctx.guild.get_member(warn.member_id)
		if not warned:
			return await ctx.send(f'{ctx.tick(False)} Warned member not found.')
		warner = ctx.guild.get_member(warn.warner_id) or await self.bot.get_user_info(warn.warner_id)

		e = discord.Embed(description=warn.warn, colour=warned.top_role.color)
		e.set_author(name=warner.display_name, icon_url=warner.avatar_url)

		await ctx.send(embed=e)

	@commands.command()
	async def warns(self, ctx, member:discord.Member=None):
		pass

def setup(bot):
	bot.add_cog(Warns(bot))