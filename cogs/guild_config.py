import errors
import discord

from discord.ext import commands
from helpers.context import CustomContext


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
        await self.client.db.execute("INSERT INTO guilds (guild_id, logs_channel_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET logs_channel_id = $2", ctx.guild.id, None)

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

    # Mute commands

    # Add mute role
    @commands.group(invoke_without_command=True)
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def muterole(self, ctx: CustomContext, new_role: discord.Role = None):
        """
        Sets the mute-role. If no role is specified, shows the current mute role.
        """
        if ctx.invoked_subcommand is None:
            if new_role:
                await self.client.db.execute(
                    "INSERT INTO prefixes(guild_id, muted_id) VALUES ($1, $2) "
                    "ON CONFLICT (guild_id) DO UPDATE SET muted_id = $2",
                    ctx.guild.id, new_role.id)

                return await ctx.send(f"Updated the muted role to {new_role.mention}!",
                                      allowed_mentions=discord.AllowedMentions().none())

            mute_role = await self.client.db.fetchval('SELECT muted_id FROM prefixes WHERE guild_id = $1', ctx.guild.id)

            if not mute_role:
                raise errors.MuteRoleNotFound

            role = ctx.guild.get_role(int(mute_role))
            if not isinstance(role, discord.Role):
                raise errors.MuteRoleNotFound

            return await ctx.send(f"This server's mute role is {role.mention}"
                                  f"\nChange it with the `muterole [new_role]` command",
                                  allowed_mentions=discord.AllowedMentions().none())

    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @muterole.command(name="remove", aliases=["unset"])
    async def muterole_remove(self, ctx: CustomContext):
        """
        Unsets the mute role for the server,
        note that this will NOT delete the role, but only remove it from the bot's database!
        If you want to delete it, do "%PRE%muterole delete" instead
        """
        await self.bot.db.execute(
            "INSERT INTO prefixes(guild_id, muted_id) VALUES ($1, $2) "
            "ON CONFLICT (guild_id) DO UPDATE SET muted_id = $2",
            ctx.guild.id, None)

        return await ctx.send(f"Removed this server's mute role!",
                              allowed_mentions=discord.AllowedMentions().none())

    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    @muterole.command(name="create")
    async def muterole_create(self, ctx: CustomContext):
        starting_time = time.monotonic()

        mute_role = await self.bot.db.fetchval('SELECT muted_id FROM prefixes WHERE guild_id = $1', ctx.guild.id)

        if mute_role:
            mute_role = ctx.guild.get_role(mute_role)
            if mute_role:
                raise commands.BadArgument('You already have a mute role')

        await ctx.send(f"Creating Muted role, and applying it to all channels."
                       f"\nThis may take awhile ETA: {len(ctx.guild.channels)} seconds.")

        async with ctx.typing():
            permissions = discord.Permissions(send_messages=False,
                                              add_reactions=False,
                                              connect=False,
                                              speak=False)
            role = await ctx.guild.create_role(name="Muted", colour=0xff4040, permissions=permissions,
                                               reason=f"DuckBot mute-role creation. Requested "
                                                      f"by {ctx.author} ({ctx.author.id})")
            await self.bot.db.execute(
                "INSERT INTO prefixes(guild_id, muted_id) VALUES ($1, $2) "
                "ON CONFLICT (guild_id) DO UPDATE SET muted_id = $2",
                ctx.guild.id, role.id)

            modified = 0
            for channel in ctx.guild.channels:
                perms = channel.overwrites_for(role)
                perms.update(send_messages=None,
                             add_reactions=None,
                             create_public_threads=None,
                             create_private_threads=None
                             )
                try:
                    await channel.set_permissions(role, overwrite=perms,
                                                  reason=f"DuckBot mute-role creation. Requested "
                                                         f"by {ctx.author} ({ctx.author.id})")
                    modified += 1
                except (discord.Forbidden, discord.HTTPException):
                    continue
                await asyncio.sleep(1)

            ending_time = time.monotonic()
            complete_time = (ending_time - starting_time)
            await ctx.send(f"done! took {round(complete_time, 2)} seconds"
                           f"\nSet permissions for {modified} channel{'' if modified == 1 else 's'}!")

    @muterole.command(name="delete")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def muterole_delete(self, ctx: CustomContext):
        """
        Deletes the server's mute role if it exists.
        # If you want to keep the role but not
        """
        mute_role = await self.bot.db.fetchval('SELECT muted_id FROM prefixes WHERE guild_id = $1', ctx.guild.id)
        if not mute_role:
            raise errors.MuteRoleNotFound

        role = ctx.guild.get_role(int(mute_role))
        if not isinstance(role, discord.Role):
            await self.bot.db.execute(
                "INSERT INTO prefixes(guild_id, muted_id) VALUES ($1, $2) "
                "ON CONFLICT (guild_id) DO UPDATE SET muted_id = $2",
                ctx.guild.id, None)

            return await ctx.send("It seems like the muted role was already deleted, or I can't find it right now!"
                                  "\n I removed it from my database. If the mute role still exists, delete it manually")

        if role > ctx.me.top_role:
            return await ctx.send("I'm not high enough in role hierarchy to delete that role!")

        if role > ctx.author.top_role:
            return await ctx.send("You're not high enough in role hierarchy to delete that role!")

        try:
            await role.delete(reason=f"Mute role deletion. Requested by {ctx.author} ({ctx.author.id})")
        except discord.Forbidden:
            return await ctx.send("I can't delete that role! But I deleted it from my database")
        except discord.HTTPException:
            return await ctx.send("Something went wrong while deleting the muted role!")
        await self.bot.db.execute(
            "INSERT INTO prefixes(guild_id, muted_id) VALUES ($1, $2) "
            "ON CONFLICT (guild_id) DO UPDATE SET muted_id = $2",
            ctx.guild.id, None)
        await ctx.send("🚮")

    @muterole.command(name="fix")
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def muterole_fix(self, ctx: CustomContext):
        async with ctx.typing():
            starting_time = time.monotonic()
            mute_role = await self.bot.db.fetchval('SELECT muted_id FROM prefixes WHERE guild_id = $1', ctx.guild.id)

            if not mute_role:
                raise errors.MuteRoleNotFound

            role = ctx.guild.get_role(int(mute_role))
            if not isinstance(role, discord.Role):
                raise errors.MuteRoleNotFound

            cnf = await ctx.confirm(
                f'Are you sure you want to change the permissions for **{role.name}** in all channels?')
            if not cnf:
                return

            modified = 0
            for channel in ctx.guild.channels:
                perms = channel.overwrites_for(role)
                perms.update(send_messages=False,
                             add_reactions=False,
                             connect=False,
                             speak=False,
                             create_public_threads=False,
                             create_private_threads=False,
                             send_messages_in_threads=False,
                             )
                try:
                    await channel.set_permissions(role, overwrite=perms,
                                                  reason=f"DuckBot mute-role creation. Requested "
                                                         f"by {ctx.author} ({ctx.author.id})")
                    modified += 1
                except (discord.Forbidden, discord.HTTPException):
                    continue
                await asyncio.sleep(1)

            ending_time = time.monotonic()
            complete_time = (ending_time - starting_time)
            await ctx.send(f"done! took {round(complete_time, 2)} seconds"
                           f"\nSet permissions for {modified} channel{'' if modified == 1 else 's'}!")

