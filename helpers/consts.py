from collections import namedtuple

import discord

CUSTOM_TICKS = {
    True: '<:tickYes:885222891883470879>',
    False: '<:tickNo:885222934036226068>',
    None: '<:tickNone:885223045751529472>',
}

DEFAULT_TICKS = {
    True: '✅',
    False: '❌',
    None: '➖',
}

USER_FLAGS = {
    'staff': '<:staff:903705903205842984>',
    'partner': '<:partnernew:903710462707900467>',
    'hypesquad': '<:hypesquad:903710550377254912>',
    'bug_hunter': '<:bughunter:903710583126376530>',
    'hypesquad_bravery': '<:bravery:903710635525828688>',
    'hypesquad_brilliance': '<:brilliance:903710687346454628>',
    'hypesquad_balance': '<:balance:903710741788500018>',
    'early_supporter': '<:supporter:903710821132152842>',
    'bug_hunter_level_2': '<:bughunter_gold:903710860692815962>',
    'verified_bot_developer': '<:verifiedbotdev:903759130265804810>',
    'verified_bot': '<:Verified:903759390358782004>',
    'discord_certified_moderator': '<:certified_moderator:903710990959525929>'
            }

GUILD_FEATURES = {
    'ANIMATED_ICON': 'Animated Server Icon',
    'BANNER': 'Server Banner',
    'COMMERCE': 'Commerce',
    'COMMUNITY': 'Community Server',
    'DISCOVERABLE': 'Discoverable',
    'FEATURABLE': 'Featured',
    'INVITE_SPLASH': 'Invite Splash',
    'MEMBER_VERIFICATION_GATE_ENABLED': 'Membership Screening',
    'MONETIZATION_ENABLED': 'Monetization',
    'MORE_EMOJI': 'More Emoji',
    'MORE_STICKERS': 'More Stickers',
    'NEWS': 'News Channels',
    'PARTNERED': 'Partnered',
    'PREVIEW_ENABLED': 'Preview Enabled',
    'PRIVATE_THREADS': 'Private Threads',
    'SEVEN_DAY_THREAD_ARCHIVE': '1 Week Thread Archive',
    'THREE_DAY_THREAD_ARCHIVE': '3 Day Thread Archive',
    'TICKETED_EVENTS_ENABLED': 'Ticketed Events',
    'VANITY_URL': 'Vanity Invite URL',
    'VERIFIED': 'Verified',
    'VIP_REGIONS': 'VIP Voice Regions',
    'WELCOME_SCREEN_ENABLED': 'Welcome Screen',
            }


st_nt = namedtuple('statuses', ['ONLINE', 'IDLE', 'DND', 'OFFLINE'])

statuses = st_nt(
    ONLINE='<:status_online:596576749790429200>',
    IDLE='<:status_idle:596576773488115722>',
    DND='<:status_dnd:596576774364856321>',
    OFFLINE='<:status_offline:596576752013279242>'
            )