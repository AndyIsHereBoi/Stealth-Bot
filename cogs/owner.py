import discord
import os
import time
import textwrap
import asyncpg
import tabulate
import traceback
import sys
import math
from collections import defaultdict
import shutil
import pathlib
import typing
import asyncio
import itertools
import asyncbing
import psutil
import random
import pomice
import jishaku
from discord.ext import commands, menus
from discord.ext.menus.views import ViewMenuPages
import importlib
from jishaku.paginators import WrappedPaginator, PaginatorInterface
from jishaku.codeblocks import codeblock_converter
from helpers.context import CustomContext
from jishaku.modules import ExtensionConverter
import io
import contextlib


def setup(client):
    client.add_cog(Owner(client))

def format_table(db_res):
    result_dict = defaultdict(list)
    for x in db_res:
        for key, value in x.items():
            result_dict[key].append(value)

    def key(i):
        return len(i)

    # I just wrote some weird code and it worked lmfao
    total_length = [
        (len(max([str(column_name)] + [str(row) for row in rows], key=key)) + 2)
        for column_name, rows in result_dict.items()
    ]
    result = (
        "┍" + ("┯".join("━" * times for times in total_length)) + "┑" + "\n│"
    )
    columns = [str(col) for col in result_dict.keys()]
    rows = [list() for _, _1 in enumerate(list(result_dict.values())[0])]
    for row in result_dict.values():
        for index, item in enumerate(row):
            rows[index].append(item)

    column_lengths = list()
    for index, column in enumerate(columns):
        column_length = (
            len(max([str(column)] + [str(row[index]) for row in rows], key=key)) + 2
        )
        column_lengths.append(column_length)
        before = math.ceil((column_length - len(column)) / 2)
        after = math.floor((column_length - len(column)) / 2)
        result += (" " * before) + column + (" " * after) + "│"
    result += (
        "\n" + "┝" + ("┿".join("━" * times for times in total_length)) + "┥\n│"
    )

    for row in rows:
        for index, item in enumerate(row):
            before = math.ceil((column_lengths[index] - len(str(item))) / 2)
            after = math.floor((column_lengths[index] - len(str(item))) / 2)
            result += (" " * before) + str(item) + (" " * after) + "│"
        result += (
            "\n" + "┝" + ("┿".join("━" * times for times in total_length)) + "┥\n│"
        )

    result = "\n".join(result.split("\n")[:-2])
    result += (
        "\n" + "┕" + ("┷".join("━" * times for times in total_length)) + "┙"
    )

    return result


# bytes pretty-printing
UNITS_MAPPING = [
    (1 << 50, ' PB'),
    (1 << 40, ' TB'),
    (1 << 30, ' GB'),
    (1 << 20, ' MB'),
    (1 << 10, ' KB'),
    (1, (' byte', ' bytes')),
]


def pretty_size(bytes, units=UNITS_MAPPING):
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


def cleanup_code(content):
    if content.startswith('```') and content.endswith('```'):
        return '\n'.join(content.split('\n')[1:-1])

    # remove `foo`
    return content.strip('` \n')


def get_ram_usage():
    return int(psutil.virtual_memory().total - psutil.virtual_memory().available)


def get_ram_total():
    return int(psutil.virtual_memory().total)


def get_ram_usage_pct():
    return psutil.virtual_memory().percent


class BlacklitedUsersEmbedPage(menus.ListPageSource):
    def __init__(self, data):
        self.data = data
        super().__init__(data, per_page=20)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        colors = [0x910023, 0xA523FF]
        color = random.choice(colors)
        embed = discord.Embed(title=f"Blacklisted users", description="\n".join(entries),
                              timestamp=discord.utils.utcnow(), color=color)
        return embed


class Owner(commands.Cog):
    """Commands that only the developer of this bot can use"""

    def __init__(self, client):
        self.client = client
        self.hidden = True
        self._last_result = None
        self.select_emoji = "<:owner_crown:845946530452209734>"
        self.select_brief = "Commands that only the developer of this bot can use."

    @commands.group(
        invoke_without_commands=True,
        help="<:ayb_developer:913472701551747132> All developer commands",
        aliases=['d', 'developer'])
    async def dev(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @dev.command(
        help="Shows information about the system the bot is hosted on",
        aliases=['sys'])
    @commands.is_owner()
    async def system(self, ctx: CustomContext):
        colors = [0x910023, 0xA523FF]
        color = random.choice(colors)

        start = time.perf_counter()

        pid = os.getpid()
        process = psutil.Process(pid)
        total, used, free = shutil.disk_usage("/")
        ver = sys.version_info
        full_version = f"{ver.major}.{ver.minor}.{ver.micro}"

        delta_uptime = discord.utils.utcnow() - self.client.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

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

        pings = []
        number = 0

        typings = time.monotonic()
        await ctx.trigger_typing()
        typinge = time.monotonic()
        typingms = (typinge - typings) * 1000
        pings.append(typingms)

        start2 = time.perf_counter()
        message = await ctx.send("Getting system information...")
        end2 = time.perf_counter()
        messagems = (end2 - start2) * 1000
        pings.append(messagems)

        # discords = time.monotonic()
        # url = "https://discordapp.com/"
        # resp = await self.client.session.get(url)
        # if resp.status == 200:
        #         discorde = time.monotonic()
        #         discordms = (discorde - discords) * 1000
        #         pings.append(discordms)
        # else:
        #         discordms = 0

        latencyms = self.client.latency * 1000
        pings.append(latencyms)

        pstart = time.perf_counter()
        await self.client.db.fetch("SELECT 1")
        pend = time.perf_counter()
        psqlms = (pend - pstart) * 1000
        pings.append(psqlms)

        for ms in pings:
            number += ms
        average = number / len(pings)

        websocket_latency = f"{round(latencyms)}ms{' ' * (9 - len(str(round(latencyms, 3))))}"
        typing_latency = f"{round(typingms)}ms{' ' * (9 - len(str(round(typingms, 3))))}"
        message_latency = f"{round(messagems)}ms{' ' * (9 - len(str(round(messagems, 3))))}"
        # discord_latency = f"{round(discordms)}ms{' ' * (9-len(str(round(discordms, 3))))}"
        database_latency = f"{round(psqlms)}ms{' ' * (9 - len(str(round(psqlms, 3))))}"
        average_latency = f"{round(average)}ms{' ' * (9 - len(str(round(average, 3))))}"

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(description=f"""
```yaml
PID: {os.getpid()}
CPU: {psutil.cpu_percent()}% / 100%
RAM: {int(get_ram_usage() / 1024 / 1024)}MB / {int(get_ram_total() / 1024 / 1024)}MB ({get_ram_usage_pct()}%)
Disk: {used // (2 ** 30)}GB / {total // (2 ** 30)}GB
Uptime: {days} days, {hours} hours, {minutes} minutes and {seconds} seconds
```
                              """, timestamp=discord.utils.utcnow(), color=color)

        embed.add_field(name="\u200b", value=f"""
```yaml
Files: {fc}
Lines: {ls:,}
Classes: {cl}
Functions: {fn}
Coroutine: {cr}
Comments: {cm:,}
```
                        """, inline=True)

        embed.add_field(name="\u200b", value=f"""
```yaml
PostgreSQL:
Pomice: {pomice.__version__}
e-dpy: {discord.__version__}
asyncpg: {asyncpg.__version__}
Python: {full_version}
Async bing: {asyncbing.__version__}
```
                        """, inline=True)

        embed.add_field(name="\u200b", value=f"""
```yaml
Websocket: {websocket_latency}
Typing: {typing_latency}
Message: {message_latency}
Database: {database_latency}
Average: {average_latency}
```
                        """, inline=True)

        embed.set_footer(text=f"Requested by {ctx.author} • {round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.me.avatar.url)

        await message.edit("Received system information!", embed=embed)

    @commands.command(pass_context=True, hidden=True, name='eval', aliases=['ev'])
    @commands.is_owner()
    async def _eval(self, ctx: CustomContext, *, body: str, return_result: bool = False):
        """ Evaluates arbitrary python code """
        env = {
            'bot': self.client,
            '_b': self.client,
            'ctx': ctx,
            'channel': ctx.channel,
            '_c': ctx.channel,
            'author': ctx.author,
            '_a': ctx.author,
            'guild': ctx.guild,
            '_g': ctx.guild,
            'message': ctx.message,
            '_m': ctx.message,
            'reference': getattr(ctx.message.reference, 'resolved', None),
            '_r': getattr(ctx.message.reference, 'resolved', None),
            '_get': discord.utils.get,
            '_find': discord.utils.find,
            '_now': discord.utils.utcnow,
        }
        env.update(globals())

        body = cleanup_code(body)
        stdout = io.StringIO()
        to_send: str = None

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            try:
                await ctx.message.add_reaction('⚠')
            except (discord.Forbidden, discord.HTTPException):
                pass
            to_send = f'{e.__class__.__name__}: {e}'
            if len(to_send) > 1880:
                return await ctx.send(file=discord.File(io.StringIO(to_send), filename='output.py'))
            await ctx.send(f'```py\n{to_send}\n```')
            return

        func = env['func']
        # noinspection PyBroadException
        try:
            with contextlib.redirect_stdout(stdout):
                ret = await func()
        except Exception:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('⚠')
            except (discord.Forbidden, discord.HTTPException):
                pass
            to_send = f'\n{value}{traceback.format_exc()}'
            if len(to_send) > 1880:
                await ctx.send(file=discord.File(io.StringIO(to_send), filename='output.py'))
                return
            await ctx.send(f'```py\n{to_send}\n```')
            return

        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except (discord.Forbidden, discord.HTTPException):
                pass

            if not return_result:
                if ret is None:
                    if value:
                        to_send = f'{value}'
                else:
                    self._last_result = ret
                    to_send = f'{value}{ret}'
                if to_send:
                    to_send = to_send.replace(self.client.http.token, '[discord token redacted]')
                    if len(to_send) > 1985:
                        await ctx.send(file=discord.File(io.StringIO(to_send), filename='output.py'))
                    else:
                        await ctx.send(f"```py\n{to_send}\n```")
            else:
                return ret


    @dev.command(
        help="Reloads the specified extensions. If you want to reload all extensions, use `~` as the argument.",
        aliases=['r'])
    async def reload(self, ctx: CustomContext, *extensions: ExtensionConverter) -> discord.Message:
        everything = []

        reload_fail = []
        reload_success = []

        for extension in itertools.chain(*extensions):
            everything.append(f"{extension}")
            method, icon = ((self.client.reload_extension, ":repeat:") if extension in self.client.extensions else (self.client.load_extension, ":mailbox:"))

            try:
                method(extension)

            except Exception as exc:
                traceback_data = ''.join(traceback.format_exception(type(exc), exc, exc.__traceback__, 1))
                reload_fail.append(f":warning: `{extension}`\n```py\n{traceback_data}\n```")

            else:
                reload_success.append(f"{icon} `{extension}`")

        nl = "\n"

        embed = discord.Embed(description=f"""
**Successfully reloaded**: {len(reload_success)}/{len(everything)} extension{'s' if len(everything) >= 1 else ''}.

{nl.join(reload_success)}

{nl.join(reload_fail)}
        """)

        if reload_fail:
            embed.set_footer(text=f"{len(reload_fail)} extension{'s' if len(reload_fail) >= 1 else ''} failed")
            return await ctx.send(embed=embed, footer=False)

        return await ctx.send(embed=embed)

    @dev.command()
    async def pf(self, ctx: CustomContext, *, query: str):
        body = cleanup_code(query)
        result = await self._eval(ctx, body=f"return await client.db.fetch(f\"\"\"{body}\"\"\")", return_result=True)

        if not result:
            return await ctx.send("No results found...")

        else:
            result = format_table(result)
            embed = discord.Embed(description=f"```py\n{result}\n```")
            await ctx.send(embed=embed)

    @dev.command(
        help="Update the bot.",
        aliases=['upd', 'gitpull', 'pull'])
    @commands.is_owner()
    async def update(self, ctx: CustomContext):
        command = self.client.get_command("jsk git")
        await ctx.invoke(command, argument=codeblock_converter("pull"))

        command = self.client.get_command('jsk reload')
        await ctx.invoke(command, argument="~")

    @dev.command(
        help="Adds a member to the acknowledgments list",
        aliases=['ack'])
    @commands.is_owner()
    async def acknowledge(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User], *, message=None):
        if message:
            await self.client.db.execute(
                "INSERT INTO acknowledgments (user_id, acknowledgment) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET acknowledgment = $2",
                member.id, message)
            return await ctx.send(
                f"Successfully added {member.mention if isinstance(member, discord.Member) else member} to the acknowledgements list.")

        else:
            await self.client.db.execute("DELETE FROM acknowledgments WHERE user_id = $1", member.id)
            return await ctx.send(
                f"Successfully deleted {member.mention if isinstance(member, discord.Member) else member} from the acknowledgements list.")

    @dev.command(
        help="Shutdowns the bot",
        aliases=['shutdown_bot'])
    @commands.is_owner()
    async def shutdown(self, ctx: CustomContext):
        confirm = await ctx.confirm(message="Are you sure you want to shutdown the bot?")

        if confirm:
            embed = discord.Embed(title="<a:loading:747680523459231834> Shutting down...")

            message = await ctx.send(embed=embed)

            os.system("sudo systemctl stop stealthbot")

        else:
            await ctx.send("Okay, I won't.")

    @dev.command(
        help="Restarts the bot.",
        aliases=['reboot', 'restartbot', 'restart-bot'])
    @commands.is_owner()
    async def restart(self, ctx: CustomContext):
        confirm = await ctx.confirm(message="Are you sure you want to restart the bot?")

        if confirm:
            embed = discord.Embed(title="<a:loading:747680523459231834> Restarting...",
                                  description="If this takes more than 10 seconds, you're fucked.")

            await ctx.send(embed=embed)

            file = open("data/restart_log.log", "w")
            file.write(str(ctx.channel.id))

            await asyncio.sleep(1.5)

            os.system("systemctl restart stealthbot")

        else:
            return await ctx.send("Okay, I won't.")

    @dev.command(
        help="Toggles the no-prefix mode on/off",
        aliases=["no_prefix", "silentprefix", "silent_prefix"])
    @commands.is_owner()
    async def noprefix(self, ctx: CustomContext):
        if self.client.no_prefix:
            self.client.no_prefix = False
            await ctx.send("Successfully turned off no-prefix mode.")

        else:
            self.client.no_prefix = True
            await ctx.send("Successfully turned on no-prefix mode.")

    @dev.command(
        help="Toggles the bot-maintenance mode on/off",
        aliases=["bot_maintenance", "maintenancebot", "maintenance_bot", 'botmaintenance'])
    @commands.is_owner()
    async def maintenance(self, ctx: CustomContext):
        if self.client.maintenance:
            self.client.maintenance = False

            embed = discord.Embed(description=f"{ctx.toggle(False)} Successfully turned off maintenance mode.")

            await ctx.send(embed=embed)

        else:
            self.client.maintenance = True

            embed = discord.Embed(description=f"{ctx.toggle(True)} Successfully turned on maintenance mode.")

            await ctx.send(embed=embed)

    @dev.group(
        invoke_without_command=True,
        help="<:scroll:904038785921187911> Commands that the owner can use to prevent someone from using this bot",
        aliases=['bl'])
    @commands.is_owner()
    async def blacklist(self, ctx: CustomContext):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @blacklist.command(
        help="Adds the specified user to the blacklist.",
        aliases=['a'])
    async def add(self, ctx: CustomContext, member: discord.User, *, reason: str):
        await self.client.db.execute("INSERT INTO blacklist(user_id, is_blacklisted, reason) VALUES ($1, $2, $3) ON CONFLICT (user_id) DO UPDATE SET is_blacklisted = $2", member.id, True, reason[0:1800])
        self.client.blacklist[member.id] = True

        embed = discord.Embed(description=f"Successfully added {member} to the blacklist with the reason being {reason[0:1800]}")

        await ctx.send(embed=embed)

    @blacklist.command(
        help="Removes the specified user from the blacklist.",
        aliases=['r', 'rm'])
    async def remove(self, ctx: CustomContext, member: discord.User):
        await self.client.db.execute("DELETE FROM blacklist where user_id = $1", member.id)
        self.client.blacklist[member.id] = False

        embed = discord.Embed(description=f"Successfully removed {member} from the blacklist")

        await ctx.send(embed=embed)

    @blacklist.command(
        help="Checks if the specified user is blacklisted or not.",
        liases=['c'])
    async def check(self, ctx: CustomContext, member: discord.User):
        status = None
        reason = None

        try:
            status = self.client.blacklist[member.id]
            reason = await self.client.db.fetchval("SELECT reason FROM blacklist WHERE user_id = $1", member.id)

        except KeyError:
            status = False

        embed = discord.Embed(description=f"{member.mention} is {'' if status else 'not'} blacklisted.\n{f'Reason: {reason}' if reason else ''}")

        await ctx.send(embed=embed)

    @blacklist.command(
        help="Sends a list of all blacklisted users.",
        aliases=['l'])
    async def list(self, ctx: CustomContext):
        blacklistedUsers = []

        blacklist = await self.client.db.fetch("SELECT * FROM blacklist")
        for stuff in blacklist:
            user = self.client.get_user(stuff["user_id"])
            reason = stuff["reason"]

            blacklistedUsers.append(f"{user.name} **|** {user.id} **|** [Hover over for reason]({ctx.message.jump_url} '{reason}')")

        paginator = ViewMenuPages(source=BlacklitedUsersEmbedPage(blacklistedUsers), clear_reactions_after=True)
        page = await paginator._source.get_page(0)
        kwargs = await paginator._get_kwargs_from_page(page)

        if paginator.build_view():
            paginator.message = await ctx.send(embed=kwargs['embed'], view=paginator.build_view())

        else:
            paginator.message = await ctx.send(embed=kwargs['embed'])

        await paginator.start(ctx)

    @dev.command(
        name="commands",
        help="Shows all used commands",
        aliases=['ch', 'cmds'])
    @commands.is_owner()
    async def _commands(self, ctx: CustomContext):
        executed_commands = await self.client.db.fetch("SELECT command, user_id, guild_id, timestamp FROM commands ORDER BY timestamp DESC")

        if not executed_commands:
            return await ctx.send("No results found...")

        table = [(command, self.client.get_user(user_id) or user_id, guild_id, str(timestamp).replace('+00:00', '')) for command, user_id, guild_id, timestamp in executed_commands]

        table = tabulate.tabulate(table, headers=["Command", "User/UID", "Guild ID", "Timestamp"], tablefmt="presto")
        lines = table.split("\n")
        lines, headers = lines[2:], '\n'.join(lines[0:2])
        header = f"Latest executed commands".center(len(lines[0]))
        pages = WrappedPaginator(prefix=f'```\n{header}\n{headers}', max_size=1950)
        [pages.add_line(line) for line in lines]
        interface = PaginatorInterface(self.client, pages)
        await interface.send_to(ctx)

