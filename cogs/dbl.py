from discord.ext import commands
import json
import asyncio
import dbl
import aiohttp
import discord
import config

class DBL():
    """Commands related to [discordbots.org](https://discordbots.org)"""
    def __init__(self, bot):
        self.bot = bot
        self.token = config.dbl_token
        self.dblpy = dbl.Client(self.bot, self.token, loop=self.bot.loop)
        self.bot.loop.create_task(self.update_stats())

    async def update_stats(self):
        while True:
            try:
                await self.dblpy.post_server_count()
            except Exception as e:
                print(e)
            await asyncio.sleep(1800)

    @commands.command()
    async def botinfo(self, ctx, *, member: discord.Member=None):
        """Gives you info from  bot."""
        if member is None:
            await ctx.send('You forgot to tell me the bot that you want the info of.')
            return
        if not member.bot:
            await ctx.send('That is not a bot...')
            return
        data = await self.dblpy.get_bot_info(bot_id=int(member.id))
        if not data:
            return await ctx.send(f'{ctx.tick(False)} This bot is not in discordbots.org\'s database.')
        if data:
            if not 'server_count' in data:
                server_count = 'Not Posted'
            else:
                server_count = data['server_count']
            has_server_count = True if server_count else False
            bot_id = data['id']
            bot_username = data['username']
            bot_discriminator = data['discriminator']
            bot_avatar = data['avatar']
            has_avatar = True if bot_avatar else False
            bot_lib = data['lib']
            bot_prefix = data['prefix']
            bot_shortdesc = data['shortdesc']
            # bot_longdesc = data['longdesc']
            # has_longdesc = True if bot_longdesc else False
            bot_tags_raw = data['tags']
            bot_tags = ', '.join(bot_tags_raw)
            bot_support = data['support']
            has_support = True if bot_support else False
            bot_website = data['website']
            has_website = True if bot_website else False
            bot_github = data['github']
            has_github = True if bot_github else False
            bot_owners_raw = data['owners']
            has_many_owners = True if len(bot_owners_raw) > 1 else False
            if has_many_owners:
                owner_names = []
                for owner in bot_owners_raw:
                    get_owner = await self.bot.get_user_info(owner)
                    owner_name = get_owner.name
                    owner_names.append(owner_name)
                bot_owners =', '.join(owner_names)
            else:
                bot_owners_id = ''.join(bot_owners_raw)
                owner = await self.bot.get_user_info(bot_owners_id)
                owner_name = owner.name
                bot_owners = ''.join(owner_name)
            bot_invite = data['invite']
            has_invite = True if bot_invite else False
            bot_date = data['date']
            bot_certified = data['certifiedBot']
            if bot_certified:
                certified_string = '<:dblCertified:392249976639455232>'
            else:
                certified_string = ' '
            bot_votes = str(data['points'])
            e = discord.Embed(title="Info of {}{}".format(bot_username, certified_string), description="Info:", color=discord.Color.blue())
            e.add_field(name="ID:", value="{}".format(bot_id), inline=True)
            e.add_field(name="Discriminator:", value="{}".format(bot_discriminator), inline=True)
            if bot_tags:
                e.add_field(name="Tags:", value="{}".format(bot_tags), inline=False)
            if bot_lib:
                e.add_field(name="Lib:", value="{}".format(bot_lib), inline=True)
            if bot_prefix:
                e.add_field(name="Prefix:", value="{}".format(bot_prefix), inline=True)
            if has_server_count:
                e.add_field(name="Server count:", value="{}".format(server_count), inline=True)
            if bot_date:
                #e.add_field(name="Approved at:", value="{}".format(bot_date), inline=True)
                e.set_footer(text="Approved at")
                e.timestamp = bot_date
            if has_many_owners:
                e.add_field(name="Owners:", value="{}".format(bot_owners), inline=True)
            else:
                e.add_field(name="Owner:", value="{}".format(bot_owners), inline=True)
            if bot_votes:
                e.add_field(name="Upvotes:", value="{}".format(bot_votes), inline=True)
            # e.add_field(name="Lib:", value="{}".format(server_count), inline=True)
            # e.add_field(name="Lib:", value="{}".format(server_count), inline=True)
            if bot_shortdesc:
                e.add_field(name="Short description:", value="{}".format(bot_shortdesc), inline=True)
            links_raw = []
            if has_invite:
                links_raw.append('[INVITE]({})'.format(bot_invite))
            if has_github:
                links_raw.append('[GITHUB]({})'.format(bot_github))
            if has_website:
                links_raw.append('[WEBSITE]({})'.format(bot_website))
            if has_support:
                links_raw.append('[SUPPORT]({})'.format('https://discord.gg/' + bot_support))
            links = ' | '.join(links_raw)
            e.add_field(name="Links:", value="{}".format(links), inline=True)
            if has_avatar:
                e.set_thumbnail(url=member.avatar_url)
            else:
                e.set_thumbnail(url=member.default_avatar_url)
            # e.add_field(name="")
            await ctx.send(embed=e)
        else:
            await ctx.send('The bot is not in the database of discordbots.org')

    @commands.command()
    async def dbl(self, ctx, member: discord.Member=None):
        """Gives you the widget from discordbots.org for a bot you specify."""
        if member is None:
            await ctx.send('You did not tag a bot.')
            return
        if not member.bot:
            await ctx.send('You need to tag a **bot**.')
            # await ctx.send(':red_circle: **WOOP WOOP** :red_circle: **WE GOT AN IDIOT OVER HERE TRYING TO VIEW THE BOT PAGE OF A USER!**')
            return
        url = await self.dblpy.generate_widget_large(bot_id=int(member.id))
        if not url:
            return await ctx.send(f'{ctx.tick(False)} This bot is not in discordbots.org\'s database.')
        e = discord.Embed(title="Discord Bot List", description="Info for {}:".format(member.name), color=discord.Color.green())
        e.set_image(url=url)
        await ctx.send(embed=e)

def setup(bot):
    bot.add_cog(DBL(bot))
