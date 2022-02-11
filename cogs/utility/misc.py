import io
import expr
import yaml
import errors
import typing
import discord
import datetime

from helpers import helpers
from ._base import UtilityBase
from discord.ext import commands
from helpers.context import CustomContext
from discord.ext.commands.cooldowns import BucketType

with open(r'/root/stealthbot/config.yaml') as file:
    full_yaml = yaml.load(file)

yaml_data = full_yaml

class Misc(UtilityBase):
    
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
        total = await self.bot.db.fetchrow(query)

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

        records = await self.bot.db.fetch(query)
        value = '\n'.join(f'{lookup[index]}: {command} ({uses} uses)' for (index, (command, uses)) in enumerate(records))
        e.add_field(name='Top Commands', value=value, inline=False)

        query = """SELECT guild_id, COUNT(*) AS "uses"
                   FROM commands
                   GROUP BY guild_id
                   ORDER BY "uses" DESC
                   LIMIT 5;
                """

        records = await self.bot.db.fetch(query)
        value = []
        for (index, (guild_id, uses)) in enumerate(records):
            if guild_id is None:
                guild = 'Private Message'
            else:
                guild = self.bot.get_guild(guild_id) or f'<Unknown {guild_id}>'

            emoji = lookup[index]
            value.append(f'{emoji}: {guild} ({uses} uses)')

        e.add_field(name='Top Guilds', value='\n'.join(value), inline=False)

        query = """SELECT user_id, COUNT(*) AS "uses"
                   FROM commands
                   GROUP BY user_id
                   ORDER BY "uses" DESC
                   LIMIT 5;
                """

        records = await self.bot.db.fetch(query)
        value = []
        for (index, (author_id, uses)) in enumerate(records):
            user = self.bot.get_user(author_id) or f'<Unknown {author_id}>'
            emoji = lookup[index]
            value.append(f'{emoji}: {user} ({uses} uses)')

        e.add_field(name='Top Users', value='\n'.join(value), inline=False)
        await ctx.send(embed=e)
    
    @commands.command(
        help=":art: Shows the avatar of the specified member.",
        aliases=['av'],
        brief="avatar\navatar @Jeff\navatar Luke#1951")
    @commands.cooldown(1, 5, BucketType.member)
    async def avatar(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None) -> discord.Message:
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
            return await ctx.send(f"{'You dont' if member.id == ctx.author.id else f'{member.display_name} doesnt'} have a avatar.")

    @commands.group(
        help=":frame_photo: Gets the banner of the specified member.",
        invoke_without_command=True,
        aliases=['bn'],
        brief="banner\nbanner @Bruno\nbanner Mars#0001")
    async def banner(self, ctx: CustomContext, member: discord.Member = None) -> discord.Message:
        await ctx.trigger_typing()

        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        fetched_member = await self.bot.fetch_user(member.id)

        if fetched_member.banner:
            embed = discord.Embed(title=f"{'Your' if member.id == ctx.author.id else f'{member.display_name}s'} banner", description=f"{helpers.get_member_banner_urls(fetched_member, ctx, member.id)}")
            embed.set_image(url=fetched_member.banner.url)

            return await ctx.send(embed=embed)

        else:
            return await ctx.send(f"{'You dont' if member.id == ctx.author.id else f'{member.display_name} doesnt'} have a banner.")

    @banner.command(
        help="Shows the banner of this server.",
        aliases=['guild'])
    async def server(self, ctx: CustomContext) -> discord.Message:
        await ctx.trigger_typing()

        if ctx.guild.banner:
            embed = discord.Embed(title=f"{ctx.guild.name}'s banner", description=f"{helpers.get_server_banner_urls(ctx.guild)}")
            embed.set_image(url=ctx.guild.banner.url)

            return await ctx.send(embed=embed)

        else:
            embed = discord.Embed(description=f"This server doesn't have a banner.")
            return await ctx.send(embed=embed)

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

        request = await self.bot.session.get('https://api.openrobot.xyz/api/translate',
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
        
    @commands.command()
    async def covid(self, ctx: CustomContext, country: str = None):
        url = f"https://disease.sh/v3/covid-19/countries/{country}"

        if country is None:
            url = f"https://disease.sh/v3/covid-19/all"

        coviddata = await self.bot.session.get(url)
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

        response = await self.bot.session.get("https://api.jeyy.xyz/discord/spotify", params={'title': spotify.title, 'cover_url': spotify.album_cover_url, 'duration_seconds': spotify.duration.seconds, 'start_timestamp': spotify.start.timestamp(), 'artists': spotify.artists})
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
            post = await self.bot.mystbin.post(code, syntax=language)
            return await ctx.send(f"Successfully posted to mystbin, here's the link: {str(post)}")

        except Exception as e:
            return await ctx.send(f"Failed to post to mystbin, here's the error: {e}")

    @commands.command()
    async def weather(self, ctx, *, location: str) -> discord.Message:
        request = await self.bot.session.get(f"http://api.weatherapi.com/v1/current.json?key={yaml_data['WEATHER_TOKEN']}&q={location}")
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
        help="Checks the specified member's avatar for any inappropriate content.",
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

        request = await self.bot.session.get(f'https://api.openrobot.xyz/api/nsfw-check', headers={'Authorization': f'{yaml_data["OR_TOKEN"]}'}, params={'url': member.display_avatar.url})
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

        return await ctx.send(embeds=[embed1, embed2])