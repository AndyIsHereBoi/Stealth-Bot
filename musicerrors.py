import discord
from discord.ext import commands

__all__ = (
    'NoPlayer',
    'FullVoiceChannel',
    'NotAuthorized',
    'IncorrectChannelError',
    'IncorrectTextChannelError',
    'AlreadyConnectedToChannel',
    'NoVoiceChannel',
    'QueueIsEmpty',
    'NoCurrentTrack',
    'NoConnection',
    'PlayerIsAlreadyPaused',
    'PlayerIsNotPaused',
    'NoMoreTracks',
    'InvalidTimeString',
    'NoPerms',
    'AfkChannel',
    'InvalidTrack',
    'InvalidPosition',
    'InvalidVolume',
    'OutOfTrack',
    'NegativeSeek',
    'NotAuthorized',
            )

class BotError(commands.CommandError):
    def __init__(self, e) -> None:
        self.custom = True
        self.embed = discord.Embed(description=e)
        super().__init__(e)

class NoPlayer(BotError):
    def __init__(self) -> None:
        super().__init__(f"There isn't a active player in this server")

class FullVoiceChannel(BotError):
    def __init__(self, ctx : commands.Context) -> None:
        super().__init__(f"I can't join {ctx.author.voice.channel.mention} because it's full")

class NotAuthorized(BotError):
    def __init__(self) -> None:
        super().__init__("You cannot perform this action.")

class IncorrectChannelError(BotError):
    def __init__(self, ctx : commands.Context) -> None:
        player = ctx.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        channel = ctx.bot.get_channel(int(player.channel_id))
        super().__init__(f'You must be {channel.mention} to control music')
        
class IncorrectTextChannelError(BotError):
    def __init__(self, ctx : commands.Context) -> None:
        player = ctx.bot.lavalink.player_manager.create(ctx.guild.id, endpoint=str(ctx.guild.region))
        channel = ctx.bot.get_channel(int(player.text_channel))
        super().__init__(f'You must be in {channel.mention} to control music')

class AlreadyConnectedToChannel(BotError):
    def __init__(self) -> None:
        super().__init__("I'm already connected to a voice channel")

class NoVoiceChannel(BotError):
    def __init__(self) -> None:
        super().__init__("I'm not connected to any voice channel")

class QueueIsEmpty(BotError):
    def __init__(self) -> None:
        super().__init__("There's no tracks in the queue")

class NoCurrentTrack(BotError):
    def __init__(self) -> None:
        super().__init__("There isn't currently a song playing")

class PlayerIsAlreadyPaused(BotError):
    def __init__(self) -> None:
        super().__init__("The current song is already paused")

class PlayerIsNotPaused(BotError):
    def __init__(self) -> None:
        super().__init__("The current song isn't paused")

class NoMoreTracks(BotError):
    def __init__(self) -> None:
        super().__init__("There's no more tracks in the queue")

class InvalidTimeString(BotError):
    def __init__(self) -> None:
        super().__init__("Invalid time string")

class NoPerms(BotError):
    def __init__(self) -> None:
        super().__init__("I don't have permissions to join/speak in that voice channel")

class NoConnection(BotError):
    def __init__(self) -> None:
        super().__init__("You must be in a voice channel to control music")

class AfkChannel(BotError):
    def __init__(self) -> None:
        super().__init__("I can't play music in the AFK channel")

class NotAuthorized(BotError):
    def __init__(self) -> None:
        super().__init__("You aren't allowed to perform that action")

class InvalidTrack(BotError):
    def __init__(self) -> None:
        super().__init__("I can't perform actions on a track that isn't in the current queue")

class InvalidPosition(BotError):
    def __init__(self) -> None:
        super().__init__("I can't perform actions with a invalid position in the current queue")

class InvalidVolume(BotError):
    def __init__(self) -> None:
        super().__init__("The volume has to be between 1 and 100")

class OutOfTrack(BotError):
    def __init__(self) -> None:
        super().__init__("I can't seek out of the track")

class NegativeSeek(BotError):
    def __init__(self) -> None:
        super().__init__("I can'T seek on a negative timestamp")