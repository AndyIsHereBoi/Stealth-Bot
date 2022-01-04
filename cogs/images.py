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

        self._cd = commands.CooldownMapping.from_cooldown(1, 10, commands.BucketType.user)

    async def cog_check(self, ctx):
        bucket = self._cd.get_bucket(ctx.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            raise commands.CommandOnCooldown(bucket, retry_after)
            return True
        return False

    async def jeyy_image_api(self, endpoint: str, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji, None]]):
        await ctx.trigger_typing()

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

    async def dagpi_image_api(self, feature: imageFeatures, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji, None]], **kwargs):
        await ctx.trigger_typing()

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

        return await ctx.dagpi(member, feature=feature, **kwargs)

    @commands.command()
    async def dog(self, ctx) -> discord.Message:
        request = await self.client.session.get(f"https://some-random-api.ml/animal/dog")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def cat(self, ctx):
        request = await self.client.session.get(f"https://some-random-api.ml/animal/cat")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def fox(self, ctx):
        request = await self.client.session.get(f"https://some-random-api.ml/animal/fox")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def koala(self, ctx):
        request = await self.client.session.get(f"https://some-random-api.ml/animal/koala")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def panda(self, ctx):
        request = await self.client.session.get(f"https://some-random-api.ml/animal/panda----------")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def redpanda(self, ctx):
        request = await self.client.session.get(f"https://some-random-api.ml/animal/redpanda")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def bird(self, ctx):
        request = await self.client.session.get(f"https://some-random-api.ml/animal/birb")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def raccoon(self, ctx):
        request = await self.client.session.get(f"https://some-random-api.ml/animal/raccoon")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def kangaroo(self, ctx):
        request = await self.client.session.get(f"https://some-random-api.ml/animal/kangaroo")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def whale(self, ctx):
        request = await self.client.session.get(f"https://some-random-api.ml/animal/cat")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def duck(self, ctx):
        request = await self.client.session.get(f"https://random-d.uk/api/v2/random")
        data = await request.json()

        embed = discord.Embed()
        embed.set_image(url=data['url'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def bunny(self, ctx):
        return

    @commands.command()
    async def penguin(self, ctx):
        return

    @commands.command()
    async def lizard(self, ctx):
        return

    @commands.command(
        help=":piccasso:",
        aliases=['abs'],
        usage="[member|user|emoji]")
    async def abstract(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help=":flushed:",
        aliases=['ball'],
        usage="[member|user|emoji]")
    async def balls(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="I need glasses, no I really do.",
        usage="[member|user|emoji]")
    async def blur(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="THIS IS HOT.",
        usage="[member|user|emoji]")
    async def boil(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="KABOOOM",
        usage="[member|user|emoji]")
    async def bomb(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="BONK.",
        aliases=['bonk'],
        usage="[member|user|emoji]")
    async def bonks(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="THIS IS FINE.",
        aliases=['hell', 'elmo', 'flame'],
        usage="[member|user|emoji]")
    async def burn(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Cannifies the edges.",
        usage="[member|user|emoji]")
    async def canny(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Cartoonifies",
        usage="[member|user|emoji]")
    async def cartoon(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Tik tok",
        usage="[member|user|emoji]")
    async def clock(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="START RUNNING ALREADY!",
        aliases=['eq'],
        usage="[member|user|emoji]")
    async def earthquake(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Confusion.",
        aliases=['equation', 'equ'],
        usage="[member|user|emoji]")
    async def equations(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Parental advisory required.",
        usage="[member|user|emoji]")
    async def explicit(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="A moving gallery.",
        aliases=['gal'],
        usage="[member|user|emoji]")
    async def gallery(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Glitchifies",
        usage="[member|user|emoji]")
    async def glitch(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Inverts halfly.",
        aliases=['hi', 'halfinvert', 'half-invert'],
        usage="[member|user|emoji]")
    async def half_invert(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Love's in the air.",
        aliases=['love', 'loves', 'heart'],
        usage="[member|user|emoji]")
    async def hearts(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Never ending.",
        aliases=['infinite', 'inf'],
        usage="[member|user|emoji]")
    async def infinity(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="A flickering lamp.",
        usage="[member|user|emoji]")
    async def lamp(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Shows layers with a mirror.",
        aliases=['layer', 'lay'],
        usage="[member|user|emoji]")
    async def layers(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="For detectives.",
        aliases=['magnifying'],
        usage="[member|user|emoji]")
    async def magnify(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Some weird stuff man",
        usage="[member|user|emoji]")
    async def matrix(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="An optical distortion.",
        aliases=['optic'],
        usage="[member|user|emoji]")
    async def optics(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Yes.",
        aliases=['pprz', 'ppz'],
        usage="[member|user|emoji]")
    async def paparazzi(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Pat pat.",
        aliases=['pats', 'pet', 'petpet'],
        usage="[member|user|emoji]")
    async def patpat(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Uh don't use this we are out of ink.",
        usage="[member|user|emoji]")
    async def print(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Radiates.",
        aliases=['rad'],
        usage="[member|user|emoji]")
    async def radiate(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Get yo umbrella out.",
        usage="[member|user|emoji]")
    async def rain(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="What you know about **rolling* down in the deep",
        usage="[member|user|emoji]")
    async def roll(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command( # TODO: Fix this
        help="Makes a scrapbook styled gif from the given text. Max length is 40.",
        aliases=['scrap'],
        usage="[member|user|emoji]")
    async def scrapbook(self, ctx, member: typing.Optional[typing.Union[str]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Sensetive.",
        usage="[member|user|emoji]")
    async def sensitive(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Shear the sheep.",
        usage="[member|user|emoji]")
    async def shear(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="OH MY GOD I AM REALLY SHOCKED!",
        usage="[member|user|emoji]")
    async def shock(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Creates a very touching sort movie.",
        usage="[member|user|emoji]")
    async def shoot(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help=":sob::sob::sob:",
        usage="[member|user|emoji]")
    async def sob(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command(
        help="Warps.",
        usage="[member|user|emoji]")
    async def warp(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

    @commands.command( # TODO: Fix this too
        help="For detectives",
        aliases=['yt'],
        usage="[member|user|emoji]")
    async def youtube(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.gif")
        return await ctx.send(embed=embed, file=await self.jeyy_image_api(f"{ctx.command.name}", ctx, member))

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

    @commands.command(
        help="Warps.",
        usage="[member|user|emoji]")
    async def colors(self, ctx, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]] = None) -> discord.Message:
        embed = discord.Embed().set_image(url=f"attachment://{ctx.command.name}.png")
        return await ctx.send(embed=embed, file=await self.dagpi_image_api(imageFeatures.colors(), ctx, member))