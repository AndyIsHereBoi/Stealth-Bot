import os
import random
import errors
import difflib
import typing
import discord
import contextlib

from discord.ui import Button
from discord import Interaction
from discord.ext import commands
from helpers.context import CustomContext
from helpers import paginator as paginator


def reading_recursive(root: str, /) -> int:
    for x in os.listdir(root):
        if os.path.isdir(x):
            yield from reading_recursive(root + "/" + x)
        else:
            if x.endswith((".py", ".c")):
                with open(f"{root}/{x}") as r:
                    yield len(r.readlines())


def count_python(root: str) -> int:
    return sum(reading_recursive(root))


class VoteButtons(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(emoji="<:dbl:757235965629825084>", label="top.gg", url="https://top.gg/bot/760179628122964008"))


class HelpCentre(discord.ui.View):
    def __init__(self, ctx: CustomContext, other_view: discord.ui.View):
        super().__init__()
        self.embed = None
        self.ctx = ctx
        self.other_view = other_view

    @discord.ui.button(label="Go Back", emoji="🏠", style=discord.ButtonStyle.blurple)
    async def go_back(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.embed, view=self.other_view)
        self.stop()

    async def start(self, interaction: discord.Interaction):
        colors = [0x910023, 0xA523FF]
        color = random.choice(colors)

        embed = discord.Embed(title=f"Here's a guild on how to use the help menu", description=f"""
`<argument>`
This means that the argument is **required**.

`[argument]`
This means that the argument is **optional**.

`[argument=\"default\"]`
This means that the argument is **optional** and has a default value.

**Do not use these brackets when running a command.**
**They're only there to indicate if the argument is required or not.**
                              """, color=color)

        embed.set_footer(text=f"To continue browsing the help menu, press the \"Go back\" button.")

        self.embed = interaction.message.embeds[0]
        self.add_item(discord.ui.Button(label="Support server", emoji="❓", url="https://discord.gg/MrBcA6PZPw"))
        self.add_item(discord.ui.Button(label="Invite me", emoji="<:invite:895688440639799347>", url="https://discord.com/oauth2/authorize?client_id=760179628122964008&scope=applications.commands+bot&permissions=549755813887"))

        await interaction.response.edit_message(embed=embed, view=self)

    async def interaction_check(self, interaction: Interaction):
        if interaction.user and interaction.user == self.ctx.author:
            return True
        await interaction.response.defer()
        return False


class NewsCentre(discord.ui.View):
    def __init__(self, ctx: CustomContext, other_view: discord.ui.View):
        super().__init__()
        self.embed = None
        self.ctx = ctx
        self.other_view = other_view

    @discord.ui.button(label="Go Back", emoji="🏠", style=discord.ButtonStyle.blurple)
    async def go_back(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.edit_message(embed=self.embed, view=self.other_view)
        self.stop()

    async def start(self, interaction: discord.Interaction):
        colors = [0x910023, 0xA523FF]
        color = random.choice(colors)

        embed = discord.Embed(title=f"Latest news", description=f"""
__**<:google_turtle:787675845371363338> Translate command fixed & improved (<t:1639819756:R>)**__ 
The translate command has been fixed and improved! It's very fast!
To try it out, do **{self.ctx.prefix}help translate**.

__**:mute: Mute commands! (<t:1639338972:R>)**__
New mute commands have been added! To manage your mute role, do **{self.ctx.prefix}help muterole**.
To see the actual mute commands, do **{self.ctx.prefix}help mod** and go to the last page.
    
__**<a:music:888778105844563988> Music system improved (<t:1637504100:R>)**__
The music system has been improved and is now way faster and smoother!
Do **{self.ctx.prefix}help Music** to try it out!

__**:wave: New welcoming system (<t:1637247577:R>)**__
With this you can welcome new members that join your server!
Do **{self.ctx.prefix}help welcome** for more info.

__**<:scroll:904038785921187911> Logging system (<t:1637074743:R>)**__
The logging system can log various actions in your server.
For more info, do **{self.ctx.prefix}help log**.
NOTE: This is in beta and some bugs may occur.
                              """, color=color)

        embed.set_footer(text=f"To continue browsing the help menu, press the \"Go back\" button.")

        self.embed = interaction.message.embeds[0]
        self.add_item(discord.ui.Button(label="Invite me", emoji="<:invite:895688440639799347>", url="https://discord.com/oauth2/authorize?client_id=760179628122964008&scope=applications.commands+bot&permissions=549755813887"))
        self.add_item(discord.ui.Button(label="Vote on top.gg", emoji="<:dbl:757235965629825084>", url="https://top.gg/bot/760179628122964008"))

        await interaction.response.edit_message(embed=embed, view=self)

    async def interaction_check(self, interaction: Interaction):
        if interaction.user and interaction.user == self.ctx.author:
            return True
        await interaction.response.defer()
        return False


class HelpView(discord.ui.View):
    def __init__(self, ctx: CustomContext, usable_commands, data: typing.Dict[commands.Cog, typing.List[commands.Command]]):
        super().__init__()
        self.ctx = ctx
        self.usable_commands = usable_commands
        self.data = data
        self.bot = ctx.bot
        self.main_embed = self.build_main_page()
        self.current_page = 0
        self.message = None
        self.embeds: typing.List[discord.Embed] = [self.main_embed]

    @discord.ui.select(placeholder="Select a category...", row=0)
    async def category_select(self, select: discord.ui.Select, interaction: discord.Interaction):
        if select.values[0] == "index":
            self.current_page = 0
            self.embeds = [self.main_embed]
            self._update_buttons()
            return await interaction.response.edit_message(embed=self.main_embed, view=self)
        cog = self.bot.get_cog(select.values[0])
        if not cog:
            return await interaction.response.send_message('Somehow, that category was not found? 🤔')
        else:
            self.embeds = self.build_embeds(cog)
            self.current_page = 0
            self._update_buttons()
            return await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)


    def build_embeds(self, cog: commands.Cog):
        colors = [0x910023, 0xA523FF]
        color = random.choice(colors)

        embeds = []
        cog_commands = cog.get_commands()
        embed = discord.Embed(title=f"{str(cog.qualified_name).title()} commands [{len(cog_commands)}]", description=f"{cog.description if cog.description else 'No description provided...'[0:1024]}", color=color, timestamp=discord.utils.utcnow())

        for cmd in cog_commands:
            embed.add_field(name=f"{cmd.name} {cmd.signature}", value=f"{cmd.help if cmd.help else 'No help provided...'[0:1024]}", inline=False)
            embed.set_footer(text="For info on a command, do help <command>")

            if len(embed.fields) == 5:
                embeds.append(embed)
                embed = discord.Embed(title=f"{str(cog.qualified_name).title()} commands [{len(cog_commands)}]", description=cog.description or "No description provided", color=color, timestamp=discord.utils.utcnow())

        if len(embed.fields) > 0:
            embeds.append(embed)

        return embeds


    def build_select(self):
        self.category_select: discord.ui.Select
        self.category_select.options = []
        self.category_select.add_option(label="Main page", value="index", emoji="🏠")

        for cog, comm in self.data.items():
            if not comm:
                continue

            emoji = getattr(cog, "select_emoji", None)
            label = cog.qualified_name
            brief = getattr(cog, "select_brief", None)

            self.category_select.add_option(label=label, value=label, emoji=emoji, description=brief)


    def build_main_page(self):
        delta_uptime = discord.utils.utcnow() - self.ctx.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        embed = discord.Embed(title="Help menu", description=f"""
Hello there! I'm **Stealth Bot**. Welcome to the help menu.

**Getting help**
Use **sb!help <command>** for more info on a command.
There's also **sb!help <command> [sub-command]**.
Use **sb!help <category>** for more info on a category.
You can also use the dropdown below to select a category.

**Getting support**
To get help, you can join my [support server](https://discord.gg/MrBcA6PZPw).
You can also send me a DM if you prefer to.

**Wait a minute... Who are you?**
I'm a multipurpose discord bot created by <:github:895688440492986389> [Ender2K89#9999](https://github.com/Ender2K89/).
You can use me to moderate your server, play music,
manipulate images and way more!

I've been on discord since {discord.utils.format_dt(self.ctx.me.created_at)} ({discord.utils.format_dt(self.ctx.me.created_at, style='R')})
I've been online for {self.ctx.time(days=days, hours=hours, minutes=minutes, seconds=seconds)}
I have **{len(self.bot.commands)}** commands.
But you can only use **{self.usable_commands}** of those in this server.
         """)

#         embed.add_field(name=f"**Getting help**", value=f"""
# Use **sb!help <command>** for more info on a command.
# There's also **sb!help <command> [sub-command]**.
# Use **sb!help <category>** for more info on a category.
# You can also use the dropdown below to select a category.
#                         """, inline=False)
#
#         embed.add_field(name=f"**Getting support**", value=f"""
# To get help, you can join my [support server](https://discord.gg/MrBcA6PZPw).
# You can also send me a DM if you prefer to.
#                         """, inline=False)
#
#         embed.add_field(name=f"**Wait a minute.. Who are you?**", value=f"""
# I'm a multipurpose discord bot created by <:github:895688440492986389> [Ender2K89#9999](https://github.com/Ender2K89/).
# You can use me to moderate your server, play music,
# manipulate images and way more!
#
# I've been on discord since {discord.utils.format_dt(self.ctx.me.created_at)} ({discord.utils.format_dt(self.ctx.me.created_at, style='R')})
# I've been online for {self.ctx.time(days=days, hours=hours, minutes=minutes, seconds=seconds)}
# I have **{len(self.bot.commands)}** commands.
# But you can only use **{self.usable_commands}** of those in this server.
#                         """, inline=False)

        embed.set_footer(text=f"This command is inspired by R. Danny and DuckBot")

        return embed

    @discord.ui.button(label="Help", emoji="❓", style=discord.ButtonStyle.blurple, row=1)
    async def help(self, button: Button, interaction: Interaction):
        view = HelpCentre(self.ctx, self)
        await view.start(interaction)

    @discord.ui.button(emoji="<:previous:921408043470688267>", style=discord.ButtonStyle.gray, row=1)
    async def previous(self, button: Button, interaction: Interaction):
        self.current_page -= 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)

    @discord.ui.button(emoji="<:close:921408051091759114>", style=discord.ButtonStyle.red, row=1)
    async def delete(self, button: Button, interaction: Interaction):
        await interaction.message.delete()
        if self.ctx.channel.permissions_for(self.ctx.me).manage_messages:
            await self.ctx.message.delete()

    @discord.ui.button(emoji="<:next:921408056766636073>", style=discord.ButtonStyle.gray, row=1)
    async def next(self, button: Button, interaction: Interaction):
        self.current_page += 1
        self._update_buttons()
        await interaction.response.edit_message(embed=self.embeds[self.current_page], view=self)
        print(self.embeds[self.current_page].fields[0].name)
        print(self.current_page)

    @discord.ui.button(label="News", emoji="📰", style=discord.ButtonStyle.blurple, row=1)
    async def news(self, button: discord.ui.Button, interaction: discord.Interaction):
        view = NewsCentre(self.ctx, self)
        await view.start(interaction)

    def _update_buttons(self):
        page = self.current_page
        total = len(self.embeds) - 1
        self.next.disabled = page == total
        self.previous.disabled = page == 0

    async def interaction_check(self, interaction: Interaction) -> bool:
        if interaction.user and interaction.user == self.ctx.author:
            return True
        await interaction.response.defer()
        return False

    async def on_timeout(self) -> None:
        self.clear_items()
        await self.message.edit(view=self)

    async def start(self):
        self.build_select()
        self._update_buttons()
        self.message = await self.ctx.send(embed=self.main_embed, view=self, footer=False)


class GeneralView(discord.ui.View):
    def __init__(self, ctx: CustomContext):
        super().__init__()
        self.ctx = ctx
        self.bot = ctx.bot
        self.message = None

    @discord.ui.button(label="Help", emoji="❓", style=discord.ButtonStyle.blurple, row=1)
    async def help(self, button: Button, interaction: Interaction):
        view = HelpCentre(self.ctx, self)
        await view.start(interaction)

    @discord.ui.button(emoji="🗑️", style=discord.ButtonStyle.red, row=1)
    async def delete(self, button: Button, interaction: Interaction):
        await interaction.message.delete()
        if self.ctx.channel.permissions_for(self.ctx.me).manage_messages:
            await self.ctx.message.delete()

    @discord.ui.button(label="News", emoji="📰", style=discord.ButtonStyle.blurple, row=1)
    async def news(self, button: discord.ui.Button, interaction: discord.Interaction):
        view = NewsCentre(self.ctx, self)
        await view.start(interaction)

    async def interaction_check(self, interaction: Interaction):
        if interaction.user and interaction.user == self.ctx.author:
            return True

        await interaction.response.defer()
        return False

    async def on_timeout(self):
        self.clear_items()
        await self.message.edit(view=self)

    async def start(self):
        self.build_select()


class StealthHelp(commands.HelpCommand):
    def __init__(self, **options):
        super().__init__(**options)
        self.context = None

    def get_bot_mapping(self):
        """Retrieves the bot mapping passed to :meth:`send_bot_help`."""
        bot = self.context.bot
        ignored_cogs = ['NSFW', 'Events', 'Levels', 'IPC', 'SignalPvP', 'Help', 'Jishaku']

        if self.context.channel.is_nsfw():
            ignored_cogs = ['Events', 'Levels', 'IPC', 'SignalPvP', 'Help', 'Jishaku']

        mapping = {cog: cog.get_commands() for cog in sorted(bot.cogs.values(), key=lambda c: len(c.get_commands()), reverse=True) if cog.qualified_name not in ignored_cogs}
        return mapping


    def get_minimal_command_signature(self, command):
        if isinstance(command, commands.Group):
            return '[G] %s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)
        return '(c) %s%s %s' % (self.context.clean_prefix, command.qualified_name, command.signature)


    async def send_bot_help(self, mapping):
        view = HelpView(self.context, usable_commands=f"{len(await self.filter_commands(list(self.context.bot.commands), sort=True)):,}",
                                                                data=mapping)
        await view.start()


    async def send_cog_help(self, cog):
        entries = [command for command in cog.get_commands()]
        menu = paginator.ViewPaginator(paginator.GroupHelpPageSource(cog, entries, prefix=self.context.clean_prefix,
                                                                total_commands=len(cog.get_commands()),
                                                                usable_commands=len(await self.filter_commands(cog.get_commands()))),
                                                                ctx=self.context, compact=True)
        await menu.start()


    async def send_group_help(self, group):
        entries = [command for command in group.commands]
        menu = paginator.ViewPaginator(paginator.GroupHelpPageSource(group, entries, prefix=self.context.clean_prefix,
                                                                total_commands=len(group.commands),
                                                                usable_commands=len(await self.filter_commands(group.commands, sort=True))),
                                                                ctx=self.context, compact=True)
        await menu.start()


    async def send_command_help(self, command: commands.Command):
        embed = discord.Embed(title=f"{self.get_minimal_command_signature(command)}", description=f"""
{command.help if command.help else 'No help given...'}
                              """)

        # <---- Command Information ---->

        aliases = command.aliases

        commandInformation = [f"Category: {command.cog_name}"]

        if aliases:
            aliases = ', '.join(aliases)
            commandInformation.append(f"Aliases: {aliases}")

        commandInformation = '\n'.join(commandInformation)

        # <---- Command Information ---->

        # <---- Command Checks ---->

        commandChecks = []

        with contextlib.suppress(commands.CommandError):
            if await command.can_run(self.context):
                commandChecks.append("Usable by you: Yes")

            else:
                commandChecks.append("Usable by you: No")

        try:
            slowmode = command._buckets._cooldown.per
            commandChecks.append(f"Slowmode: {slowmode}s")

        except:
            pass

        try:
            await command.can_run(self.context)

        except Exception as e:
            try:
                if isinstance(e, discord.ext.commands.CheckAnyFailure):
                    for e in e.errors:

                        if not isinstance(e, commands.NotOwner):
                            raise e
                raise e

            except commands.MissingPermissions as error:
                text = ', '.join(error.missing_permissions).replace('_', ' ').replace('guild', 'server').title()
                commandChecks.append(f"Author permissions: {text}")

            except commands.BotMissingPermissions as error:
                text = ', '.join(error.missing_permissions).replace('_', ' ').replace('guild', 'server').title()
                commandChecks.append(f"Bot permissions: {text}")

            except commands.NotOwner:
                commandChecks.append(f"Rank required: Bot Owner")

            except commands.PrivateMessageOnly:
                commandChecks.append(f"Restricted access: Can only be executed in DMs")

            except commands.NoPrivateMessage:
                commandChecks.append(f"Restricted access: Can only be executed in servers")

            except commands.DisabledCommand:
                commandChecks.append(f"Restricted access: This is a slash only command")

            finally:
                pass

        commandChecks = '\n'.join(commandChecks)

        embed.add_field(name="<:info:888768239889424444> Command Information", value=f"""
```yaml
{commandInformation}
```
                        """, inline=False)

        if commandChecks:
            embed.add_field(name="<:greenTick:895688440690147370> Command Checks", value=f"""
```yaml
{commandChecks}
```
                            """, inline=False)

        if command.brief:
            embed.add_field(name="Examples", value=f"""
```yaml
{command.brief}
```
                            """, inline=False)
        embed.set_footer(text="<> = required argument | [] = optional argument\nDo NOT type these when using commands!")

        view = GeneralView(ctx=self.context)
        view.message = await self.context.send(embed=embed, footer=False, view=view)


    def command_not_found(self, string):
        return string


    def subcommand_not_found(self, command, string):
        if isinstance(command, commands.Group) and len(command.all_commands) > 0:
            return command.qualified_name + string
        return command.qualified_name


    async def send_error_message(self, error):
        ctx = self.context

        error = error.lower().replace("No command called", "", ).replace('"', '').replace("found.", "")

        listOfStuff = list(ctx.bot.cogs.keys()) + [c.qualified_name for c in ctx.bot.commands]
        string = ''.join(difflib.get_close_matches(error, listOfStuff, n=1, cutoff=0.1))

        if "mod" in error:
            return await ctx.send_help(ctx.bot.get_cog("Moderation"))

        elif ctx.bot.get_cog(string):
            return await ctx.send_help(ctx.bot.get_cog(string))

        elif ctx.bot.get_command(string):
            return await ctx.send_help(ctx.bot.get_command(string))

        else:
            raise errors.CommandDoesntExist


    async def on_help_command_error(self, ctx: CustomContext, error):
        if isinstance(error, commands.CommandInvokeError):
            embed = discord.Embed(description=f"{str(error.original)}")
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)

            await ctx.send(embed=embed)


def setup(client):
    client.add_cog(Help(client))

class Help(commands.Cog):
    """The help command, how did you find this though..."""
    def __init__(self, client):
        self.client = client
        self.hidden = True

        self.select_emoji = "<:info:888768239889424444>"
        self.select_brief = "The help command.. but how did you find this?!"

        help_command = StealthHelp(command_attrs=dict(slash_command=True))
        help_command.cog = self
        client.help_command = help_command