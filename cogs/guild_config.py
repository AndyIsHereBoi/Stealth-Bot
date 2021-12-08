import discord

from discord.ext import commands


def setup(client):
    client.add_cog(GuildSettings(client))


class GuildSettings(commands.Cog, name="Guild settings"):
    """Commands for managing guild settings like logging system, welcome system etc."""

    def __init__(self, client):
        self.client = client
        self.select_emoji = "<:gear:899622456191483904>"
        self.select_brief = "Commands for managing guild settings."

    def make_ordinal(n):
        n = int(n)
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        if 11 <= (n % 100) <= 13:
            suffix = 'th'

        return str(n) + suffix

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

    @commands.group(
        invoke_without_command=True,
        help=":wave: | Welcome commands. If no argument is specified it will show you the current welcome channel.")
    async def welcome(self, ctx):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", ctx.guild.id)

        if not database['welcome_channel_id']:
            message = f"This server doesn't have a welcome channel set-up.\nTo set it up do `{ctx.prefix}welcome enable <channel>`"

        else:
            channel = self.client.get_channel(database['welcome_channel_id'])
            message = f"This server has a welcome channel set up. It's {channel.mention}.\nTo remove it do `{ctx.prefix}welcome disable`"

        if not database['welcome_message']:
            message2 = f"This server doesn't have a welcome message set-up.\nIf you would like to change that do `{ctx.prefix}welcome message <message>`"

        else:
            message2 = f"The welcome message for this server is: `{database['welcome_message']}`"

        embed = discord.Embed(title="Welcome Module", description=f"""
This is the welcome module. This module can log when a user joins the server and when they leave.

{message}
{message2}
                              """)

        await ctx.send(embed=embed)

    @welcome.command(
        help="Changes the welcome channel to the specified channel. If no channel is specified it will default to the current one.",
        aliases=['set', 'add'])
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def enable(self, ctx, channel: discord.TextChannel = None):
        if not channel:
            channel = ctx.channel

        await self.client.db.execute(
            "INSERT INTO guilds (guild_id, welcome_channel_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET welcome_channel_id = $2",
            ctx.guild.id, channel.id)

        embed = discord.Embed(title="Welcome channel updated", description=f"""
The welcome channel for this server has been set to {channel.mention}!
Now you will be notified when a user joins or leaves the server in that channel.
If you would like to set a custom welcome message do `{ctx.prefix}welcome message <message>`.
                            """, color=discord.Color.green())

        await ctx.send(embed=embed, color=False)

    @welcome.command(
        help="Disables the welcome module for the current server.",
        aliases=['remove', 'delete'])
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def disable(self, ctx):
        await self.client.db.execute(
            "INSERT INTO guilds (guild_id, welcome_channel_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET welcome_channel_id = $2",
            ctx.guild.id, None)
        await self.client.db.execute(
            "INSERT INTO guilds (guild_id, welcome_message) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET welcome_message = $2",
            ctx.guild.id, None)

        embed = discord.Embed(title="Welcome module disabled", description=f"""
The welcome module has been disabled for this server.
You will no longer be notified when a user joins or leaves the server.
I've also deleted the welcome message for this server.
                              """, color=discord.Color.red())

        await ctx.send(embed=embed, color=False)

    @welcome.command(
        help="""
Changes the welcome message to the specified message.
You can also use all of these placeholders:
To use placeholders, surround them with `[]`. (e.g. `[server]`)

`server` - The server's name (e.g. My Server)
`user` - The user's name (e.g. John)
`full-user` - The user's name and discriminator (e.g. John#1234)
`user-mention` - The user's mention (e.g. <@123456789>)
`count` - The number of members in the server (e.g. 3rd)
`code` - The invite code (e.g. 1234567890)
`full-code` - The full invite code (e.g. discord.gg/123456789)
`full-url` - The full invite url (e.g. https://discord.gg/123456789)
`inviter` - The inviter's name (e.g. John)
`full-inviter` - The inviter's name and discriminator (e.g. John#1234)
`inviter-mention` - The inviter's mention (e.g. <@123456789>)
""",
        brief="sb!welcome message Welcome to **[server]**, [user-mention]\nsb!welcome message Welcome, [full-user]\nsb!welcome message [user] is the [count]th to join!",
        aliases=['msg', 'messages'])
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def message(self, ctx, *, message):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", ctx.guild.id)

        if not database['welcome_channel_id']:
            return await ctx.send(
                f"You need to set-up a welcome channel first!\nTo do that do `{ctx.prefix}welcome enable <channel>`")

        if len(message) > 500:
            return await ctx.send(f"Your message exceeded the 500-character limit!")

        await self.client.db.execute(
            "INSERT INTO guilds (guild_id, welcome_message) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET welcome_message = $2",
            ctx.guild.id, message)

        embed = discord.Embed(title="Welcome message updated", description=f"""
The welcome message for this server has been set to: {message}
To disable the welcome module do `{ctx.prefix}welcome disable`
                            """, color=discord.Color.green())

        await ctx.send(embed=embed, color=False)

    @welcome.command(
        help="Sends a fake welcome message.",
        aliases=['fake', 'fake-msg', 'fake-message'])
    async def fake_message(self, ctx):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", ctx.guild.id)

        if not database['welcome_channel_id']:
            return await ctx.send(
                f"You need to set-up a welcome channel first!\nTo do that do `{ctx.prefix}welcome enable <channel>`")

        if not database['welcome_message']:
            message = f"Welcome to **[server]**, **[full-user]**!"

        else:
            message = database['welcome_message']

        message = message.replace("[server]", f"{ctx.guild.name}")

        message = message.replace("[user]", f"{ctx.author.display_name}").replace("[full-user]",
                                                                                  f"{ctx.author}").replace(
            "[user-mention]", f"{ctx.author.mention}")

        message = message.replace("[count]", f"{self.make_ordinal(ctx.guild.member_count)}")

        message = message.replace("[code]", f"123456789").replace("[full-code]", f"discord.gg/123456789").replace(
            "[full-url]", f"https://discord.gg/123456789").replace("[inviter]", f"John").replace("[full-inviter]",
                                                                                                 f"John#1234").replace(
            "[inviter-mention]", f"@John")

        await ctx.send(message)
