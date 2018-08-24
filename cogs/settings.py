from discord.ext import commands
import datetime
import discord
from .utils import db
import time

class settings_table(db.Table, table_name='settings'):
    id = db.Column(db.Integer(big=True), primary_key=True)
    logging_enabled = db.Column(db.Boolean, default=False)
    logging_channel = db.Column(db.Integer(big=True))

class Settings():
    def __init__(self, bot):
        self.bot = bot
    
    @commands.group()
    @commands.has_permissions(administrator=True)
    async def settings(self, ctx):
        if not ctx.invoked_subcommand:
            
            embed = discord.Embed(color=discord.Color.dark_teal(), title='Settings', description='Configure this server\'s settings.')
            embed.add_field(name="Logging", value="Sets up logging for the major things that can happen in the server.\n``settings logging``", inline=True)
            embed.add_field(name="Prefix", value="Configrues the prefix for this server.\n``settings prefix add <prefix>`` ``settings prefix remove <prefix>``\nPut the prefix in \"quotes\" to make it have spaces.", inline=True)
            embed.add_field(name="Starboard", value="Sets up a starboard.\n``starboard [name of the starboard channel]``")
            embed.set_footer(text="For more information search across the help menu.")
            embed.timestamp = datetime.datetime.utcnow()

            await ctx.send(embed=embed)

    @settings.command()
    async def logging(self, ctx, channel: discord.TextChannel):
        cmd = self.bot.get_command('enablelogging')
        await ctx.invoke(cmd, channel=channel)

    @settings.group()
    async def prefix(self, ctx):
        if not ctx.invoked_subcommand:
            cmd = self.bot.get_command('prefix')
            await ctx.invoke(cmd)

    @prefix.command()
    async def add(self, ctx, *, prefix: str):
        prefix = prefix.strip("\"")
        cmd = self.bot.get_command('prefix add')
        await ctx.invoke(cmd, prefix=prefix)

    @prefix.command()
    async def remove(self, ctx, *, prefix: str):
        prefix = prefix.strip("\"")
        cmd = self.bot.get_command('prefix remove')
        await ctx.invoke(cmd, prefix=prefix)
    
    @settings.command()
    async def starboard(self, ctx, *, name='starboard'):
        cmd = self.bot.get_command('starboard')
        await ctx.invoke(cmd, name=name)

    @commands.command(hidden=True)
    async def realping(self, ctx):
        before = time.monotonic()
        message = await ctx.send("Pong")
        ping = (time.monotonic() - before) * 1000
        await message.edit(content=f"My ping\nMSG :: {int(ping)}ms\nAPI :: {round(self.bot.latency * 1000)}ms")

def setup(bot):
    bot.add_cog(Settings(bot))
