import discord
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
		await ctx.send(f'Have nice time away from your keyboard {ctx.author.display_name} :wave:')

	async def on_message(self, message):
		if message.author.bot: return
		try:
			if message.mentions:
				mentions = []
				reasons = []
				for mention in message.mentions:
					if isinstance(mention, discord.Member):
						mentions.append(mention.display_name)
						reason = await self.bot.pool.fetchrow(f'select reason from afk where id={mention.id}')
						name = message.guild.get_member(mention.id)
						reasons.append((reason[0], name))
				mentions = ", ".join(mentions)
				reasons = "\n".join(f'{name}: {reason}' for name, reason in reasons)
				many = 'is' if len(mentions) == 1 else 'are'
				await message.channel.send(f'{mention} {many} afk.\nReasons:\n```{reasons}```')
		except Exception as e:
			await message.channel.send(e)
		record = await self.bot.pool.fetchrow(f'select * from afk where id={message.author.id};')
		if not record: return
		if not record[0]: return
		when = eval(record[2])
		afktime = dtime.utcnow() - when
		if afktime.seconds == 0: return
		m, s = divmod(afktime.seconds, 60)
		h = None
		if m >= 60:
			h, m = divmod(m, 60)
		if h:
			if h >= 2:
				hours = f'{h} hours '
			elif h == 0:
				hours = ''
			else:
				hours = f'{h} hour '
			##########################
			if m >= 2:
				minutes = f'{m} minutes '
			elif m == 0:
				minutes = ''
			else:
				minutes = f'{m} minute '
			##########################
			if s >= 2:
				seconds = f'{s} seconds'
			elif s == 0:
				seconds = ''
			else:
				seconds = f'{s} second'
			total_length = hours + minutes + seconds
		else:
			if m >= 2:
				minutes = f'{m} minutes '
			elif m == 0:
				minutes = ''
			else:
				minutes = f'{m} minute '
			##########################
			if s >= 2:
				seconds = f'{s} seconds'
			elif s == 0:
				seconds = ''
			else:
				seconds = f'{s} second'
			hours = ''
		await self.bot.pool.execute(f'delete from afk where id={message.author.id};')
		await message.channel.send(
			f'Good to see you again {message.author.display_name}!\n'
			f'I removed your afk status. You were afk for {hours}{minutes}{seconds}.')

def setup(bot):
	bot.add_cog(AFK(bot))