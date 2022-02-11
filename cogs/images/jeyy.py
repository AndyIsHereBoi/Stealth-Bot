import io
import typing
import discord

from ._base import ImagesBase
from discord.ext import commands
from helpers.context import CustomContext

class Jeyy(ImagesBase):
    
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

        request = await self.bot.session.get(f"https://api.jeyy.xyz/image/{endpoint}", params={'image_url': url})
        return discord.File(io.BytesIO(await request.read()), f"{endpoint}.gif")

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