import re
import typing
import random
import pygit2
import discord
import datetime
import itertools

from discord import Interaction
from discord.ext import commands
from asyncdagpi import Client, ImageFeatures

target_type = typing.Union[discord.Member, discord.User, discord.PartialEmoji, discord.Guild, discord.Invite]

class ConfirmButton(discord.ui.Button):
    def __init__(self, label: str, emoji: str, button_style: discord.ButtonStyle):
        super().__init__(style=button_style, label=label, emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: Confirm = self.view
        view.value = True
        view.stop()


class CancelButton(discord.ui.Button):
    def __init__(self, label: str, emoji: str, button_style: discord.ButtonStyle):
        super().__init__(style=button_style, label=label, emoji=emoji)

    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: Confirm = self.view
        view.value = False
        view.stop()


class DeleteButton(discord.ui.Button):
    def __init__(self):
        super().__init__(style=discord.ButtonStyle.danger, emoji="🗑️")

    async def callback(self, interaction: discord.Interaction):
        await interaction.message.delete()
        if self.ctx.channel.permissions_for(self.ctx.me).manage_messages:
            await self.ctx.message.delete()


class Confirm(discord.ui.View):
    def __init__(self, buttons: typing.Tuple[typing.Tuple[str]], timeout: int = 30):
        super().__init__(timeout=timeout)
        self.message = None
        self.value = None
        self.ctx: CustomContext = None
        self.add_item(ConfirmButton(emoji=buttons[0][0],
                                    label=buttons[0][1],
                                    button_style=(
                                            buttons[0][2] or discord.ButtonStyle.green
                                    )))
        self.add_item(CancelButton(emoji=buttons[1][0],
                                   label=buttons[1][1],
                                   button_style=(
                                           buttons[1][2] or discord.ButtonStyle.red
                                   )))

    async def interaction_check(self, interaction: Interaction):
        if interaction.user and interaction.user.id in (self.ctx.bot.owner_id, self.ctx.author.id):
            return True
        messages = [
            "Oh no you can't do that! This belongs to **{user}**",
            'This is **{user}**\'s confirmation, sorry! 💖',
            '😒 Does this look yours? **No**. This is **{user}**\'s confirmation button',
            '<a:stopit:891139227327295519>',
            'HEYYYY!!!!! this is **{user}**\'s menu.',
            'Sorry but you can\'t mess with **{user}**\' menu QnQ',
            'No. just no. This is **{user}**\'s menu.',
            '<:blobstop:749111017778184302>' * 3,
            'You don\'t look like {user} do you...',
            '🤨 Thats not yours! Thats **{user}**\'s',
            '🧐 Whomst! you\'re not **{user}**',
            '_out!_ 👋'
        ]
        await interaction.response.send_message(random.choice(messages).format(user=self.ctx.author.display_name),
                                                ephemeral=True)

        return False

class Delete(discord.ui.View):
    def __init__(self, timeout: int = 30):
        super().__init__(timeout=timeout)
        self.message = None
        self.value = None
        self.ctx: CustomContext = None
        self.add_item(DeleteButton(emoji='🗑️',
                                   label='',
                                   button_style=discord.ButtonStyle.red))

    async def interaction_check(self, interaction: Interaction):
        if interaction.user and interaction.user.id in (self.ctx.bot.owner_id, self.ctx.author.id):
            return True
        messages = [
            "Oh no you can't do that! This belongs to **{user}**",
            'This is **{user}**\'s confirmation, sorry! 💖',
            '😒 Does this look yours? **No**. This is **{user}**\'s confirmation button',
            '<a:stopit:891139227327295519>',
            'HEYYYY!!!!! this is **{user}**\'s menu.',
            'Sorry but you can\'t mess with **{user}**\' menu QnQ',
            'No. just no. This is **{user}**\'s menu.',
            '<:blobstop:749111017778184302>' * 3,
            'You don\'t look like {user} do you...',
            '🤨 Thats not yours! Thats **{user}**\'s',
            '🧐 Whomst! you\'re not **{user}**',
            '_out!_ 👋'
        ]
        await interaction.response.send_message(random.choice(messages).format(user=self.ctx.author.display_name),
                                                ephemeral=True)

        return False


class CustomContext(commands.Context):

    @staticmethod
    def tick(option: bool):
        ticks = {
            True: '<:greenTick:895688440690147370>',
            False: '<:redTick:895688440568508518>',
            None: '<:greyTick:895688440690114560>'}

        emoji = ticks.get(option, "<:redTick:596576672149667840>")
        return emoji

    @staticmethod
    def toggle(option: bool):
        ticks = {
            True: '<:toggle_on:896743740285263892>',
            False: '<:toggle_off:896743704323309588>',
            None: '<:toggle_off:896743704323309588>'}

        emoji = ticks.get(option, "<:toggle_off:896743704323309588>")
        return emoji

    @staticmethod
    def time(days: int, hours: int, minutes: int, seconds: int):
        def remove_s(string):
            if re.match(r"\d+", string).group() == "1":
                return string[:-1]
            return string

        days = remove_s(f"{days} days")
        hours = remove_s(f"{hours} hours")
        minutes = remove_s(f"{minutes} minutes")
        seconds = remove_s(f"{seconds} seconds")

        return " and ".join(", ".join(filter(lambda i: int(i[0]), (days, hours, minutes, seconds))).rsplit(", ", 1))

    @staticmethod
    def short_time(days: int, hours: int, minutes: int, seconds: int):
        def remove_s(string):
            if re.match(r"\d+", string).group() == "1":
                return string[:-1]
            return string

        days = remove_s(f"{days}d")
        hours = remove_s(f"{hours}h")
        minutes = remove_s(f"{minutes}m")
        seconds = remove_s(f"{seconds}s")

        return " and ".join(", ".join(filter(lambda i: int(i[0]), (days, hours, minutes, seconds))).rsplit(", ", 1))

    @staticmethod
    def uptime(self):
        delta_uptime = discord.utils.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        def remove_s(string):
            if re.match(r"\d+", string).group() == "1":
                return string[:-1]
            return string

        days = remove_s(f"{days}d")
        hours = remove_s(f"{hours}h")
        minutes = remove_s(f"{minutes}m")
        seconds = remove_s(f"{seconds}s")

        return " and ".join(", ".join(filter(lambda i: int(i[0]), (days, hours, minutes, seconds))).rsplit(", ", 1))

    @staticmethod
    def get_last_commits(count=3):
        def format_commit(commit):
            short, _, _ = commit.message.partition('\n')
            short_sha2 = commit.hex[0:6]
            commit_tz = datetime.timezone(datetime.timedelta(minutes=commit.commit_time_offset))
            commit_time = datetime.datetime.fromtimestamp(commit.commit_time).astimezone(commit_tz)

            offset = discord.utils.format_dt(commit_time.astimezone(datetime.timezone.utc), 'R')
            return f'[`{short_sha2}`](https://github.com/Ender2K89/Stealth-Bot/commit/{commit.hex}) {short} ({offset})'

        repo = pygit2.Repository('.git')
        commits = list(itertools.islice(repo.walk(repo.head.target, pygit2.GIT_SORT_TOPOLOGICAL), count))
        return '\n'.join(format_commit(c) for c in commits)

    @staticmethod
    def members(bot):
        return len(bot.users)

    @staticmethod
    def users(bot):
        return len(bot.users)

    @staticmethod
    def guilds(bot):
        return len(bot.guilds)

    @staticmethod
    def servers(bot):
        return len(bot.guilds)

    async def send(self, content: str = None, embed: discord.Embed = None, reminders: bool = True,
                   reply: bool = True, footer: bool = True, timestamp: bool = True, color: bool = True,
                   reference: typing.Union[discord.Message, discord.MessageReference] = None,
                   view = None, **kwargs) -> discord.Message:

        reference = (reference or self.message.reference or self.message) if reply is True else reference

        if self.bot.theme == "default":
            colors = [0x910023, 0xA523FF]
            emotes = []
            unicode_emotes = []
            star_emoji = ":star:"

        elif self.bot.theme == "halloween":
            colors = [0xFF9A00, 0x000000, 0x09FF00, 0xC900FF, 0xFBFAF4]
            emotes = [':ghost:', ':jack_o_lantern:']
            unicode_emotes = ['👻', '🎃']
            star_emoji = random.choice(emotes)

        elif self.bot.theme == "christmas":
            colors = [0xB3000C, 0xE40010, 0xD8D8D8, 0x1FD537, 0x1FD537]
            emotes = [':santa:', ':christmas_tree:', ':deer:', ':gift:']
            unicode_emotes = ['🎅', '🎄', '🦌', '🎁']
            star_emoji = ":star2:"

        else:
            colors = [0x910023, 0xA523FF]
            emotes = []
            unicode_emotes = []
            star_emoji = ":star:"

        if embed:

            if footer:
                embed.set_footer(
                    text=f"{f'{random.choice(unicode_emotes)} ' if unicode_emotes else ''}Requested by {self.author}",
                    icon_url=self.author.display_avatar.url)

            if not footer and embed.footer:
                embed.set_footer(
                    text=f"{f'{random.choice(unicode_emotes)} ' if unicode_emotes else ''}{embed.footer.text}",
                    icon_url=embed.footer.icon_url if embed.footer.icon_url else discord.Embed.Empty)

            if timestamp:
                embed.timestamp = discord.utils.utcnow()

            if color:
                color = random.choice(colors)
                embed.color = color

        if reminders:
            answer = f"{star_emoji} Help **Stealth Bot** grow by voting on top.gg: **<https://top.gg/bot/760179628122964008>**"
            number = random.randint(1, 5)

            content = content

            if number == 1:
                content = f"{answer}\n\n{str(content) if content else ''}"

        if not view:
            view = Delete(timeout=60)

        try:
            return await super().send(content=content, embed=embed, reference=reference, view=view, **kwargs)

        except discord.HTTPException:
            return await super().send(content=content, embed=embed, reference=None, view=view, **kwargs)

    async def confirm(self, message: str = "Do you want to confirm?", embed: discord.Embed = None,
                      # added embed so it's possible to use ctx.confirm with an embed instead of a lame class normal message - P3ter
                      buttons: typing.Tuple[typing.Union[discord.PartialEmoji, str],
                                            str, discord.ButtonStyle] = None, timeout: int = 30,
                      delete_after_confirm: bool = False, delete_after_timeout: bool = False,
                      delete_after_cancel: bool = None):
        delete_after_cancel = delete_after_cancel if delete_after_cancel is not None else delete_after_confirm
        view = Confirm(buttons=buttons or (
            (None, 'Confirm', discord.ButtonStyle.green),
            (None, 'Cancel', discord.ButtonStyle.red)
        ), timeout=timeout)
        view.ctx = self
        if embed and message:  # checks if there was BOTH embed and message and if there wasnt:
            message = await self.send(message, view=view, embed=embed)
        elif embed:  # checks if there was an embed and if there wasnt:
            message = await self.send(view=view, embed=embed)
        else:  # sends the message alone and if it was None it sends the default one "Do you want to confirm?"
            message = await self.send(message, view=view)
        await view.wait()

        if view.value is None:
            try:
                (await message.edit(view=None)) if \
                    delete_after_timeout is False else (await message.delete())
            except (discord.Forbidden, discord.HTTPException):
                pass
            return False

        elif view.value:
            try:
                (await message.edit(view=None)) if \
                    delete_after_confirm is False else (await message.delete())
            except (discord.Forbidden, discord.HTTPException):
                pass
            return True

        else:
            try:
                (await message.edit(view=None)) if \
                    delete_after_cancel is False else (await message.delete())
            except (discord.Forbidden, discord.HTTPException):
                pass
            return False

    async def trigger_typing(self) -> None:
        try:
            await super().trigger_typing()

        except (discord.Forbidden, discord.HTTPException):
            pass

    async def dagpi(self, target: target_type = None, *, feature: ImageFeatures, **kwargs) -> discord.File:
        await self.trigger_typing()
        target = target or self.reference
        return await self.bot.dagpi_request(self, target, feature=feature, **kwargs)

    async def waifu(self, feature: str, **kwargs) -> discord.File:
        await self.trigger_typing()
        return await self.bot.waifu_request(self, feature=feature, **kwargs)

    @property
    def reference(self) -> typing.Optional[discord.Message]:
        return getattr(self.message.reference, 'resolved', None)