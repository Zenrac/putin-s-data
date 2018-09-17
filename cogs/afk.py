from discord.ext import commands
from datetime import datetime as dtime
import datetime

class AFK:
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def afk(self, ctx, *, reason=None):
		if reason is None:
			reason = 'No reason specified.'
		when = dtime.utcnow()
		when = repr(when)
		if '@' in reason:
			return await ctx.send('You can\'t have `@` in the reason.')
		await ctx.db.execute(f'insert into afk values({ctx.author.id}, \'{reason}\', \'{when}\')')
		await ctx.send(f'Have nice time away fromyour keyboard {ctx.author.display_name} :wave:')

	async def on_message(self, message):
		try:
			record = await self.bot.pool.execute(f'select reason, when from afk where id={message.author.id};')
		except Exception as e:
			if message.channel.id = 482188217400033280:
				await message.channel.send(e)
		if not record: return
		if not record[0]: return
		await self.bot.pool.execute(f'delete from afk where id={message.id};')
		when = eval(record[1])
		afktime = dtime.utcnow() - when
		await message.channel.send(f'Good to see you again {message.author.display_name}!\n'
								   f'I removed your afk status. You were afk for {afktime}.')

def setup(bot):
	bot.add_cog(AFK(bot))