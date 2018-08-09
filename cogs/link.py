from .utils import config
from discord.ext import commands
import json
import discord.utils

class guildInfo:
    def __init__(self, guild_id, channel):
        self.guild_id = guild_id
        self.channel = channel

    def __str__(self):
        output = []
        output.append('Channel: {0.prefix}'.format(self))

    def info_entries(self, ctx):
        data = [
            ('Channel', self.channel)
        ]
        return data

class guildEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, guildInfo):
            payload = obj.__dict__.copy()
            payload['__link__'] = True
            return payload
        return json.JSONEncoder.default(self, obj)

def guild_decoder(obj):
    if '__link__' in obj:
        return guildInfo(**obj)
    return obj

class Link:
    def __init__(self, bot):
        self.bot = bot
        self.config = config.Config('rooms.json', encoder=guildEncoder, object_hook=guild_decoder,
                                    loop=bot.loop, load_later=True)

    @commands.command(pass_context = True, invoke_without_command=True)
    @commands.has_permissions(manage_guild=True)
    async def link(self, ctx, *, channel_id : str = None):
        """Links a text channel to another. (This can be even in another guild I am in.)"""
        if channel_id is None:
            await ctx.send('You didn\'t tell me what channel to set the link to.')
            return
        elif channel_id == str(ctx.message.channel.id):
            await ctx.send('You can\'t link this channel to this channel.')
            return
        channel = self.config.get(str(ctx.message.channel.id))
        remote_channel = self.config.get(channel_id)
        if channel:
            approving = await ctx.send('This channel is already linked are you sure to proceed?')
            await approving.add_reaction('✅')
            await approving.add_reaction('❌')
            owner = self.bot.get_channel(int(channel_id)).guild.owner
            def check(reaction, user):
                return user == owner and str(reaction.emoji) in ['✅','❌']

            try:
                reaction, user = await self.bot.wait_for('reaction_add', check=check)
                if reaction.emoji == '✅':
                    await ctx.send('Continued...')
                elif reaction.emoji == '❌':
                    await ctx.send('Cancelled...')
                    return
            except:
                pass

        if remote_channel:
            await ctx.send('That channel is already linked to another channel.')
            return
        # await ctx.send('D')
        approving_channel = self.bot.get_channel(int(channel_id))
        approving = await approving_channel.send(f'{ctx.message.author} would like to link {ctx.message.channel.name} from {ctx.message.guild.name} to here.\nOnly reactions from owner are  counted.')
        await approving.add_reaction('✅')
        await approving.add_reaction('❌')
        owner = self.bot.get_channel(int(channel_id)).guild.owner
        await ctx.send('I have sent a request to the chat for the {} to approve.'.format(owner.name))
        def check(reaction, user):
            return user == owner and str(reaction.emoji) in ['✅','❌']

        try:
            reaction, user = await self.bot.wait_for('reaction_add', check=check)
            if reaction.emoji == '✅':
                await self.config.put(str(ctx.message.channel.id), channel_id)
                await self.config.put(channel_id, str(ctx.message.channel.id))
                await ctx.send('This channel has been linked to: ``{}``.'.format(self.bot.get_channel(int(channel_id)).name))
                channel = self.bot.get_channel(int(channel_id))
                await channel.send('This channel has been linked to: ``{}``.'.format(ctx.message.channel.name))
            elif reaction.emoji == '❌':
                await ctx.send('The owner did not approve the linking.')
        except:
            pass

    @commands.command()
    @commands.has_permissions(manage_guild=True)
    async def unlink(self, ctx):
        """Unlinks a textchannel from another."""
        with open('rooms.json') as f:
            data = json.load(f)
        linked_channel = data[str(ctx.message.channel.id)]
        channel = data[linked_channel]
        await self.config.put(str(ctx.message.channel.id), None)
        channel_id = self.bot.get_channel(int(linked_channel)).id
        await self.config.put(channel_id, None)
        await ctx.send('This channel has been unlinked from: ``{}``.'.format(self.bot.get_channel(int(channel)).name))
        channel = self.bot.get_channel(int(linked_channel))
        await channel.send('This channel has been unlinked from: ``{}``.'.format(ctx.message.channel.name))

    async def on_message(self, message):
        if message.author.bot: return
        if isinstance(message.channel, discord.DMChannel): return
        with open('prefixes.json') as file:
            data = json.load(file)
        if str(message.guild.id) in data:
            prefix = data[str(message.guild.id)]
        else:
            prefix = None
        if prefix is not None:
            if message.content.startswith(prefix): return
        if message.content.startswith('.'): return
        if message.content.startswith('<@460846291300122635> '): return
        with open('rooms.json') as f:
            data = json.load(f)
        if str(message.channel.id) in data:
            if data[str(message.channel.id)] is not None:
                e=discord.Embed(title="A message from ``{}`` at ``{}``".format(message.author.name, message.guild.name), color=discord.Color.magenta())
                e.add_field(name="Message:", value="{}".format(message.content), inline=True)
                data_channel = data[str(message.channel.id)]
                channel = self.bot.get_channel(int(data_channel))
                print(channel)
                await channel.send(embed=e)

    async def on_message_edit(self, before, after):
        if before.author.bot: return
        with open('rooms.json') as f:
            data = json.load(f)
        if before.channel.id in data:
            if data[before.channel.id] is not None:
                channel = self.bot.get_channel(int(data[before.channel.id]))
                await channel.send('``{}`` from ``{}`` edited:``{}``'.format(after.author.name, after.channel.guild.name, after.content))

def setup(bot):
    bot.add_cog(Link(bot))
