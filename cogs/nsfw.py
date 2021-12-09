import time
import discord

from discord.ext import commands
from helpers.context import CustomContext


def setup(client):
    client.add_cog(NSFW(client))


class NSFW(commands.Cog):
    """NSFW commands, type 'gif' as the type, and it'll be animated."""

    def __init__(self, client):
        self.client = client
        self.hidden = True
        self.select_emoji = "<:underage:899622685930323978>"
        self.select_brief = "NSFW commands, type 'gif' as the type and it'll be animated."

    @commands.command(
        help=":underage: Sends a picture of a hentai ass.",
        aliases=['nsfw_ass', 'ass_nsfw'])
    @commands.is_nsfw()
    async def ass(self, ctx: CustomContext, type: str = None):
        await ctx.trigger_typing()

        start = time.perf_counter()

        request = await self.client.session.get('https://api.waifu.im/nsfw/ass/?gif=True' if str(type).lower() == 'gif' else 'https://api.waifu.im/nsfw/ass/')
        json = (await request.json())['images'][0]

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Ass", url=json['source'])
        embed.set_image(url=json['url'])
        embed.set_footer(text=f"Requested by {ctx.author} • {round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help=":underage: Sends a picture of an hentai ecchi.",
        aliases=['nsfw_ecchi', 'ecchi_nsfw'])
    @commands.is_nsfw()
    async def ecchi(self, ctx: CustomContext, type: str = None):
        await ctx.trigger_typing()

        start = time.perf_counter()

        request = await self.client.session.get('https://api.waifu.im/nsfw/ecchi/?gif=True' if str(type).lower() == 'gif' else 'https://api.waifu.im/nsfw/ecchi/')
        json = (await request.json())['images'][0]

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Ecchi", url=json['source'])
        embed.set_image(url=json['url'])
        embed.set_footer(text=f"Requested by {ctx.author} • {round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help=":underage: Sends a picture of an hentai ero.",
        aliases=['nsfw_ero', 'ero_nsfw'])
    @commands.is_nsfw()
    async def ero(self, ctx: CustomContext, type: str = None):
        await ctx.trigger_typing()

        start = time.perf_counter()

        request = await self.client.session.get('https://api.waifu.im/nsfw/ero/?gif=True' if str(type).lower() == 'gif' else 'https://api.waifu.im/nsfw/ero/')
        json = (await request.json())['images'][0]

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Ero", url=json['source'])
        embed.set_image(url=json['url'])
        embed.set_footer(text=f"Requested by {ctx.author} • {round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help=":underage: Sends a picture of an hentai.",
        aliases=['nsfw_hentai', 'hentai_nsfw'])
    @commands.is_nsfw()
    async def hentai(self, ctx: CustomContext, type: str = None):
        await ctx.trigger_typing()

        start = time.perf_counter()

        request = await self.client.session.get('https://api.waifu.im/nsfw/hentai/?gif=True' if str(type).lower() == 'gif' else 'https://api.waifu.im/nsfw/hentai/')
        json = (await request.json())['images'][0]

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Hentai", url=json['source'])
        embed.set_image(url=json['url'])
        embed.set_footer(text=f"Requested by {ctx.author} • {round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help=":underage: Sends a picture of an hentai maid.",
        aliases=['nsfw_maid', 'maid_nsfw', 'hentai_maid', 'maid_hentai', 'maidh'])
    @commands.is_nsfw()
    async def hmaid(self, ctx: CustomContext, type: str = None):
        await ctx.trigger_typing()

        start = time.perf_counter()

        request = await self.client.session.get('https://api.waifu.im/nsfw/hmaid/?gif=True' if str(type).lower() == 'gif' else 'https://api.waifu.im/hmaid/ero/')
        json = (await request.json())['images'][0]

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Hentai maid", url=json['source'])
        embed.set_image(url=json['url'])
        embed.set_footer(text=f"Requested by {ctx.author} • {round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help=":underage: Sends a picture of an hentai milf.",
        aliases=['nsfw_milf', 'milf_nsfw'])
    @commands.is_nsfw()
    async def milf(self, ctx: CustomContext, type: str = None):
        await ctx.trigger_typing()

        start = time.perf_counter()

        request = await self.client.session.get('https://api.waifu.im/nsfw/milf/?gif=True' if str(type).lower() == 'gif' else 'https://api.waifu.im/nsfw/milf/')
        json = (await request.json())['images'][0]

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Milf", url=json['source'])
        embed.set_image(url=json['url'])
        embed.set_footer(text=f"Requested by {ctx.author} • {round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help=":underage: Sends a picture of an hentai oppai.",
        aliases=['nsfw_oppai', 'oppai_nsfw'])
    @commands.is_nsfw()
    async def oppai(self, ctx: CustomContext, type: str = None):
        await ctx.trigger_typing()

        start = time.perf_counter()

        request = await self.client.session.get('https://api.waifu.im/nsfw/oppai/?gif=True' if str(type).lower() == 'gif' else 'https://api.waifu.im/nsfw/oppai/')
        json = (await request.json())['images'][0]

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Oppai", url=json['source'])
        embed.set_image(url=json['url'])
        embed.set_footer(text=f"Requested by {ctx.author} • {round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help=":underage: Sends a picture of an hentai oral.",
        aliases=['nsfw_oral', 'oral_nsfw'])
    @commands.is_nsfw()
    async def oral(self, ctx: CustomContext, type: str = None):
        await ctx.trigger_typing()

        start = time.perf_counter()

        request = await self.client.session.get('https://api.waifu.im/nsfw/oral/?gif=True' if str(type).lower() == 'gif' else 'https://api.waifu.im/nsfw/oral/')
        json = (await request.json())['images'][0]

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Oral", url=json['source'])
        embed.set_image(url=json['url'])
        embed.set_footer(text=f"Requested by {ctx.author} • {round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help=":underage: Sends a picture of an hentai paizuri.",
        aliases=['nsfw_paizuri', 'paizuri_nsfw'])
    @commands.is_nsfw()
    async def paizuri(self, ctx: CustomContext, type: str = None):
        await ctx.trigger_typing()

        start = time.perf_counter()

        request = await self.client.session.get('https://api.waifu.im/nsfw/paizuri/?gif=True' if str(type).lower() == 'gif' else 'https://api.waifu.im/nsfw/paizuri/')
        json = (await request.json())['images'][0]

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Paizuri", url=json['source'])
        embed.set_image(url=json['url'])
        embed.set_footer(text=f"Requested by {ctx.author} • {round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help=":underage: Sends a picture of an hentai selfie.",
        aliases=['nsfw_selfie', 'selfie_nsfw'])
    @commands.is_nsfw()
    async def selfie(self, ctx: CustomContext, type: str = None):
        await ctx.trigger_typing()

        start = time.perf_counter()

        request = await self.client.session.get('https://api.waifu.im/nsfw/selfie/?gif=True' if str(type).lower() == 'gif' else 'https://api.waifu.im/nsfw/selfie/')
        json = (await request.json())['images'][0]

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Selfie", url=json['source'])
        embed.set_image(url=json['url'])
        embed.set_footer(text=f"Requested by {ctx.author} • {round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help=":underage: Sends a picture of an hentai uniform.",
        aliases=['nsfw_uniform', 'uniform_nsfw'])
    @commands.is_nsfw()
    async def uniform(self, ctx: CustomContext, type: str = None):
        await ctx.trigger_typing()

        start = time.perf_counter()

        request = await self.client.session.get('https://api.waifu.im/nsfw/uniform/?gif=True' if str(type).lower() == 'gif' else 'https://api.waifu.im/nsfw/uniform/')
        json = (await request.json())['images'][0]

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Uniform", url=json['source'])
        embed.set_image(url=json['url'])
        embed.set_footer(text=f"Requested by {ctx.author} • {round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)
