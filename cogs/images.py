import io
import time
import random
import errors
import typing
import discord

from discord.ext import commands
from helpers.context import CustomContext
from asyncdagpi import ImageFeatures as imageFeatures

def setup(client):
    client.add_cog(Images(client))


class Images(commands.Cog):
    """Commands that manipulate/send images."""

    def __init__(self, client):
        self.client = client
        self.select_emoji = "<:frame_photo:899621559520595968>"
        self.select_brief = "Commands that manipulate/send images."

    async def jeyy_image_api(self, endpoint: str, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji, None]]):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        if isinstance(member, discord.Emoji):
            url = member.url

        elif isinstance(member, discord.PartialEmoji):
            url = member.url

        else:
            url = member.display_avatar.url

        request = await self.client.session.get(f"https://api.jeyy.xyz/image/{endpoint}", params={'image_url': url})
        return discord.File(io.BytesIO(await request.read()), f"{endpoint}.gif")

    # @commands.group(
    #     slash_command=True,
    #     invoke_without_command=True,
    #     help="<:frame_photo:899621559520595968> | Commands that show you images of animals",
    #     aliases=['i', 'images'])
    # async def image(self, ctx: CustomContext):
    #     if ctx.invoked_subcommand is None:
    #         await ctx.send_help(ctx.command)

    @commands.command(
        help="Sends a picture of a SFW waifu",
        aliases=['sfw_waifu', 'waifu_sfw'])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def waifu(self, ctx: CustomContext, type: str = None):
        await ctx.trigger_typing()
        
        start = time.perf_counter()

        request = await self.client.session.get('https://api.waifu.im/sfw/waifu/?gif=True' if str(type).lower() == 'gif' else 'https://api.waifu.im/sfw/waifu/')
        json = (await request.json())['images'][0]

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Waifu", url=json['source'], color=int(json['dominant_color'].replace('#', ''),16))
        embed.set_image(url=json['url'])
        embed.set_footer(text=f"Requested by {ctx.author} • {round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="Sends a picture of a SFW maid",
        aliases=['sfw_maid', 'maid_sfw'])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def maid(self, ctx: CustomContext, type: str = None):
        url = "https://api.waifu.im/sfw/maid/"

        if str(type).lower() == "gif":
            url = "https://api.waifu.im/sfw/maid/?gif=True"

        start = time.perf_counter()

        request = await self.client.session.get(url)
        json = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        dominant_color1 = str(json['tags'][0]['images'][0]['dominant_color']).replace('#', '')
        dominant_color = int(dominant_color1, 16)

        embed = discord.Embed(title="Maid", url=json['url'], color=dominant_color)
        embed.set_image(url=json['tags'][0]['images'][0]['url'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, color=False, footer=False)

    @commands.command(
        help="🐶 Shows a picture of a shiba",
        aliases=['shibe'])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def shiba(self, ctx: CustomContext):
        start = time.perf_counter()

        request = await self.client.session.get('https://shibe.online/api/shibes?count=1&urls=true&httpsUrls=true')
        json = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        titles = ["Bark!", "Arf!", "Woof!", "Bork!"]

        embed = discord.Embed(title=f"{random.choice(titles)}", url=json[0])
        embed.set_image(url=json[0])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="Shows a picture of a axolotl and a random fact about axolotls")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def axolotl(self, ctx: CustomContext):
        start = time.perf_counter()

        request = await self.client.session.get('https://axoltlapi.herokuapp.com/')
        json = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Axolotl", url=json['url'])
        embed.set_image(url=json['url'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))} • {json['facts']}")

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="🐱 Shows a picture of a cat and a random fact about cats")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def cat(self, ctx: CustomContext):
        request = await self.client.session.get('https://some-random-api.ml/img/cat')
        pictureJson = await request.json()
        request2 = await self.client.session.get('https://some-random-api.ml/facts/cat')
        factJson = await request2.json()

        embed = discord.Embed(title=f"{random.choice(['Meowww', 'Meoww!', 'Meowwwww'])}", url=pictureJson['link'])
        embed.set_image(url=pictureJson['link'])
        embed.set_footer(text=f"{factJson['fact']}")

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="🐶 Shows a picture of a dog and a random fact about dogs")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def dog(self, ctx: CustomContext):
        request = await self.client.session.get("https://random.dog/woof")
        if request.status != 200:
            return await ctx.send("No dog found :(")

        request2 = await self.client.session.get('https://some-random-api.ml/facts/dog')
        factJson = await request2.json()

        filename = await request.text()
        filesize = ctx.guild.filesize_limit if ctx.guild else 8388608
        if filename.endswith((".mp4", ".webm")):
            await ctx.trigger_typing()
            other = await self.client.session.get(f"https://random.dog/{filename}")
            if request.status != 200:
                raise errors.UnknownError

            if int(other.headers['Content-Length']) >= filesize:
                return await ctx.send(f"The video was too big to upload\nSee it here: **https://random.dog/{filename}**")

            return await ctx.send(f"Random fact about dogs: {factJson['fact']}", file=discord.File(io.BytesIO(await other.read()), filename=filename))

        else:
            embed = discord.Embed(title=f"{random.choice(['Bark!', 'Arf!', 'Woof!', 'Bork!'])}", url=f"https://random.dog/{filename}")
            embed.set_image(url=f"https://random.dog/{filename}")
            embed.set_footer(text=f"{factJson['fact']}")

            await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="🐼 Shows a picture of a panda and a random fact about pandas")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def panda(self, ctx: CustomContext):
        start = time.perf_counter()

        request = await self.client.session.get('https://some-random-api.ml/img/panda')
        pictureJson = await request.json()
        request2 = await self.client.session.get('https://some-random-api.ml/facts/panda')
        factJson = await request2.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Panda!", url=pictureJson['link'])
        embed.set_image(url=pictureJson['link'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))} • {factJson['fact']}")

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="🦊 Shows a picture of a fox and a random fact about foxes")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def fox(self, ctx: CustomContext):
        start = time.perf_counter()

        request = await self.client.session.get('https://some-random-api.ml/img/fox')
        pictureJson = await request.json()
        request2 = await self.client.session.get('https://some-random-api.ml/facts/fox')
        factJson = await request2.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Fox!", url=pictureJson['link'])
        embed.set_image(url=pictureJson['link'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))} • {factJson['fact']}")

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="🐦 Shows a picture of a bird and a random fact about birds")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def bird(self, ctx: CustomContext):
        start = time.perf_counter()
        
        request = await self.client.session.get('https://some-random-api.ml/img/bird')
        pictureJson = await request.json()
        request2 = await self.client.session.get('https://some-random-api.ml/facts/bird')
        factJson = await request2.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Bird!", url=pictureJson['link'])
        embed.set_image(url=pictureJson['link'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))} • {factJson['fact']}")

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="🐨 Shows a picture of a koala and a random fact about koalas")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def koala(self, ctx: CustomContext):
        start = time.perf_counter()

        request = await self.client.session.get('https://some-random-api.ml/img/koala')
        pictureJson = await request.json()
        request2 = await self.client.session.get('https://some-random-api.ml/facts/koala')
        factJson = await request2.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Koala!", url=pictureJson['link'])
        embed.set_image(url=pictureJson['link'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))} • {factJson['fact']}")

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="🦘 Shows a picture of a kangaroo and a random fact about kangaroos")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def kangaroo(self, ctx: CustomContext):
        start = time.perf_counter()

        request = await self.client.session.get('https://some-random-api.ml/img/kangaroo')
        pictureJson = await request.json()
        request2 = await self.client.session.get('https://some-random-api.ml/facts/kangaroo')
        factJson = await request2.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Kangaroo!", url=pictureJson['link'])
        embed.set_image(url=pictureJson['link'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))} • {factJson['fact']}")

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="🦝 Shows a picture of a raccoon and a random fact about racoons",
        aliases=['raccoon'])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def racoon(self, ctx: CustomContext):
        start = time.perf_counter()

        request = await self.client.session.get('https://some-random-api.ml/img/racoon')
        pictureJson = await request.json()
        request2 = await self.client.session.get('https://some-random-api.ml/facts/racoon')
        factJson = await request2.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Racoon!", url=pictureJson['link'])
        embed.set_image(url=pictureJson['link'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))} • {factJson['fact']}")

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="🐳 Shows a picture of a whale and a random fact about whales",
        aliases=['urmom', 'ur_mom', 'yourmom', 'your_mom'])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def whale(self, ctx: CustomContext):
        start = time.perf_counter()

        request = await self.client.session.get('https://some-random-api.ml/img/whale')
        pictureJson = await request.json()
        request2 = await self.client.session.get('https://some-random-api.ml/facts/whale')
        factJson = await request2.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Whale!", url=pictureJson['link'])
        embed.set_image(url=pictureJson['link'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))} • {factJson['fact']}")

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="Shows a picture of a pikachu")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def pikachu(self, ctx: CustomContext):
        start = time.perf_counter()

        request = await self.client.session.get('https://some-random-api.ml/img/pikachu')
        pictureJson = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Pikachu!", url=pictureJson['link'])
        embed.set_image(url=pictureJson['link'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="Sends a picture of a person that doesn't exist",
        aliases=['tpdne', 'person'])
    async def thispersondoesnotexist(self, ctx: CustomContext):
        async with ctx.typing():
            async with self.client.session.get('https://thispersondoesnotexist.com/image') as request:
                request = await request.read()
                buffer = io.BytesIO(request)
                file = discord.File(fp=buffer, filename="thispersondoesnotexist.png")
                await ctx.send(file=file)

    shit = ['abstract', 'balls', 'blur', 'boil', 'bomb', 'bonks', 'burn', 'canny', 'cartoon', 'clock', 'earthquake',
            'equations', 'explicit', 'gallery', 'glitch', 'half_invert', 'hearts', 'infinity', 'lamp', 'layers',
            'magnify', 'matrix', 'optics', 'paparazzi', 'patpat', 'print', 'radiate', 'rain', 'roll', 'scrapbook',
            'sensitive', 'shear', 'shock', 'shoot', 'sob', 'tv', 'warp', 'youtube']

    @commands.command()
    async def abstract(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.invoked_with}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.invoked_with}", ctx, member))

    @commands.command( # 14
        help="""
Draw your own blocks!
There are currently **25** codes corresponding to a unique block.
```
0 = blank block    g = Gold Block
1 = Grass Block    p = Purple Block
2 = Water          l = Leaf Block
3 = Sand Block     o = Log Block
4 = Stone block    c = Coal Block
5 = Wood Planks    d = Diamond Block
6 = Glass Block    v = Lava
7 = Redstone Block h = Hay Bale
8 = Iron Block     s = Snow Layer
9 = Brick Block    f = Wooden Fence
w = Redstone Dust  r = Redstone Lamp
e = Lever (off)    # = Lever (on)
k = Cake           y = Poppy
```""",
    brief="jeyy iso 401 133 332 - 1 0 5 - 6\njeyy iso 401 133 332 - 1 0 5 - 6") # 14
    async def iso(self, ctx: CustomContext, *, iso):
        request = await self.client.session.get("https://api.jeyy.xyz/isometric", params={'iso_code': f"{iso}"})
        buffer = io.BytesIO(await request.read())
        
        embed = discord.Embed(title="Isometric drawing")
        embed.set_image(url="attachment://isometric_draw.png")
        
        await ctx.send(embed=embed, file=discord.File(buffer, "isometric_draw.png"))