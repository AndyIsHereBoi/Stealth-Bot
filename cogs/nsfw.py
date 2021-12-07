import time
import discord

from discord.ext import commands


def setup(client):
    client.add_cog(NSFW(client))


class NSFW(commands.Cog):
    """NSFW commands, type 'gif' as the type, and it'll be animated."""

    def __init__(self, client):
        self.client = client
        self.hidden = True
        self.select_emoji = "<:underage:899622685930323978>"
        self.select_brief = "NSFW commands, type 'gif' as the type and it'll be animated."

    @commands.command(aliases=['nsfw_ass', 'ass_nsfw'])
    @commands.is_nsfw()
    async def ass(self, ctx, type: str = None):
        url = "https://api.waifu.im/nsfw/ass/"

        if str(type).lower() == "gif":
            url = "https://api.waifu.im/nsfw/ass/?gif=True"

        start = time.perf_counter()

        request = await self.client.session.get(url)
        json = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        dominant_color1 = str(json['tags'][0]['images'][0]['dominant_color']).replace('#', '')
        dominant_color = int(dominant_color1, 16)

        embed = discord.Embed(title="Ass", url=json['tags'][0]['images'][0]['url'], color=dominant_color)
        embed.set_image(url=json['tags'][0]['images'][0]['url'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, color=False, footer=False)

    @commands.command(aliases=['nsfw_ecchi', 'ecchi_nsfw'])
    @commands.is_nsfw()
    async def ecchi(self, ctx, type: str = None):
        url = "https://api.waifu.im/nsfw/ass/"

        if str(type).lower() == "gif":
            url = "https://api.waifu.im/nsfw/ecchi/?gif=True"

        start = time.perf_counter()

        request = await self.client.session.get(url)
        json = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        dominant_color1 = str(json['tags'][0]['images'][0]['dominant_color']).replace('#', '')
        dominant_color = int(dominant_color1, 16)

        embed = discord.Embed(title="Ecchi", url=json['tags'][0]['images'][0]['url'], color=dominant_color)
        embed.set_image(url=json['tags'][0]['images'][0]['url'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, color=False, footer=False)

    @commands.command(aliases=['nsfw_ero', 'ero_nsfw'])
    @commands.is_nsfw()
    async def ero(self, ctx, type: str = None):
        url = "https://api.waifu.im/nsfw/ero/"

        if str(type).lower() == "gif":
            url = "https://api.waifu.im/nsfw/ero/?gif=True"

        start = time.perf_counter()

        request = await self.client.session.get(url)
        json = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        dominant_color1 = str(json['tags'][0]['images'][0]['dominant_color']).replace('#', '')
        dominant_color = int(dominant_color1, 16)

        embed = discord.Embed(title="Ero", url=json['tags'][0]['images'][0]['url'], color=dominant_color)
        embed.set_image(url=json['tags'][0]['images'][0]['url'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, color=False, footer=False)

    @commands.command(aliases=['nsfw_hentai', 'hentai_nsfw'])
    @commands.is_nsfw()
    async def hentai(self, ctx, type: str = None):
        url = "https://api.waifu.im/nsfw/hentai/"

        if str(type).lower() == "gif":
            url = "https://api.waifu.im/nsfw/ero/?gif=True"

        start = time.perf_counter()

        request = await self.client.session.get(url)
        json = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        dominant_color1 = str(json['tags'][0]['images'][0]['dominant_color']).replace('#', '')
        dominant_color = int(dominant_color1, 16)

        embed = discord.Embed(title="Hentai", url=json['tags'][0]['images'][0]['url'], color=dominant_color)
        embed.set_image(url=json['tags'][0]['images'][0]['url'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, color=False, footer=False)

    @commands.command(aliases=['maidh', 'nsfw_maid', 'maid_nsfw'])
    @commands.is_nsfw()
    async def hmaid(self, ctx, type: str = None):
        url = "https://api.waifu.im/nsfw/hmaid/"

        if str(type).lower() == "gif":
            url = "https://api.waifu.im/nsfw/hmaid/?gif=True"

        start = time.perf_counter()

        request = await self.client.session.get(url)
        json = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        dominant_color1 = str(json['tags'][0]['images'][0]['dominant_color']).replace('#', '')
        dominant_color = int(dominant_color1, 16)

        embed = discord.Embed(title="Maid", url=json['tags'][0]['images'][0]['url'], color=dominant_color)
        embed.set_image(url=json['tags'][0]['images'][0]['url'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, color=False, footer=False)

    @commands.command(aliases=['nsfw_milf', 'milf_nsfw'])
    @commands.is_nsfw()
    async def milf(self, ctx, type: str = None):
        url = "https://api.waifu.im/nsfw/milf/"

        if str(type).lower() == "gif":
            url = "https://api.waifu.im/nsfw/milf/?gif=True"

        request = await self.client.session.get(url)
        json = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        dominant_color1 = str(json['tags'][0]['images'][0]['dominant_color']).replace('#', '')
        dominant_color = int(dominant_color1, 16)

        embed = discord.Embed(title="Milf", url=json['tags'][0]['images'][0]['url'], color=dominant_color)
        embed.set_image(url=json['tags'][0]['images'][0]['url'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, color=False, footer=False)

    @commands.command(aliases=['nsfw_oppai', 'oppai_nsfw'])
    @commands.is_nsfw()
    async def oppai(self, ctx, type: str = None):
        url = "https://api.waifu.im/nsfw/oppai/"

        if str(type).lower() == "gif":
            url = "https://api.waifu.im/nsfw/oppai/?gif=True"

        start = time.perf_counter()

        request = await self.client.session.get(url)
        json = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        dominant_color1 = str(json['tags'][0]['images'][0]['dominant_color']).replace('#', '')
        dominant_color = int(dominant_color1, 16)

        embed = discord.Embed(title="Oppai", url=json['tags'][0]['images'][0]['url'], color=dominant_color)
        embed.set_image(url=json['tags'][0]['images'][0]['url'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, color=False, footer=False)

    @commands.command(aliases=['nsfw_oral', 'oral_nsfw'])
    @commands.is_nsfw()
    async def oral(self, ctx, type: str = None):
        url = "https://api.waifu.im/nsfw/oral/"

        if str(type).lower() == "gif":
            url = "https://api.waifu.im/nsfw/oral/?gif=True"

        start = time.perf_counter()

        request = await self.client.session.get(url)
        json = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        dominant_color1 = str(json['tags'][0]['images'][0]['dominant_color']).replace('#', '')
        dominant_color = int(dominant_color1, 16)

        embed = discord.Embed(title="Oral", url=json['tags'][0]['images'][0]['url'], color=dominant_color)
        embed.set_image(url=json['tags'][0]['images'][0]['url'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, color=False, footer=False)

    @commands.command(aliases=['nsfw_paizuri', 'paizuri_nsfw'])
    @commands.is_nsfw()
    async def paizuri(self, ctx, type: str = None):
        url = "https://api.waifu.im/nsfw/paizuri/"

        if str(type).lower() == "gif":
            url = "https://api.waifu.im/nsfw/paizuri/?gif=True"

        start = time.perf_counter()

        request = await self.client.session.get(url)
        json = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        dominant_color1 = str(json['tags'][0]['images'][0]['dominant_color']).replace('#', '')
        dominant_color = int(dominant_color1, 16)

        embed = discord.Embed(title="Paizuri", url=json['tags'][0]['images'][0]['url'], color=dominant_color)
        embed.set_image(url=json['tags'][0]['images'][0]['url'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, color=False, footer=False)

    @commands.command(aliases=['nsfw_selfies', 'selfies_nsfw', 'selfie', 'nsfw_selfie', 'selfie_nsfw'])
    @commands.is_nsfw()
    async def selfies(self, ctx, type: str = None):
        url = "https://api.waifu.im/nsfw/selfie/"

        if str(type).lower() == "gif":
            url = "https://api.waifu.im/nsfw/selfie/?gif=True"

        start = time.perf_counter()

        request = await self.client.session.get(url)
        json = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        dominant_color1 = str(json['tags'][0]['images'][0]['dominant_color']).replace('#', '')
        dominant_color = int(dominant_color1, 16)

        embed = discord.Embed(title="Selfie", url=json['tags'][0]['images'][0]['url'], color=dominant_color)
        embed.set_image(url=json['tags'][0]['images'][0]['url'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, color=False, footer=False)

    @commands.command(aliases=['nsfw_uniform', 'uniform_nsfw'])
    @commands.is_nsfw()
    async def uniform(self, ctx, type: str = None):
        url = "https://api.waifu.im/nsfw/uniform/"

        if str(type).lower() == "gif":
            url = "https://api.waifu.im/nsfw/uniform/?gif=True"

        start = time.perf_counter()

        request = await self.client.session.get(url)
        json = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        dominant_color1 = str(json['tags'][0]['images'][0]['dominant_color']).replace('#', '')
        dominant_color = int(dominant_color1, 16)

        embed = discord.Embed(title="Uniform", url=json['tags'][0]['images'][0]['url'], color=dominant_color)
        embed.set_image(url=json['tags'][0]['images'][0]['url'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, color=False, footer=False)
