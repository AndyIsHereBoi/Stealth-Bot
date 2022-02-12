import re
import random
import typing
import discord

from ._base import FunBase
from discord.ext import commands, owoify
from helpers.context import CustomContext

def text(text, *, style: list, normal: list = None):
    normal = normal or ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r',
                        's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    sub = dict(zip(normal, style))
    pattern = '|'.join(sorted(re.escape(k) for k in sub))

    return re.sub(pattern, lambda m: sub.get(m.group(0)), text, flags=re.IGNORECASE)

class Text(FunBase):

    @commands.command(
        help="Fancifies the given text 𝓵𝓲𝓴𝓮 𝓽𝓱𝓲𝓼.",
        aliases=['fancy', 'ff'])
    async def fancify(self, ctx, *, text) -> discord.Message:
        return await ctx.send(text(text, style=['𝓪', '𝓫', '𝓬', '𝓭', '𝓮', '𝓯', '𝓰', '𝓱', '𝓲', '𝓳', '𝓴', '𝓵', '𝓶', '𝓷', '𝓸', '𝓹', '𝓺', '𝓻', '𝓼', '𝓽', '𝓾', '𝓿', '𝔀', '𝔁', '𝔂', '𝔃']))

    @commands.command(
        help="Makes the given text thicker 𝗹𝗶𝗸𝗲 𝘁𝗵𝗶𝘀.",
        aliases=['thick', 'thicc'])
    async def thickify(self, ctx, *, text) -> discord.Message:
        return await ctx.send(text(text, style=['𝗔', '𝗕', '𝗖', '𝗗', '𝗘', '𝗙', '𝗚', '𝗛', '𝗜', '𝗝', '𝗞', '𝗟', '𝗠', '𝗡', '𝗢', '𝗣', '𝗤', '𝗥', '𝗦', '𝗧', '𝗨', '𝗩', '𝗪', '𝗫', '𝗬', '𝗭', '𝗮', '𝗯', '𝗰', '𝗱', '𝗲', '𝗳', '𝗴', '𝗵', '𝗶', '𝗷', '𝗸', '𝗹', '𝗺', '𝗻', '𝗼', '𝗽', '𝗾', '𝗿', '𝘀', '𝘁', '𝘂', '𝘃', '𝘄', '𝘅', '𝘆', '𝘇', '𝟭', '𝟮', '𝟯', '𝟰', '𝟱', '𝟲', '𝟳', '𝟴', '𝟵', '𝟬'], normal=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']))

    @commands.command(
        help="<a:mOcK:913874174387322971> Mocks the given message.",
        brief="mock\nmock Your mom is straight")
    async def mock(self, ctx: CustomContext, *, message: typing.Union[str, discord.Message] = None):
        if message is None:
            if ctx.message.reference:
                message = ctx.message.reference.resolved.content

            else:
                message = "im not gay"

        await ctx.send(''.join(random.choice((str.upper, str.lower))(word) for word in message))

    @commands.command(
        help=":leftwards_arrow_with_hook: Reverses the given message.",
        brief="reverse\nreverse Your mom is straight")
    async def reverse(self, ctx: CustomContext, *, message: typing.Union[str, discord.Message] = None):
        if message is None:
            if ctx.message.reference:
                message = ctx.message.reference.resolved.content

            else:
                message = "im not gay"

        await ctx.send(message[::-1])

    @commands.command(
        help="<a:OwOUwU:913874401404018698> Owoifies the given message.",
        brief="owoify\nowoify Hello there!")
    async def owoify(self, ctx: CustomContext, *, message: typing.Union[str, discord.Message] = None):
        if message is None:
            if ctx.message.reference:
                message = ctx.message.reference.resolved.content

            else:
                message = "im not gay"

        await ctx.send(owoify.owoify(message))

    @commands.command(
        help=":clap: Claps the given message.",
        brief="clap\nclap Hello there!")
    async def clap(self, ctx: CustomContext, *, message: typing.Union[str, discord.Message] = None):
        if message is None:
            if ctx.message.reference:
                message = ctx.message.reference.resolved.content

            else:
                message = "im not gay"

        if len(message) >= 150:
            return await ctx.send("Your message exceeded the 150-character limit!")

        await ctx.send(f":clap: {discord.utils.remove_markdown(message.replace(' ', ' :clap: '))} :clap:")