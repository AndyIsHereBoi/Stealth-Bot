import difflib
import errors
import discord
import asyncio

from helpers.helpers import LoggingEventsFlags
from discord.ext import commands
from helpers.context import CustomContext


async def get_wh(channel: discord.TextChannel):
    if channel.permissions_for(channel.guild.me).manage_webhooks:
        webhooks = await channel.webhooks()
        for w in webhooks:
            if w.user == channel.guild.me:
                return w.url
        else:
            return (
                await channel.create_webhook(name='Stealth Bot Logging', avatar=await channel.guild.me.avatar.read())).url
    else:
        raise commands.BadArgument('Cannot create webhook!')


def setup(client):
    client.add_cog(GuildSettings(client))


class ValidEventConverter(commands.Converter):
    async def convert(self, ctx: CustomContext, argument: str):
        new = argument.replace('-', '_')
        all_events = dict(LoggingEventsFlags.all())
        if new in all_events:
            return new
        maybe_events = difflib.get_close_matches(argument, all_events)
        if maybe_events:
            c = await ctx.confirm(f'Did you mean... **`{maybe_events[0]}`**?', delete_after_confirm=True,
                                  delete_after_timeout=False,
                                  buttons=(
                                  ('☑', None, discord.ButtonStyle.blurple), ('🗑', None, discord.ButtonStyle.gray)))
            if c:
                return maybe_events[0]
            elif c is None:
                raise commands.BadArgument('Invalid event!')
        raise commands.BadArgument(f'`{argument[0:100]}` is not a valid logging event.')
    
    
class ChannelsView(discord.ui.View):
    def __init__(self, ctx: CustomContext):
        super().__init__()
        self.message: discord.Message = None
        self.ctx = ctx
        self.bot = ctx.bot
        self.lock = asyncio.Lock()
        self.valid_channels = ['default', 'message', 'member', 'join_leave', 'voice', 'server']

    @discord.ui.button(style=discord.ButtonStyle.gray, emoji='♾', row=0)
    async def default(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.lock.locked():
            return await interaction.response.defer()

        async with self.lock:
            button.style = discord.ButtonStyle.green
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(view=self)
            to_delete = []
            m = await self.ctx.send('Please send a channel to change the **Message Events Channel**')
            to_delete.append(m)

            def check(msg: discord.Message):
                if msg.channel == self.ctx.channel and msg.author == self.ctx.author:
                    to_delete.append(msg)
                    return True
                return False

            while True:
                message: discord.Message = await self.bot.wait_for('message', check=check)
                if message.content == 'cancel':
                    break
                else:
                    try:
                        channel = await commands.TextChannelConverter().convert(self.ctx, message.content)
                        break
                    except commands.ChannelNotFound:
                        pass

            await message.add_reaction('✅')
            channel_string = message.content
            if channel_string.lower() == 'cancel':
                pass
            else:
                try:
                    webhook_url = await get_wh(channel)
                    await self.bot.db.execute(
                        'UPDATE log_channels SET default_channel = $2, default_chid = $3 WHERE guild_id = $1',
                        self.ctx.guild.id, webhook_url, channel.id)
                    self.bot.update_log('default', webhook_url, message.guild.id)
                except commands.ChannelNotFound:
                    pass
                except (commands.BadArgument, discord.Forbidden):
                    await self.ctx.send('Could not create a webhook in that channel!\n'
                                        'Do i have **Manage Webhooks** permissions there?')
                except discord.HTTPException:
                    await self.ctx.send('Something went wrong while creating a webhook...')
            await self.update_message()
            try:
                await self.ctx.channel.delete_messages(to_delete)
            except:
                pass

    @discord.ui.button(style=discord.ButtonStyle.gray, emoji='📨', row=0)
    async def message(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.lock.locked():
            return await interaction.response.defer()

        async with self.lock:
            button.style = discord.ButtonStyle.green
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(view=self)
            to_delete = []
            m = await self.ctx.send('Please send a channel to change the **Message Events Channel**')
            to_delete.append(m)

            def check(message: discord.Message):
                if message.channel == self.ctx.channel and message.author == self.ctx.author:
                    to_delete.append(message)
                    return True
                return False

            while True:
                message: discord.Message = await self.bot.wait_for('message', check=check)
                if message.content == 'cancel':
                    break
                else:
                    try:
                        channel = await commands.TextChannelConverter().convert(self.ctx, message.content)
                        break
                    except commands.ChannelNotFound:
                        pass

            await message.add_reaction('✅')
            channel_string = message.content
            if channel_string.lower() == 'cancel':
                pass
            else:
                try:
                    webhook_url = await get_wh(channel)
                    await self.bot.db.execute(
                        'UPDATE log_channels SET message_channel = $2, message_chid = $3 WHERE guild_id = $1',
                        self.ctx.guild.id, webhook_url, channel.id)
                    self.bot.update_log('message', webhook_url, message.guild.id)
                except commands.ChannelNotFound:
                    pass
                except (commands.BadArgument, discord.Forbidden):
                    await self.ctx.send('Could not create a webhook in that channel!\n'
                                        'Do i have **Manage Webhooks** permissions there?')
                except discord.HTTPException:
                    await self.ctx.send('Something went wrong while creating a webhook...')
            await self.update_message()
            try:
                await self.ctx.channel.delete_messages(to_delete)
            except:
                pass

    @discord.ui.button(style=discord.ButtonStyle.gray, emoji='👋', row=1)
    async def join_leave(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.lock.locked():
            return await interaction.response.defer()

        async with self.lock:
            button.style = discord.ButtonStyle.green
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(view=self)
            to_delete = []
            m = await self.ctx.send('Please send a channel to change the **Join and Leave Events Channel**')
            to_delete.append(m)

            def check(message: discord.Message):
                if message.channel == self.ctx.channel and message.author == self.ctx.author:
                    to_delete.append(message)
                    return True
                return False

            while True:
                message: discord.Message = await self.bot.wait_for('message', check=check)
                if message.content == 'cancel':
                    break
                else:
                    try:
                        channel = await commands.TextChannelConverter().convert(self.ctx, message.content)
                        break
                    except commands.ChannelNotFound:
                        pass

            await message.add_reaction('✅')
            channel_string = message.content
            if channel_string.lower() == 'cancel':
                pass
            else:
                try:
                    webhook_url = await get_wh(channel)
                    await self.bot.db.execute(
                        'UPDATE log_channels SET join_leave_channel = $2, join_leave_chid = $3 WHERE guild_id = $1',
                        self.ctx.guild.id, webhook_url, channel.id)
                    self.bot.update_log('join_leave', webhook_url, message.guild.id)
                except commands.ChannelNotFound:
                    pass
                except (commands.BadArgument, discord.Forbidden):
                    await self.ctx.send('Could not create a webhook in that channel!\n'
                                        'Do i have **Manage Webhooks** permissions there?')
                except discord.HTTPException:
                    await self.ctx.send('Something went wrong while creating a webhook...')
            await self.update_message()
            try:
                await self.ctx.channel.delete_messages(to_delete)
            except:
                pass

    @discord.ui.button(style=discord.ButtonStyle.gray, emoji='👤', row=0)
    async def member(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.lock.locked():
            return await interaction.response.defer()

        async with self.lock:
            button.style = discord.ButtonStyle.green
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(view=self)
            to_delete = []
            m = await self.ctx.send(
                'Please send a channel to change the **Member Events Channel**\nSend "cancel" to cancel')
            to_delete.append(m)

            def check(message: discord.Message):
                if message.channel == self.ctx.channel and message.author == self.ctx.author:
                    to_delete.append(message)
                    return True
                return False

            while True:
                message: discord.Message = await self.bot.wait_for('message', check=check)
                if message.content == 'cancel':
                    break
                else:
                    try:
                        channel = await commands.TextChannelConverter().convert(self.ctx, message.content)
                        break
                    except commands.ChannelNotFound:
                        pass

            await message.add_reaction('✅')
            channel_string = message.content
            if channel_string.lower() == 'cancel':
                pass
            else:
                try:
                    webhook_url = await get_wh(channel)
                    await self.bot.db.execute(
                        'UPDATE log_channels SET member_channel = $2, member_chid = $3 WHERE guild_id = $1',
                        self.ctx.guild.id, webhook_url, channel.id)
                    self.bot.update_log('member', webhook_url, message.guild.id)
                except commands.ChannelNotFound:
                    pass
                except (commands.BadArgument, discord.Forbidden):
                    await self.ctx.send('Could not create a webhook in that channel!\n'
                                        'Do i have **Manage Webhooks** permissions there?')
                except discord.HTTPException:
                    await self.ctx.send('Something went wrong while creating a webhook...')
            await self.update_message()
            try:
                await self.ctx.channel.delete_messages(to_delete)
            except:
                pass

    @discord.ui.button(style=discord.ButtonStyle.gray, emoji='⚙', row=1)
    async def server(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.lock.locked():
            return await interaction.response.defer()

        async with self.lock:
            button.style = discord.ButtonStyle.green
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(view=self)
            to_delete = []
            m = await self.ctx.send('Please send a channel to change the **Server Events Channel**')
            to_delete.append(m)

            def check(message: discord.Message):
                if message.channel == self.ctx.channel and message.author == self.ctx.author:
                    to_delete.append(message)
                    return True
                return False

            while True:
                message: discord.Message = await self.bot.wait_for('message', check=check)
                if message.content == 'cancel':
                    break
                else:
                    try:
                        channel = await commands.TextChannelConverter().convert(self.ctx, message.content)
                        break
                    except commands.ChannelNotFound:
                        pass

            await message.add_reaction('✅')
            channel_string = message.content
            if channel_string.lower() == 'cancel':
                pass
            else:
                try:
                    webhook_url = await get_wh(channel)
                    await self.bot.db.execute(
                        'UPDATE log_channels SET server_channel = $2, server_chid = $3 WHERE guild_id = $1',
                        self.ctx.guild.id, webhook_url, channel.id)
                    self.bot.update_log('server', webhook_url, message.guild.id)
                except commands.ChannelNotFound:
                    pass
                except (commands.BadArgument, discord.Forbidden):
                    await self.ctx.send('Could not create a webhook in that channel!\n'
                                        'Do i have **Manage Webhooks** permissions there?')
                except discord.HTTPException:
                    await self.ctx.send('Something went wrong while creating a webhook...')
            await self.update_message()
            try:
                await self.ctx.channel.delete_messages(to_delete)
            except:
                pass

    @discord.ui.button(style=discord.ButtonStyle.gray, emoji='🎙', row=1)
    async def voice(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.lock.locked():
            return await interaction.response.defer()

        async with self.lock:
            button.style = discord.ButtonStyle.green
            for child in self.children:
                child.disabled = True
            await interaction.response.edit_message(view=self)
            to_delete = []
            m = await self.ctx.send('Please send a channel to change the **Voice Events Channel**'
                                    '\n_Send "cancel" to cancel_')
            to_delete.append(m)

            def check(message: discord.Message):
                if message.channel == self.ctx.channel and message.author == self.ctx.author:
                    to_delete.append(message)
                    return True
                return False

            while True:
                message: discord.Message = await self.bot.wait_for('message', check=check)
                if message.content == 'cancel':
                    break
                else:
                    try:
                        channel = await commands.TextChannelConverter().convert(self.ctx, message.content)
                        break
                    except commands.ChannelNotFound:
                        pass

            await message.add_reaction('✅')
            channel_string = message.content
            if channel_string.lower() == 'cancel':
                pass
            else:
                try:
                    webhook_url = await get_wh(channel)
                    await self.bot.db.execute(
                        'UPDATE log_channels SET voice_channel = $2, voice_chid = $3 WHERE guild_id = $1',
                        self.ctx.guild.id, webhook_url, channel.id)
                    self.bot.update_log('voice', webhook_url, message.guild.id)
                except commands.ChannelNotFound:
                    pass
                except (commands.BadArgument, discord.Forbidden):
                    await self.ctx.send('Could not create a webhook in that channel!\n'
                                        'Do i have **Manage Webhooks** permissions there?')
                except discord.HTTPException:
                    await self.ctx.send('Something went wrong while creating a webhook...')
            await self.update_message()
            try:
                await self.ctx.channel.delete_messages(to_delete)
            except:
                pass

    @discord.ui.button(style=discord.ButtonStyle.red, label='stop', row=2)
    async def stop_button(self, button: discord.ui.Button, interaction: discord.Interaction):
        if self.lock.locked():
            return await interaction.response.send_message('Can\'t do that while waiting for a message!',
                                                           ephemeral=True)
        await interaction.response.defer()
        await self.on_timeout()

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True
            child.style = discord.ButtonStyle.grey
        await self.message.edit(view=self)
        self.stop()

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user and interaction.user.id in (self.ctx.bot.owner_id, self.ctx.author.id):
            return True
        await interaction.response.send_message(f'This menu belongs to **{self.ctx.author}**, sorry! 💖',
                                                ephemeral=True)
        return False

    async def update_message(self, edit: bool = True):
        channels = await self.bot.db.fetchrow('SELECT * FROM log_channels WHERE guild_id = $1', self.ctx.guild.id)
        embed = discord.Embed(title='Logging Channels', colour=discord.Colour.blurple(),
                              timestamp=self.ctx.message.created_at)
        default = self.bot.get_channel(channels['default_chid'] or 1)
        message = self.bot.get_channel(channels['message_chid'] or 1)
        join_leave = self.bot.get_channel(channels['join_leave_chid'] or 1)
        member = self.bot.get_channel(channels['member_chid'] or 1)
        server = self.bot.get_channel(channels['server_chid'] or 1)
        voice = self.bot.get_channel(channels['voice_chid'] or 1)
        embed.description = f"**♾ Default channel:** {default.mention}" \
                            f"\n**📨 Message events:** {message.mention if message else ''}" \
                            f"\n**👋 Joining and Leaving:** {join_leave.mention if join_leave else ''}" \
                            f"\n**👤 Member events:** {member.mention if member else ''}" \
                            f"\n**⚙ Server events:** {server.mention if server else ''}" \
                            f"\n**🎙 Voice events:** {voice.mention if voice else ''}" \
                            f"\n" \
                            f"\n_Channels not shown here will be_" \
                            f"\n_delivered to the default channel._"
        loggings = self.bot.guild_loggings[self.ctx.guild.id]
        enabled = [x for x, y in set(loggings) if y is True]
        embed.set_footer(text=f'{len(enabled)}/{len(set(loggings))} events enabled.')
        for child in self.children:
            child.disabled = False
            if child.row < 2:
                child.style = discord.ButtonStyle.grey
            else:
                child.style = discord.ButtonStyle.red
        if edit:
            await self.message.edit(embed=embed, view=self)
        else:
            return await self.ctx.send(embed=embed, view=self)

    async def start(self):
        self.message = await self.update_message(edit=False)



class GuildSettings(commands.Cog, name="Guild settings"):
    """Commands for managing guild settings like logging system, welcome system etc."""

    def __init__(self, client):
        self.bot = client
        self.select_emoji = "<:gear:899622456191483904>"
        self.select_brief = "Commands for managing guild settings."

    def make_ordinal(self, n):
        n = int(n)
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        if 11 <= (n % 100) <= 13:
            suffix = 'th'

        return str(n) + suffix

    # Logging commands

    @commands.group(aliases=['logging', 'logger'])
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def log(self, ctx: CustomContext):
        """Base command to manage the logging events.
        Run this command without sub-commands to show more detailed information on the logging module"""
        if ctx.invoked_subcommand is None:
            embed = discord.Embed(title='Stealth Bot Logging Module', colour=discord.Colour.yellow(),
                                  description='**What is this?**\n'
                                              'The Logging module is a fully customizable logger for different server events. '
                                              'It can be configured to log up to 30 unique events, and for those events to be '
                                              'delivered into 5 different channels.\n'
                                              '**Available commands:**\n'
                                              f'\n`{ctx.clean_prefix}log enable <channel>` Enables logging for this server.'
                                              f'\n`{ctx.clean_prefix}log disable` Disables logging for this server.'
                                              f'\n`{ctx.clean_prefix}log channels` Shows the current channel settings.'
                                              f'\n`{ctx.clean_prefix}log edit-channels` Modifies the log channels (interactive menu).'
                                              f'\n`{ctx.clean_prefix}log all-events` Shows all events, disabled and enabled.'
                                              f'\n`{ctx.clean_prefix}log enable-event <event>` Enables a specific event from the list.'
                                              f'\n`{ctx.clean_prefix}log disable-event <event>` Disables a specific event from the list.'
                                              f'\n`{ctx.clean_prefix}log auto-setup` Creates a logging category with different channels.'
                                              f'\n'
                                              f'\nFor more info on a specific command, run the `help` command with it, E.G:'
                                              f'\n`db.help log enable-event`')
            await ctx.send(embed=embed)

    @log.command(name='enable', aliases=['set-default'], preview='https://i.imgur.com/SYOrcfG.gif')
    @commands.has_permissions(manage_guild=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def log_enable(self, ctx: CustomContext, channel: discord.TextChannel):
        """Enables the logging module to deliver to one channel.
        If logging is already enabled, it will set the default logging channel to the one specified.
        _Note: This will not modify your enabled/disabled events, if any._"""
        if ctx.guild.id in self.bot.log_channels:
            raise commands.BadArgument('This server already has a logging enabled.')
        if not channel.permissions_for(ctx.me).manage_webhooks and not channel.permissions_for(ctx.me).send_messages:
            raise commands.BadArgument(f"I'm missing the Manage Webhooks permission in {channel.mention}")
        await ctx.trigger_typing()

        try:
            webhooks = await channel.webhooks()
        except (discord.Forbidden, discord.HTTPException):
            raise commands.BadArgument(
                f'I was unable to get the list of webhooks in {channel.mention}. (Missing Permissions - Manage Webhooks)')
        for w in webhooks:
            if w.user == self.bot.user:
                webhook_url = w.url
                break
        else:
            if len(webhooks) == 10:
                raise commands.BadArgument(f'{channel.mention} has already the max number of webhooks! (10 webhooks)')
            try:
                w = await channel.create_webhook(name='Stealth Bot logging', avatar=await ctx.me.avatar.read(),
                                                 reason='Stealth Bot logging')
                webhook_url = w.url
            except discord.Forbidden:
                raise commands.BadArgument(
                    f'I couldn\'t create a webhook in {channel.mention}(Missing Permissions - Manage Webhooks)')
            except discord.HTTPException:
                raise commands.BadArgument(
                    f'There was an unexpected error while creating a webhook in {channel.mention} (HTTP exception) - Perhaps try again?')
        await self.bot.db.execute('INSERT INTO guilds (guild_id) VALUES ($1) '
                                  'ON CONFLICT (guild_id) DO NOTHING', ctx.guild.id)
        await self.bot.db.execute(
            "INSERT INTO log_channels(guild_id, default_channel, default_chid) VALUES ($1, $2, $3) "
            "ON CONFLICT (guild_id) DO UPDATE SET default_channel = $2, default_chid = $3",
            ctx.guild.id, webhook_url, channel.id)
        await self.bot.db.execute("INSERT INTO logging_events(guild_id) VALUES ($1) ON CONFLICT (guild_id) DO NOTHING",
                                  ctx.guild.id)
        self.bot.guild_loggings[ctx.guild.id] = LoggingEventsFlags.all()
        try:
            self.bot.log_channels[ctx.guild.id]._replace(default=webhook_url)
        except KeyError:
            self.bot.log_channels[ctx.guild.id] = self.bot.log_webhooks(default=webhook_url, voice=None, message=None,
                                                                        member=None, server=None, join_leave=None)
        await ctx.send(f'Successfully set the logging channel to {channel.mention}'
                       f'\n_see `{ctx.clean_prefix}help log` for more customization commands!_')

    @log.command(name='disable', aliases=['disable-logging'])
    @commands.has_permissions(manage_guild=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def log_disable(self, ctx: CustomContext):
        """Disables logging for this server, and deletes all the bots logging webhooks."""
        if ctx.guild.id not in self.bot.log_channels:
            raise commands.BadArgument('Logging is not enabled for this server!')
        confirm = await ctx.confirm('**Are you sure you want to disable logging?**'
                                    '\nThis will overwrite and disable **all** delivery channels, and delete all my webhooks.',
                                    delete_after_confirm=True, delete_after_timeout=False)
        if not confirm:
            return
        async with ctx.typing():
            try:
                self.bot.log_channels.pop(ctx.guild.id)
            except KeyError:
                pass
            channels = await self.bot.db.fetchrow('DELETE FROM log_channels WHERE guild_id = $1 RETURNING *',
                                                  ctx.guild.id)

            channel_ids = channels['default_chid'], channels['message_chid'], channels['join_leave_chid'], channels[
                'member_chid'], channels['voice_chid'], channels['server_chid']
            failed = 0
            success = 0
            for channel in channel_ids:
                channel = self.bot.get_channel(channel)
                if isinstance(channel, discord.TextChannel):
                    try:
                        webhooks = await channel.webhooks()
                        for webhook in webhooks:
                            if webhook.user == ctx.me:
                                await webhook.delete()
                                success += 1
                    except (discord.Forbidden, discord.HTTPException, discord.NotFound):
                        failed += 1
            await ctx.send('✅ **Successfully unset all logging channels!**'
                           f'\n_Deleted {success} webhooks. {failed} failed to delete._')

    @log.command(name='channels')
    @commands.has_permissions(manage_guild=True)
    async def log_channels(self, ctx: CustomContext):
        """Shows this server's logging channels"""
        if ctx.guild.id not in self.bot.log_channels:
            raise commands.BadArgument('This server doesn\'t have logging enabled.')
        channels = await self.bot.db.fetchrow('SELECT * FROM log_channels WHERE guild_id = $1', ctx.guild.id)
        embed = discord.Embed(title='Logging Channels', colour=discord.Colour.blurple(),
                              timestamp=discord.utils.utcnow())
        default = self.bot.get_channel(channels['default_chid'] or 1)
        message = self.bot.get_channel(channels['message_chid'] or 1)
        join_leave = self.bot.get_channel(channels['join_leave_chid'] or 1)
        member = self.bot.get_channel(channels['member_chid'] or 1)
        server = self.bot.get_channel(channels['server_chid'] or 1)
        voice = self.bot.get_channel(channels['voice_chid'] or 1)
        embed.description = f"**Default channel:** {default.mention}" \
                            f"\n**Message events:** {message.mention if message else ''}" \
                            f"\n**Joining and Leaving:** {join_leave.mention if join_leave else ''}" \
                            f"\n**Member events:** {member.mention if member else ''}" \
                            f"\n**Server events:** {server.mention if server else ''}" \
                            f"\n**Voice events:** {voice.mention if voice else ''}" \
                            f"\n" \
                            f"\n_Channels not shown here will be_" \
                            f"\n_delivered to the default channel._"
        loggings = self.bot.guild_loggings[ctx.guild.id]
        enabled = [x for x, y in set(loggings) if y is True]
        embed.set_footer(text=f'{len(enabled)}/{len(set(loggings))} events enabled.')
        await ctx.send(embed=embed)

    @log.command(name='disable-event', aliases=['disable_event', 'de'])
    @commands.has_permissions(manage_guild=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def log_disable_event(self, ctx, *, event: ValidEventConverter):
        """**Disables a logging event, which can be one of the following:**
        `message_delete`, `message_purge`, `message_edit`, `member_join`, `member_leave`, `member_update`, `user_ban`, `user_unban`, `user_update`, `invite_create`, `invite_delete`, `voice_join`, `voice_leave`, `voice_move`, `voice_mod`, `emoji_create`, `emoji_delete`, `emoji_update`, `sticker_create`, `sticker_delete`, `sticker_update`, `server_update`, `stage_open`, `stage_close`, `channel_create`, `channel_delete`, `channel_edit`, `role_create`, `role_delete`, `role_edit`
        You can either use underscore `_` or dash `-` when specifying the event.
        _Note that the command will attempt to auto-complete to the closest match, if not specified._
        """
        if ctx.guild.id not in self.bot.log_channels:
            raise commands.BadArgument('This server doesn\'t have logging enabled.')
        arg = getattr(self.bot.guild_loggings[ctx.guild.id], event, None)
        if arg is False:
            raise commands.BadArgument(
                f'❌ **|** **{str(event).replace("_", " ").title()} Events** are already disabled!')
        await self.bot.db.execute(f'UPDATE logging_events SET {event} = $2 WHERE guild_id = $1',
                                  ctx.guild.id, False)
        setattr(self.bot.guild_loggings[ctx.guild.id], event, False)
        await ctx.send(f'✅ **|** Successfully disabled **{str(event).replace("_", " ").title()} Events**')

    @log.command(name='enable-event', aliases=['enable_event', 'ee'])
    @commands.has_permissions(manage_guild=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def log_enable_event(self, ctx: CustomContext, *, event: ValidEventConverter):
        """**Enables a logging event, which can be one of the following:**
        `message_delete`, `message_purge`, `message_edit`, `member_join`, `member_leave`, `member_update`, `user_ban`, `user_unban`, `user_update`, `invite_create`, `invite_delete`, `voice_join`, `voice_leave`, `voice_move`, `voice_mod`, `emoji_create`, `emoji_delete`, `emoji_update`, `sticker_create`, `sticker_delete`, `sticker_update`, `server_update`, `stage_open`, `stage_close`, `channel_create`, `channel_delete`, `channel_edit`, `role_create`, `role_delete`, `role_edit`
        You can either use underscore `_` or dash `-` when specifying the event.
        _Note that the command will attempt to auto-complete to the closest match, if not specified._
        """
        if ctx.guild.id not in self.bot.log_channels:
            raise commands.BadArgument('This server doesn\'t have logging enabled.')
        arg = getattr(self.bot.guild_loggings[ctx.guild.id], event, None)
        if arg is True:
            raise commands.BadArgument(
                f'❌ **|** **{str(event).replace("_", " ").title()} Events** are already enabled!')
        await self.bot.db.execute(f'UPDATE logging_events SET {event} = $2 WHERE guild_id = $1',
                                  ctx.guild.id, True)
        setattr(self.bot.guild_loggings[ctx.guild.id], event, True)
        await ctx.send(f'✅ **|** Successfully enabled **{str(event).replace("_", " ").title()} Events**')

    @log.command(name='edit-channels', aliases=['edit_channels', 'ec'], preview='https://i.imgur.com/FO9e9VC.gif')
    @commands.has_permissions(manage_guild=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    async def log_edit_channels(self, ctx):
        """Shows an interactive menu to modify the server's logging channels."""
        if ctx.guild.id not in self.bot.log_channels:
            raise commands.BadArgument('This server doesn\'t have logging enabled.')
        view = ChannelsView(ctx)
        await view.start()
        await view.wait()

    @log.command(name='all-events')
    @commands.has_permissions(manage_guild=True)
    async def log_all_events(self, ctx: CustomContext):
        if ctx.guild.id not in self.bot.log_channels:
            raise commands.BadArgument('This server doesn\'t have logging enabled.')
        await ctx.trigger_typing()
        events = self.bot.guild_loggings[ctx.guild.id]
        embed = discord.Embed(title='Logging events for this server', colour=discord.Colour.blurple(),
                              timestamp=ctx.message.created_at)
        message_events = [ctx.tick(events.message_delete, 'Message Delete'),
                          ctx.tick(events.message_edit, 'Message Edit'),
                          ctx.tick(events.message_purge, 'Message Purge')]
        embed.add_field(name='Message Events', value='\n'.join(message_events))
        join_leave_events = [ctx.tick(events.member_join, 'Member Join'),
                             ctx.tick(events.member_leave, 'Member Leave')]
        subtract = 0
        if not ctx.me.guild_permissions.manage_channels:
            if events.invite_create:
                join_leave_events.append('⚠ Invite Create'
                                         '\n╰ Manage Channels')
                subtract += 1
            else:
                join_leave_events.append(ctx.tick(events.invite_create, 'Invite Create'))
            if events.invite_delete:
                join_leave_events.append('⚠ Invite Delete'
                                         '\n╰ Manage Channels')
                subtract += 1
            else:
                join_leave_events.append(ctx.tick(events.invite_delete, 'Invite Create'))
        else:
            join_leave_events.append(ctx.tick(events.invite_create, 'Invite Create'))
            join_leave_events.append(ctx.tick(events.invite_delete, 'Invite Delete'))
        embed.add_field(name='Join Leave Events', value='\n'.join(join_leave_events))
        member_update_evetns = [ctx.tick(events.member_update, 'Member Update'),
                                ctx.tick(events.user_update, 'User Update'),
                                ctx.tick(events.user_ban, 'User Ban'),
                                ctx.tick(events.user_unban, 'User Unban')]
        embed.add_field(name='Member Events', value='\n'.join(member_update_evetns))
        voice_events = [ctx.tick(events.voice_join, 'Voice Join'),
                        ctx.tick(events.voice_leave, 'Voice Leave'),
                        ctx.tick(events.voice_move, 'Voice Move'),
                        ctx.tick(events.voice_mod, 'Voice Mod'),
                        ctx.tick(events.stage_open, 'Stage Open'),
                        ctx.tick(events.stage_close, 'Stage Close')]
        embed.add_field(name='Voice Events', value='\n'.join(voice_events))
        server_events = [ctx.tick(events.channel_create, 'Channel Create'),
                         ctx.tick(events.channel_delete, 'Channel Delete'),
                         ctx.tick(events.channel_edit, 'Channel Edit'),
                         ctx.tick(events.role_create, 'Role Create'),
                         ctx.tick(events.role_delete, 'Role Delete'),
                         ctx.tick(events.role_edit, 'Role Edit'),
                         ctx.tick(events.server_update, 'Server Update'),
                         ctx.tick(events.emoji_create, 'Emoji Create'),
                         ctx.tick(events.emoji_delete, 'Emoji Delete'),
                         ctx.tick(events.emoji_update, 'Emoji Update'),
                         ctx.tick(events.sticker_create, 'Sticker Create'),
                         ctx.tick(events.sticker_delete, 'Sticker Delete'),
                         ctx.tick(events.sticker_update, 'Sticker Update')]
        embed.add_field(name='Server Events', value='\n'.join(server_events))
        embed.description = '✅ Enabled • ❌ Disabled • ⚠ Missing Perms'
        enabled = [x for x, y in set(events) if y is True]
        amount_enabled = len(enabled) - subtract
        embed.set_footer(text=f'{amount_enabled}/{len(set(events))} events enabled.')
        await ctx.send(embed=embed)

    @log.command(name='auto-setup')
    @commands.has_permissions(administrator=True)
    @commands.max_concurrency(1, commands.BucketType.guild)
    @commands.bot_has_guild_permissions(manage_channels=True, manage_webhooks=True)
    async def log_auto_setup(self, ctx: CustomContext):
        """Creates a Logging category, with channels for each event to be delivered.
        The channels would be the following (inside a logging category):
        `#join-leave-log`
        `#message-log`
        `#voice-log`
        `#member-log`
        `#server-log`
        """
        if ctx.guild in self.bot.log_channels:
            raise commands.BadArgument('This server already has Logging Set up!')
        c = await ctx.confirm('**Do you want to proceed?**'
                              '\nThis command will set up logging for you,'
                              '\nBy creating the followinc category:'
                              '\n'
                              f'\n`#logging` (category)'
                              f'\n- `#join-leave-log`'
                              f'\n- `#message-log`'
                              f'\n- `#voice-log`'
                              f'\n- `#member-log`',
                              delete_after_timeout=False, delete_after_cancel=False, delete_after_confirm=True)
        if not c:
            return
        async with ctx.typing():
            try:
                over = {ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
                        ctx.me: discord.PermissionOverwrite(read_messages=True, send_messages=True,
                                                            manage_channels=True, manage_webhooks=True)}
                avatar = await ctx.me.avatar.read()
                cat = await ctx.guild.create_category(name='logging', overwrites=over)
                join_leave_channel = await cat.create_text_channel(name='join-leave-log')
                join_leave_webhook = await join_leave_channel.create_webhook(name='Stealth Bot logging', avatar=avatar)
                message_channel = await cat.create_text_channel(name='message-log')
                message_webhook = await message_channel.create_webhook(name='Stealth Bot logging', avatar=avatar)
                voice_channel = await cat.create_text_channel(name='voice-log')
                voice_webhook = await voice_channel.create_webhook(name='Stealth Bot logging', avatar=avatar)
                member_channel = await cat.create_text_channel(name='member-log')
                member_webhook = await member_channel.create_webhook(name='Stealth Bot logging', avatar=avatar)
                server_channel = await cat.create_text_channel(name='server-log')
                server_webhook = await server_channel.create_webhook(name='Stealth Bot logging', avatar=avatar)
                self.bot.log_channels[ctx.guild.id] = self.bot.log_webhooks(join_leave=join_leave_webhook.url,
                                                                            server=server_webhook.url,
                                                                            default=server_webhook.url,
                                                                            message=message_webhook.url,
                                                                            member=member_webhook.url,
                                                                            voice=voice_webhook.url)
                self.bot.guild_loggings[ctx.guild.id] = LoggingEventsFlags.all()
                await self.bot.db.execute('INSERT INTO guilds (guild_id) VALUES ($1) '
                                          'ON CONFLICT (guild_id) DO NOTHING', ctx.guild.id)
                await self.bot.db.execute("""
                INSERT INTO log_channels(guild_id, default_channel, default_chid, message_channel, message_chid, 
                                         join_leave_channel, join_leave_chid, member_channel, member_chid,
                                         voice_channel, voice_chid, server_channel, server_chid) 
                                         VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                                    ON CONFLICT (guild_id) DO UPDATE SET
                                        default_channel = $2,
                                        default_chid = $3,
                                        message_channel = $4,
                                        message_chid = $5,
                                        join_leave_channel = $6,
                                        join_leave_chid = $7,
                                        member_channel = $8,
                                        member_chid = $9,
                                        voice_channel = $10,
                                        voice_chid = $11,
                                        server_channel = $12,
                                        server_chid = $13; """,
                                          ctx.guild.id, server_webhook.url, server_channel.id,
                                          message_webhook.url, message_channel.id,
                                          join_leave_webhook.url, join_leave_channel.id,
                                          member_webhook.url, member_channel.id,
                                          voice_webhook.url, voice_channel.id,
                                          server_webhook.url, server_channel.id)
                await self.bot.db.execute('INSERT INTO logging_events(guild_id) VALUES ($1)'
                                          'ON CONFLICT (guild_id) DO NOTHING', ctx.guild.id)
                try:
                    embed = discord.Embed(title='Successfully set up!', colour=discord.Colour.blurple(),
                                          description=f"{join_leave_channel.mention}"
                                                      f"\n{message_channel.mention}"
                                                      f"\n{voice_channel.mention}"
                                                      f"\n{server_channel.mention}")
                    await ctx.send(embed=embed, mention_author=True)
                except (discord.Forbidden, discord.HTTPException):
                    pass
            except discord.Forbidden:
                await ctx.send('For some reason, I didn\'t have the necessary permissions to do that.'
                               '\nTry assigning me a role with `Administrator` permissions')
            except discord.HTTPException:
                await ctx.send('Something went wrong, ups!')
    # Welcome commands

    @commands.group(
        invoke_without_command=True,
        help=":wave: | Welcome commands. If no argument is specified it will show you the current welcome channel.")
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def welcome(self, ctx):
        database = await self.bot.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", ctx.guild.id)

        if not database['welcome_channel_id']:
            message = f"This server doesn't have a welcome channel set-up.\nTo set it up do `{ctx.prefix}welcome enable <channel>`"

        else:
            channel = self.bot.get_channel(database['welcome_channel_id'])
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
        name="enable",
        help="Changes the welcome channel to the specified channel. If no channel is specified it will default to the current one.",
        aliases=['set', 'add'])
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def welcome_enable(self, ctx, channel: discord.TextChannel = None):
        if not channel:
            channel = ctx.channel

        await self.bot.db.execute("INSERT INTO guilds (guild_id, welcome_channel_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET welcome_channel_id = $2", ctx.guild.id, channel.id)

        embed = discord.Embed(title="Welcome channel updated", description=f"""
The welcome channel for this server has been set to {channel.mention}!
Now you will be notified when a user joins or leaves the server in that channel.
If you would like to set a custom welcome message do `{ctx.prefix}welcome message <message>`.
                            """, color=discord.Color.green())

        await ctx.send(embed=embed, color=False)

    @welcome.command(
        name="disable",
        help="Disables the welcome module for the current server.",
        aliases=['remove', 'delete'])
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def welcome_disable(self, ctx):
        await self.bot.db.execute("INSERT INTO guilds (guild_id, welcome_channel_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET welcome_channel_id = $2", ctx.guild.id, None)
        await self.bot.db.execute("INSERT INTO guilds (guild_id, welcome_message) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET welcome_message = $2", ctx.guild.id, None)

        embed = discord.Embed(title="Welcome module disabled", description=f"""
The welcome module has been disabled for this server.
You will no longer be notified when a user joins or leaves the server.
I've also deleted the welcome message for this server.
                              """, color=discord.Color.red())

        await ctx.send(embed=embed, color=False)

    @welcome.command(
        name="message",
        help="""
Changes the welcome message to the specified message.
You can also use all of these placeholders:
To use placeholders, surround them with `[]`. (e.g. `[server]`)

`server` - The server's name (e.g. My Server)
`user` - The user's name (e.g. John)
`full-user` - The user's name and discriminator (e.g. John#1234)
`user-mention` - The user's mention (e.g. <@123456789>)
`count` - The number of members in the server (e.g. 2)
`ordinal-count` - The number of members in the server, but ordinal (e.g. 3rd)
`code` - The invite code (e.g. 1234567890)
`full-code` - The full invite code (e.g. discord.gg/123456789)
`full-url` - The full invite url (e.g. https://discord.gg/123456789)
`inviter` - The inviter's name (e.g. John)
`full-inviter` - The inviter's name and discriminator (e.g. John#1234)
`inviter-mention` - The inviter's mention (e.g. <@123456789>)
""",
        brief="sb!welcome message Welcome to **[server]**, [user-mention]\nsb!welcome message Welcome, [full-user]\nsb!welcome message [user] is the [ordinal-count] to join!",
        aliases=['msg', 'messages'])
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def welcome_message(self, ctx, *, message):
        database = await self.bot.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", ctx.guild.id)

        if not database['welcome_channel_id']:
            return await ctx.send(
                f"You need to set-up a welcome channel first!\nTo do that do `{ctx.prefix}welcome enable <channel>`")

        if len(message) > 500:
            return await ctx.send(f"Your message exceeded the 500-character limit!")

        await self.bot.db.execute("INSERT INTO guilds (guild_id, welcome_message) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET welcome_message = $2", ctx.guild.id, message)

        embed = discord.Embed(title="Welcome message updated", description=f"""
The welcome message for this server has been set to: {message}
To disable the welcome module do `{ctx.prefix}welcome disable`
                            """, color=discord.Color.green())

        await ctx.send(embed=embed, color=False)

    @welcome.command(
        help="Sends a fake welcome message.",
        aliases=['fake', 'fake-msg', 'fake-message'])
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def fake_message(self, ctx):
        database = await self.bot.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", ctx.guild.id)

        if not database['welcome_channel_id']:
            return await ctx.send(f"You need to set-up a welcome channel first!\nTo do that do `{ctx.prefix}welcome enable <channel>`")

        if not database['welcome_message']:
            message = f"Welcome to **[server]**, **[full-user]**!"

        else:
            message = database['welcome_message']

        message = message.replace("[server]", f"{ctx.guild.name}")
        message = message.replace("[user]", f"{ctx.author.display_name}").replace("[full-user]", f"{ctx.author}").replace("[user-mention]", f"{ctx.author.mention}")
        message = message.replace("[count]", f"{ctx.guild.member_count}").replace("[ordinal-count]", f"{self.make_ordinal(ctx.guild.member_count)}")
        message = message.replace("[code]", f"123456789").replace("[full-code]", f"discord.gg/123456789").replace("[full-url]", f"https://discord.gg/123456789").replace("[inviter]", f"John").replace("[full-inviter]", f"John#1234").replace("[inviter-mention]", f"@John")

        await ctx.send(message)

    # Mute commands

    @commands.group(
        invoke_without_command=True,
        help="Changes the mute-role for the server. If no role is specified it will show the current mute-role.",
        aliases=['mute-role', 'mute_role'])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def muterole(self, ctx: CustomContext, role: discord.Role = None):
        if ctx.invoked_subcommand is None:
            if role:
                await self.bot.db.execute("INSERT INTO guilds(guild_id, muted_role_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET muted_role_id = $2", ctx.guild.id, role.id)

                embed = discord.Embed(title="Mute role updated", description=f"The mute-role for this server has been changed to {role.mention}", color=discord.Color.green())

                return await ctx.send(embed=embed, color=False)

            mute_role = await self.bot.db.fetchval("SELECT muted_role_id FROM guilds WHERE guild_id = $1", ctx.guild.id)

            if not mute_role:
                raise errors.MuteRoleNotFound

            role = ctx.guild.get_role(int(mute_role))
            if not isinstance(role, discord.Role):
                raise errors.MuteRoleNotFound

            embed = discord.Embed(ittle="Mute role", description=f"""
The mute-role for this server is: {role.mention}
To change the mute-role do `{ctx.prefix}mute-role <role>`.
And to remove it, do `{ctx.prefix}mute-role remove`.
            """, color=discord.Color.green())

            return await ctx.send(embed=embed, color=False)

    @muterole.command(
        name="remove",
        help="Removes the mute-role for the server.\nNote that this will not delete the role from the server. It'll only remove it from the bot's database.\nIf you want to delete it, do it manually.",
        aliases=['unset'])
    @commands.has_permissions(manage_roles=True)
    @commands.bot_has_permissions(manage_roles=True)
    async def muterole_remove(self, ctx: CustomContext):
        await self.bot.db.execute("INSERT INTO guilds(guild_id, muted_role_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET muted_role_id = $2", ctx.guild.id, None)

        embed = discord.Embed(title="Mute role removed", description="The mute-role for this server has been removed.", color=discord.Color.green())

        return await ctx.send(embed=embed)

    @muterole.command(
        name="create",
        help="Creates a new mute-role for the server.\nThis will make a new role called `Muted` and setup all permissions for it in all channels.",
        aliases=[])
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def muterole_create(self, ctx: CustomContext):
        mute_role = await self.bot.db.fetchval("SELECT muted_role_id FROM guilds WHERE guild_id = $1", ctx.guild.id)

        if mute_role:
            mute_role = ctx.guild.get_role(mute_role)
            if mute_role:
                return await ctx.send(f"This server already has a mute role! It's {mute_role.mention}")

        embed = discord.Embed(title="<a:Loading:936549536770457620> Creating mute role...", description=f"This might take a while. ETA: {len(ctx.guild.channels)} seconds", color=discord.Color.yellow())
        await ctx.send(embed=embed, color=False)

        await ctx.trigger_typing()
        permissions = discord.Permissions(send_messages=False,
                                          add_reactions=False,
                                          connect=False,
                                          speak=False)

        role = await ctx.guild.create_role(name="Muted", permissions=permissions, reason=f"Mute role created by {ctx.author} ({ctx.author.id})")

        await self.bot.db.execute("INSERT INTO guilds(guild_id, muted_role_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET muted_role_id = $2", ctx.guild.id, role.id)

        modified = 0
        for channel in ctx.guild.channels:
            perms = channel.overwrites_for(role)
            perms.update(send_messages=None,
                         add_reactions=None,
                         create_public_threads=None,
                         create_private_threads=None)

            try:
                await channel.set_permissions(role, overwrite=perms, reason=f"Mute role creation by {ctx.author} ({ctx.author.id})")
                modified += 1

            except (discord.Forbidden, discord.HTTPException):
                continue

            await asyncio.sleep(0.5)

        embed = discord.Embed(title="Mute role created", description=f"The mute-role has been created.\n{modified} channel(s) have been modified.", color=discord.Color.green())

        await ctx.send(embed=embed, color=False)

    @muterole.command(
        name="fix",
        help="Fixes the mute role permissions for all channels in the server.")
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def muterole_fix(self, ctx: CustomContext):
        await ctx.trigger_typing()
        mute_role = await self.bot.db.fetchval('SELECT muted_role_id FROM guilds WHERE guild_id = $1', ctx.guild.id)

        if not mute_role:
            raise errors.MuteRoleNotFound

        role = ctx.guild.get_role(int(mute_role))

        if not isinstance(role, discord.Role):
            raise errors.MuteRoleNotFound

        confirm = await ctx.confirm(f"Are you sure, you want to change the permissions of {role.mention} in all channels?")
        if not confirm:
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
                         send_messages_in_threads=False)

            try:
                await channel.set_permissions(role, overwrite=perms, reason=f"Mute role fix by {ctx.author} ({ctx.author.id})")
                modified += 1

            except (discord.Forbidden, discord.HTTPException):
                continue

            await asyncio.sleep(1)

        embed = discord.Embed(title="Mute role fixed", description=f"Changed permissions for {modified} channel(s)")

        await ctx.send(embed=embed)

    # Verify commands

    @commands.group(
        invoke_without_command=True,
        help="<:greenTick:895688440690147370> | Verify commands. If no argument is specified it will show you the current verify role.",
        aliases=['verify_role', 'verify-role', 'vr'])
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def verifyrole(self, ctx: CustomContext):
        role = await self.bot.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", ctx.guild.id)

        if not role['verify_role_id']:
            return await ctx.send(f"This server doesn't have a verify role. To set it do `{ctx.prefix}verifyrole set <role>`")

        else:
            role = ctx.guild.get_role(role['verify_role_id'])
            return await ctx.send(f"The current verify role for this server is {role.mention}.")

    @verifyrole.command(
        name="set",
        help="Changes the verify role to the specified role.")
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def _set(self, ctx: CustomContext, role: discord.Role):
        await self.bot.db.execute("INSERT INTO guilds (guild_id, verify_role_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET verify_role_id = $2", ctx.guild.id, role.id)
        await ctx.send(f"Successfully set the verify role for this server to {role.mention}.")

    @verifyrole.command(
        help="Removes the verify role")
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def remove(self, ctx: CustomContext):
        await self.bot.db.execute("INSERT INTO guilds (guild_id, verify_role_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET verify_role_id = $2", ctx.guild.id, None)
        await ctx.send(f"Successfully removed the verify role for this server.")