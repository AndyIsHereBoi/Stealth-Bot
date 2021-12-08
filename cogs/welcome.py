"""
MIT License
Copyright (c) 2020-2021 cyrus01337, XuaTheGrate
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
https://github.com/cyrus01337/invites/
"""

import time
import discord
import asyncio
import datetime
import contextlib
from typing import Dict, Optional
from discord.ext import commands, tasks

POLL_PERIOD = 25

def setup(client):
    client.add_cog(WelcomeCog(client))
    
class WelcomeCog(commands.Cog):
    """Welcome system"""
    def __init__(self, client):
        self.client = client
        self.hidden = True
        
        self.select_emoji = "👋"
        self.select_brief = "Welcome system"
        
        self._invites_ready = asyncio.Event()
        self._dict_filled = asyncio.Event()

        self.client.invites = {}
        self.client.get_invite = self.get_invite
        self.client.wait_for_invites = self.wait_for_invites

        self.client.loop.create_task(self.__ainit__())
        
    def make_ordinal(n):
        '''
        Convert an integer into its ordinal representation::

            make_ordinal(0)   => '0th'
            make_ordinal(3)   => '3rd'
            make_ordinal(122) => '122nd'
            make_ordinal(213) => '213th'
        '''
        n = int(n)
        suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
        if 11 <= (n % 100) <= 13:
            suffix = 'th'
        return str(n) + suffix

    async def __ainit__(self):
        await self.client.wait_until_ready()

        for guild in self.client.guilds:
            fetched = await self.fetch_invites(guild)
            invites = self.client.invites[guild.id] = fetched or {}

            if "VANITY_URL" in guild.features:
                with contextlib.suppress(discord.HTTPException):
                    vanity = await guild.vanity_invite()
                    invites["VANITY"] = invites[vanity.code] = vanity
        self.update_invite_expiry.start()
        self.delete_expired.start()

    def cog_unload(self):
        self.update_invite_expiry.cancel()
        self.delete_expired.cancel()

    @tasks.loop()
    async def delete_expired(self):
        if not self.client.expiring_invites:
            await self._dict_filled.wait()
            
        invites = self.client.expiring_invites
        expiry_time = min(invites.keys())
        inv = invites[expiry_time]
        sleep_time = expiry_time - (int(time.time()) - self.client.last_update)
        self.client.shortest_invite = expiry_time
        await asyncio.sleep(sleep_time)
        # delete invite from cache
        self.delete_invite(inv)
        # delete invite from expiring invite list
        # bot.shortest_invite is updated in update_invite_expiry
        # and since the expiring_invites dict is also updated
        # so the time goes down we use this instead
        self.client.expiring_invites.pop(self.client.shortest_invite, None)

    @delete_expired.before_loop
    async def wait_for_list(self):
        await self.wait_for_invites()

    @tasks.loop(minutes=POLL_PERIOD)
    async def update_invite_expiry(self):
        # flatten all the invites in the cache into one single list
        flattened = [invite for inner in self.client.invites.values() for invite in inner.values()]
        # get current posix time
        current = time.time()
        self.client.expiring_invites = {
            inv.max_age - int(current - inv.created_at.replace(tzinfo=datetime.timezone.utc).timestamp()): inv
            for inv in flattened if inv.max_age != 0}

        exists = True

        # update self.client.shortest_invite
        # so we can compare it with invites
        # that were just created
        try:  # self.client.shortest_invite might not exist
            self.client.shortest_invite = self.client.shortest_invite - int(time.time() - self.client.last_update)
        except AttributeError:
            exists = False

        if self.update_invite_expiry.current_loop == 0:
            # this needs to be updated before
            # setting self._invites_ready
            self.client.last_update = int(current)
            self._invites_ready.set()
        # we need to check that expiring_invites
        # is truthy otherwise this conditional will
        # raise an error because we passed an
        # empty sequence to min()
        elif exists and self.client.expiring_invites and self.client.shortest_invite > min(self.client.expiring_invites.keys()):
            # this conditional needs to run before we
            # update self._last_update
            self.delete_expired.restart()
            self.client.last_update = int(current)
        else:
            # the last update needs to be updated regardless or
            # it will cause updates getting deleted from the cache
            # too early because the expiring_invites list will be
            # updated with new times but delete_expired will think
            # that the last update was ages ago and will deduct a huge
            # amount of seconds from the expiry time to form the sleep_time
            self.client.last_update = int(current)
        # set the event so if the delete_expired
        # task is cancelled it will start again
        if self.client.expiring_invites:
            self._dict_filled.set()
            self._dict_filled.clear()

    def delete_invite(self, invite: discord.Invite) -> None:
        entry_found = self.get_invites(invite.guild.id)
        entry_found.pop(invite.code, None)

    def get_invite(self, code: str) -> Optional[discord.Invite]:
        for invites in self.client.invites.values():
            find = invites.get(code)

            if find:
                return find
        return None

    def get_invites(self, guild_id: int) -> Optional[Dict[str, discord.Invite]]:
        return self.client.invites.get(guild_id, None)

    async def wait_for_invites(self) -> None:
        if not self._invites_ready.is_set():
            await self._invites_ready.wait()

    async def fetch_invites(self, guild: discord.Guild) -> Optional[Dict[str, discord.Invite]]:
        try:
            invites = await guild.invites()
        except discord.HTTPException:
            return None
        else:
            return {invite.code: invite for invite in invites}

    async def _schedule_deletion(self, guild: discord.Guild) -> None:
        seconds_passed = 0

        while seconds_passed < 300:
            seconds_passed += 1

            if guild in self.client.guilds:
                return
            await asyncio.sleep(1)

        if guild not in self.client.guilds:
            self.client.invites.pop(guild.id, None)

    @commands.Cog.listener()
    async def on_invite_create(self, invite: discord.Invite) -> None:
        print(f"created invite {invite} in {invite.guild}")
        cached = self.client.invites.get(invite.guild.id, None)

        if cached:
            cached[invite.code] = invite

    @commands.Cog.listener()
    async def on_invite_delete(self, invite: discord.Invite) -> None:
        self.delete_invite(invite)
        
    @commands.Cog.listener()
    async def on_invite_update(self, member: discord.Member, invite: discord.Invite) -> None:
        database = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", member.guild.id)
        
        if not database:
            return
        
        if not database['welcome_channel_id']:
            return
        
        if not database['welcome_message']:
            message = f"Welcome to **[server]**, **[full-user]**!"
            
        else:
            message = database['welcome_message']
            
        message = message.replace("[server]", f"{member.guild.name}")
        
        message = message.replace("[user]", f"{member.display_name}").replace("[full-user]", f"{member}").replace("[user-mention]", f"{member.mention}")
        
        message = message.replace("[count]", f"{self.make_ordinal(member.guild.member_count)}")
        
        message = message.replace("[code]", f"{str(invite.code)}").replace("[full-code]", f"discord.gg/{invite.code}").replace("[full-url]", f"{str(invite.url)}").replace("[inviter]", f"{str(((member.guild.get_member(invite.inviter.id).display_name) or invite.inviter.name) if invite.inviter else 'N/A')}").replace("[full-inviter]", f"{str(invite.inviter if invite.inviter else 'N/A')}").replace("[inviter-mention]", f"{str(invite.inviter.mention if invite.inviter else 'N/A')}")
        
        channel = self.client.get_channel(database['welcome_channel_id'])
        
        await channel.send(message)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel) -> None:
        invites = self.client.invites.get(channel.guild.id)

        if invites:
            for invite in list(invites.values()):
                # changed to use id because of doc warning
                if invite.channel.id == channel.id:
                    invites.pop(invite.code)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        invites = await self.fetch_invites(guild) or {}
        self.client.invites[guild.id] = invites

    @commands.Cog.listener()
    async def on_guild_available(self, guild: discord.Guild) -> None:
        # reload all invites in case they changed during
        # the time that the guilds were unavailable
        self.client.invites[guild.id] = await self.fetch_invites(guild) or {}

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        self.client.loop.create_task(self._schedule_deletion(guild))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        invites = await self.fetch_invites(member.guild)

        if invites:
            # we sort the invites to ensure we are comparing
            # A.uses == A.uses
            invites = sorted(invites.values(), key=lambda i: i.code)
            cached = sorted(self.client.invites[member.guild.id].values(),
                            key=lambda i: i.code)

            # zipping is the easiest way to compare each in order, and
            # they should be the same size? if we do it properly
            for old, new in zip(cached, invites):
                if old.uses < new.uses:
                    self.client.invites[member.guild.id][old.code] = new
                    self.client.dispatch("invite_update", member, new)
                    break
                
    # if you want to use this command you
    # might want to make a error handler
    # to handle commands.NoPrivateMessage
    @commands.guild_only()
    @commands.command()
    async def invitestats(self, ctx):
        """Displays the top 10 most used invites in the guild."""
        # PEP8 + same code, more readability
        invites = self.client.invites.get(ctx.guild.id, None)

        # falsey check for None or {}
        if not invites:
            # if there is no invites send this information
            # in an embed and return
            embed = discord.Embed(colour=discord.Colour.red(), description='No invites found...')
            await ctx.send(embed=embed)
            return

        # if you got here there are invites in the cache
        embed = discord.Embed(colour=discord.Colour.green(), title='Most used invites')
        # sort the invites by the amount of uses
        # by default this would make it in increasing
        # order so we pass True to the reverse kwarg
        invites = sorted(invites.values(), key=lambda i: i.uses, reverse=True)
        # if there are 10 or more invites in the cache we will
        # display 10 invites, otherwise display the amount
        # of invites
        amount = 10 if len(invites) >= 10 else len(invites)
        # list comp on the sorted invites and then
        # join it into one string with str.join
        description = '\n'.join([f'{i + 1}. {invites[i].inviter.mention} {invites[i].code} - {invites[i].uses}' for i in range(amount)])
        embed.description = description
        # if there are more than 10 invites
        # add a footer saying how many more
        # invites there are
        if amount > 10:
            embed.set_footer(text=f'There are {len(invites) - 10} more invites in this guild.')
        await ctx.send(embed=embed)
        
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
    async def enable(self, ctx, channel: discord.TextChannel=None):
        if not channel:
            channel = ctx.channel
            
        await self.client.db.execute("INSERT INTO guilds (guild_id, welcome_channel_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET welcome_channel_id = $2", ctx.guild.id, channel.id)
        
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
        await self.client.db.execute("INSERT INTO guilds (guild_id, welcome_channel_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET welcome_channel_id = $2", ctx.guild.id, None)
        await self.client.db.execute("INSERT INTO guilds (guild_id, welcome_message) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET welcome_message = $2", ctx.guild.id, None)
        
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
            return await ctx.send(f"You need to set-up a welcome channel first!\nTo do that do `{ctx.prefix}welcome enable <channel>`")
        
        if len(message) > 500:
            return await ctx.send(f"Your message exceeded the 500-character limit!")
        
        await self.client.db.execute("INSERT INTO guilds (guild_id, welcome_message) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET welcome_message = $2", ctx.guild.id, message)
        
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
            return await ctx.send(f"You need to set-up a welcome channel first!\nTo do that do `{ctx.prefix}welcome enable <channel>`")
        
        if not database['welcome_message']:
            message = f"Welcome to **[server]**, **[full-user]**!"
            
        else:
            message = database['welcome_message']
            
        message = message.replace("[server]", f"{ctx.guild.name}")
        
        message = message.replace("[user]", f"{ctx.author.display_name}").replace("[full-user]", f"{ctx.author}").replace("[user-mention]", f"{ctx.author.mention}")
        
        message = message.replace("[count]", f"{self.make_ordinal(ctx.guild.member_count)}")
        
        message = message.replace("[code]", f"123456789").replace("[full-code]", f"discord.gg/123456789").replace("[full-url]", f"https://discord.gg/123456789").replace("[inviter]", f"John").replace("[full-inviter]", f"John#1234").replace("[inviter-mention]", f"@John")
        
        await ctx.send(message)
        
    ##################################################################################################################################################################
    ##################################################################################################################################################################
    ##################################################################################################################################################################
    ##################################################################################################################################################################