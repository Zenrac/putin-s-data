"""Money based commands."""
from discord.ext import commands

class Wallet:
	"""Money based commands."""
	def __init__(self, bot):
		"""Initializes the cog."""
		self.bot = bot

	@commands.command(aliases=['wallet'])
    async def balance(self, ctx):
        """Checks you wallet balance."""
        try:
            cash = await ctx.bot.pool.fetchrow(f'select cash from wallet where id={ctx.author.id}')

            if cash is None:
                await ctx.bot.pool.execute(f'insert into wallet values ({ctx.author.id}, 0);')
                return await ctx.send('You do not have a wallet yet.')

            if cash[0] is None:
                return await ctx.send('You do not have a wallet yet.')

            await ctx.send(f'You have {cash[0]} robux.')
        except Exception as e:
            await ctx.send(e)

    #indentation is too hard for ********.

def setup(bot):
	"""Adds the cog to the bot."""
	bot.add_cog(Wallet(bot))