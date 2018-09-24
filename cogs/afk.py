import discord
from discord.ext import commands
from datetime import datetime as dtime
import datetime

class AFK:
	"""AFK status commands."""
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	async def afk(self, ctx, *, reason=None):
		"""Sets your afk status reason is optional.
		This means that if someone mentions you they get
		a message that you are afk."""
		if reason is None:
			reason = 'No reason specified.'
		reason = reason.replace("'", "\'")
		when = dtime.utcnow()
		when = repr(when)
		if '@' in reason:
			return await ctx.send('You can\'t have `@` in the reason.')
		await ctx.db.execute(f'insert into afk values({ctx.author.id}, \'{reason}\', \'{when}\')')
		await ctx.send(f'Have nice time away from your keyboard {ctx.author.display_name} :wave:')

	async def on_message(self, message):
		if message.author.bot: return
		if message.mentions:
			mentions = []
			reasons = []
			for mention in message.mentions:
				if isinstance(mention, discord.Member):
					mentions.append(mention.display_name)
					record = await self.bot.pool.fetchrow(f'select * from afk where id={mention.id}')
					if reason:
						name = message.guild.get_member(mention.id)
						when = eval(record['when'])
						afk_time = dtime.utcnow() - when
						reasons.append((record['reason'], name, afk_time))
			many = 'is' if len(mentions) == 1 else 'are'
			s = '' if len(mentions) == 1 else 's'
			reasons = "\n".join(f'{name}: {reason} ({afk_time})' for name, reason, afk_time in reasons)
			mentions = ", ".join(mentions)
			if reasons:
				try:
					await message.channel.send(f'{mention} {many} afk.\nReason{s}:\n```{reasons}```')
				except:
					pass
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