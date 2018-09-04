from discord.ext import commands
import discord
import json

from .utils import config

class CommandInfo:
    def __init__(self, invoke, reply, owner_id, **kwargs):
        self.invoke = invoke
        self.reply = reply
        self.owner_id = owner_id
        self.uses = kwargs.pop('uses', 0)
        self.location = kwargs.pop('location')

    @property
    def is_generic(self):
        return self.loaction == 'generic'

    def __str__(self):
        return self.reply

    def info_entries(self, ctx):
        data = [
            ('Invoke', self.invoke),
            ('Uses', self.uses),
            ('Type', 'Generic' if self.is_generic else 'Guild-specific')
        ]

        members = ctx.bot.get_all_members() if self.is_generic else ctx.message.guild.members
        owner = discord.utils.get(members, id=self.owner_id)
        data.append(('Owner', owner.name if owner is not None else '<Not Found>'))
        data.append(('Owner ID', self.owner_id))
        return data

class CommandEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, CommandInfo):
            payload = obj.__dict__.copy()
            payload['__command__'] = True
            return payload
        return json.JSONEncoder.default(self, obj)

def command_decoder(obj):
    if '__command__' in obj:
        return CommandInfo(**obj)
    return obj

class Command():
    def __init__(self, bot):
        self.bot = bot
        self.config = config.Config('commands.json', encoder=CommandEncoder, object_hook=command_decoder,
                                                    loop=bot.loop, load_later=True)

    def get_command(self, guild, invoke):
        generic = self.config.get('generic', {})
        if guild is None:
            return generic.get(invoke)

        db = self.config.get(str(guild.id))
        if db is None:
            return generic.get(invoke)

        entry = db.get(invoke)
        if entry is None:
            return generic.get(invoke)
        return entry

    def get_database_location(self, message):
        return 'generic' if isinstance(message.channel, discord.DMChannel) else str(message.guild.id)


    def get_possible_commands(self, guild):
        generic = self.config.get('generic', {}).copy()
        if guild is None:
            return generic

        generic.update(self.config.get(str(guild.id), {}))
        return generic

    @commands.group(name='command')
    async def ccommand(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send('Use ``{}help command``'.format(ctx.prefix))

    @ccommand.command()
    async def create(self, ctx, invoke: str, *, reply: str):
        """Creates a new custom command owned by you."""
        reply = reply.replace('@', '@\u200b')
        lookup = invoke.lower()
        location = self.get_database_location(ctx.message)
        db = self.config.get(location, {})
        __commands = [__ocommand.name for __ocommand in self.bot.commands]
        if invoke.lower() in __commands:
            return await ctx.send('That is an original command.')
        if lookup in db:
            await ctx.send('A command with that invokation already exists.')
            return
        # await ctx.send(CommandInfo(invoke, reply, location=location))
        db[lookup] = CommandInfo(lookup, reply, str(ctx.author.id), location=location)
        await self.config.put(location, db)
        await ctx.send(f'Your custom command has been created, invoke it with ``{invoke}``.')

    @ccommand.command(hidden=True)
    @commands.is_owner()
    async def generic(self, ctx, invoke: str, *, reply: str=None):
        """Makes a global command."""
        lookup = invoke.lower()
        db = self.config.get('generic', {})
        __commands = [__ocommand.name for __ocommand in self.bot.commands]
        if invoke.lower() in __commands:
            return await ctx.send('That is an original command.')
        if lookup in db:
            await ctx.send('A command with that invoke already exists.')
            return

        db[lookup] = CommandInfo(invoke, reply, str(ctx.author.id), location='generic')
        await self.config.put('generic', db)
        await ctx.send('The command has been created.')

    @ccommand.command()
    async def make(self, ctx):
        """Interactively makes a custom command for you.
        """
        message = ctx.message
        location = self.get_database_location(message)
        db = self.config.get(location, {})
        await ctx.send('Hi there {}. What would you like the invoke of the command to be?'.format(message.author.mention))
        def pred(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel

        invoke = await self.bot.wait_for('message', timeout=60.0, check=pred)
        __commands = [__ocommand.name for __ocommand in self.bot.commands]
        if invoke.content.lower() in __commands:
            return await ctx.send('That is an original command.')
        lookup = invoke.content.lower()
        if lookup in db:
            fmt = 'Sorry. A command with that invoke exists already. Use {0.prefix}ccommand make again.'
            await ctx.send(fmt.format(ctx))
            return

        await ctx.send('Ok. So the name is {0.content}. What about the command\'s reply?'.format(invoke))
        def pred(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel

        reply = await self.bot.wait_for('message', timeout=60.0, check=pred)

        reply = reply.content.replace('@everyone', '@\u200beveryone')
        db[lookup] = CommandInfo(invoke.content, reply, str(ctx.author.id), location=location)
        await self.config.put(location, db)
        await ctx.send('Dude you just made your \"{}\" command. Invoke it with it\'s name.'.format(invoke.content))

    @ccommand.command(aliases=['update'])
    async def edit(self, ctx, invoke: str, *, reply: str):
        """Modifies an existing command."""
        lookup = invoke.lower()
        guild = ctx.guild
        command = self.get_command(guild, lookup)

        if command.owner_id != str(ctx.author.id):
            await ctx.send('Only the command owner can edit the command.')
            return

        if command is None:
            await ctx.send('The command "{}" does not exist.'.format(name))
            return

        db = self.config.get(command.location)
        command.reply = reply
        await self.config.put(command.location, db)
        await ctx.send('Command successfully edited.')

    @ccommand.command(aliases=['delete'])
    async def remove(self, ctx, *, invoke: str):
        """Removes a command."""
        lookup = invoke.lower()
        guild = ctx.guild
        _command = self.get_command(guild, lookup)

        if _command is None:
            return await ctx.send('That command does not exist.')

        # can_delete = commands.has_permissions(manage_messages=True)
        # can_delete = perms.manage_messages
        can_delete = _command.owner_id == str(ctx.author.id)
        if not can_delete:
            return await ctx.send('You do not have permissions to delete that command.')

        db = self.config.get(_command.location)
        del db[lookup]
        await self.config.put(_command.reply, db)
        await ctx.send('Command successfully deleted.')

    @ccommand.command(aliases=['fdelete'])
    @commands.has_permissions(manage_messages=True)
    async def fremove(self, ctx, *, invoke: str):
        """Force removes a command."""
        lookup = invoke.lower()
        guild = ctx.guild
        _command = self.get_command(guild, lookup)

        if _command is None:
            return await ctx.send('That command does not exist.')

        # can_delete = commands.has_permissions(manage_messages=True)
        # can_delete = perms.manage_messages
        # can_delete = _command.owner_id == str(ctx.author.id)
        # if not can_delete:
        #     return await ctx.send('You do not have permissions to delete that command.')

        db = self.config.get(_command.location)
        del db[lookup]
        await self.config.put(_command.reply, db)
        await ctx.send('Command successfully deleted.')

    @ccommand.command(name='list')
    async def _list(self, ctx):
        """Lists all the commands you own."""
        owner = str(ctx.author.id)
        guild = ctx.guild
        _commands = [_command.invoke for _command in self.config.get('generic', {}).values() if _command.owner_id == owner]
        if guild is not None:
            _commands.extend(_command.invoke for _command in self.config.get(str(guild.id), {}).values() if _command.owner_id == owner)

        if _commands:
            fmt = ':mag_right: | You have the following commands:\n{}'
            await ctx.send(fmt.format(', '.join(_commands)))
        else:
            await ctx.send('You don\'t have any commands.')

    async def on_message(self, message):
        if message.author.bot: return
       
        
        if message.content.startswith('.'):
            invoke = message.content.replace('.', '', 1)
            # await message.channel.send(invoke)
            location = self.get_database_location(message)
            db = self.config.get(location, {})
            guild = message.guild
            if invoke in db:
                _command = self.get_command(guild, invoke)
                command_reply = _command.reply
                if '{user}' in _command.reply:
                    command_reply = command_reply.replace('{user}', message.author.name)
                if '{user_avatar}' in _command.reply:
                    command_reply = command_reply.replace('{user_avatar}', message.author.avatar_url_as(format='png', size=1024))
                if '{server}' in _command.reply:
                    command_reply = command_reply.replace('{server}', message.guild.name)
                if '{channel}' in _command.reply:
                    command_reply = command_reply.replace('{channel}', message.channel.name)
                if '{members}' in _command.reply:
                    command_reply = command_reply.replace('{members}', str(len(message.guild.members)))
                if '{channels}' in _command.reply:
                    command_reply = command_reply.replace('{channels}', str(len(message.guild.channels)))
                if '{server_icon}' in _command.reply:
                    command_reply = command_reply.replace('{server_icon}', message.guild.icon_url)
                await message.channel.send(command_reply)
        
        if message.content.startswith('<@460846291300122635> '):
            invoke = message.content.replace('<@460846291300122635> ', '', 1)
            # await message.channel.send(invoke)
            location = self.get_database_location(message)
            db = self.config.get(location, {})
            guild = message.guild
            if invoke in db:
                _command = self.get_command(guild, invoke)
                command_reply = _command.reply
                if '{user}' in _command.reply:
                    command_reply = command_reply.replace('{user}', message.author.name)
                if '{user_avatar}' in _command.reply:
                    command_reply = command_reply.replace('{user_avatar}', message.author.avatar_url_as(format='png', size=1024))
                if '{server}' in _command.reply:
                    command_reply = command_reply.replace('{server}', message.guild.name)
                if '{channel}' in _command.reply:
                    command_reply = command_reply.replace('{channel}', message.channel.name)
                if '{members}' in _command.reply:
                    command_reply = command_reply.replace('{members}', str(len(message.guild.members)))
                if '{channels}' in _command.reply:
                    command_reply = command_reply.replace('{channels}', str(len(message.guild.channels)))
                if '{server_icon}' in _command.reply:
                    command_reply = command_reply.replace('{server_icon}', message.guild.icon_url)
                await message.channel.send(command_reply)
            
def setup(bot):
    bot.add_cog(Command(bot))
