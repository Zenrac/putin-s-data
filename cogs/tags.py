from .utils import config, formats
from discord.ext import commands
import json
import discord.utils

class TagInfo:
    def __init__(self, name, content, owner_id, **kwargs):
        self.name = name
        self.content = content
        self.owner_id = owner_id
        self.uses = kwargs.pop('uses', 0)
        self.location = kwargs.pop('location')

    @property
    def is_generic(self):
        return self.loaction == 'generic'

    def __str__(self):
        return self.content

    def info_entries(self, ctx):
        data = [
            ('Name', self.name),
            ('Uses', self.uses),
            ('Type', 'Generic' if self.is_generic else 'Guild-specific')
        ]

        members = ctx.bot.get_all_members() if self.is_generic else ctx.message.guild.members
        owner = discord.utils.get(members, id=self.owner_id)
        data.append(('Owner', owner.name if owner is not None else '<Not Found>'))
        data.append(('Owner ID', self.owner_id))
        return data

class TagEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, TagInfo):
            payload = obj.__dict__.copy()
            payload['__tag__'] = True
            return payload
        return json.JSONEncoder.default(self, obj)

def tag_decoder(obj):
    if '__tag__' in obj:
        return TagInfo(**obj)
    return obj

class Tags:
    """The tag realted commands."""

    def __init__(self, bot):
        self.bot = bot
        self.config = config.Config('tags.json', encoder=TagEncoder, object_hook=tag_decoder,
                                                 loop=bot.loop, load_later=True)
    def get_tag(self, guild, name):

        generic = self.config.get('generic', {})
        if guild is None:
            return generic.get(name)

        db = self.config.get(str(guild.id))
        if db is None:
            return generic.get(name)

        entry = db.get(name)
        if entry is None:
            return generic.get(name)
        return entry

    def get_database_location(self, message):
        return 'generic' if isinstance(message.channel, discord.DMChannel) else str(message.guild.id)

    def get_possible_tags(self, guild):
        """Returns a dict of possible tags that the guild can execute.

        If this is a private message then onlu the generic tags are possible.
        Guild specific tags will override the generic tags.
        """
        generic = self.config.get('generic', {}).copy()
        if guild is None:
            return generic

        generic.update(self.config.get(str(guild.id), {}))
        return generic

    @commands.group(invoke_without_command=True)
    async def tag(self, ctx, *, name : str = None):
        """Allows you to tag text for later retrieval. Use ``(prefix)help tag`` for more info.

        If a subcommand is not called the this will search the tag database
        for the tag requested. If a tag is not specified then the bot will
        prompt you to create one interactively.
        """
        if name is None:
            await ctx.invoke(self.make)
        lookup = name.lower()
        guild = ctx.message.guild
        tag = self.get_tag(guild, lookup)
        if tag is None:
            await ctx.send(':exclamation: | Tag "{}" not found.'.format(name))
            return

        tag.uses += 1
        await ctx.send(tag)

        db = self.config.get(tag.location)
        await self.config.put(tag.location, db)

    @tag.error
    async def tag_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.invoke(self.make)

    @tag.command(aliases=['add'])
    async def create(self, ctx, name : str, *, content : str):
        """Creates a new tag owned by you.

        If you create a tag via private message then the tag is a generic
        tag that can be accessed in all guilds. Otherwise the tag you
        create can only be accessed in the guild that it was created in.
        """
        content = content.replace('@', '@\u200b')
        lookup = name.lower()
        location = self.get_database_location(ctx.message)
        db = self.config.get(location, {})
        if lookup in db:
            await ctx.send(':exclamation: | {} a tag with then name of "{}" already exists.'.format(ctx.message.author.mention, name))
            return
        db[lookup] = TagInfo(name, content, str(ctx.message.author.id), location=location)
        await self.config.put(location, db)
        await ctx.send(':ballot_box_with_check: | {} tag "{}" successfully created.'.format(ctx.message.author.mention, name))

    @tag.command()
    async def generic(self, ctx, name : str, *, content : str):
        """Creates a new generic tag owned by you.

        Unlike the create tag subcommand,  this will always attempt to create
        a generic tag and not a guild-specific one.
        """
        content = content.replace('@everyone', '@\u200beveryone')
        lookup = name.lower()
        db = self.config.get('generic', {})
        if lookup in db:
            await ctx.send(':exclamation: | A tag with the name of "{}" already exists.'.format(name))
            return

        db[lookup] = TagInfo(name, content, str(ctx.message.author.id), location='generic')
        await self.config.put('generic', db)
        await ctx.send(':ballot_box_with_check: | Tag "{}" successfully created.'.format(name))

    @tag.command()
    async def make(self, ctx):
        """Interactive makes a tag for you.

        Thiis walks through the rocess of creating a tag with
        its name and its content. This works similar to the tag
        create command.
        """
        message = ctx.message
        location = self.get_database_location(message)
        db = self.config.get(location, {})
        await ctx.send(':wave: Hello {}. What would you like the name of the tag to be?'.format(message.author.mention))
        def pred(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel

        name = await self.bot.wait_for('message', timeout=60.0, check=pred)

        lookup = name.content.lower()
        if lookup in db:
            fmt = ':exclamation: | Sorry. A tag with that name exists already. Use {0.prefix}tag make again.'
            await ctx.send(fmt.format(ctx))
            return

        await ctx.send(':ballot_box_with_check: | Alright. So the name is {0.content}. What about the tag\'s content?'.format(name))
        def pred(m):
            return m.author == ctx.message.author and m.channel == ctx.message.channel

        content = await self.bot.wait_for('message', timeout=60.0, check=pred)

        content = content.content.replace('@everyone', '@\u200beveryone')
        db[lookup] = TagInfo(name.content, content, str(name.author.id), location=location)
        await self.config.put(location, db)
        await ctx.send(':ballot_box_with_check: | Cool I\'ve made your {0.content} tag.'.format(name))

    def generate_stats(self, db, label):
        yield '- Total {} tags: {}'.format(label, len(db))
        if db:
            popular = sorted(db.values(), key=lambda t: t.uses, reverse=True)
            total_uses = sum(t.uses for t in popular)
            yield '- Total {} tag uses: {}'.format(label, total_uses)
            yield '- Most used {0} tag: {1.name} with {1.uses} uses'.format(label, popular[0])

    @tag.command()
    async def stats(self, ctx):
        """Gives stats about the tag database."""
        result = []
        guild = ctx.message.guild
        generic = self.config.get('generic', {})
        result.extend(self.generate_stats(generic, 'Generic'))

        if guild is not None:
            result.extend(self.generate_stats(self.config.get(str(guild.id), {}), 'Guild Specific'))

        await ctx.send('\n'.join(result))

    @tag.command(aliases=['update'])
    async def edit(self, ctx, name : str, *, content : str):
        """Modifies an existing tag that you own.

        This command completely replaces the original text. If you edit
        a tag via private message then the tag i looked up in the generic
        tag database. Otherwise it looks at the guild-specific databse.
        """
        content = content.replace('@everyone', '@\u200beveryone')
        lookup = name.lower()
        guild = ctx.message.guild
        tag = self.get_tag(guild, lookup)
        if tag is None:
            await ctx.send(':exclamation: | The tag "{}" does not exist.'.format(name))
            return

        if tag.owner_id != str(ctx.message.author.id):
            await ctx.send(':exclamation: | Only the tag owner can edit this tag.')
            return

        db = self.config.get(tag.location)
        tag.content = content
        await self.config.put(tag.location, db)
        await ctx.send(':ballot_box_with_check: Tag successfully edited.')

    @tag.command(aliases=['delete'])
    async def remove(self, ctx, *, name : str):
        """Removes a tag that you own.

        The tag owner can always delete their own tags. If someone requests
        deletion and has Manage Messages permissions or a Bot Mod role then
        they can also remove tags from the guild-specific database. Generic
        tags can only be deleted by the bot owner or the tag owner.
        """
        lookup = name.lower()
        guild = ctx.message.guild
        tag = self.get_tag(guild, lookup)

        if tag is None:
            await ctx.send(':exclamation: | Tag not found.')
            return
        can_delete = commands.has_permissions(manage_message=True)
        can_delete = can_delete or tag.owner.id == str(ctx.message.author.id)

        if not can_delete:
            await ctx.send(':exclamation: | You do not have permissions to delete this tag.')
            return

        db = self.config.get(tag.location)
        del db[lookup]
        await self.config.put(tag.content, db)
        await ctx.send(':ballot_box_with_check: | Tag successfully removed.')

    @tag.command(hidden=True)
    async def info(self, ctx, *, name : str):
        """Retrieves info about a tag.
        The info includes things like the owner and how many times it was used.
        """

        lookup = name.lower()
        guild = ctx.message.guild
        tag = self.get_tag(guild, lookup)

        if tag is None:
            await ctx.send(':exclamation: | Tag "{}" not found.'.format(name))
            return

        entries = tag.info_entries(ctx)
        await formats.entry_to_code(self.bot, entries)

    @info.error
    async def info_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(':exclamation: | You did not tell the tags name you want the info of.')

    @tag.command(name="list")
    async def _list(self, ctx):
        """Lists all the tags that belong to you.

        This includes generic tag as well. If this is done in private
        message then you will only get the generic tags you own not the
        guild specific tags.
        """

        owner = str(ctx.message.author.id)
        guild = ctx.message.guild
        tags = [tag.name for tag in self.config.get('generic', {}).values() if tag.owner_id == owner]
        if guild is not None:
            tags.extend(tag.name for tag in self.config.get(str(guild.id), {}).values() if tag.owner_id == owner)

        if tags:
            fmt = ':mag_right: | You have the following tags:\n{}'
            await ctx.send(fmt.format(', '.join(tags)))
        else:
            await ctx.send(':exclamation: | You have no tags.')
    @tag.command()
    async def search(self, ctx, *, query : str):
        """Searches for a tag.

        This searches both the generic and guild-specific database. If it's
        a private message, then only generic tags are searched.

        The query must be at least 2 characters.
        """

        guild = ctx.message.guild
        query = query.lower()
        if len(query) < 2:
            await ctx.send(':exclamation: | The query lenght must be at least two characters.')
            return

        generic = self.config.get('generic', {})
        results = {value.name for name, value in generic.items() if query in name}

        if guild is not None:
            db = self.config.get(str(guild.id), {})
            for name, value in db.items():
                if query in name:
                    results.add(value.name)

        fmt = ':mag_right: | {} tag(s) found.\n{}'
        if results:
            await ctx.send(fmt.format(len(results), '\n'.join(results)))
        else:
            await ctx.send(':exclamation: | No tags found.')

    @search.error
    async def search_error(self, error, ctx):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(':exclamation: | Missing query to search for.')

def setup(bot):
    c = Tags(bot)
    bot.add_cog(c)
