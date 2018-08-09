from .utils import config
from discord.ext import commands
import json
import discord.utils

class guildInfo:
    def __init__(self, guild_id, prefix):
        self.guild_id = guild_id
        self.prefix = prefix

    def __str__(self):
        output = []
        output.append('Prefix: {0.prefix}'.format(self))

    def info_entries(self, ctx):
        data = [
            ('Prefix', self.prefix)
        ]
        guilds = ctx.bot.guilds
        return data

class guildEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, guildInfo):
            payload = obj.__dict__.copy()
            payload['__guild__'] = True
            return payload
        return json.JSONEncoder.default(self, obj)

def guild_decoder(obj):
    if '__guild__' in obj:
        return guildInfo(**obj)
    return obj

class Prefix:
    def __init__(self, bot):
        self.bot = bot
        self.config = config.Config('prefixes.json', encoder=guildEncoder, object_hook=guild_decoder,
                                    loop=bot.loop, load_later=True)
    def get_prefix(self, guild):
        db = self.config.get(guild_id)
        entry = db.get(prefix)
        if entry is None:
            return '.'
        return entry

    def get_pre(guild):
        pre = get_prefix(self, guild)
        return pre

    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def setprefix(self, ctx, *, prefix : str = None):
        """Sets a guild specific prefix."""
        if prefix is None:
            await ctx.send('You didn\'t tell me what to set the prefix.')
            return
        await self.config.put(str(ctx.message.guild.id), prefix)
        await ctx.send('Prefix has been set to ``{}`` on this guild.\nMy original prefix ``.`` or mentioning me works still too.'.format(prefix))

def setup(bot):
    bot.add_cog(Prefix(bot))
