import errors
import discord
import datetime

from helpers import helpers
from helpers import time_inputs
from ._base import ModerationBase
from discord.ext import commands, tasks
from helpers.context import CustomContext

def ensure_muterole(*, required: bool = True):
    async def predicate(ctx):
        if not ctx.guild:
            raise commands.BadArgument('Only servers can have mute roles')
        if not required:
            return True
        if not (role := await ctx.bot.db.fetchval('SELECT muted_role_id FROM guilds WHERE guild_id = $1', ctx.guild.id)):
            raise commands.BadArgument('This server has no mute role set')
        if not (role := ctx.guild.get_role(role)):
            raise commands.BadArgument("It seems like I could not find this server's mute role. Was it deleted?")
        if role >= ctx.me.top_role:
            raise commands.BadArgument("This server's mute role seems to be above my top role. I can't assign it!")
        return True
    return commands.check(predicate)


async def muterole(ctx) -> discord.Role:
    if not ctx.guild:
        raise commands.BadArgument('Only servers can have mute roles')
    if not (role := await ctx.bot.db.fetchval('SELECT muted_role_id FROM guilds WHERE guild_id = $1', ctx.guild.id)):
        raise commands.BadArgument('This server has no mute role set')
    if not (role := ctx.guild.get_role(role)):
        raise commands.BadArgument("It seems like I could not find this server's mute role. Was it deleted?")
    if role >= ctx.me.top_role:
        raise commands.BadArgument("This server's mute role seems to be above my top role. I can't assign it!")
    return role

class Mute(ModerationBase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.temporary_mutes.start()

    def cog_unload(self):
        self.temporary_mutes.cancel()

    @tasks.loop()
    async def temporary_mutes(self):
        # if you don't care about keeping records of old tasks, remove this WHERE and change the UPDATE to DELETE
        next_task = await self.bot.db.fetchrow('SELECT * FROM temporary_mutes ORDER BY end_time LIMIT 1')
        # if no remaining tasks, stop the loop
        if next_task is None:
            self.temporary_mutes.cancel()
            return

        await discord.utils.sleep_until(next_task['end_time'])

        guild: discord.Guild = self.bot.get_guild(next_task['guild_id'])

        if guild:

            mute_role = await self.bot.db.fetchval('SELECT muted_role_id FROM guilds WHERE guild_id = $1',
                                                      next_task['guild_id'])
            if mute_role:

                role = guild.get_role(int(mute_role))
                if isinstance(role, discord.Role):

                    if not role > guild.me.top_role:
                        try:
                            member = (guild.get_member(next_task['member_id']) or
                                      await guild.fetch_member(next_task['member_id']))
                            if member:
                                await member.remove_roles(role)
                        except(discord.Forbidden, discord.HTTPException):
                            pass

        await self.bot.db.execute('DELETE FROM temporary_mutes WHERE (guild_id, member_id) = ($1, $2)',
                                     next_task['guild_id'], next_task['member_id'])

    @temporary_mutes.before_loop
    async def wait_for_bot_ready(self):
        await self.bot.wait_until_ready()

    def mute_task(self):
        if self.temporary_mutes.is_running():
            self.temporary_mutes.restart()
        else:
            self.temporary_mutes.start()

    @commands.command(
        help="Mutes the specified member forever.",
        brief="mute @Joy Spamming in #general :angy:")
    @ensure_muterole()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def mute(self, ctx: CustomContext, member: discord.Member, *, reason: str = None):
        if member.id == ctx.author.id:
            return await ctx.send("You can't mute yourself!")

        if member.id == self.bot.user.id:
            return await ctx.send("Noooo! Don't mute me :(")

        if member.id == ctx.guild.owner.id:
            return await ctx.send("You can't mute the owner of this server!")

        if member.guild_permissions.administrator:
            return await ctx.send("You can't mute that user since they have the administrator permission!")

        if isinstance(member, discord.Member):
            if member.top_role >= ctx.me.top_role:
                raise errors.Forbidden

        if reason is None or len(reason) > 500:
            reason = "Reason was not provided or it exceeded the 500-character limit."

        role = await muterole(ctx)

        await member.add_roles(role,
                               reason=f"Muted by {ctx.author} ({ctx.author.id}) {f'for: {reason}' if reason else ''}"[
                                      0:500])

        await self.bot.db.execute("DELETE FROM temporary_mutes WHERE (guild_id, member_id) = ($1, $2)", ctx.guild.id,
                                     member.id)

        self.mute_task()

        if ctx.channel.permissions_for(role).send_messages_in_threads:
            try:
                embed = discord.Embed(title="Mute role has permissions to create threads!", description=f"""
    The mute role in your server (`{ctx.guild.name}`) has permissions to create threads!
    You may want to fix that using the `mute_role fix` command.
                    """, color=discord.Color.red())

                await ctx.author.send(embed=embed)

            except:
                pass

        embed = discord.Embed(description=f"Successfully muted `{member}` for `{reason}`", color=discord.Color.green())
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        return await ctx.send(embed=embed)

    @commands.command(
        help="Unmutes the specified member",
        aliases=['un_mute', 'un-mute'],
        brief="unmute @Jeff Good guy")
    @ensure_muterole()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def unmute(self, ctx: CustomContext, member: discord.Member, *, reason: str = None):
        if member.id == ctx.author.id:
            return await ctx.send("You can't un-mute yourself!")

        if member.id == self.bot.user.id:
            return await ctx.send("Noooo! Don't un-mute me :(")

        if member.id == ctx.guild.owner.id:
            return await ctx.send("You can't un-mute the owner of this server!")

        if member.guild_permissions.administrator:
            return await ctx.send("You can't un-mute that user since they have the administrator permission!")

        if isinstance(member, discord.Member):
            if member.top_role >= ctx.me.top_role:
                raise errors.Forbidden

        if reason is None or len(reason) > 500:
            reason = "Reason was not provided or it exceeded the 500-character limit."

        role = await muterole(ctx)

        await member.remove_roles(role,
                                  reason=f"Unmuted by {ctx.author} ({ctx.author.id}) {f'for {reason}' if reason else ''}"[
                                         0:500])

        await self.bot.db.execute("DELETE FROM temporary_mutes WHERE (guild_id, member_id) = ($1, $2)", ctx.guild.id,
                                     member.id)

        self.mute_task()

        embed = discord.Embed(description=f"Successfully un-muted `{member}` for `{reason}`",
                              color=discord.Color.green())
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        return await ctx.send(embed=embed)

    @commands.command(
        help="Temporary mutes the specified member for the specified duration.\nDuration must be a short time for example: 1h, 2d, 5m or a combination of those like 1h2d5m",
        aliases=['temp_mute', 'temp-mute', 'tmute'],
        brief="tempmute @Noob 5h\ntempmute @Cat 5m1s")
    @ensure_muterole()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def tempmute(self, ctx: CustomContext, member: discord.Member, *, duration: time_inputs.ShortTime):
        if member.id == ctx.author.id:
            return await ctx.send("You can't temp-mute yourself!")

        if member.id == self.bot.user.id:
            return await ctx.send("Noooo! Don't temp-mute me :(")

        if member.id == ctx.guild.owner.id:
            return await ctx.send("You can't temp-mute the owner of this server!")

        if member.guild_permissions.administrator:
            return await ctx.send("You can't temp-mute that user since they have the administrator permission!")

        if isinstance(member, discord.Member):
            if member.top_role >= ctx.me.top_role:
                raise errors.Forbidden

        role = await muterole(ctx)

        created_at = ctx.message.created_at
        if duration.dt < (created_at + datetime.timedelta(minutes=1)):
            return await ctx.send("You can't temp-mute someone for less than a minute!")

        if duration.dt > (created_at + datetime.timedelta(days=1)):
            return await ctx.send("You can't self-mute yourself for more than a day!")

        delta = helpers.human_timedelta(duration.dt, source=created_at)

        try:
            await member.add_roles(role, reason=f"Temporary mute by {ctx.author} ({ctx.author.id})")

        except discord.Forbidden:
            return await ctx.send(f"I don't seem to have permissions to add the `{role.name}` role")

        await self.bot.db.execute(
            "INSERT INTO temporary_mutes(guild_id, member_id, reason, end_time) VALUES ($1, $2, $3, $4) ON CONFLICT (guild_id, member_id) DO UPDATE SET reason = $3, end_time = $4",
            ctx.guild.id, member.id, f"Temporary mute by {ctx.author} ({ctx.author.id})", duration.dt)

        self.mute_task()

        embed = discord.Embed(description=f"Successfully temp-muted `{member}` for `{delta}`",
                              color=discord.Color.green())
        embed.set_footer(text=f"Executed by {ctx.author}", icon_url=ctx.author.avatar.url)

        return await ctx.send(embed=embed)

    @commands.command(
        help="Temporary mutes you for the specified duration.\nDuration must be a short time for example: 1h, 2d, 5m or a combination of those like 1h2d5m",
        aliases=['self_mute', 'self-mute', 'smute'],
        brief="selfmute 5h\nselfmute 5m1s")
    @ensure_muterole()
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def selfmute(self, ctx: CustomContext, *, duration: time_inputs.ShortTime):
        role = await muterole(ctx)

        created_at = ctx.message.created_at
        if duration.dt < (created_at + datetime.timedelta(minutes=1)):
            return await ctx.send("You can't self-mute yourself for less than a minute!")

        if duration.dt > (created_at + datetime.timedelta(days=1)):
            return await ctx.send("You can't self-mute yourself for more than a day!")

        delta = helpers.human_timedelta(duration.dt, source=created_at)

        try:
            await ctx.author.add_roles(role, reason=f"Self-mute")

        except discord.Forbidden:
            return await ctx.send(f"I don't seem to have permissions to add the `{role.name}` role")

        confirmation = await ctx.confirm(
            "Are you sure you want to do this?\n__**Do not ask moderators to undo this!**__")

        if not confirmation:
            return await ctx.send("Okay, I won't self-mute you then.")

        else:

            await self.bot.db.execute(
                "INSERT INTO temporary_mutes(guild_id, member_id, reason, end_time) VALUES ($1, $2, $3, $4) ON CONFLICT (guild_id, member_id) DO UPDATE SET reason = $3, end_time = $4",
                ctx.guild.id, ctx.author.id, f"Self-mute mute by {ctx.author} ({ctx.author.id})", duration.dt)

            self.mute_task()

            return await ctx.send("You've successfully been self-muted. Be sure to not bother anyone about it.")