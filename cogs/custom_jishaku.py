import sys
import math
import discord

from jishaku.repl import Scope
from jishaku.flags import Flags
from helpers.context import CustomContext
from jishaku.modules import package_version
from jishaku.features.baseclass import Feature
from jishaku.cog import STANDARD_FEATURES, OPTIONAL_FEATURES

try:
    import psutil

except ImportError:
    psutil = None

try:
    from importlib.metadata import distribution, packages_distributions

except ImportError:
    from importlib_metadata import distribution, packages_distributions


def natural_size(size_in_bytes: int):
    units = ('B', 'KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB')
    power = int(math.log(size_in_bytes, 1024))
    return f"{size_in_bytes / (1024 ** power):.2f} {units[power]}"

class CustomJishaku(*OPTIONAL_FEATURES, *STANDARD_FEATURES):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._scope = Scope()
        self.retain = Flags.RETAIN
        self.last_result = None
        self.hidden = True

    @Feature.Command(name="jishaku", aliases=["jsk"], invoke_without_command=True, ignore_extra=False)
    async def jsk(self, ctx: CustomContext):
        """
        The Jishaku debug and diagnostic commands.
        This command on its own gives a status brief.
        All other functionality is within its subcommands.
        """
        # Try to locate what vends the `discord` package
        distributions = [
            dist for dist in packages_distributions()['discord']
            if any(
                file.parts == ('discord', '__init__.py')
                for file in distribution(dist).files
            )
        ]
        if distributions:
            dist_version = f'{distributions[0]} `{package_version(distributions[0])}`'
        else:
            dist_version = f'unknown `{discord.__version__}`'
        summary = [
            f"Jishaku v{package_version('jishaku')}, {dist_version}, "
            f"`Python {sys.version}` on `{sys.platform}`".replace("\n", ""),
            f"Module was loaded <t:{self.load_time.timestamp():.0f}:R>, "
            f"cog was loaded <t:{self.start_time.timestamp():.0f}:R>.",
            ""
        ]
        # detect if [procinfo] feature is installed
        if psutil:
            try:
                proc = psutil.Process()
                with proc.oneshot():
                    try:
                        mem = proc.memory_full_info()
                        summary.append(f"Using {natural_size(mem.rss)} physical memory and "
                                       f"{natural_size(mem.vms)} virtual memory, "
                                       f"{natural_size(mem.uss)} of which unique to this process.")
                    except psutil.AccessDenied:
                        pass
                    try:
                        name = proc.name()
                        pid = proc.pid
                        thread_count = proc.num_threads()
                        summary.append(f"Running on PID {pid} (`{name}`) with {thread_count} thread(s).")
                    except psutil.AccessDenied:
                        pass
                    summary.append("")  # blank line
            except psutil.AccessDenied:
                summary.append(
                    "psutil is installed, but this process does not have high enough access rights "
                    "to query process information."
                )
                summary.append("")  # blank line
        cache_summary = f"{len(self.bot.guilds)} guild(s) and {len(self.bot.users)} user(s)"
        # Show shard settings to summary
        if isinstance(self.bot, discord.AutoShardedClient):
            if len(self.bot.shards) > 20:
                summary.append(
                    f"This bot is automatically sharded ({len(self.bot.shards)} shards of {self.bot.shard_count})"
                    f" and can see {cache_summary}."
                )
            else:
                shard_ids = ', '.join(str(i) for i in self.bot.shards.keys())
                summary.append(
                    f"This bot is automatically sharded (Shards {shard_ids} of {self.bot.shard_count})"
                    f" and can see {cache_summary}."
                )
        elif self.bot.shard_count:
            summary.append(
                f"This bot is manually sharded (Shard {self.bot.shard_id} of {self.bot.shard_count})"
                f" and can see {cache_summary}."
            )
        else:
            summary.append(f"This bot is not sharded and can see {cache_summary}.")
        # pylint: disable=protected-access
        if self.bot._connection.max_messages:
            message_cache = f"Message cache capped at {self.bot._connection.max_messages}"
        else:
            message_cache = "Message cache is disabled"
        if discord.version_info >= (1, 5, 0):
            presence_intent = f"presence intent is {'enabled' if self.bot.intents.presences else 'disabled'}"
            members_intent = f"members intent is {'enabled' if self.bot.intents.members else 'disabled'}"
            summary.append(f"{message_cache}, {presence_intent} and {members_intent}.")
        else:
            guild_subscriptions = f"guild subscriptions are {'enabled' if self.bot._connection.guild_subscriptions else 'disabled'}"
            summary.append(f"{message_cache} and {guild_subscriptions}.")
        # pylint: enable=protected-access
        # Show websocket latency in milliseconds
        summary.append(f"Average websocket latency: {round(self.bot.latency * 1000, 2)}ms")
        embed = discord.Embed(title="Custom Jishaku", description='\n'.join(summary))
        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(CustomJishaku(bot=bot))