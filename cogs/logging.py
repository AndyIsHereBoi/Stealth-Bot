import discord

from discord.ext import commands

def setup(client):
    client.add_cog(Logging(client))
    
class Logging(commands.Cog):
    "Commands used to control the logging system."
    def __init__(self, client):
        self.client = client
        self.select_emoji = "<:hypesquad:895688440610422900>"
        self.select_brief = "Commands used to control the logging system."

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
    async def enable(self, ctx, channel : discord.TextChannel=None):
        if channel is None:
            channel = ctx.channel

        await self.client.db.execute("INSERT INTO guilds (guild_id, logs_channel_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET logs_channel_id = $2", ctx.guild.id, channel.id)
        
        embed = discord.Embed(title="Logs channel updated", description=f"The logs channel for this server has been set to {channel.mention}!", color=discord.Color.green())
        await ctx.send(embed=embed, color=False)

    @log.command(
        help="Disables the logging module for the current server.",
        aliases=['remove'])
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def disable(self, ctx):
        await self.client.db.execute("INSERT INTO guilds (guild_id, logs_channel_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET logs_channel_id = $2", ctx.guild.id, None)
        
        embed = discord.Embed(title="Logging module disabled", description=f"The logging module for this server has been disabled!", color=discord.Color.red())
        await ctx.send(embed=embed, color=False)
        
    ##################################################################################################################################################################
    ##################################################################################################################################################################
    ##################################################################################################################################################################
    ##################################################################################################################################################################

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", message.guild.id)
        try:

            if not database['logs_channel_id']:
                return
            
            else:
                embed = discord.Embed(title=f"Message deleted in #{message.channel.name}", description=f"{message.content[0:4000] if message.content else '*No content*'}", color=discord.Color.red())
                embed.set_author(name=f"{message.author}", icon_url=f"{message.author.display_avatar.url}")
                
                if message.attachments: # if the message has attachments (images, files etc)
                    embed.add_field(name=f"Attachments", value="\n".join([attachment.filename for attachment in message.attachments]), inline=False)
                    
                if message.stickers: # if the message has stickers
                    embed.add_field(name=f"Stickers", value="\n".join([sticker.name for sticker in message.stickers]), inline=False)
                    
                channel = self.client.get_channel(database['logs_channel_id'])
                await channel.send(embed=embed)
                
        except TypeError: #if  no records found for that guild
            pass
        except KeyError: # records exist but not set up a logging channel
            pass


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", before.guild.id)
        try:

            if not database['logs_channel_id']:
                return
            
            else:
                embed = discord.Embed(title=f"Message edited in #{before.channel.name}", url=after.jump_url, color=discord.Color.blurple())
                embed.set_author(name=f"{before.author}", icon_url=f"{before.author.display_avatar.url}")
                embed.add_field(name=f"Before", value=f"{before.content[0:1000] if before.content else '*No content*'}", inline=False)
                embed.add_field(name=f"After", value=f"{after.content[0:1000] if after.content else '*No content*'}", inline=False)
                
                channel = self.client.get_channel(database['logs_channel_id'])
                await channel.send(embed=embed)

        except TypeError: #if  no records found for that guild
            pass
        
        except KeyError: # records exist but not set up a logging channel
            pass
            
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", channel.guild.id)
        try :

            if not database['logs_channel_id']:
                return
            
            else:
                embed = discord.Embed(title=f"Channel deleted", color=discord.Color.red())
                embed.add_field(name=f"Name", value=f"{channel.name}", inline=False)
                embed.add_field(name=f"Topic", value=f"{channel.topic}", inline=False)
                embed.add_field(name=f"Category", value=f"{channel.category}", inline=False)
                embed.add_field(name=f"Created at", value=f"{discord.utils.format_dt(channel.created_at, style='F')} ({discord.utils.format_dt(channel.created_at, style='R')})", inline=False)
                
                channel = self.client.get_channel(database['logs_channel_id'])
                await channel.send(embed=embed)
                
        except TypeError: #if  no records found for that guild
            pass
        
        except KeyError: # records exist but not set up a logging channel
            pass
        
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", channel.guild.id)
        try:

            if not database['logs_channel_id']:
                return
            
            else:
                embed = discord.Embed(title=f"Channel created", color=discord.Color.green())
                embed.add_field(name=f"Name", value=f"{channel.name}", inline=False)
                embed.add_field(name=f"Topic", value=f"{channel.topic}", inline=False)
                embed.add_field(name=f"Category", value=f"{channel.category}", inline=False)
                
                channel = self.client.get_channel(database['logs_channel_id'])
                await channel.send(embed=embed)
                
        except TypeError: #if  no records found for that guild
            pass
        
        except KeyError: # records exist but not set up a logging channel
            pass
        
    @commands.Cog.listener()
    async def on_invite_update(self, member, invite):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", member.guild.id)
        try:

            if not database['logs_channel_id']:
                return
            
            else:
                embed = discord.Embed(title=f"Member joined", color=discord.Color.green())
                embed.add_field(name=f"Name", value=f"{member.name}", inline=False)
                embed.add_field(name=f"Created at", value=f"{discord.utils.format_dt(member.created_at, style='F')} ({discord.utils.format_dt(member.created_at, style='R')})", inline=False)
                embed.set_footer(text=f"{member.guild.member_count}th to join")
                
                if invite:
                    expiresAt = "Never"
                    
                    if invite.expires_at:
                        expiresAt = discord.utils.format_dt(invite.expires_at)
                    
                    embed.add_field(name="Invited by:", value=f"""
Inviter: {invite.inviter} **|** {invite.inviter.mention}
Invite code: [{invite.code}]({invite.url})
Expires at: {expiresAt}
Uses: {invite.uses}
                                    """)
                
                channel = self.client.get_channel(database['logs_channel_id'])
                await channel.send(embed=embed)
                
        except TypeError: #if  no records found for that guild
            pass
        
        except KeyError: # records exist but not set up a logging channel
            pass
            
    @commands.Cog.listener()
    async def on_member_remove(self, member):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", member.guild.id)
        try:

            if not database['logs_channel_id']:
                return
            
            else:
                embed = discord.Embed(title=f"Member left", color=discord.Color.red())
                embed.add_field(name=f"Name", value=f"{member.name}", inline=False)
                embed.add_field(name=f"Created at", value=f"{discord.utils.format_dt(member.created_at, style='F')} ({discord.utils.format_dt(member.created_at, style='R')})", inline=False)
                embed.add_field(name=f"Joined at", value=f"{discord.utils.format_dt(member.joined_at, style='F')} ({discord.utils.format_dt(member.joined_at, style='R')})", inline=False)
                
                channel = self.client.get_channel(database['logs_channel_id'])
                try:
                    await channel.send(embed=embed)
                    
                except:
                    return

        except TypeError: #if  no records found for that guild
            pass
        
        except KeyError: # records exist but not set up a logging channel
            pass
        
    @commands.Cog.listener()
    async def on_member_update(self, before, after):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", before.guild.id)
        try:

            if not database['logs_channel_id']:
                return
            
            else:
                embed = discord.Embed(title="Member updated", color=discord.Color.blurple())
                if after.avatar:
                    embed.set_author(name=f"{after}", icon_url=f"{after.avatar.url}")
                deliver = False
                
                if before.avatar != after.avatar:
                    if after.avatar is None:
                        embed.add_field(name=f"Display avatar updated", value=f"Member removed their server avatar.", inline=False)
                        
                    else:
                        embed.add_field(name=f"Display avatar updated", value=f"Member {'updated' if before.avatar else 'set'} their display avatar.", inline=False)
                        embed.set_image(url=f"{after.avatar.url}")
                    deliver = True
                    
                if before.roles != after.roles:
                    added = set(after.roles) - set(before.roles)
                    removed = set(before.roles) - set(after.roles)
                    add = False

                    if added:
                        added = f"Added:" + ", ".join([role.mention for role in added])
                        add = True

                    else:
                        added = ''
                        
                    if removed:
                        removed = f"Removed:" + ", ".join([role.mention for role in removed])
                        add = True
                        
                    else:
                        removed = ''
                        
                    if add:
                        embed.add_field(name=f"Roles updated", value=f"{added}\n{removed}", inline=False)
                        
                    deliver = True
                    
                if before.nick != after.nick:
                    embed.add_field(name="Nickname updated", value=f"Before: {before.nick}\nAfter: {after.nick}", inline=False)
                    
                    deliver = True
                    
                if deliver:
                    channel = self.client.get_channel(database['logs_channel_id'])
                    await channel.send(embed=embed)
                
        except TypeError: #if  no records found for that guild
            pass
        
        except KeyError: # records exist but not set up a logging channel
            pass
            
    @commands.Cog.listener()
    async def on_user_update(self, before, after):
        guilds = [g.id for g in before.mutual_guilds]
        channels = []
        
        for id in guilds:
            database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", id)
            if not database:
                continue

            else:
                channels.append(database['logs_channel_id'])
        try:

            if not database['logs_channel_id']:
                return
            
            else:
                embed = discord.Embed(title="User updated", color=discord.Color.blurple())
                embed.set_author(name=f"{after}", icon_url=f"{after.display_avatar.url}")
                deliver = False
                
                if before.avatar != after.avatar:
                    if after.avatar is None:
                        embed.add_field(name=f"Avatar updated", value=f"User removed their server avatar.", inline=False)
                        
                    else:
                        embed.add_field(name=f"Avatar updated", value=f"User {'updated' if before.avatar else 'set'} their avatar.", inline=False)
                        embed.set_image(url=f"{after.avatar.url}")
                    deliver = True
                    
                if before.name != after.name:
                    embed.add_field(name="Changed name", value=f"Before: {before.name}\nAfter: {after.name}", inline=False)
                    
                    deliver = True
                    
                if before.discriminator  != after.discriminator :
                    embed.add_field(name="Changed discriminator", value=f"Before: #{before.discriminator}\nAfter: #{after.discriminator}", inline=False)
                    
                    deliver = True
                    
                if deliver:
                    if channels:
                        for channel in channels:
                            channel = self.client.get_channel(channel)
                            if channel:
                                try:
                                    await channel.send(embed=embed)

                                except:
                                    continue
                
        except TypeError: #if  no records found for that guild
            pass
        
        except KeyError: # records exist but not set up a logging channel
            pass
    
    @commands.Cog.listener()
    async def on_guild_update(self, before, after):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", before.id)
        try:

            if not database['logs_channel_id']:
                return
            
            else:
                if before.icon != after.icon:
                    if after.icon and before.icon:
                        embed = discord.Embed(title="Server icon updated", color=discord.Color.blurple())
                        embed.set_image(url=after.icon.url)
                    
                    elif after.icon and not before.icon:
                        embed = discord.Embed(title="Server icon set", color=discord.Color.green())
                        embed.set_image(url=after.icon.url)
                        
                    else:
                        embed = discord.Embed(title="Server icon removed", color=discord.Color.red())
                    
                    channel = self.client.get_channel(database['logs_channel_id'])
                    await channel.send(embed=embed)
                    
                if before.name != after.name:
                    embed = discord.Embed(title="Server name updated", color=discord.Color.blurple())
                    embed.add_field(name=f"Before", value=f"{before.name}")
                    embed.add_field(name=f"After", value=f"{after.name}")
                    
                    channel = self.client.get_channel(database['logs_channel_id'])
                    await channel.send(embed=embed)
                    
                if before.owner != after.owner:
                    embed = discord.Embed(title="Server owner updated", color=discord.Color.blurple())
                    embed.add_field(name=f"From", value=f"{before.owner}")
                    embed.add_field(name=f"To", value=f"{after.owner}")
                    channel = self.client.get_channel(database['logs_channel_id'])
                    await channel.send(embed=embed)

        except TypeError: #if  no records found for that guild
            pass
        
        except KeyError: # records exist but not set up a logging channel
            pass
                
    @commands.Cog.listener()
    async def on_guild_role_create(self, role):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", role.guild.id)
        try:

            if not database['logs_channel_id']:
                return
            
            else:
                embed = discord.Embed(title="Role created", color=discord.Color.green())
                embed.add_field(name=f"Name", value=f"{role.name}")
                embed.add_field(name=f"Color", value=f"{role.color}")
                embed.add_field(name=f"Position", value=f"{role.position}")
                embed.add_field(name=f"Mentionable?", value=f"{'<:greenTick:895688440690147370>' if role.mentionable else '<:redTick:895688440568508518>'}")
                embed.add_field(name=f"Show seperately?", value=f"{'<:greenTick:895688440690147370>' if role.hoist else '<:redTick:895688440568508518>'}")
                
                channel = self.client.get_channel(database['logs_channel_id'])
                await channel.send(embed=embed)
                
        except TypeError: #if  no records found for that guild
            pass
        
        except KeyError: # records exist but not set up a logging channel
            pass
          
    @commands.Cog.listener()
    async def on_guild_role_delete(self, role):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", role.guild.id)
        try:

            if not database['logs_channel_id']:
                return
            
            else:
                embed = discord.Embed(title="Role deleted", color=discord.Color.red())
                embed.add_field(name=f"Name", value=f"{role.name}")
                embed.add_field(name=f"Color", value=f"{role.color}")
                embed.add_field(name=f"Position", value=f"{role.position}")
                embed.add_field(name=f"Mentionable?", value=f"{'<:greenTick:895688440690147370>' if role.mentionable else '<:redTick:895688440568508518>'}")
                embed.add_field(name=f"Show seperately?", value=f"{'<:greenTick:895688440690147370>' if role.hoist else '<:redTick:895688440568508518>'}")
                
                channel = self.client.get_channel(database['logs_channel_id'])
                await channel.send(embed=embed)
                
        except TypeError: #if  no records found for that guild
            pass
        
        except KeyError: # records exist but not set up a logging channel
            pass
    
    @commands.Cog.listener()
    async def on_guild_role_update(self, before, after):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", before.guild.id)
        try:

            if not database['logs_channel_id']:
                return
            
            else:
                embed = discord.Embed(title="Role updated", color=discord.Color.blurple())
                deliver = False
                
                if before.permissions != after.permissions:
                    before_true = [str(name).replace('guild', 'server').replace('_', ' ').title() for name, value in set(before.permissions) if value is True]
                    before_false = [str(name).replace('guild', 'server').replace('_', ' ').title() for name, value in set(before.permissions) if value is False]
                    after_true = [str(name).replace('guild', 'server').replace('_', ' ').title() for name, value in set(after.permissions) if value is True]
                    after_false = [str(name).replace('guild', 'server').replace('_', ' ').title() for name, value in set(after.permissions) if value is False]
                    added = ''
                    
                    if before_true != after_true:
                        added = set(after_true) - set(before_true)
                        
                        if added:
                            added = f"Added:" + ", ".join(added)
                            
                        else:
                            added = ''
                    removed = ''
                    
                    if after_false != before_false:
                        removed = set(after_false) - set(before_false)
                        
                        if removed:
                            removed = f"Removed" + ", ".join(added)
                            
                        else:
                            removed = ''
                            
                    embed.add_field(name="Permissions updated:", value=f"{added}\n{removed}", inline=False)
                    deliver = True
                    
                hoist_update = ''
                if before.hoist != after.hoist:
                    hoist_update = f"Show seperately: {'<:greenTick:895688440690147370>' if before.hoist else '<:redTick:895688440568508518>'} > {'<:greenTick:895688440690147370>' if after.hoist else '<:redTick:895688440568508518>'}"
                    deliver = True
                
                ping_update = ''
                if before.mentionable != after.mentionable:
                    ping_update = f"Mentionable: {'<:greenTick:895688440690147370>' if before.mentionable else '<:redTick:895688440568508518>'} > {'<:greenTick:895688440690147370>' if after.mentionable else '<:redTick:895688440568508518>'}"
                    deliver = True
                
                role_update = f"Name: {after.name}"
                if before.name != after.name:
                    role_update = f"Name: {before.name} > {after.name}"
                    deliver = True
                    
                color_update = ''
                if before.color != after.color:
                    color_update = f"Updated color: `{before.color}` > `{after.color}`"
                    deliver = True
                    
                position_update = ''
                if before.position != after.position:
                    position_update = f"Updated position: `{before.position}` > `{after.position}`"
                    deliver = True
                    
                embed.description = role_update + hoist_update + ping_update + color_update + position_update
                
                if deliver:
                    channel = self.client.get_channel(database['logs_channel_id'])
                    await channel.send(embed=embed)
                
        except TypeError: #if  no records found for that guild
            pass
        
        except KeyError: # records exist but not set up a logging channel
            pass
                    
    # @commands.Cog.listener()
    # async def on_guild_emojis_update(self, before, after):
    #     database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", channel.guild.id)
    #     try:

    #         if not database['logs_channel_id']:
    #             return
            
    #         else:
    
    # @commands.Cog.listener()
    # async def on_guild_stickers_update(self, guild, before, after):
    #     database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", channel.guild.id)
    #     try:

    #         if not database['logs_channel_id']:
    #             return
            
    #         else:
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", member.guild.id)
        try:

            if not database['logs_channel_id']:
                return
            
            else:
                if before.channel and after.channel and before.channel != after.channel:
                    embed = discord.Embed(title="Member moved voice channels", color=discord.Color.blurple())
                    embed.add_field(name=f"From", value=f"{before.channel.mention} ({before.channel.id})", inline=False)
                    embed.add_field(name=f"To", value=f"{after.channel.mention} ({after.channel.id})", inline=False)
                    embed.set_author(name=f"{member}", icon_url=f"{member.avatar.url}")
                    
                    channel = self.client.get_channel(database['logs_channel_id'])
                    await channel.send(embed=embed)
                
                if not before.channel and after.channel:
                    embed = discord.Embed(title="Member joined a voice channel", color=discord.Color.green())
                    embed.add_field(name=f"Joined", value=f"{after.channel.mention} ({after.channel.id})", inline=False)
                    embed.set_author(name=f"{member}", icon_url=f"{member.avatar.url}")
                    
                    channel = self.client.get_channel(database['logs_channel_id'])
                    await channel.send(embed=embed)
                    
                if before.channel and not after.channel:
                    embed = discord.Embed(title="Member left a voice channel", color=discord.Color.red())
                    embed.add_field(name=f"Left", value=f"{before.channel.mention} ({before.channel.id})", inline=False)
                    embed.set_author(name=f"{member}", icon_url=f"{member.avatar.url}")
                    
                    channel = self.client.get_channel(database['logs_channel_id'])
                    await channel.send(embed=embed)
                    
                if before.deaf != after.deaf:
                    if after.deaf:
                        embed = discord.Embed(title="Member deafened by a moderator", color=discord.Color.red())
                        embed.add_field(name=f"Member", value=f"{member} ({member.id})", inline=False)
                        embed.set_author(name=f"{member}", icon_url=f"{member.avatar.url}")
                        
                        channel = self.client.get_channel(database['logs_channel_id'])
                        await channel.send(embed=embed)
                        
                    if before.deaf:
                        embed = discord.Embed(title=f"Member undeafened by a moderator", color=discord.Color.green())
                        embed.add_field(name=f"Member", value=f"{member} ({member.id})", inline=False)
                        embed.set_author(name=f"{member}", icon_url=f"{member.avatar.url}")
                        
                        channel = self.client.get_channel(database['logs_channel_id'])
                        await channel.send(embed=embed)
                        
                if before.mute != after.mute:
                    if after.mute:
                        embed = discord.Embed(title="Member muted by a moderator", color=discord.Color.red())
                        embed.add_field(name=f"Member", value=f"{member} ({member.id})", inline=False)
                        embed.set_author(name=f"{member}", icon_url=f"{member.avatar.url}")
                        
                        channel = self.client.get_channel(database['logs_channel_id'])
                        await channel.send(embed=embed)
                        
                    if before.mute:
                        embed = discord.Embed(title=f"Member unmuted by a moderator", color=discord.Color.green())
                        embed.add_field(name=f"Member", value=f"{member} ({member.id})", inline=False)
                        embed.set_author(name=f"{member}", icon_url=f"{member.avatar.url}")
                        
                        channel = self.client.get_channel(database['logs_channel_id'])
                        await channel.send(embed=embed)
                        
        except TypeError: #if  no records found for that guild
            pass
        
        except KeyError: # records exist but not set up a logging channel
            pass
                    
    @commands.Cog.listener()
    async def on_stage_instance_create(self, stage_instance):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", stage_instance.guild.id)
        try:

            if not database['logs_channel_id']:
                return
            
            else:
                embed = discord.Embed(title="Stage opened", color=discord.Color.green())
                embed.add_field(name=f"Channel", value=f"{stage_instance.channel.mention}")
                embed.add_field(name=f"Public", value=f"{'<:greenTick:895688440690147370>' if stage_instance.is_public() else '<:redTick:895688440568508518>'}")
                embed.add_field(name=f"Discoverable?", value=f"{'<:greenTick:895688440690147370>' if stage_instance.discoverable_disabled else '<:redTick:895688440568508518>'}")
                
                channel = self.client.get_channel(database['logs_channel_id'])
                await channel.send(embed=embed)
                
        except TypeError: #if  no records found for that guild
            pass
        
        except KeyError: # records exist but not set up a logging channel
            pass
            
    @commands.Cog.listener()
    async def on_stage_instance_delete(self, stage_instance):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", stage_instance.guild.id)
        try:

            if not database['logs_channel_id']:
                return
            
            else:
                embed = discord.Embed(title="Stage closed", color=discord.Color.red())
                embed.add_field(name=f"Channel", value=f"{stage_instance.channel.mention}")
                
                channel = self.client.get_channel(database['logs_channel_id'])
                await channel.send(embed=embed)
                
        except TypeError: #if  no records found for that guild
            pass
        
        except KeyError: # records exist but not set up a logging channel
            pass
            
    # @commands.Cog.listener()
    # async def on_stage_instance_update(self, before, after):
    #     database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", before.guild.id)
    #     try:

    #         if not database['logs_channel_id']:
    #             return
            
    #         else:

    @commands.Cog.listener()
    async def on_member_ban(self, guild, user):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", guild.id)
        try:

            if not database['logs_channel_id']:
                return
            
            else:
                embed = discord.Embed(title="User banned", color=discord.Color.red())
                embed.add_field(name=f"User", value=f"{user.name} **|** {user.mention} **|** {user.id}")
                embed.add_field(name=f"Created at", value=f"{discord.utils.format_dt(user.created_at, style='F')} ({discord.utils.format_dt(user.created_at, style='R')})")
                
                channel = self.client.get_channel(database['logs_channel_id'])
                await channel.send(embed=embed)
                
        except TypeError: #if  no records found for that guild
            pass
        
        except KeyError: # records exist but not set up a logging channel
            pass
        
    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", guild.id)
        try:

            if not database['logs_channel_id']:
                return
            
            else:
                embed = discord.Embed(title="User unbanned", color=discord.Color.green())
                embed.add_field(name=f"User", value=f"{user.name} **|** {user.mention} **|** {user.id}")
                embed.add_field(name=f"Created at", value=f"{discord.utils.format_dt(user.created_at, style='F')} ({discord.utils.format_dt(user.created_at, style='R')})")
                
                channel = self.client.get_channel(database['logs_channel_id'])
                await channel.send(embed=embed)
                
        except TypeError: #if  no records found for that guild
            pass
        
        except KeyError: # records exist but not set up a logging channel
            pass
        
    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", invite.guild.id)
        try:

            if not database['logs_channel_id']:
                return
            
            else:
                expiresAt = "Never"
                maxUses = "Unlimited"
                
                if invite.expires_at:
                    expiresAt = discord.utils.format_dt(invite.expires_at)
                    
                if invite.max_uses > 0:
                    maxUses = invite.max_uses
                
                embed = discord.Embed(title="Invite created", color=discord.Color.green())
                embed.add_field(name=f"Inviter", value=f"{invite.inviter.name} **|** {invite.inviter.mention} **|** {invite.inviter.id}")
                embed.add_field(name=f"Invite code", value=f"[{invite.code}]({invite.url})")
                embed.add_field(name=f"Expires", value=f"{expiresAt}")
                embed.add_field(name=f"Max uses", value=f"{maxUses}")
                embed.add_field(name=f"Channel", value=f"{invite.channel.mention}")
                embed.add_field(name=f"Grants temporary membership?", value=f"{'<:greenTick:895688440690147370>' if invite.temporary else '<:redTick:895688440568508518>'}")
                
                channel = self.client.get_channel(database['logs_channel_id'])
                await channel.send(embed=embed)
                
        except TypeError: #if  no records found for that guild
            pass
        
        except KeyError: # records exist but not set up a logging channel
            pass
        
    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", invite.guild.id)
        try:

            if not database['logs_channel_id']:
                return
            
            else:
                embed = discord.Embed(title="Invite created", color=discord.Color.red())
                embed.add_field(name=f"Inviter", value=f"{invite.inviter.name if invite.inviter else 'Unknown'} **|** {invite.inviter.mention if invite.inviter else 'Unknown'} **|** {invite.inviter.id if invite.inviter else 'Unknown'}")
                embed.add_field(name=f"Invite code", value=f"[{invite.code if invite.code else 'Unknown'}]({invite.url})")
                embed.add_field(name=f"Channel", value=f"{invite.channel.mention if invite.channel else 'Unknown'}")
                embed.add_field(name=f"Grants temporary membership?", value=f"{'<:greenTick:895688440690147370>' if invite.temporary else '<:redTick:895688440568508518>'}")
                
                channel = self.client.get_channel(database['logs_channel_id'])
                await channel.send(embed=embed)
                
        except TypeError: #if  no records found for that guild
            pass
        
        except KeyError: # records exist but not set up a logging channel
            pass