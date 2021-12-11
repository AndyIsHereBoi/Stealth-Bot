
from discord.ext import commands

class UnknownError(commands.CheckFailure):
    pass

class CommandDoesntExist(commands.CheckFailure):
    pass

class AuthorBlacklisted(commands.CheckFailure):
    pass

class Forbidden(commands.CheckFailure):
    pass

class BotMaintenance(commands.CheckFailure):
    pass

class NoBannedMembers(commands.CheckFailure):
    pass

class TooLongPrefix(commands.CheckFailure):
    pass

class EmptyTodoList(commands.CheckFailure):
    pass

class NoSpotifyStatus(commands.CheckFailure):
    pass

class InvalidThread(commands.CheckFailure):
    pass

class TooManyPrefixes(commands.CheckFailure):
    pass

class PrefixAlreadyExists(commands.CheckFailure):
    pass

class PrefixDoesntExist(commands.CheckFailure):
    pass

class KillYourself(commands.CheckFailure):
    pass

class InvalidError(commands.CheckFailure):
    pass

class NotStartedEconomy(commands.CheckFailure):
    pass

########################################################################################################################
##### MUSIC ERRORS #####
########################################################################################################################

class NoPlayer(commands.CheckFailure):
    pass

class FullVoiceChannel(commands.CheckFailure):
    pass

class NotAuthorized(commands.CheckFailure):
    pass

class IncorrectChannelError(commands.CheckFailure):
    pass

class IncorrectTextChannelError(commands.CheckFailure):
    pass

class AlreadyConnectedToChannel(commands.CheckFailure):
    pass

class NoVoiceChannel(commands.CheckFailure):
    pass

class QueueIsEmpty(commands.CheckFailure):
    pass

class NoCurrentTrack(commands.CheckFailure):
    pass

class PlayerIsAlreadyPaused(commands.CheckFailure):
    pass

class PlayerIsNotPaused(commands.CheckFailure):
    pass

class NoMoreTracks(commands.CheckFailure):
    pass

class InvalidTimeString(commands.CheckFailure):
    pass

class NoPerms(commands.CheckFailure):
    pass

class NoConnection(commands.CheckFailure):
    pass

class AfkChannel(commands.CheckFailure):
    pass

class NotAuthorized(commands.CheckFailure):
    pass

class InvalidTrack(commands.CheckFailure):
    pass

class InvalidPosition(commands.CheckFailure):
    pass

class InvalidVolume(commands.CheckFailure):
    pass

class InvalidSeek(commands.CheckFailure):
    pass
    
class AlreadyVoted(commands.CheckFailure):
    pass

class NothingToShuffle(commands.CheckFailure):
    pass

class NoLyrics(commands.CheckFailure):
    pass

class ActiveVote(commands.CheckFailure):
    pass

class LoadFailed(commands.CheckFailure):
    pass

class NoMatches(commands.CheckFailure):
    pass

class InvalidInput(commands.CheckFailure):
    pass

class LoopDisabled(commands.CheckFailure):
    pass

class TrackFailed(commands.CheckFailure):
    pass

########################################################################################################################
##### MUTE ROLE ERRORS #####
########################################################################################################################

class MuteRoleNotFound(commands.CheckFailure):
    pass

class MuteRoleAlreadyExists(commands.CheckFailure):
    pass