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
from helpers.context import CustomContext

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
        
    def make_ordinal(self, n):
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
        self.delete_invite(inv)
        self.client.expiring_invites.pop(self.client.shortest_invite, None)

    @delete_expired.before_loop
    async def wait_for_list(self):
        await self.wait_for_invites()

    @tasks.loop(minutes=POLL_PERIOD)
    async def update_invite_expiry(self):
        flattened = [invite for inner in self.client.invites.values() for invite in inner.values()]
        current = time.time()
        self.client.expiring_invites = {
            inv.max_age - int(current - inv.created_at.replace(tzinfo=datetime.timezone.utc).timestamp()): inv
            for inv in flattened if inv.max_age != 0}

        exists = True

        try:
            self.client.shortest_invite = self.client.shortest_invite - int(time.time() - self.client.last_update)

        except AttributeError:
            exists = False

        if self.update_invite_expiry.current_loop == 0:
            self.client.last_update = int(current)
            self._invites_ready.set()

        elif exists and self.client.expiring_invites and self.client.shortest_invite > min(self.client.expiring_invites.keys()):
            self.delete_expired.restart()
            self.client.last_update = int(current)

        else:
            self.client.last_update = int(current)

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
                if invite.channel.id == channel.id:
                    invites.pop(invite.code)

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild) -> None:
        invites = await self.fetch_invites(guild) or {}
        self.client.invites[guild.id] = invites

    @commands.Cog.listener()
    async def on_guild_available(self, guild: discord.Guild) -> None:
        self.client.invites[guild.id] = await self.fetch_invites(guild) or {}

    @commands.Cog.listener()
    async def on_guild_remove(self, guild: discord.Guild) -> None:
        self.client.loop.create_task(self._schedule_deletion(guild))

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member) -> None:
        invites = await self.fetch_invites(member.guild)

        if invites:
            invites = sorted(invites.values(), key=lambda i: i.code)
            cached = sorted(self.client.invites[member.guild.id].values(),
                            key=lambda i: i.code)

            for old, new in zip(cached, invites):
                if old.uses < new.uses:
                    self.client.invites[member.guild.id][old.code] = new
                    self.client.dispatch("invite_update", member, new)
                    break
