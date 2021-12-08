import discord

from discord.ext import commands


def setup(client):
    client.add_cog(GuildSettings(client))


class GuildSettings(name="Guild settings", commands.Cog):
    """Commands for managing guild settings like logging system, welcome system etc."""

    def __init__(self, client):
        self.client = client
        self.select_emoji = "<:gear:899622456191483904>"
        self.select_brief = "Commands for managing guild settings."

    # Logging commands

    @commands.group(
        invoke_without_command=True,
        help="<:lock:904037834141364275> | Logging commands. If no argument is specified it will show you the current logs channel.",
        aliases=['logs'])
    async def log(self, ctx):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", ctx.guild.id)

        if not database:
            message = f"This server doesn't have a logging channel set-up.\nTo set it up do `{ctx.prefix}log enable <channel>`."

        if database and not database['logs_channel_id']:
            message = f"This server doesn't have a logging channel set-up.\nTo set it up do `{ctx.prefix}log enable <channel>`."

        if database and database['logs_channel_id']:
            channel = self.client.get_channel(database['logs_channel_id'])
            message = f"This server has a logging channel set up. It's {channel.mention}.\nTo remove it do `{ctx.prefix}log disable`"

        embed = discord.Embed(title="Logging Module", description=f"""
This is the logging module. The logging module can log various actions in your server such as bans, kicks channel creations and way more!

{message}
                              """)

        await ctx.send(embed=embed)

    @log.command(
        help="Changes the logging channel to the specified channel. If no channel is specified it will default to the current one.",
        aliases=['set', 'add'])
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def enable(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel

        await self.client.db.execute(
            "INSERT INTO guilds (guild_id, logs_channel_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET logs_channel_id = $2",
            ctx.guild.id, channel.id)

        embed = discord.Embed(title="Logs channel updated",
                              description=f"The logs channel for this server has been set to {channel.mention}!",
                              color=discord.Color.green())
        await ctx.send(embed=embed, color=False)

    @log.command(
        help="Disables the logging module for the current server.",
        aliases=['remove'])
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def disable(self, ctx):
        await self.client.db.execute(
            "INSERT INTO guilds (guild_id, logs_channel_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET logs_channel_id = $2",
            ctx.guild.id, None)

        embed = discord.Embed(title="Logging module disabled",
                              description=f"The logging module for this server has been disabled!",
                              color=discord.Color.red())
        await ctx.send(embed=embed, color=False)

    # Welcome commands