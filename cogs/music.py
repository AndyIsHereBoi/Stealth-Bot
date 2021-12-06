import re
import math
import pomice
import typing
import aiohttp
import discord
import asyncio
import logging
import datetime
import time as t
from errors import *
from discord.ext import commands
from async_timeout import timeout
from helpers.helpers import convert_bytes
from helpers import mpaginator as paginator
from ._music.player import QueuePlayer as Player


URL_RX = re.compile(r'https?://(?:www\.)?.+')
HH_MM_SS_RE = re.compile(r"(?P<h>\d{1,2}):(?P<m>\d{1,2}):(?P<s>\d{1,2})")
MM_SS_RE = re.compile(r"(?P<m>\d{1,2}):(?P<s>\d{1,2})")
HUMAN_RE = re.compile(r"(?:(?P<m>\d+)\s*m\s*)?(?P<s>\d+)\s*[sm]")
OFFSET_RE = re.compile(r"(?P<s>(?:\-|\+)\d+)\s*s", re.IGNORECASE)

def setup(bot):
    bot.add_cog(Music(bot))

def format_time(milliseconds: typing.Union[float, int]) -> str:
    hours, rem = divmod(int(milliseconds // 1000), 3600)
    minutes, seconds = divmod(rem, 60)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

class Music(commands.Cog):
    "Commands used to play/control music in a VC."
    
    def __init__(self, bot):
        self.bot = bot
        self.select_emoji = "<a:music:888778105844563988>"
        self.select_brief = "Commands used to play/control music in a VC."
    
    async def cog_before_invoke(self, ctx: commands.Context):
        if (is_guild := ctx.guild is not None)\
            and ctx.command.name not in ('lyrics', 'current', 'queue', 'nodes', 'toggle', 'role', 'settings', 'dj'):
            await self.ensure_voice(ctx)

        if (is_guild := ctx.guild is not None)\
            and ctx.command.name in ('current', 'queue'):

            if (ctx.voice_client is None):
                raise NoPlayer

        return is_guild
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        if (player := member.guild.voice_client) is None:
            player = self.bot.pomice.get_node().get_player(member.guild.id)
        
        if not player:
            return
        
        if member.id == self.bot.user.id and after.channel:

            if not player.is_paused:
                await player.set_pause(True)
                await asyncio.sleep(1)
                await player.set_pause(False)
        
        if member.id == self.bot.user.id and not after.channel:
                
            await player.destroy()

        if member.bot:
            return
        
        if member.id == player.dj.id and not after.channel:
            members = self.get_members(player.channel.id)
            
            if len(members) != 0:
                for m in members:
                    if m == player.dj or m.bot:
                        continue
                    else:
                        player.dj = m
            else:
                return
            
            embed = discord.Embed(title="New DJ", description=f"The new DJ is {player.dj.mention}!", color=discord.Color.green())
            return await player.text_channel.send(embed=embed)
        
        if after.channel and after.channel.id == player.channel.id and player.dj not in player.channel.members and player.dj != member:
            if not member.bot:
                player.dj = member
                
            else:
                return
            
            embed = discord.Embed(title="New DJ", description=f"The new DJ is {player.dj.mention}!", color=discord.Color.green())
            return await player.text_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_pomice_track_start(self, player: Player, track: pomice.Track):
        track = player.current.original
        ctx = track.ctx
        
        if player.loop == 1:
            return

        if player.loop == 2 and player.queue.is_empty:
            return

        embed = self.build_embed(player)
        
        player.message = await ctx.send(embed=embed, reply=False, footer=False)

    @commands.Cog.listener()
    async def on_pomice_track_end(self, player: Player, track: pomice.Track, _):
        player = player or self.bot.pomice.get_node().get_player(track.ctx.guild.id)
        if not player:
            return

        text: discord.TextChannel = player.text_channel
        channel: discord.TextChannel = player.channel
        player.clear_votes()

        if player.loop == 1:
            await player.play(track)
            return

        if player.loop == 2:
            player.queue.put(track)

        try:
            await player.message.delete()
        except (discord.HTTPException, AttributeError):
            pass

        try:
            async with timeout(300):
                track = await player.queue.get_wait()

                try:
                    await player.play(track, ignore_if_playing=True)
                    
                except Exception as e:
                    self.bot.dispatch("pomice_track_end", player, track, "Failed playing the next track in a queue")
                    logging.error(e)
                    raise TrackFailed(track)

        except asyncio.TimeoutError:
            try:
                await player.destroy()
                
            except:
                return
            
            else:
                await text.send(f":wave: **|** I've left {channel.mention} due to inactivity in the past 5 minutes.")
        
    async def ensure_voice(self, ctx:commands.Context):
        """ This check ensures that the bot and command author are in the same voicechannel. """
        should_connect = ctx.command.name in ('play', 'join', 'playnext', 'playnow')
        player = ctx.voice_client
        
        if ctx.command.name in ('join') and player:
            raise AlreadyConnectedToChannel

        if not ctx.author.voice or not (channel := ctx.author.voice.channel):
            raise NoConnection

        if not player:
            if not should_connect:
                raise NoVoiceChannel 
              
            if ctx.guild.afk_channel:
                if channel.id == ctx.guild.afk_channel.id:
                    raise AfkChannel

            permissions = channel.permissions_for(ctx.me)

            if not permissions.connect:
                raise NoPerms

            if not permissions.speak:
                raise NoPerms

            if channel.user_limit != 0:
                limit = channel.user_limit
                if len(channel.members) == limit:
                    raise FullVoiceChannel

            player = await channel.connect(cls=Player)
            player.text_channel = ctx.channel
            player.dj = ctx.author
        
        else:
            if int(player.channel.id) != channel.id:
                raise IncorrectChannelError
            if int(player.text_channel) != ctx.channel.id:
                raise IncorrectTextChannelError

    def get_channel(self, id:int):
        return self.bot.get_channel(id)

    def get_members(self, channel_id:int):
        channel = self.bot.get_channel(int(channel_id))
        return list(member for member in channel.members if not member.bot)

    async def get_tracks(self, ctx: commands.Context, query:str):
        return await ctx.voice_client.get_tracks(query.strip("<>"), ctx=ctx)

    def get_thumbnail(self, track:pomice.Track) -> typing.Union[str, discord.embeds._EmptyEmbed]:
        if (thumbnail := track.info.get("thumbnail")):
            return thumbnail
        
        elif any(i in track.uri for i in ("youtu.be", "youtube.com")):
            return f"https://img.youtube.com/vi/{track.identifier}/maxresdefault.jpg"
        
        else:
            return discord.embeds.EmptyEmbed

    def build_embed(self, player:pomice.Player):
        track = player.current
        
        if not track.spotify:
            track: pomice.Track = player.current.original

        if track.is_stream:
            length = "<:status_streaming:596576747294818305> Live Stream"
            
        else:
            length = format_time(track.length)

        embed = discord.Embed(title=f"**{track.title if not track.spotify else str(track.title)}**", url=f"{track.uri}")
        embed.set_thumbnail(url=self.get_thumbnail(track))
        
        if player.volume < 25 or player.volume == 25:
            volume_emoji = "<:low:909834343655034881>"
            
        elif player.volume < 50 or player.volume == 50:
            volume_emoji = "<:medium:909834343822790676>"
            
        else:
            volume_emoji = "<:high:909834343449501707>"

        if "spotify" in track.uri:
            embed.add_field(name=f"{'Artists' if ', ' in track.author else 'Artist'}", value=f"{track.author}", inline=False)
            embed.add_field(name=f"Duration", value=f"{length if length else 'No length'}", inline=False)
            embed.add_field(name=f"Volume", value=f"{volume_emoji} {f'{player.volume}%' if player.volume else 'No volume'}", inline=False)
            embed.add_field(name=f"Up next", value=f"{player.queue[0] if player.queue else 'Nothing is up next.'}", inline=False)
            
            embed.set_footer(text=f"{f'Spotify song • Songs in queue: {len(player.queue)}' if player.queue else 'Spotify song'}", icon_url="https://cdn.discordapp.com/emojis/899263771342700574.png?size=96")
        
        elif "soundcloud" in track.uri:
            embed.add_field(name=f"{'Artists' if ', ' in track.author else 'Artist'}", value=f"{track.author}", inline=False)
            embed.add_field(name=f"Duration", value=f"{length if length else 'No length'}", inline=False)
            embed.add_field(name=f"Volume", value=f"{volume_emoji} {f'{player.volume}%' if player.volume else 'No volume'}", inline=False)
            embed.add_field(name=f"Up next", value=f"{player.queue[0] if player.queue else 'Nothing is up next.'}", inline=False)
            
            embed.set_footer(text=f"{f'SoundCloud song • Songs in queue: {len(player.queue)}' if player.queue else 'SoundCloud song'}", icon_url="https://cdn.discordapp.com/emojis/908786462315671573.png?size=96")

        elif "youtu" in track.uri:
            embed.add_field(name=f"Channel", value=f"{track.author}")
            embed.add_field(name=f"Duration", value=f"{length if length else 'No length'}", inline=False)
            embed.add_field(name=f"Volume", value=f"{volume_emoji} {f'{player.volume}%' if player.volume else 'No volume'}", inline=False)
            embed.add_field(name=f"Up next", value=f"{player.queue[0] if player.queue else 'Nothing is up next.'}", inline=False)
            
            embed.set_footer(text=f"{f'YouTube song • Songs in queue: {len(player.queue)}' if player.queue else 'YouTube song'}", icon_url="https://cdn.discordapp.com/emojis/845592321177026560.png?size=96")
        
        else:
            pass
        
        return embed

    def is_privileged(self, ctx):
        """Check whether the user have perms to be DJ"""
        player = ctx.voice_client 

        dj_only = self.bot.dj_only(ctx.guild)
        dj_role = self.bot.dj_role(ctx.guild)
        
        if not dj_only:
            return True

        elif dj_role and dj_role in ctx.author.roles:
            return True
        
        elif player.dj == ctx.author:
            return True

        elif ctx.author.guild_permissions.manage_roles:
            return True

        else:
            return False

    def required(self, ctx:commands.Context):
        """ Method which returns required votes based on amount of members in a channel. """
        
        members = len(self.get_members((ctx.voice_client).channel.id))
        return math.ceil(members / 2.5)

    @commands.command(
        help="Adds the specified song to the queue.",
        aliases=['p', 'sing', 'playsong', 'playmusic', 'listen', 'listenmusic', 'musiclisten'])
    async def play(self, ctx, *, song: str):
        player = ctx.voice_client 
        
        try:
            results = await self.get_tracks(ctx, song)
            
        except pomice.TrackLoadError:
            raise LoadFailed
        
        if not results:
            raise NoMatches

        if isinstance(results, pomice.Playlist):
            tracks = results.tracks
            
            for track in tracks:
                player.queue.put(track)
            
            if results.spotify:
                thumbnail = results.thumbnail
                
            else:
                thumbnail = self.get_thumbnail(results.tracks[0])

            embed = discord.Embed(title="Added a playlist to the queue", description=f"**[{results}]({song})** with **{len(tracks)}** songs.")
            embed.set_thumbnail(url=thumbnail or discord.embeds.EmptyEmbed)
            
            await ctx.send(embed=embed)

        else:
            track = results[0]
            player.queue.put(track)

            embed = discord.Embed(title="Added a song to the queue", description=f"**[{track.title.upper()}]({track.uri})**")
            embed.set_thumbnail(url=self.get_thumbnail(track))
            
            await ctx.send(embed=embed)
            
        if not player.is_playing:
            await player.play(player.queue.get())

    @commands.command(
        help="Adds the specified song to the top of the queue.",
        aliases=['pnext', 'p_next', 'p-next'])
    async def playnext(self, ctx, *, song: str):
        player = ctx.voice_client 
        
        try:
            results = await self.get_tracks(ctx, song)
            
        except pomice.TrackLoadError:
            raise LoadFailed
        
        if not results:
            raise NoMatches

        if isinstance(results, pomice.Playlist):
            tracks = results.tracks
            
            for track in reversed(tracks):
                player.queue.put_at_front(track)
            
            if results.spotify:
                thumbnail = results.thumbnail
                
            else:
                thumbnail = self.get_thumbnail(results.tracks[0])

            embed = discord.Embed(title="Added a playlist to the queue", description=f"**[{results}]({song})** with **{len(tracks)}** songs.")
            embed.set_thumbnail(url=thumbnail or discord.embeds.EmptyEmbed)
            
            await ctx.send(embed=embed)

        else:
            track = results[0]
            player.queue.put_at_front(track)

            embed = discord.Embed(title="Added a song to the queue", description=f"**[{track.title.upper()}]({track.uri})**")
            embed.set_thumbnail(url=self.get_thumbnail(track))
            
            await ctx.send(embed=embed)
            
        if not player.is_playing:
            track = player.queue.get()
            await player.play(track)

    @commands.command(
        help="Plays the specified song instantly.",
        aliases=['pnow', 'p_now', 'p-now'])
    async def playnow(self, ctx, *, song: str):
        player = ctx.voice_client 
        
        try:
            results = await self.get_tracks(ctx, song)
            
        except pomice.TrackLoadError:
            raise LoadFailed
        
        if not results:
            raise NoMatches

        if isinstance(results, pomice.Playlist):
            tracks = results.tracks
            
            for track in reversed(tracks):
                player.queue.put_at_front(track)
            
            if results.spotify:
                thumbnail = results.thumbnail
                
            else:
                thumbnail = self.get_thumbnail(results.tracks[0])

            embed = discord.Embed(title="Added a playlist to the queue", description=f"**[{results}]({song})** with **{len(tracks)}** songs.")
            embed.set_thumbnail(url=thumbnail or discord.embeds.EmptyEmbed)
            
            await ctx.send(embed=embed)

        else:
            track = results[0]
            player.queue.put_at_front(track)

            embed = discord.Embed(title="Added a song to the queue", description=f"**[{track.title.upper()}]({track.uri})**")
            embed.set_thumbnail(url=self.get_thumbnail(track))
            
            await ctx.send(embed=embed)
        
        if player.loop == 1:
            player.loop = 0

        if not player.is_playing:
            track = player.queue.get()
            await player.play(track)
        else:
            await player.stop()

    @commands.command(
        help="Sends information about the current song.",
        aliases=['now_playing', 'now-playing', 'current', 'np', 'song'])
    async def nowplaying(self, ctx):
        player = ctx.voice_client
        
        if not player:
            raise NoPlayer

        if not player.is_playing:
            raise NoCurrentTrack
        
        await ctx.send(embed=self.build_embed(player))
        
    @commands.command(
        help="Makes the bot join your VC.",
        aliases=['connect'])
    async def join(self, ctx):
        player = ctx.voice_client
        
        await ctx.send(f"<:low:909834343655034881> **|** Successfully joined {player.channel.mention}.")

    @commands.command(
        help="Makes the bot leave the current VC and clears the queue.",
        aliases=['disconnect', 'dc', 'fuckoff'])
    async def leave(self, ctx):
        player = ctx.voice_client
        
        if not self.is_privileged(ctx):
            raise NotAuthorized
        
        await player.destroy()
        text = "the current VC"
        await ctx.send(f"<:high:909834343449501707> **|** Successfully left {f'{ctx.author.voice.channel.mention if ctx.author.voice else text}' if isinstance(ctx.author, discord.Member) else 'the current VC'} and cleared the queue.")

    @commands.command(
        help="Skips the current song and plays the next one from queue.",
        aliases=['sk', 'next'])
    async def skip(self, ctx: commands.Context):
        player = ctx.voice_client

        if not player.current:
            raise NoCurrentTrack

        if self.is_privileged(ctx):
            await player.skip()
        
        else:
            required = self.required(ctx)

            if required == 1:
                await player.skip()
                return
                
            if not player.current_vote:
                player.current_vote = ctx.command.name
                player.add_vote(ctx.author)
                
                embed = discord.Embed(title="The voting has begun!", description=f"{ctx.author.mention if ctx.author else 'Someone'} has started a vote to skip **[{player.current.title}]({player.current.uri})**")
                embed.set_footer(text=f"Current votes: {len(player.votes)}/{required}")
                
                return await ctx.send(embed=embed)
        
            if ctx.author in player.votes:
                raise AlreadyVoted

            player.add_vote(ctx.author)
            if len(player.votes) >= required:
                embed = discord.Embed(title="The vote has been passed", description=f"The required amount of votes ({required}) has been reached!", color=discord.Color.green())
                embed.set_footer(text=f"Current votes: {len(player.votes)}/{required}")
                
                await player.skip()
                await ctx.send(embed=embed, footer=False, color=False)
                
            else:
                embed = discord.Embed(title="A vote has been added", description=f"{ctx.author.mention if ctx.author else 'Someone'} has voted for skipping **[{player.current.title}]({player.current.uri})**")
                embed.set_footer(text=f"Current votes: {len(player.votes)}/{required}")

                await ctx.send(content=f"{ctx.author.mention if ctx.author else 'Someone'} has voted!", embed=embed, footer=False)

    @commands.command(
        help="Stops the current song and returns to the beginning of the queue.")
    async def stop(self, ctx):
        player = ctx.voice_client

        if not player.queue.is_empty:
            player.queue.clear()
        
        if player.loop == 1:
            player.loop = 0
        
        await player.stop()
        await ctx.send(f":octagonal_sign: **|** Successfully stopped the current song.")
        
    @commands.command(help="**a**")
    async def destroy(self, ctx):
        if ctx.author.id == 772585958549356564 or ctx.author.id == 564890536947875868:
            
            try:
                await ctx.voice_client.destroy()
                return await ctx.send(":boom: **|** Successfully destroyed the player.")

            except Exception as e:
                return await ctx.send(f"""
An unexpected error occurred while destroying the player.
```py
{e}
```
                """)

        else:
            await ctx.send("Only <@772585958549356564> or <@564890536947875868> can execute this command. Sorry!")

    @commands.command(
        help="Removes all songs from the queueg.",
        aliases=['cq', 'clearq'])
    async def clear(self, ctx):
        player = ctx.voice_client

        if player.queue.is_empty:
            raise QueueIsEmpty
            
        player.queue.clear()
        await ctx.send(f":wastebasket: **|** Successfully cleared the queue.")

    @commands.command(
        help="Sends the current queue.",
        aliases=['q', 'upcoming'])
    async def queue(self, ctx):
        player = ctx.voice_client
        
        if player.queue.is_empty:
            raise QueueIsEmpty
        
        songs = []
        for song in player.queue:
            songs.append(f'**[{song.title.upper()}]({song.uri})** ({format_time(song.length)})\n')
        
        menu = paginator.ViewPaginator(paginator.QueueMenu(songs, ctx), ctx=ctx)
        await menu.start()
    
    @commands.command(
        help="Seeks to the specified position in the song.")
    async def seek(self, ctx, *, time:str):
        player = ctx.voice_client
        
        if not player.is_playing:
            raise NoCurrentTrack
        
        milliseconds = 0

        if match := HH_MM_SS_RE.fullmatch(time):
            milliseconds += int(match.group("h")) * 3600000
            milliseconds += int(match.group("m")) * 60000
            milliseconds += int(match.group("s")) * 1000
            new_position = milliseconds

        elif match := MM_SS_RE.fullmatch(time):
            milliseconds += int(match.group("m")) * 60000
            milliseconds += int(match.group("s")) * 1000
            new_position = milliseconds

        elif match := OFFSET_RE.fullmatch(time):
            milliseconds += int(match.group("s")) * 1000

            position = player.position
            new_position = position + milliseconds

        elif match := HUMAN_RE.fullmatch(time):
            if m := match.group("m"):
                if match.group("s") and time.lower().endswith("m"):
                    embed = discord.Embed(title=f"Invalid timestamp!")
                    embed.add_field(name=f"Here are some supported timestamps", value=f"""
{ctx.prefix}seek 01:23:45
{ctx.prefix}seek 00:12
{ctx.prefix}seek 1m 23s
{ctx.prefix}seek 50s
{ctx.prefix}seek +50s
{ctx.prefix}seek -69s
                                    """, inline=True)

                    return await ctx.send(embed=embed)
                
                milliseconds += int(m) * 60000
                
            if s := match.group("s"):
                
                if time.lower().endswith("m"):
                    milliseconds += int(s) * 60000
                    
                else:
                    milliseconds += int(s) * 1000

            new_position = milliseconds

        else:
            embed = discord.Embed(title=f"Invalid timestamp!")
            embed.add_field(name=f"Here are some supported timestamps", value=f"""
{ctx.prefix}seek 01:23:45
{ctx.prefix}seek 00:12
{ctx.prefix}seek 1m 23s
{ctx.prefix}seek 50s
{ctx.prefix}seek +50s
{ctx.prefix}seek -69s
                            """, inline=True)

            return await ctx.send(embed=embed)

        if new_position < 0 or new_position > player.current.length-1:
            raise InvalidSeek

        old_position = player.current.length
        
        if round(new_position) < round(old_position):
            emoji = ":fast_forward:"
            
        else:
            emoji = ":rewind:"
        
        await player.seek(new_position)
        await ctx.send(f"{emoji} **|** Successfully sought the current song to {format_time(new_position)}")

    @commands.command(
        help="Pauses the current song.")
    async def pause(self, ctx):
        player = ctx.voice_client

        if not self.is_privileged(ctx):
            raise NotAuthorized
        
        if player.is_paused:
            raise PlayerIsAlreadyPaused
        
        await player.set_pause(True)
        await ctx.send(f":pause_button: **|** Successfully paused the current song.")

    @commands.command(
        help="Resumes the current song.")
    async def resume(self, ctx):
        player = ctx.voice_client

        if not self.is_privileged(ctx):
            raise NotAuthorized
        
        if not player.is_paused:
            raise PlayerIsNotPaused
        
        await player.set_pause(False)
        await ctx.send(f":arrow_forward: **|** Successfully resumed the current song.")

    @commands.command(
        help="Changes the volume to the specified number, if you input \"resest\" it will reset the volume to the default",
        aliases=['vol'])
    async def volume(self, ctx, volume: typing.Union[int, str]):
        await ctx.trigger_typing()
        
        player = ctx.voice_client

        if not self.is_privileged(ctx):
            raise NotAuthorized

        if not player.current:
            raise NoCurrentTrack
        
        if isinstance(volume, str):
            if volume.lower() == "reset":
                await player.set_volume(100)
                
                if player.volume < 25 or player.volume == 25:
                    volume_emoji = "<:low:909834343655034881>"
                    
                elif player.volume < 50 or player.volume == 50:
                    volume_emoji = "<:medium:909834343822790676>"
                    
                else:
                    volume_emoji = "<:high:909834343449501707>"
                
                await ctx.send(f"{volume_emoji} **|** The volume has been set to **100%**")
                
            else:
                raise InvalidInput
        
        if isinstance(volume, int):
            if volume > 126 or volume < 0:
                raise InvalidVolume
            
            await player.set_volume(volume)
            
            if player.volume < 25 or player.volume == 25:
                volume_emoji = "<:low:909834343655034881>"
                
            elif player.volume < 50 or player.volume == 50:
                volume_emoji = "<:medium:909834343822790676>"
                
            else:
                volume_emoji = "<:high:909834343449501707>"
            
            await ctx.send(f"{volume_emoji} **|** The volume has been set to **{volume}%**")

    @commands.command(
        help="Shuffles the current queue. This randomizes the current order of the songs in the queue.",
        aliases=['sh'])
    async def shuffle(self, ctx):
        player = ctx.voice_client
        
        if not self.is_privileged(ctx):
            raise NotAuthorized

        if not player.current:
            raise NoCurrentTrack
        
        if player.queue.is_empty:
            raise NothingToShuffle

        player.queue.shuffle()
        
        await ctx.send(":twisted_rightwards_arrows: **|** The current queue has been shuffled.")

    @commands.group(
        invoke_without_command=True,
        help=":repeat: | Commands used to loop.",
        aliases=['repeat', 'l'])
    async def loop(self, ctx):
        await ctx.send_help(ctx.command)
        
    @loop.command(
        help="Loops the current song.")
    async def song(self, ctx):
        player: Player = ctx.voice_client

        if not self.is_privileged(ctx):
            raise NotAuthorized

        if not player.current:
            raise NoCurrentTrack

        if player.loop == 1:
            return await ctx.send(":x: **|** The loop mode is already set to **track**.")

        player.loop = 1
        await ctx.send(":repeat: **|** The loop mode has been set to **track**.")

    @loop.command(
        name="queue",
        help="Loops the current queue.")
    async def _queue(self, ctx):
        player: Player = ctx.voice_client

        if not self.is_privileged(ctx):
            raise NotAuthorized

        if not player.current:
            raise NoCurrentTrack
        
        if player.queue.is_empty:
            raise QueueIsEmpty

        if player.loop == 2:
            return await ctx.send(':x: **|** The loop mode is already set to **queue**')

        player.loop = 2
        await ctx.send(':repeat: **|** The loop mode has been set to **queue**.')


    @loop.command(
        help="Disables the loop mode.")
    async def disable(self, ctx):
        player: Player = ctx.voice_client

        if not self.is_privileged(ctx):
            raise NotAuthorized

        if not player.current:
            raise NoCurrentTrack
        
        if player.queue.is_empty:
            raise QueueIsEmpty
                
        if player.loop == 0:
            return await ctx.send(":x: **|** The loop mode is already **disabled**.")

        player.loop = 0
        await ctx.send(":repeat: **|** The loop mode has been **disabled.**")

    @commands.command(
        help="Sends the lyrics of the specified song")
    async def lyrics(self, ctx, *, song: str):
        async with aiohttp.ClientSession() as session:
            lyrics = await session.get(f'https://evan.lol/lyrics/search/top?q={song}')
            lyrics = await lyrics.json()
            
        try:
            title = f'{lyrics["artists"][0]["name"]} - {lyrics["name"]}'
            href=f'https://open.spotify.com/track/{lyrics["id"]}'
            image = lyrics["album"]["icon"]["url"]
            text = lyrics["lyrics"]
            lyrics = [text[i:i+250] for i in range(0, len(text), 250)]
            menu = paginator.ViewPaginator(paginator.LyricsPageSource(title, href, lyrics, image, ctx),ctx=ctx)
            await menu.start()
            
        except KeyError:
            raise NoLyrics

    @commands.group(
        invoke_without_command=True,
        help="<a:music:888778105844563988> | DJ commands")
    async def dj(self, ctx):
        await ctx.send_help(ctx.command)

    @dj.command(
        help="Toggles if the DJ is required to use DJ")
    @commands.check_any(commands.has_permissions(manage_roles=True), commands.has_permissions(manage_guild=True), commands.is_owner())
    async def toggle(self, ctx):
        state = not (self.bot.dj_only(ctx.guild))

        await self.bot.db.execute("INSERT INTO music(guild_id, dj_only) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET dj_only = $2", ctx.guild.id, state)

        self.bot.dj_modes[ctx.guild.id] = state
        
        await ctx.send(f"<a:music:888778105844563988> **|** The DJ only mode has been {'**enabled**' if state else '**disabled**'}.")

    @dj.command(
        help="Sets the DJ role to the specified role, if you put \"remove\" as the role, it will be removed.")
    @commands.check_any(commands.has_permissions(manage_roles=True), commands.has_permissions(manage_guild=True), commands.is_owner())
    async def role(self, ctx:commands.Context, role: typing.Union[discord.Role, str]):
        if isinstance(role, str):
            if str(role).lower() == 'remove':
                await self.bot.db.execute("INSERT INTO music(guild_id, dj_role_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET dj_role_id = $2", ctx.guild.id, None)

                self.bot.dj_roles[ctx.guild.id] = None
                await ctx.send("<a:music:888778105844563988> | The DJ role has been **removed** from this server.")
                
            else:
                raise InvalidInput
        
        else:
            await self.bot.db.execute("INSERT INTO music(guild_id, dj_role_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET dj_role_id = $2",
                ctx.guild.id, role.id)

            self.bot.dj_roles[ctx.guild.id] = role.id
            await ctx.send(embed=discord.Embed(title='DJ Role updated', description=f'DJ role has been set to {role.mention}'))

    @dj.command(
        help="Shows the DJ settings for this server.")
    async def settings(self, ctx):
        player = ctx.voice_client
         
        embed = discord.Embed(title=f"DJ settings for {ctx.guild.name}")
        
        embed.add_field(name=f"__**Explanation**__", value=f"""
```yaml
Current DJ: This member can use DJ commands no matter the settings.

DJ role: Members with this role can use DJ commands.

DJ only: Whenever everyone can use DJ commands or not.
```
                        """, inline=True)
        
        embed.add_field(name=f"__**Settings**__", value=f"""
```yaml
Current DJ: {f'@{player.dj}' if player else 'No current DJ'}
DJ role: {f'@{self.bot.dj_role(ctx.guild)}' if self.bot.dj_role(ctx.guild) else 'No DJ role'}
DJ only mode: {'Enabled' if self.bot.dj_only(ctx.guild) else 'Disabled'}
```
                        """, inline=False)

        await ctx.send(embed=embed)

    @dj.command(
        help="Swaps the current DJ to the specified member. If no member is specified it will choose one from the current VC.")
    async def swap(self, ctx, member: discord.Member = None):
        player = ctx.voice_client
        
        if not self.bot.dj_only(ctx.guild):
            return await ctx.send("You cannot use this command because the **DJ only mode** is disabled.")

        if not self.is_privileged(ctx): 
            raise NotAuthorized

        members = self.get_members(player.channel.id)

        if member and member not in members:
            embed = discord.Embed(description=f"{member.mention} isn't in a VC so they cannot be a DJ")
            
            return await ctx.send(embed=embed)
        
        if member and member == player.dj:
            embed = discord.Embed(description=f"That person is already the DJ.")
            
            return await ctx.send(embed=embed)

        if len(members) == 1:
            embed = discord.Embed(description=f"There need to be at least 2 members in the VC to swap the DJ.")
            
            return await ctx.send(embed=embed)

        if member:
            player.dj = member
            embed = discord.Embed(title=f"New DJ", description=f"The new DJ is {player.dj.mention}!", color=discord.Color.green())
            
            return await ctx.send(embed=embed, color=False, footer=False, timestamp=False)

        for member in members:
            if member == player.dj:
                continue
            
            if member.bot:
                continue
            
            else:
                player.dj = member
                embed = discord.Embed(title=f"New DJ", description=f"The new DJ is {member.mention}!", color=discord.Color.green())
                
                return await ctx.send(embed=embed, color=False, footer=False, timestamp=False)

    @commands.command()
    async def nodes(self, ctx:commands.Context):
        nodes = [x for x in self.bot.pomice.nodes.values()]
        raw = []

        for node in nodes:
            stats = node._stats

            before = t.monotonic()
            async with self.bot.session.get(node._rest_uri):
                now = t.monotonic()
                ping = round((now - before) * 1000)
            uptime = str(datetime.timedelta(milliseconds=stats.uptime))
            uptime = uptime.split('.')
            
            raw.append([
                {'Identifier': '`{}`'.format(node._identifier)}, 
                {'All Players': '`{}`'.format(stats.players_total)},
                {'Active Players': '`{}`'.format(stats.players_active)},
                {'Free RAM': '`{}`'.format(convert_bytes(stats.free))}, 
                {'Used RAM': '`{}`'.format(convert_bytes(stats.used))}, 
                {'All RAM': '`{}`'.format(convert_bytes(stats.allocated))}, 
                {'Ping': '`{} ms`'.format(ping)},
                {'Available': '`{}`'.format(node._available)}, 
                {'Uptime': '`{}`'.format(uptime[0])}
                      ])

        menu = paginator.ViewPaginator(paginator.NodesMenu(raw, ctx),ctx=ctx)
        await menu.start()
        