import re
import typing
import errors
import random
import asyncio
import difflib
import discord
import itertools

from discord.ext import commands
from helpers.context import CustomContext

def main(string):
    string = str(string).lower()
    string = string.replace("ö", "o").replace("ä", "a").replace("ü", "u").replace("@", "a").replace("$", "s").replace(
        "!", "i").replace('"', "").replace("§", "s").replace("/", "").replace("{", "").replace("[", "").replace("]",
                                                                                                                "").replace(
        "}", "").replace("(", "").replace(")", "").replace("=", "").replace(".", "").replace(",", "").replace(":",
                                                                                                            "").replace(
        ";", "").replace("-", "").replace("_", "").replace("#", "").replace("'", "").replace("´", "").replace("`",
                                                                                                            "").replace(
        "^", "").replace("°", "").replace("*", "").replace("+", "").replace("~", "").replace("€", "").replace("%",
                                                                                                            "").replace(
        "&", "").replace("?", "").replace("ó", "o").replace("ú", "u").replace("á", "a").replace("é", "e").replace("ë",
                                                                                                                "e").replace(
        "ï", "i").replace("í", "i").replace("y", "y").replace("ß", "").replace("ć", "c").replace("ś", "s").replace("ő",
                                                                                                                "o").replace(
        "`", "").replace("´", "")
    return string

def unique_list(text_str):
    l = text_str.split()
    temp = []
    for x in l:
        if x not in temp:
            temp.append(x)
    return ' '.join(temp)


def setup(client):
    client.add_cog(Misc(client))


UNITS_MAPPING = [
    (1 << 50, ' PB'),
    (1 << 40, ' TB'),
    (1 << 30, ' GB'),
    (1 << 20, ' MB'),
    (1 << 10, ' KB'),
    (1, (' byte', ' bytes')),
]


def pretty_size(bytes, units=UNITS_MAPPING):
    for factor, suffix in units:
        if bytes >= factor:
            break
    amount = int(bytes / factor)

    if isinstance(suffix, tuple):
        singular, multiple = suffix
        if amount == 1:
            suffix = singular
        else:
            suffix = multiple
    return str(amount) + suffix


class Button(discord.ui.Button):
    def __init__(self):
        invisible_character = "\u2800"
        super().__init__(style=discord.ButtonStyle.green,
                         label=f"{invisible_character * 19}Accept{invisible_character * 20}")

    async def callback(self, interaction):
        embed = discord.Embed(title="You received a gift, but...",
                              description="The gift link has either expired or has been revoked.\nThe sender can "
                                          "still create a new link to send again.",
                              color=0x2F3136)
        embed.set_image(
            url="https://external-preview.redd.it/9HZBYcvaOEnh4tOp5EqgcCr_vKH7cjFJwkvw-45Dfjs.png?auto=webp&s"
                "=ade9b43592942905a45d04dbc5065badb5aa3483")
        view = self.view
        for child in view.children:
            child.disabled = True
            invisible_character = "\u2800"
            child.label = f"{invisible_character * 13}Accepted{invisible_character * 14}"
            child.style = discord.ButtonStyle.gray

        await interaction.message.edit(embed=embed, view=view)  # Sends nitro expired/redeemed message
        await interaction.response.send_message(
            "https://images-ext-1.discordapp.net/external/AoV9l5YhsWBj92gcKGkzyJAAXoYpGiN6BdtfzM-00SU/https/i.imgur"
            ".com/NQinKJB.mp4",
            ephemeral=True)  # Sends 4K rickroll
        view.stop()


class Nitro(discord.ui.View):
    def __init__(self, ctx: CustomContext):
        super().__init__()
        self.ctx = ctx
        self.add_item(Button())


class Misc(commands.Cog):
    """Commands that don't belong under any category."""

    def __init__(self, client):
        self.client = client
        self.select_emoji = "<:gear:899622456191483904>"
        self.select_brief = "Commands that don't belong under any category."

    @commands.group(
        help="<:PES_Sniper:896787924903919648> | Snipes the most recently deleted message from this server.")
    async def snipe(self, ctx: CustomContext):
        if ctx.invoked_subcommand is None:
            if self.client.messages.get(ctx.guild.id) is None:
                embed = discord.Embed(description=f"I couldn't find any deleted self.client.messages in this server.")
                await ctx.send(embed=embed)

            else:
                message = self.client.messages.get(ctx.guild.id)["message"]
                content = self.client.messages.get(ctx.guild.id)["content"]
                author = self.client.messages.get(ctx.guild.id)["author"]
                time_deleted = self.client.messages.get(ctx.guild.id)["time_deleted"]
                deleted_embed = self.client.messages.get(ctx.guild.id)["embed"]

                if content is None or len(content) == 0:
                    content = "*Message did not contain any content*"

                elif content is not None or len(content) > 0:
                    content = content

                colors = [0x910023, 0xA523FF]
                color = random.choice(colors)

                embed = discord.Embed(description=content, color=color, timestamp=discord.utils.utcnow())

                if author.avatar.url is not None:
                    embed.set_author(name=f"{author} ({author.id}) said in #{message.channel}...",
                                     icon_url=author.avatar.url)

                elif author.avatar.url is None:
                    embed.set_author(name=f"{author} ({author.id}) said in #{message.channel}...")

                if message.attachments:
                    embed.set_image(url=message.attachments[0].url)

                delta_uptime = discord.utils.utcnow() - time_deleted
                hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
                minutes, seconds = divmod(remainder, 60)
                days, hours = divmod(hours, 24)

                embed.set_footer(
                    text=f"Message deleted {days} days, {hours} hours, {minutes} minutes and {seconds} seconds ago")

                if deleted_embed != "":
                    await ctx.send(embeds=[embed, deleted_embed], footer=False)

                elif deleted_embed == "":
                    await ctx.send(embed=embed, footer=False)

    @snipe.command(
        help="<:PES_Sniper:896787924903919648> Snipes the most recently edited message from this server.",
        aliases=['edited', 'e'])
    async def edit(self, ctx: CustomContext):
        if self.client.edited_messages.get(ctx.guild.id) == None:
            embed = discord.Embed(description=f"I couldn't find any edited self.client.messages in this server.")
            await ctx.send(embed=embed)

        else:
            before = self.client.edited_messages.get(ctx.guild.id)["before"]
            before_content = self.client.edited_messages.get(ctx.guild.id)["before_content"]
            before_author = self.client.edited_messages.get(ctx.guild.id)["before_author"]

            after = self.client.edited_messages.get(ctx.guild.id)["after"]
            after_content = self.client.edited_messages.get(ctx.guild.id)["after_content"]
            after_author = self.client.edited_messages.get(ctx.guild.id)["after_author"]

            if before_content is None or len(before_content) == 0:
                before_content = "*Message did not contain any content*"

            elif before_content is not None or len(before_content) > 0:
                before_content = before_content

            if after_content is None or len(after_content) == 0:
                after_content = "*Message did not contain any content*"

            elif after_content is not None or len(after_content) > 0:
                after_content = after_content

            colors = [0x910023, 0xA523FF]
            color = random.choice(colors)

            embed = discord.Embed(color=color, timestamp=discord.utils.utcnow())

            embed.add_field(name="Before", value=before_content)
            embed.add_field(name="After", value=after_content)

            if before_author.avatar.url is not None:
                embed.set_author(name=f"{before_author} ({before_author.id}) said in #{before.channel}...",
                                 icon_url=before_author.avatar.url)

            elif before_author.avatar.url is None:
                embed.set_author(name=f"{before_author} ({before_author.id}) said in #{before.channel}...")

            await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="Scans the given text for bad words. Note that this is not close to being done and is still in development.")
    async def scan(self, ctx: CustomContext, *, string: str):
        with open("./data/badwords.txt", "r") as file:
            allText = file.read()
            blacklistedWords = list(map(str, allText.split()))

        OriginalMessage = string.lower()
        # message = re.sub(r"(?i)[^a-z]", "", message)
        message = main(string=OriginalMessage)
        message = unique_list(message)
        message = [(a, list(b)) for a, b in itertools.groupby(message)]
        message = ''.join(''.join(b[:-1]) if len(b) > 2 else ''.join(b) for a, b in message)
        invite_regex = re.compile(r"<?(https?:\/\/)?(www\.)?(discord\.gg|discordapp\.com\/invite)\b([-a-zA-Z0-9/]*)>?")
        url_regex = re.compile(
            r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))")

        scanned = difflib.get_close_matches(message, blacklistedWords, n=1, cutoff=1)

        if scanned:
            scanned = ", ".join(scanned)
            embed = discord.Embed(title="Profanity detected!", description=f"""
Scanned: `{scanned}`
Message: `{message}`
        """)

            return await ctx.send(embed=embed)

        elif invite_regex.search(OriginalMessage):
            embed = discord.Embed(title="Invite detected!", description=f"""
Message: `{OriginalMessage}`
        """)

            return await ctx.send(embed=embed)

        elif url_regex.search(OriginalMessage):
            embed = discord.Embed(title="URL detected!", description=f"""
Message: {OriginalMessage}
            """)

        else:
            embed = discord.Embed(title="No profanity detected!", description=f"""
Message: `{message}`
            """)

            return await ctx.send(embed=embed)

    @commands.command()
    async def nitro(self, ctx: CustomContext):
        invisible_character = "\u2800"
        embed = discord.Embed(title="You've been gifted a subscription.",
                              description=f"Stealth Bot#1082 has gifted you Nitro for 1 year.", color=0x2F3136)
        embed.set_image(
            url="https://cdn.discordapp.com/app-assets/521842831262875670/store/633877574094684160.png?size=1024")
        embed.set_footer(text=f"{invisible_character * 38}Expires in 48 hours")
        gifts = [
            "eJ2vpGYnKMspc2AgjMQXuk96",
            "bR2tJjuu2n6CbGG9VbHgjkJy",
            "FTQK8fkHcM5y4WwBRUBpqAuZ",
            "CSfRUy8yChjJ6czUzGc3vnHS",
            "5mm3zsJvWvJsxRZHY6C4JbKj",
            "N4XkBc3BGThT7UZcZDFdakFa",
            "fkCwRs6tYDMrqCPbZTtPDwrG",
            "6VRERw6mSMQN3ZmTxj2utfmd",
            "9v7R2VGFmT5RXbWXUXcbeYxj",
            "tJvD6axBjd6nAJX2tfH75bGK",
            "UzzVdyeCuf59StkEjR8zzYrC",
            "FfYjr4egf5s6QswsdxnTQBhG",
            "GkgUqZaUAxynWPqQ8zSBeGF7",
            "tSdvcQpqm4qBnn8bUftqmKjd",
            "hhVrBvaxbHypFX9NVqcSFBcz",
            "NQz8TUYstMyM5jrq8HFbqPqP",
            "N4XkBc3BGThT7UZcZDFdakFa",
            "hX876GGp95RgEsv6v6AGP2tV",
            "txeYnvGmx3geYHgGhQkR4F63",
            "f9HqQGmDj43rXXEXpdxG3zXs",
            "kewp3avmCeHmMdZrQEYnCPxR",
            "j3T4yCkkNHjTufwgmTpmSRt8",
            "hMg7bgpRds4kkVyYNF32uTaX",
            "RG32fFHc45SVNZzhcEgn5ddV",
            "TanVaXE3DRtg69QjDDsCkPFX",
            "Nwd74a628Hpzxvs8E5YfK7bv",
            "JNYHxhg568UV4HcGft3WQkZk",
        ]

        gift = f"<https://discord.gift\{random.choice(gifts)}>"
        v = Nitro(ctx=ctx)
        await ctx.send(content=gift, embed=embed, reminders=False, color=False, footer=False, timestamp=False, view=v)
        await v.wait()

    @commands.command(
        help="Sends invite links to invite the bot to your server.",
        aliases=['inv', 'invite_me', 'inviteme'])
    async def invite(self, ctx: CustomContext):
        view = discord.ui.View()
        style = discord.ButtonStyle.gray
        item = discord.ui.Button(style=style, emoji="⭐", label="Recommended",
                                 url="https://discord.com/oauth2/authorize?client_id=760179628122964008&scope=applications.commands+bot&permissions=294171045078")
        view.add_item(item=item)
        
        item = discord.ui.Button(style=style, emoji="🛡️", label="All",
                                 url="https://discord.com/oauth2/authorize?client_id=760179628122964008&scope=applications.commands+bot&permissions=549755813887")
        view.add_item(item=item)
        
        embed = discord.Embed(title="Invite me!", description=f"""
[❌ No permissions](https://discord.com/oauth2/authorize?client_id=760179628122964008&scope=applications.commands+bot&permissions=0)
[😔 Minimal permissions](https://discord.com/oauth2/authorize?client_id=760179628122964008&scope=applications.commands+bot&permissions=274948541504)
[⭐ Mod permissions](https://discord.com/oauth2/authorize?client_id=760179628122964008&scope=applications.commands+bot&permissions=294171045078)
[🛠️ Admin permissions](https://discord.com/oauth2/authorize?client_id=760179628122964008&scope=applications.commands+bot&permissions=8)
[🛡️ All permissions](https://discord.com/oauth2/authorize?client_id=760179628122964008&scope=applications.commands+bot&permissions=549755813887)
                              """)
        
        await ctx.send(embed=embed, view=view)
        
    @commands.command(
        help="Sends you the link of the Stealth Bot website.")
    async def website(self, ctx: CustomContext):
        view = discord.ui.View()
        style = discord.ButtonStyle.gray
        item = discord.ui.Button(style=style, emoji="🌐", label="Website",
                                 url="https://stealthbot.xyz")
        view.add_item(item=item)
        
        await ctx.send(content="Click the button below to be redirected to the website.", view=view)
    
    @commands.command(
        help="Sends you a link where you can vote for the bot.",
        aliases=['topgg', 'top-gg', 'top_gg'])
    async def vote(self, ctx: CustomContext):
        view = discord.ui.View()
        style = discord.ButtonStyle.gray
        item = discord.ui.Button(style=style, emoji="<:dbl:757235965629825084>", label="Vote for me",
                                 url="https://stealthbot.xyz/vote.html")
        view.add_item(item=item)
        
        await ctx.send(content="Click the button below to vote for me.", view=view)

    @commands.command(
        help="Sends the support server of the bot.",
        aliases=['supportserver', 'support_server'])
    async def support(self, ctx: CustomContext):
        view = discord.ui.View()
        style = discord.ButtonStyle.gray
        item = discord.ui.Button(style=style, emoji="<:servers:895688440690147371>", label="Join support server",
                                 url="https://stealthbot.xyz/support.html")
        view.add_item(item=item)

        await ctx.send(content="Click the button below to join the support server.", view=view)

    @commands.group(
        invoke_without_command=True,
        help="<:rich_presence:895688440887246858> | Shows you a list of the bot's prefixes",
        aliases=['prefix'])
    async def prefixes(self, ctx: CustomContext):
        prefixes = await self.client.get_pre(self.client, ctx.message, raw_prefix=True)
        embed = discord.Embed(title="Here's a list of my prefixes for this server:",
                              description=ctx.me.mention + '\n' + '\n'.join(prefixes))

        return await ctx.send(embed=embed)

    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    @prefixes.command(
        name="add",
        help="Adds a prefix to the bot's prefixes",
        aliases=['a', 'create'])
    async def prefixes_add(self, ctx: CustomContext, new: str):
        old = list(await self.client.get_pre(self.client, ctx.message, raw_prefix=True))

        if len(new) > 50:
            raise errors.TooLongPrefix
            # return await ctx.send("Prefixes can only be up to 50 characters!")

        if len(old) > 30:
            raise errors.TooManyPrefixes
            # return await ctx.send("You can only have 20 prefixes!")

        if new not in old:
            old.append(new)
            await self.client.db.execute(
                "INSERT INTO guilds(guild_id, prefix) VALUES ($1, $2) "
                "ON CONFLICT (guild_id) DO UPDATE SET prefix = $2",
                ctx.guild.id, old)

            self.client.prefixes[ctx.guild.id] = old

            return await ctx.send(f"Successfully added `{new}` to the prefixes.\nMy prefixes are: `{'`, `'.join(old)}`")
        else:
            raise errors.PrefixAlreadyExists
            # return await ctx.send("That's already one of my prefixes!")

    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    @prefixes.command(
        name="remove",
        help="Removes a prefix from the bot's prefixes",
        aliases=['r', 'delete'])
    async def prefixes_remove(self, ctx: CustomContext, prefix: str):
        old = list(await self.client.get_pre(self.client, ctx.message, raw_prefix=True))

        if prefix in old:
            old.remove(prefix)
            await self.client.db.execute(
                "INSERT INTO guilds(guild_id, prefix) VALUES ($1, $2) "
                "ON CONFLICT (guild_id) DO UPDATE SET prefix = $2",
                ctx.guild.id, old)

            self.client.prefixes[ctx.guild.id] = old

            if prefix == "sb!":
                # raise errors.UnremoveablePrefix
                return
            else:
                pass

            return await ctx.send(f"Successfully removed `{prefix}`.\nMy prefixes are: `{'`, `'.join(old)}`")
        else:
            raise errors.PrefixDoesntExist
            # return await ctx.send(f"That is not one of my prefixes!")

    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    @prefixes.command(
        name="clear",
        help="Clears the bot's prefixes",
        aliases=['c', 'deleteall'])
    async def prefixes_clear(self, ctx: CustomContext):
        await self.client.db.execute(
            "INSERT INTO guilds(guild_id, prefix) VALUES ($1, $2) "
            "ON CONFLICT (guild_id) DO UPDATE SET prefix = $2",
            ctx.guild.id, None)
        self.client.prefixes[ctx.guild.id] = self.client.PRE
        return await ctx.send("Cleared prefixes!")

    @commands.command(
        help="<:greenTick:895688440690147370> Sends 2 random words, the author has 60 seconds to re-type the words. Copy pasting doesn't work.")
    # @helpers.is_sh_server()
    async def verify(self, ctx: CustomContext):
        with open("./data/verifyWords.txt", "r") as file:
            allText = file.read()
            wordsList = list(map(str, allText.split()))

        member = ctx.author
        stealth_hangout_role = 'Members'
        classicsmp_role = 'Members'

        correctAnswer = f"{random.choice(wordsList)}" + f" {random.choice(wordsList)}"
        character = "\u200b"

        embed = discord.Embed(title="Type the following text to verify:",
                              description=f"```\n{character.join(correctAnswer)}\n```")
        embed.set_footer(text=f"Don't try to copy paste, it won't work.")

        message = await ctx.send(embed=embed, footer=False)

        def check(m):
            return m.content.lower() == correctAnswer and m.channel.id == ctx.channel.id and m.author.id == ctx.author.id

        try:
            msg = await self.client.wait_for(event='message', check=check, timeout=60)

        except asyncio.TimeoutError:
            await message.delete()  # Deletes the bot's message | Please say ... to verify
            await ctx.send(f"It's been over 30 seconds, please try again by doing `{ctx.prefix}verify`",
                           delete_after=5.0)  # Replies to the author's message

            try:
                await ctx.message.delete()  # Deletes the author's message | -verify

            except:
                pass

        else:
            await message.delete()  # Deletes the bot's message | Please say ... to verify

            try:
                await msg.delete()  # Delete the member's answer

            except:
                pass

            role = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", ctx.guild.id)

            if not role['verify_role_id']:
                return await ctx.send(
                    f"This server doesn't have a verify role setup so I couldn't give you it.\nTo setup a verify role a server admin needs to do `{ctx.prefix}verifyrole set <role>`",
                    delete_after=5.0)

            else:
                role = ctx.guild.get_role(role['verify_role_id'])
                await member.add_roles(role)
                return await ctx.send("You've been successfully verified!", delete_after=5.0)

            try:
                await ctx.message.delete()  # Deletes the author's message | -verify

            except:
                pass

    @commands.group(
        invoke_without_command=True,
        help="<:greenTick:895688440690147370> | Verify commands. If no argument is specified it will show you the current verify role.",
        aliases=['verify_role', 'verify-role', 'vr'])
    @commands.has_permissions(manage_guild=True)
    @commands.bot_has_permissions(manage_guild=True)
    async def verifyrole(self, ctx: CustomContext):
        role = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", ctx.guild.id)

        if not role['verify_role_id']:
            return await ctx.send(
                f"This server doesn't have a verify role. To set it do `{ctx.prefix}verifyrole set <role>`")

        else:
            role = ctx.guild.get_role(role['verify_role_id'])
            return await ctx.send(f"The current verify role for this server is {role.mention}.")

    @verifyrole.command(
        name="set",
        help="Changes the verify role to the specified role.")
    async def _set(self, ctx: CustomContext, role: discord.Role):
        await self.client.db.execute(
            "INSERT INTO guilds (guild_id, verify_role_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET verify_role_id = $2",
            ctx.guild.id, role.id)
        await ctx.send(f"Successfully set the verify role for this server to {role.mention}.")

    @verifyrole.command(
        help="Removes the verify role")
    async def remove(self, ctx: CustomContext):
        await self.client.db.execute(
            "INSERT INTO guilds (guild_id, verify_role_id) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET verify_role_id = $2",
            ctx.guild.id, None)
        await ctx.send(f"Successfully removed the verify role for this server.")

    @commands.command(
        help="Takes a screenshot of a website",
        aliases=["ss"])
    @commands.is_nsfw()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def screenshot(self, ctx: CustomContext, link):
        URL_REGEX = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

        if not re.fullmatch(URL_REGEX, link):
            return await ctx.send("Invalid URL! Make sure you put `https://` infront of it.")

        else:
            embed = discord.Embed(title=f"{link}")
            embed.set_image(url=f"https://api.popcat.xyz/screenshot?url={link}")
            await ctx.send(embed=embed)
            
    @commands.command(
        help="Shows you the avatar history of the specified member.")
    async def avatarhistory(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        await ctx.trigger_typing()
        
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        async with self.client.session.get(f"https://api.popcat.xyz/screenshot?url=https://krix.xyz/discord/avatarhistory/{member.id}",
                                           allow_redirects=True) as request:
            embed = discord.Embed()
            embed.set_image(url=request.url)
            
            

            await ctx.send(embed=embed)

    @commands.command(
        help="Sends the specified suggestion to the bot developer.",
        aliases=['suggestion', 'botsuggest', 'bot_suggest', 'bot-suggest'],
        brief="suggest Filters to music")
    async def suggest(self, ctx: CustomContext, *, suggestion):
        if len(suggestion) > 1000:
            return await ctx.send("Your suggestion has exceeded the 1000-character limit.")
        
        channel = self.client.get_channel(914145974052614154)
        
        embed1 = discord.Embed(title=f"New suggestion from {ctx.author}", description=f"""
```
{suggestion}
```
                              """, color=discord.Color.yellow())
        
        embed1.set_footer(text=f"Not approved/denied.")
        
        if ctx.message.attachments:
            file = ctx.message.attachments[0]
            spoiler = file.is_spoiler()
            
            if not spoiler and file.url.lower().endswith(("png", "jpg", "jpeg", "webp", "gif")):
                embed1.set_image(url=file.url)
                
            else:
                embed1.add_field(name="Attachment", value=f"{f'||[{file.filename}]({file.url})||' if spoiler else f'[{file.filename}]({file.url})'}", inline=False)
        
        embed2 = discord.Embed(title=f"Information", description=f"""
Author: {ctx.author} **|** {ctx.author.mention} **|** {ctx.author.id}
Guild: {ctx.guild} **|** {ctx.guild.name} **|** {ctx.guild.id}
Guild owner: {ctx.guild.owner} **|** {ctx.guild.owner.mention} **|** {ctx.guild.owner.id}
                               """, color=discord.Color.blurple())
        
        await channel.send(embeds=[embed1, embed2])
        
        await ctx.send(f"Your suggestion has been sent to the owner!")
