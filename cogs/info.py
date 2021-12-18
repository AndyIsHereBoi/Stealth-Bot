import io
import os
import re
import sys
import zlib
import time
import expr
import yaml
import random
import errors
import shutil
import typing
import psutil
import pathlib
import inspect
import discord
import humanize
import datetime

from helpers import helpers as helpers
from discord.ext import commands, menus
from helpers.context import CustomContext
from discord.ext.menus.views import ViewMenuPages
from discord.ext.commands.cooldowns import BucketType


with open(r'/root/stealthbot/config.yaml') as file:
    full_yaml = yaml.load(file)
yaml_data = full_yaml


def get_ram_usage():
    return int(psutil.virtual_memory().total - psutil.virtual_memory().available)


def get_ram_total():
    return int(psutil.virtual_memory().total)


def get_ram_usage_pct():
    return psutil.virtual_memory().percent


def finder(text, collection, *, key=None, lazy=True):
    suggestions = []
    text = str(text)
    pat = '.*?'.join(map(re.escape, text))
    regex = re.compile(pat, flags=re.IGNORECASE)
    for item in collection:
        to_search = key(item) if key else item
        r = regex.search(to_search)
        if r:
            suggestions.append((len(r.group()), r.start(), item))

    def sort_key(tup):
        if key:
            return tup[0], tup[1], key(tup[2])
        return tup

    if lazy:
        return (z for _, _, z in sorted(suggestions, key=sort_key))
    else:
        return [z for _, _, z in sorted(suggestions, key=sort_key)]


class SphinxObjectFileReader:
    # Inspired by Sphinx's InventoryFileReader
    BUFSIZE = 16 * 1024

    def __init__(self, buffer):
        self.stream = io.BytesIO(buffer)

    def readline(self):
        return self.stream.readline().decode('utf-8')

    def skipline(self):
        self.stream.readline()

    def read_compressed_chunks(self):
        decompressor = zlib.decompressobj()
        while True:
            chunk = self.stream.read(self.BUFSIZE)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)
        yield decompressor.flush()

    def read_compressed_lines(self):
        buf = b''
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b'\n')
            while pos != -1:
                yield buf[:pos].decode('utf-8')
                buf = buf[pos + 1:]
                pos = buf.find(b'\n')


# bytes pretty-printing
UNITS_MAPPING = [
    (1 << 50, ' PB'),
    (1 << 40, ' TB'),
    (1 << 30, ' GB'),
    (1 << 20, ' MB'),
    (1 << 10, ' KB'),
    (1, (' byte', ' bytes')),
]


def pretty_size(bytes, units=None):
    if units is None:
        units = UNITS_MAPPING

    for factor, suffix in units:
        if bytes >= factor:
            break
    amount = int(bytes / factor)

    if isinstance(suffix, tuple):
        singular, multiple = suffix
        if amount == 1:
            suffix = singular
        else:
            suffix = multiple
    return str(amount) + suffix

class ServerEmotesEmbedPage(menus.ListPageSource):
    def __init__(self, data, guild):
        self.data = data
        self.guild = guild
        super().__init__(data, per_page=10)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        colors = [0x910023, 0xA523FF]
        color = random.choice(colors)

        embed = discord.Embed(title=f"{self.guild}'s emotes ({len(self.guild.emojis):,})",
                              description="\n".join(f'{i + 1}. {v}' for i, v in enumerate(entries, start=offset)),
                              timestamp=discord.utils.utcnow(), color=color)
        return embed


class ServerMembersEmbedPage(menus.ListPageSource):
    def __init__(self, data, guild):
        self.data = data
        self.guild = guild
        super().__init__(data, per_page=20)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        colors = [0x910023, 0xA523FF]
        color = random.choice(colors)
        embed = discord.Embed(title=f"{self.guild}'s members ({self.guild.member_count:,})",
                              description="\n".join(f'{i + 1}. {v}' for i, v in enumerate(entries, start=offset)),
                              timestamp=discord.utils.utcnow(), color=color)
        return embed


class TodoListEmbedPage(menus.ListPageSource):
    def __init__(self, title, author, data):
        self.title = title
        self.author = author
        self.data = data
        super().__init__(data, per_page=15)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        colors = [0x910023, 0xA523FF]
        color = random.choice(colors)
        embed = discord.Embed(title=self.title, description="\n".join(entries), timestamp=discord.utils.utcnow(), color=color)
        embed.set_footer(text=f"Requested by: {self.author.name}", icon_url=self.author.avatar.url)

        return embed


def setup(client):
    client.add_cog(Info(client))


class Info(commands.Cog):
    "All informative commands like serverinfo, userinfo and more!"

    def __init__(self, client):
        self.client = client
        
        self.select_emoji = "<:info:888768239889424444>"
        self.select_brief = "All informative commands like serverinfo, userinfo and more!"

    async def build_rtfm_lookup_table(self, page_types):
        cache = {}
        for key, page in page_types.items():
            sub = cache[key] = {}
            async with self.client.session.get(page + '/objects.inv') as resp:
                if resp.status != 200:
                    continue

                stream = SphinxObjectFileReader(await resp.read())
                cache[key] = self.parse_object_inv(stream, page)

        self._rtfm_cache = cache

    def parse_object_inv(self, stream, url):
        # key: URL
        # n.b.: key doesn't have `discord` or `discord.ext.commands` namespaces
        result = {}

        # first line is version info
        inv_version = stream.readline().rstrip()

        if inv_version != '# Sphinx inventory version 2':
            raise RuntimeError('Invalid objects.inv file version.')

        # next line is "# Project: <name>"
        # then after that is "# Version: <version>"
        projname = stream.readline().rstrip()[11:]
        version = stream.readline().rstrip()[11:]

        # next line says if it's a zlib header
        line = stream.readline()
        if 'zlib' not in line:
            raise RuntimeError('Invalid objects.inv file, not z-lib compatible.')

        # This code mostly comes from the Sphinx repository.
        entry_regex = re.compile(r'(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)')
        for line in stream.read_compressed_lines():
            match = entry_regex.match(line.rstrip())
            if not match:
                continue

            name, directive, prio, location, dispname = match.groups()
            domain, _, subdirective = directive.partition(':')
            if directive == 'py:module' and name in result:
                # From the Sphinx Repository:
                # due to a bug in 1.1 and below,
                # two inventory entries are created
                # for Python modules, and the first
                # one is correct
                continue

            # Most documentation pages have a label
            if directive == 'std:doc':
                subdirective = 'label'

            if location.endswith('$'):
                location = location[:-1] + name

            key = name if dispname == '-' else dispname
            prefix = f'{subdirective}:' if domain == 'std' else ''

            if projname == 'discord.py':
                key = key.replace('discord.ext.commands.', '').replace('discord.', '')

            result[f'{prefix}{key}'] = os.path.join(url, location)

        return result

    async def do_rtfm(self, ctx: CustomContext, key, obj):
        page_types = {
            'latest': 'https://discordpy.readthedocs.io/en/latest',
            'latest-jp': 'https://discordpy.readthedocs.io/ja/latest',
            'python': 'https://docs.python.org/3',
            'python-jp': 'https://docs.python.org/ja/3',
            'master': 'https://discordpy.readthedocs.io/en/master',
            'edpy': 'https://enhanced-dpy.readthedocs.io/en/latest',
            'chai': 'https://chaidiscordpy.readthedocs.io/en/latest',
            'bing': 'https://asyncbing.readthedocs.io/en/latest',
            'pycord': 'https://pycord.readthedocs.io/en/master',
            'pomice': 'https://pomice.readthedocs.io/en/latest'
        }
        embed_titles = {
            'latest': 'discord.py v1.7.3',
            'latest-jp': 'discord.py v1.7.3 in Japanese',
            'python': 'python',
            'python-jp': 'python in Japanese',
            'master': 'discord.py v2.0.0a',
            'edpy': 'enhanced-dpy',
            'chai': 'chaidiscord.py',
            'bing': 'asyncbing',
            'pycord': 'pycord',
            'pomice': 'pomice'
        }
        embed_icons = {
            'latest': 'https://cdn.discordapp.com/icons/336642139381301249/3aa641b21acded468308a37eef43d7b3.png',
            'latest-jp': 'https://cdn.discordapp.com/icons/336642139381301249/3aa641b21acded468308a37eef43d7b3.png',
            'python': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1200px-Python-logo-notext.svg.png',
            'python-jp': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1200px-Python-logo-notext.svg.png',
            'master': 'https://cdn.discordapp.com/icons/336642139381301249/3aa641b21acded468308a37eef43d7b3.png',
            'edpy': 'https://cdn.discordapp.com/emojis/781918475009785887.png?size=96',
            'chai': 'https://cdn.discordapp.com/icons/336642139381301249/3aa641b21acded468308a37eef43d7b3.png',
            'bing': 'https://pbs.twimg.com/profile_images/1313103135414448128/0EVE9TeW.png',
            'pycord': 'https://avatars.githubusercontent.com/u/89700626?v=4',
            'pomice': 'https://media.discordapp.net/attachments/381963689470984203/918592368465285140/pomice.png'
        }

        if obj is None:
            await ctx.send(page_types[key])
            return

        if not hasattr(self, '_rtfm_cache'):
            await ctx.trigger_typing()
            await self.build_rtfm_lookup_table(page_types)

        obj = re.sub(r'^(?:discord\.(?:ext\.)?)?(?:commands\.)?(.+)', r'\1', obj)

        if key.startswith('latest'):
            # point the abc.Messageable types properly:
            q = obj.lower()
            for name in dir(discord.abc.Messageable):
                if name[0] == '_':
                    continue
                if q == name:
                    obj = f'abc.Messageable.{name}'
                    break

        cache = list(self._rtfm_cache[key].items())

        matches = finder(obj, cache, key=lambda t: t[0], lazy=False)[:8]

        if len(matches) == 0:
            return await ctx.send('Could not find anything. Sorry.')

        embed = discord.Embed(title=f"RTFM Search: `{obj}`", description='\n'.join(f'[`{key}`]({url})' for key, url in matches))
        embed.set_author(name=embed_titles.get(key, 'Documentation'), icon_url=embed_icons.get(key, 'Documentation'))
        embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/d0As41Nt_Dkw41hMwucOJg-T4wdwOAngLJ5mHB4bfEc/https/readthedocs-static-prod.s3.amazonaws.com/images/home-logo.eaeeed28189e.png")

        await ctx.send(embed=embed)

    # This is all danny's code:
    # https://github.com/rapptz/robodanny
    @staticmethod
    async def show_guild_stats(ctx):
        lookup = (
            '\N{FIRST PLACE MEDAL}',
            '\N{SECOND PLACE MEDAL}',
            '\N{THIRD PLACE MEDAL}',
            '\N{SPORTS MEDAL}',
            '\N{SPORTS MEDAL}'
        )
        embed = discord.Embed(title='Server Command Stats', colour=discord.Colour.blurple())
        # total command uses
        query = "SELECT COUNT(*), MIN(timestamp) FROM commands WHERE guild_id=$1;"
        count = await ctx.bot.db.fetchrow(query, ctx.guild.id)
        embed.description = f'{count[0]} commands used.'
        if count[1]:
            timestamp = count[1].replace(tzinfo=datetime.timezone.utc)
        else:
            timestamp = discord.utils.utcnow()
        embed.set_footer(text='Tracking command usage since').timestamp = timestamp
        query = """SELECT command,
                          COUNT(*) as "uses"
                   FROM commands
                   WHERE guild_id=$1
                   GROUP BY command
                   ORDER BY "uses" DESC
                   LIMIT 5;
                """
        records = await ctx.bot.db.fetch(query, ctx.guild.id)
        value = '\n'.join(f'{lookup[index]}: {command} ({uses} uses)'
                          for (index, (command, uses)) in enumerate(records)) or 'No Commands'
        embed.add_field(name='Top Commands', value=value, inline=True)
        query = """SELECT command,
                          COUNT(*) as "uses"
                   FROM commands
                   WHERE guild_id=$1
                   AND timestamp > (CURRENT_TIMESTAMP - INTERVAL '1 day')
                   GROUP BY command
                   ORDER BY "uses" DESC
                   LIMIT 5;
                """
        records = await ctx.bot.db.fetch(query, ctx.guild.id)
        value = '\n'.join(f'{lookup[index]}: {command} ({uses} uses)'
                          for (index, (command, uses)) in enumerate(records)) or 'No Commands.'
        embed.add_field(name='Top Commands Today', value=value, inline=True)
        embed.add_field(name='\u200b', value='\u200b', inline=True)
        query = """SELECT user_id,
                          COUNT(*) AS "uses"
                   FROM commands
                   WHERE guild_id=$1
                   GROUP BY user_id
                   ORDER BY "uses" DESC
                   LIMIT 5;
                """
        records = await ctx.bot.db.fetch(query, ctx.guild.id)
        value = '\n'.join(f'{lookup[index]}: <@!{author_id}> ({uses} bot uses)'
                          for (index, (author_id, uses)) in enumerate(records)) or 'No bot users.'
        embed.add_field(name='Top Command Users', value=value, inline=True)
        query = """SELECT user_id,
                          COUNT(*) AS "uses"
                   FROM commands
                   WHERE guild_id=$1
                   AND timestamp > (CURRENT_TIMESTAMP - INTERVAL '1 day')
                   GROUP BY user_id
                   ORDER BY "uses" DESC
                   LIMIT 5;
                """
        records = await ctx.bot.db.fetch(query, ctx.guild.id)
        value = '\n'.join(f'{lookup[index]}: <@!{author_id}> ({uses} bot uses)'
                          for (index, (author_id, uses)) in enumerate(records)) or 'No command users.'
        embed.add_field(name='Top Command Users Today', value=value, inline=True)
        await ctx.send(embed=embed, footer=False, timestamp=False)

    @staticmethod
    async def show_member_stats(ctx, member):
        lookup = (
            '\N{FIRST PLACE MEDAL}',
            '\N{SECOND PLACE MEDAL}',
            '\N{THIRD PLACE MEDAL}',
            '\N{SPORTS MEDAL}',
            '\N{SPORTS MEDAL}'
        )

        embed = discord.Embed(title='Command Stats', colour=member.colour)
        embed.set_author(name=str(member), icon_url=member.display_avatar.url)

        # total command uses
        query = "SELECT COUNT(*), MIN(timestamp) FROM commands WHERE guild_id=$1 AND user_id=$2;"
        count = await ctx.bot.db.fetchrow(query, ctx.guild.id, member.id)

        embed.description = f'{count[0]} commands used.'
        if count[1]:
            timestamp = count[1].replace(tzinfo=datetime.timezone.utc)
        else:
            timestamp = discord.utils.utcnow()

        embed.set_footer(text='First command used').timestamp = timestamp

        query = """SELECT command,
                          COUNT(*) as "uses"
                   FROM commands
                   WHERE guild_id=$1 AND user_id=$2
                   GROUP BY command
                   ORDER BY "uses" DESC
                   LIMIT 5;
                """

        records = await ctx.bot.db.fetch(query, ctx.guild.id, member.id)

        value = '\n'.join(f'{lookup[index]}: {command} ({uses} uses)'
                          for (index, (command, uses)) in enumerate(records)) or 'No Commands'

        embed.add_field(name='Most Used Commands', value=value, inline=False)

        query = """SELECT command,
                          COUNT(*) as "uses"
                   FROM commands
                   WHERE guild_id=$1
                   AND user_id=$2
                   AND timestamp > (CURRENT_TIMESTAMP - INTERVAL '1 day')
                   GROUP BY command
                   ORDER BY "uses" DESC
                   LIMIT 5;
                """

        records = await ctx.bot.db.fetch(query, ctx.guild.id, member.id)

        value = '\n'.join(f'{lookup[index]}: {command} ({uses} uses)'
                          for (index, (command, uses)) in enumerate(records)) or 'No Commands'

        embed.add_field(name='Most Used Commands Today', value=value, inline=False)
        await ctx.send(embed=embed)

    @commands.group(
        invoke_without_command=True,
        help="Shows you the most used commands by the specified user, if no user is specified it will show the guild's most used commands",
        aliases=['commandstats'],
        brief="stats Jake\nstats\nstats @Clown")
    async def stats(self, ctx, *, member: discord.Member = None):
        if member is None:
            await self.show_guild_stats(ctx)

        else:
            await self.show_member_stats(ctx, member)

    @stats.command(
        name="global",
        help="Shows you the most used commands.",
        aliases=['all'])
    async def stats_global(self, ctx):
        query = "SELECT COUNT(*) FROM commands;"
        total = await self.client.db.fetchrow(query)

        e = discord.Embed(title='Command Stats', colour=discord.Colour.blurple())
        e.description = f'{total[0]} commands used.'

        lookup = (
            '\N{FIRST PLACE MEDAL}',
            '\N{SECOND PLACE MEDAL}',
            '\N{THIRD PLACE MEDAL}',
            '\N{SPORTS MEDAL}',
            '\N{SPORTS MEDAL}'
        )

        query = """SELECT command, COUNT(*) AS "uses"
                   FROM commands
                   GROUP BY command
                   ORDER BY "uses" DESC
                   LIMIT 5;
                """

        records = await self.client.db.fetch(query)
        value = '\n'.join(f'{lookup[index]}: {command} ({uses} uses)' for (index, (command, uses)) in enumerate(records))
        e.add_field(name='Top Commands', value=value, inline=False)

        query = """SELECT guild_id, COUNT(*) AS "uses"
                   FROM commands
                   GROUP BY guild_id
                   ORDER BY "uses" DESC
                   LIMIT 5;
                """

        records = await self.client.db.fetch(query)
        value = []
        for (index, (guild_id, uses)) in enumerate(records):
            if guild_id is None:
                guild = 'Private Message'
            else:
                guild = self.client.get_guild(guild_id) or f'<Unknown {guild_id}>'

            emoji = lookup[index]
            value.append(f'{emoji}: {guild} ({uses} uses)')

        e.add_field(name='Top Guilds', value='\n'.join(value), inline=False)

        query = """SELECT user_id, COUNT(*) AS "uses"
                   FROM commands
                   GROUP BY user_id
                   ORDER BY "uses" DESC
                   LIMIT 5;
                """

        records = await self.client.db.fetch(query)
        value = []
        for (index, (author_id, uses)) in enumerate(records):
            user = self.client.get_user(author_id) or f'<Unknown {author_id}>'
            emoji = lookup[index]
            value.append(f'{emoji}: {user} ({uses} uses)')

        e.add_field(name='Top Users', value='\n'.join(value), inline=False)
        await ctx.send(embed=e)

    @commands.command()
    async def covid(self, ctx: CustomContext, country: str = None):
        url = f"https://disease.sh/v3/covid-19/countries/{country}"

        if country is None:
            url = f"https://disease.sh/v3/covid-19/all"

        coviddata = await self.client.session.get(url)
        data = await coviddata.json()

        embed = discord.Embed(title=f"COVID-19 - {data['country'] if data['country'] else 'Global'}")

        embed.add_field(name=f"__**Total**__", value=f"""
:mag_right: Cases: {data['cases']:,}
:skull_crossbones: Deaths: {data['deaths']:,}
:ambulance: Recovered: {data['recovered']:,}
:thermometer_face: Active: {data['active']:,}
:scream: Critical: {data['critical']:,}
:syringe: Tests: {data['tests']:,}
        """, inline=True)

        embed.add_field(name=f"__**Today**__", value=f"""
:mag_right: Cases: {data['todayCases']:,}
:skull_crossbones: Deaths: {data['todayDeaths']:,}
:ambulance: Recovered: {data['todayRecovered']:,}
        """, inline=True)

        embed.add_field(name=f"__**Per million**__", value=f"""
:mag_right: Cases: {data['casesPerOneMillion']:,}
:skull_crossbones: Deaths: {data['deathsPerOneMillion']:,}
:syringe: Tests: {data['testsPerOneMillion']:,}
        """, inline=True)

        embed.add_field(name=f"__**Other**__", value=f"""
:busts_in_silhouette: Population: {data['population']:,}
:map: Continent: {data['continent'] if data['continent'] else 'Unknown'}
        """)

        await ctx.send(embed=embed)

    @commands.command(
        help="Shows info about the song the specified member is currently listening to. If no member is specified it will default to the author of the message.",
        aliases=['sp'],
        brief="spotify\nspotify @Jake\nspotify 80088516616269824")
    async def spotify(self, ctx: CustomContext, member: discord.Member = None) -> discord.Message:
        await ctx.trigger_typing()

        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        spotify = discord.utils.find(lambda a: isinstance(a, discord.Spotify), member.activities)

        if spotify is None:
            raise errors.NoSpotifyStatus

        response = await self.client.session.get("https://api.jeyy.xyz/discord/spotify", params={'title': spotify.title, 'cover_url': spotify.album_cover_url, 'duration_seconds': spotify.duration.seconds, 'start_timestamp': spotify.start.timestamp(), 'artists': spotify.artists})
        buffer = io.BytesIO(await response.read())

        view = discord.ui.View()
        item = discord.ui.Button(style=discord.ButtonStyle.gray, emoji="<:spotify:899263771342700574>", label=f"listen on spotify", url=spotify.track_url)
        view.add_item(item=item)

        return await ctx.send(f"{f'**You** are' if member.id == ctx.author.id else f'{member.mention} is'} listening to **{spotify.title}** by **{', '.join(spotify.artists)}**", file=discord.File(buffer, 'spotify.png'), view=view)

    @commands.command(
        help="Posts the specified code in the specified language to mystb.in",
        aliases=['mystb.in'],
        brief="mystbin python print('Hello World!')")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def mystbin(self, ctx, language: str, *, code: str) -> discord.Message:
        try:
            post = await self.client.mystbin.post(code, syntax=language)
            return await ctx.send(f"Successfully posted to mystbin, here's the link: {str(post)}")

        except Exception as e:
            return await ctx.send(f"Failed to post to mystbin, here's the error: {e}")

    @commands.command()
    async def weather(self, ctx, location: str) -> discord.Message:
        request = await self.client.session.get(f"http://api.weatherapi.com/v1/current.json?key={yaml_data['WEATHER_TOKEN']}&q={location}")
        data = await request.json()

        embed = discord.Embed(title=f"Weather in {location.title()}")
        location = data['location']
        current = data['current']

        embed.add_field(name=f"__**Location**__", value=f"""
Name: {location['name']}
Region: {location['region']}
Country: {location['country']}
        """, inline=True)

        embed.add_field(name=f"__**Weather**__", value=f"""
Current time: {location['localtime']}
Weather: 
Temperature: {round(current['temp_c'])} °C **|** {round(current['temp_f'])} °F
        """, inline=True)

        embed.add_field(name=f"__**Wind**__", value=f"""
Wind direction: {current['wind_dir']}
Wind speed: {current['wind_mph']} mph
        """, inline=True)

        embed.add_field(name=f"__**Other**__", value=f"""
Humidity: {current['humidity']}%
Cloud: {current['cloud']}%
UV index: {current['uv']}
        """, inline=False)

        return await ctx.send(embed=embed)

    @commands.command(
        help="Checks the specified member's avatar for any innapropriate content.",
        aliases=['nsfw_check', 'nsfw-check', 'nsfwcheck'],
        brief="check\ncheck @Jake")
    async def check(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None) -> discord.Message:
        await ctx.trigger_typing()

        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        if not member.display_avatar:
            return await ctx.send(f"{'You have' if member.id == ctx.author.id else f'{member.mention} has'} no avatar.")

        request = await self.client.session.get(f'https://api.openrobot.xyz/api/nsfw-check', headers={'Authorization': f'{yaml_data["OR_TOKEN"]}'}, params={'url': ctx.author.display_avatar.url})
        json = await request.json()

        safe = round(100 - json['nsfw_score'] * 100, 2)
        safe = int(safe) if safe % 1 == 0 else safe
        unsafe = round(json['nsfw_score'] * 100, 2)
        unsafe = int(unsafe) if unsafe % 1 == 0 else unsafe

        is_safe = not bool(json['labels']) and safe > unsafe

        embed = discord.Embed(title="NSFW Check", description=f"""
Safe: {'Yes' if is_safe else 'No'}    
{f'Labels: {", ".join(json["labels"])}' if json['labels'] else ''}    
        """)
        embed.add_field(name="<:status_dnd:596576774364856321> Unsafe score:", value=f"{unsafe}%")
        embed.add_field(name="<:status_online:596576749790429200> Safe score", value=f"{safe}%")
        embed.set_image(url=member.display_avatar.url)

        return await ctx.send(embed=embed)

    @commands.command(
        slash_command=True,
        message_command=True,
        help="Shows information about the specified member. If no member is specified it will default to the author of the message.",
        aliases=['ui', 'user', 'member', 'memberinfo'],
        brief="userinfo\nuserinfo @Andy\nuserinfo Jake#9999")
    @commands.cooldown(1, 5, BucketType.member)
    async def userinfo(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None) -> discord.Message:
        await ctx.trigger_typing()

        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        if isinstance(member, discord.Member):
            fetched_member = await self.client.fetch_user(member.id)

            embed = discord.Embed(title=member.name if member.name else "No name", url=f"https://discord.com/users/{member.id}", description=f"<:greyTick:596576672900186113> ID: {member.id}")

            embed.add_field(name="__**General**__", value=f"""
<:nickname:895688440912437258> Nick: {member.nick if member.nick else f'{member.name} (No nick)'}
:hash: Discriminator:  #{member.discriminator}
<:mention:908055690277433365> Mention: {member.mention}
:robot: Bot: {'Yes' if member.bot else 'No'} **|** :zzz: AFK {'Yes' if member.id in self.client.afk_users else 'No'}
            """, inline=True)

            embed.add_field(name="__**Activity**__", value=f"""
{helpers.get_member_status_emote(member)} Status: {helpers.get_member_custom_status(member)}
:video_game: Activity: {helpers.get_member_activity(member)}
<:discord:904442480450224191> Client: {helpers.get_member_client(member)}
<:spotify:899263771342700574> Spotify: {helpers.get_member_spotify(member)}
            """, inline=True)

            embed.add_field(name="__**Something**__", value=f"""
<:invite:895688440639799347> Created: {discord.utils.format_dt(member.created_at, style="F")} ({discord.utils.format_dt(member.created_at, style="R")})
<:joined:895688440786595880> Joined: {discord.utils.format_dt(member.joined_at, style="F")} ({discord.utils.format_dt(member.joined_at, style="R")})
<:boost:858326699234164756> Boosting: {f'{discord.utils.format_dt(member.premium_since, style="F")} ({discord.utils.format_dt(member.premium_since, style="R")})' if member.premium_since else 'Not boosting'}
            """, inline=False)

            embed.add_field(name="__**Assets**__", value=f"""
{helpers.get_member_avatar_urls(member, ctx, member.id)}
{helpers.get_member_banner_urls(fetched_member, ctx, member.id)}
:art: Color: {helpers.get_member_color(member)}
:art: Accent color: {helpers.get_member_accent_color(fetched_member)}
            """, inline=True)

            ack = await self.client.db.fetchval("SELECT acknowledgment FROM acknowledgments WHERE user_id = $1", member.id)

            embed.add_field(name="__**Other**__", value=f"""
<:role:895688440513974365> Top role: {member.top_role.mention if member.top_role else 'No top role'}
<:role:895688440513974365> Roles: {helpers.get_member_roles(member, ctx.guild)}
<:badges:876507747292700713> Staff permissions: {helpers.get_member_permissions(member.guild_permissions)}
<:badges:876507747292700713> Badges: {helpers.get_member_badges(member, fetched_member)}
<:voice_channel:904474834526937120> Voice: {member.voice.channel.mention if member.voice else 'Not in a VC'} {f'**|** Muted: {"Yes" if member.voice.mute or member.voice.self_mute else "No"} **|** Deafened: {"Yes" if member.voice.deaf or member.voice.self_deaf else "No"}' if member.voice else ''}
Mutual servers: {len(member.mutual_guilds) if member.id != 760179628122964008 else 'No mutual servers'}
:star: Acknowledgments: {ack if ack else 'No acknowledgments'}
            """, inline=False)

            view = discord.ui.View()

            if member.avatar:
                item = discord.ui.Button(style=discord.ButtonStyle.gray, emoji="🎨", label="Avatar",
                                         url=member.avatar.url, row=1)
                view.add_item(item=item)

                embed.set_thumbnail(url=member.avatar.url)

            if fetched_member.banner:
                item = discord.ui.Button(style=discord.ButtonStyle.gray, emoji="🎨", label="Banner",
                                         url=fetched_member.banner.url, row=1)
                view.add_item(item=item)

            if discord.utils.find(lambda act: isinstance(act, discord.Spotify), member.activities):
                item = discord.ui.Button(style=discord.ButtonStyle.gray, emoji="<:spotify:899263771342700574>", label="Spotify",
                                         url=discord.utils.find(lambda act: isinstance(act, discord.Spotify), member.activities).track_url, row=2)
                view.add_item(item=item)

            return await ctx.send(embed=embed, view=view)

        elif isinstance(member, discord.User):

            embed = discord.Embed(title=member.name if member.name else "No name", url=f"https://discord.com/users/{member.id}", description=f"*Less info cause this is a user not a member*\n<:greyTick:596576672900186113> ID: {member.id}")

            embed.add_field(name="__**General**__", value=f"""
:hash: Discriminator:  #{member.discriminator}
<:mention:908055690277433365> Mention: {member.mention}
:robot: Bot: {'Yes' if member.bot else 'No'} **|** :zzz: AFK {'Yes' if member.id in self.client.afk_users else 'No'}
            """, inline=True)

            ack = await self.client.db.fetchval("SELECT acknowledgment FROM acknowledgments WHERE user_id = $1", member.id)

            embed.add_field(name="__**Something**__", value=f"""
<:invite:895688440639799347> Created: {discord.utils.format_dt(member.created_at, style="F")} ({discord.utils.format_dt(member.created_at, style="R")})
:star: Acknowledgments: {ack if ack else 'No acknowledgments'}
            """, inline=False)

            embed.add_field(name="__**Assets**__", value=f"""
Avatar: {helpers.get_member_avatar_urls(await self.client.fetch_user(member.id))}
Banner: {helpers.get_member_banner_urls(member)}
:rainbow: Color: {helpers.get_member_color(member)}
:rainbow: Accent color: {helpers.get_member_accent_color(member)}
            """, inline=True)

            if member.avatar:
                embed.set_thumbnail(url=member.avatar.url)

            # embed.add_field(name="__**Join order**__", value=f"""
    # {helpers.get_join_order(member, ctx.guild)}
            # """, inline=False)

            return await ctx.send(embed=embed)

        else:
            raise errors.UnknownError

    @commands.command()
    async def run(self, ctx, *, code):
        request = await self.client.session.get("https://repi.openrobot.xyz/eval",
                                                params={"auth": f"{yaml_data['OR_TEST_TOKEN']}", "code": f"{code}"})
        json = await request.json()

        if json['error']:
            embed = discord.Embed(description=f"""
```log
{json['error']}
```
            """)
            return await ctx.send(embed=embed)

        else:
            embed = discord.Embed(title="Output", description=f"""
```py
{json['result']}
```
            """)
            return await ctx.send(embed=embed)

    @commands.command(
        help="Shows information about the specified server. If no server is specified it will default to the current server.",
        aliases=['si', 'guild', 'guildinfo'])
    async def serverinfo(self, ctx: CustomContext) -> discord.Message:
        await ctx.trigger_typing()
        guild = ctx.guild

        embed = discord.Embed(title=guild.name if guild.name else 'No name', description=f"""
<:greyTick:596576672900186113> ID: {guild.id}
<:info:888768239889424444> Description: {guild.description if guild.description else 'No description'}
        """)

        embed.add_field(name="<:text_channel:904473407524048916> __**Channels**__", value=f"""
<:text_channel:904473407524048916> Text: {len(guild.text_channels):,}
<:voice_channel:904474834526937120> Voice: {len(guild.voice_channels):,}
<:category:895688440220356669> Category: {len(guild.categories):,}
<:stage_channel:904474823927926785> Stages: {len(guild.stage_channels):,}
<:thread_channel:904474878390968412> Threads: {len(guild.threads):,}
(only threads
visible by me)
        """, inline=True)

        embed.add_field(name="<:emoji_ghost:895414463354785853> __**Emojis**__", value=f"""
Animated: {len([e for e in guild.emojis if not e.animated]):,}/{guild.emoji_limit:,}
Static: {len([e for e in guild.emojis if e.animated]):,}/{guild.emoji_limit:,}
<:stickers:906902448243892244> __**Stickers**__
Total: {len(guild.stickers):,}/{guild.sticker_limit:,}
        """, inline=True)

        embed.add_field(name="<:boost:858326699234164756> __**Boosts**__", value=f"""
{helpers.get_guild_boosts(guild)}
        """, inline=True)

        embed.add_field(name="<:members:858326990725709854> __**Members**__", value=f"""
:bust_in_silhouette: Humans: {len([m for m in guild.members if not m.bot]):,}
:robot: Bots: {len([m for m in guild.members if m.bot]):,}
:infinity: Total: {len(guild.members):,}
:file_folder: Limit: {guild.max_members:,}
:tools: Admins: {len([m for m in guild.members if m.guild_permissions.administrator]):,}
        """, inline=True)

        embed.add_field(name="<:status_offline:596576752013279242> __**Member statuses**__", value=f"""
<:status_online:596576749790429200> Online: {len([m for m in guild.members if m.status is discord.Status.online]):,}
<:status_idle:596576773488115722> Idle: {len([m for m in guild.members if m.status is discord.Status.idle]):,}
<:status_dnd:596576774364856321> Dnd: {len([m for m in guild.members if m.status is discord.Status.dnd]):,}
<:status_streaming:596576747294818305> Streaming: {len([m for m in guild.members if discord.utils.find(lambda a: isinstance(a, discord.Streaming), m.activities)]):,}
<:status_offline:596576752013279242> Offline: {len([m for m in guild.members if m.status is discord.Status.offline]):,}
        """, inline=True)

        embed.add_field(name="<:gear:899622456191483904> __**Other**__", value=f"""
<:role:895688440513974365> Roles: {len(guild.roles):,}
{helpers.get_server_region_emote(guild)} Region: {helpers.get_server_region(guild)}
:file_folder: Filesize limit: {humanize.naturalsize(guild.filesize_limit)}
<:voice_channel:904474834526937120> Voice bit-rate: {humanize.naturalsize(guild.bitrate_limit)}
{helpers.get_server_verification_level_emote(guild)} Verification level: {str(guild.verification_level).title()}
:calendar_spiral: Created: {discord.utils.format_dt(guild.created_at, style="f")} ({discord.utils.format_dt(guild.created_at, style="R")})
<:nsfw:906587263624945685> Explicit content filter: {helpers.get_server_explicit_content_filter(guild)}
        """, inline=False)

        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)

        return await ctx.send(embed=embed)

    @commands.command(
        help="<:emoji_ghost:658538492321595393> Shows information about a emoji. If the emoji is from a server the bot is in it will show more information. If it's not it will send a bit less information.",
        aliases=['ei', 'emoteinfo', 'emoinfo', 'eminfo', 'emojinfo', 'einfo', 'emoji', 'emote'],
        brief="emojiinfo :bonk:")
    async def emojiinfo(self, ctx: CustomContext, emoji: typing.Union[discord.Emoji, discord.PartialEmoji]) -> discord.Message:
        if isinstance(emoji, discord.Emoji):
            fetchedEmoji = await ctx.guild.fetch_emoji(emoji.id)

            embed = discord.Embed(title=f"{emoji.name}", url=emoji.url)

            embed.add_field(name=f"__**General**__", value=f"""
<:greyTick:596576672900186113> ID: {emoji.id}
:link: Link: [Click here]({emoji.url})
            """, inline=True)

            embed.add_field(name=f"__**Emoji**__", value=f"""
<:servers:895688440690147371> Guild: {emoji.guild} ({emoji.id})
<:owner_crown:895688440610422901> Created by: {fetchedEmoji.user if fetchedEmoji.user else 'Unavailable'}
<:invite:895688440639799347> Created at: {discord.utils.format_dt(emoji.created_at, style="f")} ({discord.utils.format_dt(emoji.created_at, style="R")})
            """, inline=False)

            embed.add_field(name=f"__**Other**__", value=f"""
:gear: Available: {'Yes' if emoji.available else 'No'}
<:emoji_ghost:919657977957474404> Animated: {'Yes' if emoji.animated else 'No'}
            """, inline=True)

            embed.set_image(url=emoji.url)

            view = discord.ui.View()
            item = discord.ui.Button(style=discord.ButtonStyle.gray, emoji="🔗", label="Emoji", url=emoji.url)
            view.add_item(item=item)

            return await ctx.send(embed=embed, view=view)

        elif isinstance(emoji, discord.PartialEmoji):
            embed = discord.Embed(title=f"{emoji.name}", url=emoji.url)

            embed.add_field(name=f"__**General**__", value=f"""
<:greyTick:596576672900186113> ID: {emoji.id}
:link: Link: [Click here]({emoji.url})
Usage: {emoji}
                        """, inline=True)

            embed.add_field(name=f"__**Emoji**__", value=f"""
<:invite:895688440639799347> Created at: {discord.utils.format_dt(emoji.created_at, style="f")} ({discord.utils.format_dt(emoji.created_at, style="R")})
                        """, inline=False)

            embed.add_field(name=f"__**Other**__", value=f"""
<:emoji_ghost:919657977957474404> Animated: {'Yes' if emoji.animated else 'No'}
                        """, inline=True)

            embed.set_image(url=emoji.url)

            view = discord.ui.View()
            item = discord.ui.Button(style=discord.ButtonStyle.gray, emoji="🔗", label="Emoji", url=emoji.url)
            view.add_item(item=item)

            return await ctx.send(embed=embed, view=view)
        else:
            raise errors.UnknownError

    @commands.command(
        help="Shows basic information about the bot.",
        aliases=['bi', 'about', 'info'])
    async def botinfo(self, ctx: CustomContext):
        shards_guilds = {i: {"guilds": 0, "users": 0} for i in range(len(self.client.shards))}
        for guild in self.client.guilds:
            shards_guilds[guild.shard_id]["guilds"] += 1
            shards_guilds[guild.shard_id]["users"] += guild.member_count

        p = pathlib.Path('./')
        cm = cr = fn = cl = ls = fc = 0
        for f in p.rglob('*.py'):
            if str(f).startswith("venv"):
                continue
            fc += 1
            with f.open() as of:
                for l in of.readlines():
                    l = l.strip()
                    if l.startswith('class'):
                        cl += 1
                    if l.startswith('def'):
                        fn += 1
                    if l.startswith('async def'):
                        cr += 1
                    if '#' in l:
                        cm += 1
                    ls += 1

        delta_uptime = discord.utils.utcnow() - self.client.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        total, used, free = shutil.disk_usage("/")

        embed = discord.Embed(title="Bot info", description=f"""
[Invite me](https://discord.com/api/oauth2/authorize?client_id=760179628122964008&permissions=8&scope=bot%20applications.commands) **|** [Support server](https://discord.gg/MrBcA6PZPw) **|** [Vote](https://top.gg/bot/760179628122964008) **|** [Website](https://stealthbot.xyz)

I'm a discord bot made by Ender2K89#9999.
I've been on discord since {discord.utils.format_dt(ctx.me.created_at)} ({discord.utils.format_dt(ctx.me.created_at, style='R')})
I have a lot of features such as moderation, fun, info and more!
I've been online for {ctx.time(days=days, hours=hours, minutes=minutes, seconds=seconds)}.
                              """)

        embed.add_field(name=f"__**Numbers**__", value=f"""
Guilds: `{len(self.client.guilds):,}`
Users: `{len(self.client.users):,}`
Commands: `{len(self.client.commands):,}`
Commands used: `{self.client.commands_used:,}`
Messages seen: `{self.client.messages_count:,}`
                        """, inline=True)

        embed.add_field(name=f"__**System**__", value=f"""
PID: `{os.getpid()}`
CPU: `{round(psutil.cpu_percent())}%`/`100%`
RAM: `{int(get_ram_usage() / 1024 / 1024)}MB`/`{int(get_ram_total() / 1024 / 1024)}MB`
Disk: `{used // (2 ** 30)}GB`/`{total // (2 ** 30)}GB`
Python: `{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}`
                          """, inline=True)

        embed.add_field(name=f"__**Files**__", value=f"""
Files: `{fc:,}`
Lines: `{ls:,}`
Classes: `{cl:,}`
Functions: `{fn:,}`
Courtines: `{cr:,}`
                          """, inline=True)

        embed.add_field(name=f"__**Latest changes**__", value=ctx.get_last_commits(5), inline=False)

        for shard_id, shard in self.client.shards.items():
            embed.add_field(name=f"__**Shard #{shard_id}**__", value=f"""
Latency: `{round(shard.latency * 1000)}`ms{' ' * (9 - len(str(round(shard.latency * 1000, 3))))}
Guilds: `{shards_guilds[shard_id]['guilds']:,}`
Users: `{shards_guilds[shard_id]['users']:,}`
            """, inline=True)

        await ctx.send(embed=embed)

    @commands.command(
        help="Calculates the specified math problem.",
        aliases=['calculator', 'math', 'calc'])
    async def calculate(self, ctx: CustomContext, *, expression: str):
        embed1 = discord.Embed(title="Input", description=f"""
```
{expression.replace(', ', '').replace('x', '*')}
```
                """, color=discord.Color.blue())

        embed2 = discord.Embed(title="Output", description=f"""
```
{expr.evaluate(expression.replace(', ', '').replace('x', '*'))}
```
                """, color=discord.Color.blue())

        await ctx.send(embeds=[embed1, embed2])

    @commands.group(
        invoke_without_command=True,
        help="Shows the 1 policy of the bot.",
        aliases=['privacy-policy', 'privacy_policy'])
    async def privacy(self, ctx: CustomContext):
        embed = discord.Embed(title="Stealth Bot Privacy Policy", description=f"""
We store your server id to make multiple prefixes work.

We store user ids to make the AFK command work.

When a unexpected error happens, we store the following information:
Server id, server owner id, author id and the command executed.

When a command is excuted, we store the following information:
Server id, server owner id, author id and the command executed.
This is used for fixing bugs, statistics and more.
If you do not like this, disable it by doing: `{ctx.prefix}privacy disable_commands`
                            """)
        embed.set_footer(text=f"TL;DR: Privacy doesn't exist 👍")

        await ctx.send(embed=embed, footer=False)

    @privacy.command(
        help="Disables the log-commands features.",
        aliases=['dc', 'disable_command'])
    @commands.has_permissions(manage_guild=True)
    async def disable_commands(self, ctx: CustomContext):
        if ctx.guild.id not in self.client.disable_commands_guilds:
            await self.client.db.execute("INSERT INTO guilds (guild_id, disable_commands) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET disable_commands = $2", ctx.guild.id, True)
            self.client.disable_commands_guilds[ctx.guild.id] = True

            embed = discord.Embed(title="Changed Stealth Bot Privacy Policy for this server", description=f"""
The developers will no longer be notified when you do a command in this server.
To enable it, do `{ctx.prefix}privacy enable_commands`
                                """)

            await ctx.send(embed=embed)

        else:
            return await ctx.send("That setting is already **disabled** for this server!")

    @privacy.command(
        help="Enables the log-commands features.",
        aliases=['ec', 'enable_command'])
    @commands.has_permissions(manage_guild=True)
    async def enable_commands(self, ctx: CustomContext):
        if ctx.guild.id in self.client.disable_commands_guilds:
            await self.client.db.execute("INSERT INTO guilds (guild_id, disable_commands) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET disable_commands = $2", ctx.guild.id, True)
            self.client.disable_commands_guilds.pop(ctx.guild.id)

            embed = discord.Embed(title="Changed Stealth Bot Privacy Policy for this server", description=f"""
The developers will now be notified when you do a command in this server.
To disable it, do `{ctx.prefix}privacy enable_commands`
                                """)

            await ctx.send(embed=embed)

        else:
            return await ctx.send("That setting is already **enabled** for this server!")

    @commands.command(
        help="Translates the given message to English.",
        aliases=['trans', 'translator'],
        brief="translate Hallo!\ntranslate こんにちは")
    async def translate(self, ctx: CustomContext, *, message: str = None):
        if message is None:
            reference = ctx.message.reference

            if reference and isinstance(reference.resolved, discord.Message):
                message = reference.resolved.content

            else:
                embed = discord.Embed(description="Please specfiy the message to translate.")
                return await ctx.send(embed=embed)

        request = await self.client.session.get('https://api.openrobot.xyz/api/translate',
                                                headers={"Authorization": f"{yaml_data['OR_TOKEN']}"},
                                                params={"text": f"{message}", "to_lang": "English",
                                                        'from_lang': 'auto'})
        json = await request.json()

        embed = discord.Embed(title="Translator")

        embed.add_field(name=f"__**Before ({json[0]['source']})**__", value=f"""
{json[0]['before']}
                    """)

        embed.add_field(name=f"__**After ({json[0]['to']})**__", value=f"""
{json[0]['text']}
                    """, inline=False)

        await ctx.send(embed=embed)

    @commands.command(
        help="Shows you a list of emotes from the specified server. If no server is specified it will default to the current one.",
        aliases=['emojilist', 'emote_list', 'emoji_list', 'emotes', 'emojis'],
        brief="emotelist\nemotelist 799330949686231050")
    async def emotelist(self, ctx: CustomContext, guildID: int = None):
        if guildID:
            guild = self.client.get_guild(guildID)
            if not guild:
                return await ctx.send("I couldn't find that server. Make sure the ID you entered was correct.")
        else:
            guild = ctx.guild

        guildEmotes = guild.emojis
        emotes = []

        for emoji in guildEmotes:

            if emoji.animated:
                emotes.append(f"<a:{emoji.name}:{emoji.id}> **|** {emoji.name} **|** [`<a:{emoji.name}:{emoji.id}>`]({emoji.url})")

            if not emoji.animated:
                emotes.append(f"<:{emoji.name}:{emoji.id}> **|** {emoji.name} **|** [`<:{emoji.name}:{emoji.id}>`]({emoji.url})")

        paginator = ViewMenuPages(source=ServerEmotesEmbedPage(emotes, guild), clear_reactions_after=True)
        page = await paginator._source.get_page(0)
        kwargs = await paginator._get_kwargs_from_page(page)

        if paginator.build_view():
            paginator.message = await ctx.send(embed=kwargs['embed'], view=paginator.build_view())

        else:
            paginator.message = await ctx.send(embed=kwargs['embed'])

        await paginator.start(ctx)

    @commands.command(
        help="Shows you a list of members from the specified server. If no server is specified it will default to the current one.",
        aliases=['member_list', 'memlist', 'mem_list', 'members'],
        brief="memberlist\nmemberlist 799330949686231050")
    async def memberlist(self, ctx: CustomContext, guildID: int = None):
        if guildID:
            guild = self.client.get_guild(guildID)
            if not guild:
                return await ctx.send("I couldn't find that server. Make sure the ID you entered was correct.")
        else:
            guild = ctx.guild

        guildMembers = guild.members
        members = []

        for member in guildMembers:
            members.append(f"{member.name} **|** {member.mention} **|** `{member.id}`")

        paginator = ViewMenuPages(source=ServerMembersEmbedPage(members, guild), clear_reactions_after=True)
        page = await paginator._source.get_page(0)
        kwargs = await paginator._get_kwargs_from_page(page)
        if paginator.build_view():
            paginator.message = await ctx.send(embed=kwargs['embed'], view=paginator.build_view())
        else:
            paginator.message = await ctx.send(embed=kwargs['embed'])
        await paginator.start(ctx)

    @commands.command(
        help="Shows information about the specified role. If no role is specified it will default to the author's top role.",
        aliases=['ri'],
        brief="roleinfo @Members\nroleinfo Admim\nroleinfo 799331025724375040")
    async def roleinfo(self, ctx: CustomContext, role: discord.Role = None):
        if role is None:
            role = ctx.author.top_role

        embed = discord.Embed(title=f"{role}", description=f"""
Mention: {role.mention}
ID: {role.id}

Color: {role.color}
Position: {role.position}
Members: {len(role.members)}
Creation date: {discord.utils.format_dt(role.created_at, style="f")} ({discord.utils.format_dt(role.created_at, style="R")})

Permissions: {role.permissions}
        """)

        await ctx.send(embed=embed)

    @commands.command(
        help="Shows the first message of the specified channel. If no channel is specified it will default to the current one.",
        aliases=['fm', 'first_message'],
        brief="firstmessage\nfirstmessage #general\nfirstmessage 829418754408317029")
    async def firstmessage(self, ctx: CustomContext, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel

        async for message in channel.history(limit=1, oldest_first=True):
            content = message.content
            if len(content) > 25:
                content = f"[Hover over to see the content]({message.jump_url} '{message.clean_content}')"

            embed = discord.Embed(title=f"First message in #{channel.name}", url=f"{message.jump_url}")

            embed.add_field(name=f"__**Message**__", value=f"""
<:greyTick:596576672900186113> ID: {message.id}
<:invite:895688440639799347> Sent at: {discord.utils.format_dt(message.created_at, style='F')} ({discord.utils.format_dt(message.created_at, style='R')})
:link: Jump URL: [Click here]({message.jump_url} 'Jump URL')
            """, inline=True)

            embed.add_field(name=f"__**Author**__", value=f"""
<:greyTick:596576672900186113> ID: {message.author.id}
<:nickname:895688440912437258> Name: {message.author.display_name}
:hash: Discriminator: #{message.author.discriminator}
<:mention:908055690277433365> Mention: {message.author.mention}
:robot: Bot: {'Yes' if message.author.bot else 'No'}
            """, inline=False)

            return await ctx.send(embed=embed)

    @commands.command(
        help=":art: Shows the avatar of the specified member.",
        aliases=['av'],
        brief="avatar\navatar @Jeff\navatar Luke#1951")
    @commands.cooldown(1, 5, BucketType.member)
    async def avatar(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        await ctx.trigger_typing()

        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        if member.avatar:
            embed = discord.Embed(title=f"{'Your' if member.id == ctx.author.id else f'{member.display_name}s'} avatar", description=f"{helpers.get_member_avatar_urls(member, ctx, member.id)}")
            embed.set_image(url=member.avatar.url)

            if member.avatar != member.display_avatar:
                embed.set_thumbnail(url=member.display_avatar.url)

            return await ctx.send(embed=embed)

        else:
            await ctx.send(f"{'You dont' if member.id == ctx.author.id else f'{member.display_name} doesnt'} have a avatar.")

    @commands.group(
        help=":frame_photo: Gets the banner of the specified member.",
        invoke_without_command=True,
        aliases=['bn'],
        brief="banner\nbanner @Bruno\nbanner Mars#0001")
    async def banner(self, ctx: CustomContext, member: discord.Member = None):
        await ctx.trigger_typing()

        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        fetched_member = await self.client.fetch_user(member.id)

        if fetched_member.banner:
            embed = discord.Embed(title=f"{'Your' if member.id == ctx.author.id else f'{member.display_name}s'} banner", description=f"{helpers.get_member_banner_urls(fetched_member, ctx, member.id)}")
            embed.set_image(url=fetched_member.banner.url)

            await ctx.send(embed=embed)

        else:
            await ctx.send(f"{'You dont' if member.id == ctx.author.id else f'{member.display_name} doesnt'} have a banner.")

    @banner.command(
        help="Shows the banner of this server.",
        aliases=['guild'])
    async def server(self, ctx: CustomContext):
        errorMessage = f"This server doesn't have a banner."

        await ctx.trigger_typing()

        if ctx.guild.banner:
            embed = discord.Embed(title=f"{ctx.guild.name}'s banner", description=f"{helpers.get_server_banner_urls(ctx.guild)}")
            embed.set_image(url=ctx.guild.banner)

            await ctx.send(embed=embed)

        else:
            embed = discord.Embed(description=errorMessage)
            await ctx.send(embed=embed)

    @commands.command(
        help="Shows the latency of the bot",
        aliases=['pong'])
    async def ping(self, ctx: CustomContext):
        pings = []
        number = 0

        typing_start = time.monotonic()
        await ctx.trigger_typing()
        typing_end = time.monotonic()
        typing_ms = (typing_end - typing_start) * 1000
        pings.append(typing_ms)

        start = time.perf_counter()
        message = await ctx.send("Getting ping...")
        end = time.perf_counter()
        message_ms = (end - start) * 1000
        pings.append(message_ms)

        latency_ms = self.client.latency * 1000
        pings.append(latency_ms)

        postgres_start = time.perf_counter()
        await self.client.db.fetch("SELECT 1")
        postgres_end = time.perf_counter()
        postgres_ms = (postgres_end - postgres_start) * 1000
        pings.append(postgres_ms)

        for ms in pings:
            number += ms
        average = number / len(pings)

        embed = discord.Embed(title="🏓 Pong")
        embed.add_field(name=f":globe_with_meridians: Websocket latency", value=f"{round(latency_ms)}ms{' ' * (9 - len(str(round(latency_ms, 3))))}", inline=True)
        embed.add_field(name=f"<a:typing:597589448607399949> Typing latency", value=f"{round(typing_ms)}ms{' ' * (9 - len(str(round(typing_ms, 3))))}", inline=True)
        embed.add_field(name=f":speech_balloon: Message latency", value=f"{round(message_ms)}ms{' ' * (9 - len(str(round(message_ms, 3))))}", inline=True)
        embed.add_field(name=f"<:psql:896134588961800294> Database latency", value=f"{round(postgres_ms)}ms{' ' * (9 - len(str(round(postgres_ms, 3))))}", inline=True)
        embed.add_field(name=f":infinity: Average latency", value=f"{round(average)}ms{' ' * (9 - len(str(round(average, 3))))}")

        await ctx.send(content="Received ping!", embed=embed)

    @commands.command(brief="Gives info on pypi packages")
    async def pypi(self, ctx, *, package):
        pypi_response = await self.client.session.get(f"https://pypi.org/pypi/{package}/json")
        if pypi_response.ok:

            pypi_response = await pypi_response.json()

            pypi_data = pypi_response["info"]

            embed = discord.Embed(title=f"{pypi_data.get('name') if pypi_data.get('name') else 'None provided'}", url=f"{pypi_data.get('release_url') if pypi_data.get('release_url') else discord.Embed.Empty}", description=f"{pypi_data.get('summary') if pypi_data.get('summary') else 'None provided'}")

            embed.add_field(name=f"__**Author**__", value=f"""
<:nickname:895688440912437258> Name: {pypi_data.get('author') or 'None provided'}
:e_mail: Email: {pypi_data.get('author_email') or 'None provided'}
            """, inline=True)

            embed.add_field(name=f"__**Package**__", value=f"""
:link: Download URL: {pypi_data.get('download_url') or 'None provided'}
:link: Documentation URL: {pypi_data.get('dosc_url') or 'None provided'}
:house: Homepage: {pypi_data.get('home_page') or 'None provided'}
:newspaper: License: {pypi_data.get('license') or 'None provided'}
:key: Keywords: {pypi_data.get('keywords') or 'None provided'}
            """, inline=False)

            embed.set_thumbnail(url="https://i.imgur.com/oP0e7jK.png")

            await ctx.send(embed=embed)

        else:
            await ctx.send("Invalid package!")

    @commands.command(
        help="Get unix timestamp from datetime. Datetime example = 2020/11/25 12:56:54",
        aliases=['2uinx', 'tu', 'time', 'datetime'])
    @commands.cooldown(1, 5, BucketType.user)
    async def tounix(self, ctx, *, datetime: str):
        datetime = datetime.replace('-', '/')
        datetime = datetime.replace('.', '/')
        base_url = "https://showcase.api.linx.twenty57.net/UnixTime/tounixtimestamp?datetime="
        url = base_url + datetime

        async with self.client.session.get(url) as resp:
            try:
                js = await resp.json()

            except Exception as e:
                raise commands.BadArgument()

            else:
                error = js.get('Error')
                if error:
                    embed = discord.Embed(title="API Error", description=f"""
```log
{error}
```
                    """)

                    return await ctx.send(embed=embed)

                embed = discord.Embed(title=f"Unix timestamps for {datetime}")

                embed.add_field(name=f"__**Raw**__", value=f"""
`<t:{js['UnixTimeStamp']}>`  
`<t:{js['UnixTimeStamp']}:t>`
`<t:{js['UnixTimeStamp']}:T>`
`<t:{js['UnixTimeStamp']}:F>`
`<t:{js['UnixTimeStamp']}:d>`
`<t:{js['UnixTimeStamp']}:D>`
`<t:{js['UnixTimeStamp']}:R>`
                """, inline=True)

                embed.add_field(name=f"__**Result**__", value=f"""
<t:{js['UnixTimeStamp']}>
<t:{js['UnixTimeStamp']}:t>
<t:{js['UnixTimeStamp']}:T>
<t:{js['UnixTimeStamp']}:F>
<t:{js['UnixTimeStamp']}:d>
<t:{js['UnixTimeStamp']}:D>
<t:{js['UnixTimeStamp']}:R>
                """, inline=True)

                await ctx.send(embed=embed)

    @commands.command(
        help="Shows the uptime of the bot.",
        aliases=['up'])
    async def uptime(self, ctx: CustomContext):
        delta_uptime = discord.utils.utcnow() - self.client.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        embed = discord.Embed(title=f"I've been online for {ctx.time(days=days, hours=hours, minutes=minutes, seconds=seconds)}")

        await ctx.send(embed=embed)

    @commands.command(
        help="Shows how many servers the bot is in.",
        aliases=['guilds'])
    async def servers(self, ctx: CustomContext) -> discord.Message:
        embed = discord.Embed(title=f"I'm in `{len(self.client.guilds)}` servers.")

        await ctx.send(embed=embed)

    @commands.command(
        help="Shows how many messages the bot has seen since the last restart.",
        aliases=['msg', 'msgs', 'message'])
    async def messages(self, ctx: CustomContext) -> discord.Message:
        embed = discord.Embed(title=f"I've seen a total of `{self.client.messages_count}` messages and `{self.client.edited_messages_count}` edits.")

        await ctx.send(embed=embed)

    @commands.group(
        help="<:scroll:904038785921187911> Todo commands.",
        aliases=['tasks'])
    async def todo(self, ctx: CustomContext):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @todo.command(
        name="add",
        help="Adds the specified task to your todo list.",
        aliases=['create', 'new', 'make'])
    async def todo_add(self, ctx: CustomContext, *, text) -> discord.Message:
        todo = await self.client.db.fetchrow("INSERT INTO todo (user_id, text, jump_url, creation_date) VALUES ($1, $2, $3, $4) ON CONFLICT (user_id, text) DO UPDATE SET user_id = $1 RETURNING jump_url, creation_date", ctx.author.id, text, ctx.message.jump_url, ctx.message.created_at)

        if todo['creation_date'] != ctx.message.created_at:
            embed = discord.Embed(title="That's already in your todo list!", url=f"{todo['jump_url']}", description=f"[Added here]({todo['jump_url']})")

            return await ctx.send(embed=embed)

        embed = discord.Embed(title="Added to your todo list:", description=text)

        return await ctx.send(embed=embed)

    @todo.command(
        name="list",
        help="Sends a list of your tasks.",
        aliases=['show', 'view'])
    async def todo_list(self, ctx: CustomContext):
        todos = await self.client.db.fetch("SELECT text, creation_date, jump_url FROM todo WHERE user_id = $1 ORDER BY creation_date ASC", ctx.author.id)

        if not todos:
            raise errors.EmptyTodoList

        todoList = []
        number = 0

        for todo in todos:
            number = number + 1
            todoList.append(f"**[{number}]({todo['jump_url']})**. **({discord.utils.format_dt(todo['creation_date'], style='R')}):** {todo['text']}")

        title = f"{ctx.author.name}'s todo list"

        paginator = ViewMenuPages(source=TodoListEmbedPage(title=title, author=ctx.author, data=todoList), clear_reactions_after=True)
        page = await paginator._source.get_page(0)
        kwargs = await paginator._get_kwargs_from_page(page)

        if paginator.build_view():
            paginator.message = await ctx.send(embed=kwargs['embed'], view=paginator.build_view())

        else:
            paginator.message = await ctx.send(embed=kwargs['embed'])

        await paginator.start(ctx)

    @todo.command(
        name="clear",
        help="Deletes all tasks from your todo list.",
        aliases=['nuke'])
    async def todo_clear(self, ctx: CustomContext) -> discord.Message:
        confirm = await ctx.confirm("Are you sure you want to clear your todo list?\n*This action cannot be undone*")

        if confirm is True:
            todos = await self.client.db.fetchval("WITH deleted AS (DELETE FROM todo WHERE user_id = $1 RETURNING *) SELECT count(*) FROM deleted;", ctx.author.id)

            embed = discord.Embed(title="Cleared your todo list.", description=f"{todos} tasks were removed.")

            return await ctx.send(embed=embed)

        return await ctx.send("Okay, cancelled.")

    @todo.command(
        name="remove",
        help="Removes the specified task from your todo list",
        aliases=['delete', 'del', 'rm'])
    async def todo_remove(self, ctx: CustomContext, index: int) -> discord.Message:
        todos = await self.client.db.fetch("SELECT text, jump_url, creation_date FROM todo WHERE user_id = $1 ORDER BY creation_date ASC", ctx.author.id)

        try:
            to_delete = todos[index - 1]

        except:
            return await ctx.send(f"I couldn't find a task with index {index}")

        await self.client.db.execute("DELETE FROM todo WHERE (user_id, text) = ($1, $2)", ctx.author.id, to_delete['text'])

        embed = discord.Embed(title=f"Successfully removed task number **{index}**:", description=f"({discord.utils.format_dt(to_delete['creation_date'], style='R')}) {to_delete['text']}")

        return await ctx.send(embed=embed)

    @todo.command(
        name="edit",
        help="Edits the specified task",
        aliases=['change', 'modify'])
    async def todo_edit(self, ctx: CustomContext, index: int, *, text) -> discord.Message:
        todos = await self.client.db.fetch("SELECT text, jump_url, creation_date FROM todo WHERE user_id = $1 ORDER BY creation_date ASC", ctx.author.id)

        try:
            to_edit = todos[index - 1]

        except KeyError:
            return await ctx.send(f"I couldn't find a task with index {index}")

        old = await self.client.db.fetchrow("SELECT text, creation_date, jump_url FROM todo WHERE (user_id, text) = ($1, $2)", ctx.author.id, to_edit['text'])

        await self.client.db.execute( "UPDATE todo SET text = $1, jump_url = $2, creation_date = $3 WHERE (user_id, text) = ($4, $5)", f"{text} (edited)", ctx.message.jump_url, ctx.message.created_at, ctx.author.id, to_edit['text'])

        new = await self.client.db.fetchrow("SELECT text, creation_date, jump_url FROM todo WHERE (user_id, text) = ($1, $2)", ctx.author.id, f"{text} (edited)")

        embed = discord.Embed(title=f"Successfully edited task number **{index}**:", description=f"""
__**Old**__
Text: {old['text']}
Creation date: {discord.utils.format_dt(old['creation_date'], style='R')}
Jump URL: [Click here]({old['jump_url']})

__**New**__
Text: {new['text']}
Creation date: {discord.utils.format_dt(new['creation_date'], style='R')}
Jump URL: [Click here]({new['jump_url']})
                """)

        return await ctx.send(embed=embed)

    @commands.command(
        help="Makes you go AFK. If someone pings you the bot will tell them that you're AFK.")
    async def afk(self, ctx: CustomContext, *, reason="No reason provided"):
        if ctx.author.id in self.client.afk_users and ctx.author.id in self.client.auto_un_afk and self.client.auto_un_afk[ctx.author.id] is True:
            return

        if ctx.author.id not in self.client.afk_users:
            await self.client.db.execute("INSERT INTO afk (user_id, start_time, reason) VALUES ($1, $2, $3) ON CONFLICT (user_id) DO UPDATE SET start_time = $2, reason = $3", ctx.author.id, ctx.message.created_at, reason[0:1800])
            self.client.afk_users[ctx.author.id] = True

            embed = discord.Embed(title=f"<:idle:872784075591675904>{ctx.author.name} is now AFK",
                                  description=f"With the reason being: {reason}")

            await ctx.send(embed=embed)

        else:
            self.client.afk_users.pop(ctx.author.id)

            info = await self.client.db.fetchrow("SELECT * FROM afk WHERE user_id = $1", ctx.author.id)
            await self.client.db.execute("INSERT INTO afk (user_id, start_time, reason) VALUES ($1, null, null) ON CONFLICT (user_id) DO UPDATE SET start_time = null, reason = null", ctx.author.id)

            start_time = info["start_time"]

            delta_uptime = ctx.message.created_at - start_time
            hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            days, hours = divmod(hours, 24)

            embed = discord.Embed(title=f"👋 Welcome back {ctx.author.name}!", description=f"""
You've been AFK for {ctx.time(days=int(days), hours=int(hours), minutes=int(minutes), seconds=int(seconds))}.
With the reason being: {info['reason']}""")

            await ctx.send(embed=embed)

            await ctx.message.add_reaction("👋")

    @commands.command(
        help="Toggles if the bot should remove your AFK status after you send a message or not",
        aliases=['auto_un_afk', 'aafk', 'auto-afk-remove'])
    async def autoafk(self, ctx: CustomContext, mode: bool = None):
        mode = mode or (False if (ctx.author.id in self.client.auto_un_afk and self.client.auto_un_afk[
            ctx.author.id] is True) or ctx.author.id not in self.client.auto_un_afk else True)
        self.client.auto_un_afk[ctx.author.id] = mode

        await self.client.db.execute("INSERT INTO afk (user_id, auto_un_afk) VALUES ($1, $2) "
                                     "ON CONFLICT (user_id) DO UPDATE SET auto_un_afk = $2", ctx.author.id, mode)

        text = f'{"Enabled" if mode is True else "Disabled"}'

        embed = discord.Embed(title=f"{ctx.toggle(mode)} {text} automatic AFK removal",
                              description="To remove your AFK status do `afk` again.")

        return await ctx.send(embed=embed)

    @commands.command(
        help="Checks if the specified member has voted or not.",
        aliases=['vote_check'])
    async def votecheck(self, ctx: CustomContext, member: discord.Member = None):
        await ctx.trigger_typing()

        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        if member.bot:
            return await ctx.send("bro bots cant vote")

        url = f"{self.client.ep}bots/{ctx.me.id}/check"

        params = dict(userId=member.id)

        response = await self.client.session.get(url=url, headers=self.client.headers, params=params)

        if response.status != 200:
            return await ctx.send(f"Received code {response.status}: {response.reason}")

        data = await response.json()
        voted = bool(data['voted'])

        if member != ctx.author:
            text = f"{member.display_name} {'has' if voted else 'has not'} voted."

        else:
            text = f"You {'have' if voted else 'have not'} voted."

        embed = discord.Embed(title="Vote checker", description=text)

        return await ctx.send(embed=embed)

    @commands.command(
        help="Sends the source code of the bot/a command")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def source(self, ctx: CustomContext, *, command: str = None):
        prefix = ctx.clean_prefix
        source_url = 'https://github.com/Ender2K89/Stealth-Bot'

        if command is None:
            embed = discord.Embed(title=f"Click here for the source code of this bot", url=f"{source_url}")

            view = discord.ui.View()
            style = discord.ButtonStyle.gray
            item = discord.ui.Button(style=style, emoji="<:github:744345792172654643>", label="Source code",
                                     url=f"{source_url}")
            view.add_item(item=item)

            return await ctx.send(embed=embed, view=view)

        if command == 'help':
            src = type(self.client.help_command)
            module = src.__module__
            filename = inspect.getsourcefile(src)

        else:
            obj = self.client.get_command(command.replace('.', ' '))

            if obj is None:
                embed = discord.Embed(title=f"Click here for the source code of this bot",
                                      description="I couldn't find that command", url=f"{source_url}")

                view = discord.ui.View()
                style = discord.ButtonStyle.gray
                item = discord.ui.Button(style=style, emoji="<:github:744345792172654643>", label="Source code",
                                         url=f"{source_url}")
                view.add_item(item=item)
                return await ctx.send(embed=embed, view=view)

            src = obj.callback.__code__
            module = obj.callback.__module__
            filename = src.co_filename

        lines, firstlineno = inspect.getsourcelines(src)

        if not module.startswith('discord'):
            location = os.path.relpath(filename).replace('\\', '/')

        else:
            location = module.replace('.', '/') + '.py'
            source_url = 'https://github.com/Rapptz/discord.py'
            branch = 'master'

        final_url = f'{source_url}/tree/main/{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}'
        embed = discord.Embed(title=f"Click here for the source code of the `{prefix}{command}` command",
                              url=f"{final_url}")
        embed.set_footer(text=f"{location}#L{firstlineno}-L{firstlineno + len(lines) - 1}")

        view = discord.ui.View()
        style = discord.ButtonStyle.gray
        item = discord.ui.Button(style=style, emoji="<:github:744345792172654643>", label="Source code",
                                 url=f"{final_url}")
        view.add_item(item=item)

        await ctx.send(embed=embed, view=view)

    @commands.group(
        invoke_without_command=True,
        help=":books: | Gives you a documentation link for a discord.py entity.\nEvents, objects, and functions are all supported through a cruddy fuzzy algorithm.",
        aliases=['rtfd', 'rtdm'])
    async def rtfm(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'master', obj)

    @rtfm.command(
        help="Gives you a documentation link for a discord.py entity (Japanese).",
        name='jp')
    async def rtfm_jp(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'latest-jp', obj)

    @rtfm.command(
        help="Gives you a documentation link for a Python entity.",
        name='python',
        aliases=['py'])
    async def rtfm_python(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'python', obj)

    @rtfm.command(
        help="Gives you a documentation link for a Python entity (Japanese).",
        name='py-jp',
        aliases=['py-ja'])
    async def rtfm_python_jp(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'python-jp', obj)

    @rtfm.command(
        help="Gives you a documentation link for a discord.py entity (master branch)",
        name='master',
        aliases=['2.0'])
    async def rtfm_master(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'master', obj)

    @rtfm.command(
        help="Gives you a documentation link for a enhanced-discord.py entity",
        name='enhanced-dpy',
        aliases=['edpy'])
    async def rtfm_edpy(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'edpy', obj)

    @rtfm.command(
        help="Gives you a documentation link for an asyncbing entity",
        name='asyncbing',
        aliases=['bing'])
    async def rtfm_asyncbing(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'bing', obj)

    @rtfm.command(
        help="Gives you a documentation link for a chaidiscord.py entity",
        name='chaidiscordpy',
        aliases=['chaidpy', 'cdpy'])
    async def rtfm_chai(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'chai', obj)

    @rtfm.command(
        help="Gives you a documentation link for a pycord entity",
        name='pycord')
    async def rtfm_pycord(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'pycord', obj)

    @rtfm.command(
        help="Gives you a documentation link for a pomice entity",
        name='pomice')
    async def rtfm_pomice(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'pomice', obj)