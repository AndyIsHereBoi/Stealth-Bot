import discord

from discord.ext import commands
from discord.errors import HTTPException
from discord.ext.commands.errors import UserNotFound


def setup(client):
    client.add_cog(ModMail(client))


async def get_webhook(channel) -> discord.Webhook:
    webhook_list = await channel.webhooks()

    if webhook_list:
        for hook in webhook_list:
            if hook.token:
                return hook

            else:
                continue

    hook = await channel.create_webhook(name="ModMail")
    return hook


class ModMail(commands.Cog):
    def __init__(self, bot):
        self.client = bot

    async def get_dm_hook(self, channel: discord.TextChannel) -> discord.Webhook:
        if url := self.client.dm_webhooks.get(channel.id, None):
            return discord.Webhook.from_url(url, session=self.client.session, bot_token=self.client.http.token)
        wh = await get_webhook(channel)
        self.client.dm_webhooks[channel.id] = wh.url
        return wh

    @commands.Cog.listener('on_message')
    async def on_mail(self, message: discord.Message):
        if message.guild or message.author == self.client.user:
            return

        ctx = await self.client.get_context(message)

        category = self.client.get_guild(879050715660697622).get_channel(919172324610170930)
        channel = discord.utils.get(category.channels, topic=str(message.author.id))

        if not channel:
            if not message.reference:
                await message.author.send("Warning: This conversation will be sent to the bot developer.")

            channel = await category.create_text_channel(name=f"{message.author}", topic=str(message.author.id), position=0, reason="ModMail")

        wh = await self.get_dm_hook(channel)

        files = [await attachment.to_file(spoiler=attachment.is_spoiler()) for attachment in message.attachments if attachment.size < 8388600]

        if not files and message.attachments:
            embed = discord.Embed(description="Some files could not be delivered because they were over 8MB in size.", color=discord.Color.red())
            await message.author.send(embed=embed)

        try:
            await wh.send(content=message.content, username=message.author.name, avatar_url=message.author.display_avatar.url, files=files)

        except (discord.Forbidden, discord.HTTPException):
            return await message.add_reaction('⚠')

    @commands.Cog.listener('on_message')
    async def on_mail_reply(self, message: discord.Message):
        if not message.guild:
            return

        if any((message.author.bot, message.channel.category_id != 919172324610170930)):
            return

        channel = message.channel
        try:
            user = self.client.get_user(int(channel.topic)) or await self.client.fetch_user(int(channel.topic))

        except (HTTPException, UserNotFound):
            embed = discord.Embed(description="I couldn't find that user", color=discord.Color.red())
            return await message.author.send(embed=embed)

        files = [await attachment.to_file(spoiler=attachment.is_spoiler()) for attachment in message.attachments if attachment.size < 8388600]

        if not files and message.attachments:
            embed = discord.Embed(description="Some files could not be delivered because they were over 8MB in size.", color=discord.Color.red())
            await message.author.send(embed=embed)

        try:
            await user.send(content=message.content, files=files)

        except (discord.Forbidden, discord.HTTPException):
            return await message.add_reaction('⚠')

    @commands.Cog.listener('on_user_update')
    async def on_mail_username_change(self, before: discord.User, after: discord.User):
        if str(before) == str(after) or before.bot:
            return

        category = self.client.get_guild(879050715660697622).get_channel(919172324610170930)
        channel = discord.utils.get(category.channels, topic=str(after.id))

        if channel:
            await channel.edit(name=str(after), reason=f"ModMail channel update for {after.id}")
            wh = await self.get_dm_hook(channel)

            embed = discord.Embed(title="ModMail user update!", color=discord.Colour.blurple(), timestamp=discord.utils.utcnow())
            embed.add_field(name="Before:", value=str(before))
            embed.add_field(name="After:", value=str(after))

            await wh.send(embed=embed, avatar_url=after.display_avatar.url)