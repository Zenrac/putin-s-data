from .utils import checks

from discord.ext import commands
from datetime import datetime as dtime
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

	async def get_warn(self, id, ctx):
		record = self.bot.pool.fetchrow('SELECT * FROM warns WHERE id=$1;', id)
		if not record:
			return None
		return Warn(self.bot, ctx, record)

	async def create_warn(self, ctx, member_id, reason):
		now = datetime.utcnow()
		id_int = now.year + now.second + now.minute + now.hour + member_id
		id = base64.b64encode(str(id_int).encode('utf-8'))
		query = """
				INSERT INTO warns (id, guild_id, member_id, warner_id, reason)
				VALUES ($1, $2, $3, $4, $5);
				"""
		await self.bot.pool.execute(query, id, ctx.guild_id, member_id, ctx.author.id, reason)

		record = await self.bot.pool.fetchrow('SELECT * FROM warns WHERE id=$1;', id)
		return Warn(self.bot, ctx, record)

	@commands.command()
	@checks.is_mod()
	async def warn(self, ctx, member:discord.Member=None, warn:str=None):
		if not member:
			return await ctx.send(f'{ctx.tick(False)} You forgot to tell me who to warn.')
		if not warn:
			warn = f'{member.display_name} (ID:{member.id}) warned by {ctx.author.display_name} (ID:{ctx.author.id})'

		await self.create_warn(ctx, member.id, reason)

		warn = await self.get_warn()

def setup(bot):
	bot.add_cog(Warns(bot))