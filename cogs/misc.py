import re
import yaml
import errors
import random
import discord
import contextlib

from discord.ext import commands
from helpers.context import CustomContext

with open(r'/root/stealthbot/config.yaml') as file:
    full_yaml = yaml.load(file)
yaml_data = full_yaml

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
        item = discord.ui.Button(style=discord.ButtonStyle.gray, emoji="⭐", label="Recommended",
                                 url="https://discord.com/oauth2/authorize?client_id=760179628122964008&scope=applications.commands+bot&permissions=294171045078")
        view.add_item(item=item)
        
        item = discord.ui.Button(style=discord.ButtonStyle.gray, emoji="🛡️", label="All",
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
        item = discord.ui.Button(style=discord.ButtonStyle.gray, emoji="🌐", label="Website",
                                 url="https://stealthbot.xyz")
        view.add_item(item=item)
        
        await ctx.send("Click the button below to be redirected to the website.", view=view)
    
    @commands.command(
        help="Sends you a link where you can vote for the bot.",
        aliases=['topgg', 'top-gg', 'top_gg'])
    async def vote(self, ctx: CustomContext):
        view = discord.ui.View()
        item = discord.ui.Button(style=discord.ButtonStyle.gray, emoji="<:dbl:757235965629825084>", label="Vote for me",
                                 url="https://stealthbot.xyz/vote.html")
        view.add_item(item=item)
        
        await ctx.send("Click the button below to vote for me.", view=view)

    @commands.command(
        help="Sends the support server of the bot.",
        aliases=['supportserver', 'support_server'])
    async def support(self, ctx: CustomContext):
        view = discord.ui.View()
        item = discord.ui.Button(style=discord.ButtonStyle.gray, emoji="<:servers:895688440690147371>", label="Join support server",
                                 url="https://stealthbot.xyz/support.html")
        view.add_item(item=item)

        await ctx.send("Click the button below to join the support server.", view=view)

    @commands.group(
        invoke_without_command=True,
        help="<:rich_presence:895688440887246858> | Shows you a list of the bot's prefixes",
        aliases=['prefix'])
    async def prefixes(self, ctx: CustomContext):
        prefixes = await self.client.get_pre(self.client, ctx.message, raw_prefix=True)
        embed = discord.Embed(title="Here's a list of my prefixes for this server:", description=ctx.me.mention + '\n' + '\n'.join(prefixes))

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

        if len(old) > 30:
            raise errors.TooManyPrefixes

        if new not in old:
            old.append(new)
            await self.client.db.execute("INSERT INTO guilds(guild_id, prefix) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET prefix = $2",
                                         ctx.guild.id, old)

            self.client.prefixes[ctx.guild.id] = old

            return await ctx.send(f"Successfully added `{new}` to the prefixes.\nMy prefixes are: `{'`, `'.join(old)}`")

        else:
            raise errors.PrefixAlreadyExists

    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    @prefixes.command(
        name="remove",
        help="Removes a prefix from the bot's prefixes",
        aliases=['r', 'delete'])
    async def prefixes_remove(self, ctx: CustomContext, prefix: str) -> discord.Message:
        old = list(await self.client.get_pre(self.client, ctx.message, raw_prefix=True))

        if prefix in old:
            old.remove(prefix)
            await self.client.db.execute("INSERT INTO guilds(guild_id, prefix) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET prefix = $2",
                                         ctx.guild.id, old)

            self.client.prefixes[ctx.guild.id] = old

            if prefix == "sb!":
                return await ctx.send("You can't remove that prefix!")

            else:
                pass

            return await ctx.send(f"Successfully removed `{prefix}`.\nMy prefixes are: `{'`, `'.join(old)}`")

        else:
            raise errors.PrefixDoesntExist

    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    @prefixes.command(
        name="clear",
        help="Clears the bot's prefixes",
        aliases=['c', 'deleteall'])
    async def prefixes_clear(self, ctx: CustomContext) -> discord.Message:
        await self.client.db.execute("INSERT INTO guilds(guild_id, prefix) VALUES ($1, $2) ON CONFLICT (guild_id) DO UPDATE SET prefix = $2",
                                     ctx.guild.id, None)
        self.client.prefixes[ctx.guild.id] = self.client.PRE

        return await ctx.send("Cleared prefixes!")

    @commands.command(
        help="Takes a screenshot of a website",
        aliases=["ss"])
    @commands.is_nsfw()
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def screenshot(self, ctx: CustomContext, link) -> discord.Message:
        URL_REGEX = re.compile(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+")

        if not re.fullmatch(URL_REGEX, link):
            return await ctx.send("That's not an URL!")

        embed = discord.Embed(title=f"{link}")
        embed.set_image(url=f"https://api.popcat.xyz/screenshot?url={link}")
        return await ctx.send(embed=embed)

    @commands.command()
    @commands.cooldown(1, 5, commands.BucketType.member)
    async def verify(self, ctx: CustomContext) -> discord.Message:
        record = await self.client.db.fetchrow("SELECT * FROM guilds WHERE guild_id = $1", ctx.guild.id)

        if not record['verify_role_id']:
            return await ctx.send(f"This server doesn't have a verify role. To set it do `{ctx.prefix}verifyrole set <role>`")

        role = ctx.guild.get_role(record['verify_role_id'])

        def check(m):
            return m.author.id == ctx.author.id and m.guild.id == ctx.guild.id and m.channel.id == ctx.channel.id

        request = await self.client.session.get('https://api.dagpi.xyz/data/captcha', headers={'Authorization': yaml_data['DAGPI_TOKEN']})
        json = await request.json()

        embed = discord.Embed(title="Solve the captcha below to verify yourself!")
        embed.set_image(url=json['image'])

        msg = await ctx.send(embed=embed)
        message = await self.client.wait_for("message", check=check)

        if discord.utils.remove_markdown(message.content.lower()) != json['answer']:
            with contextlib.suppress(discord.Forbidden, discord.HTTPException): await msg.delete()
            with contextlib.suppress(discord.Forbidden, discord.HTTPException): await message.delete()
            with contextlib.suppress(discord.Forbidden, discord.HTTPException): await ctx.message.delete()

            return await ctx.send(f"<:redTick:596576672149667840> {ctx.author.mention}, you've failed the captcha!", allowed_mentions=discord.AllowedMentions(users=True), delete_after=10)

        with contextlib.suppress(discord.Forbidden, discord.HTTPException): await msg.delete()
        with contextlib.suppress(discord.Forbidden, discord.HTTPException): await message.delete()
        with contextlib.suppress(discord.Forbidden, discord.HTTPException): await ctx.message.delete()

        await ctx.send(f"<:greenTick:596576670815879169> {ctx.author.mention}, you've succeeded the captcha!", allowed_mentions=discord.AllowedMentions(users=True), delete_after=10)

        try: return await ctx.author.add_roles(role)
        except: return await ctx.send(f"<:greenTick:596576670815879169> {ctx.author.mention}, I was unable to give you the role. Tell the server administrators about this.", allowed_mentions=discord.AllowedMentions(users=True), delete_after=10)
