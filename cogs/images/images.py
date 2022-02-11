import discord

from ._base import ImagesBase
from discord.ext import commands

class Images(ImagesBase):

    @commands.command()
    async def dog(self, ctx) -> discord.Message:
        request = await self.bot.session.get(f"https://some-random-api.ml/animal/dog")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def cat(self, ctx):
        request = await self.bot.session.get(f"https://some-random-api.ml/animal/cat")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def fox(self, ctx):
        request = await self.bot.session.get(f"https://some-random-api.ml/animal/fox")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def koala(self, ctx):
        request = await self.bot.session.get(f"https://some-random-api.ml/animal/koala")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def panda(self, ctx):
        request = await self.bot.session.get(f"https://some-random-api.ml/animal/panda----------")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def redpanda(self, ctx):
        request = await self.bot.session.get(f"https://some-random-api.ml/animal/redpanda")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def bird(self, ctx):
        request = await self.bot.session.get(f"https://some-random-api.ml/animal/birb")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def raccoon(self, ctx):
        request = await self.bot.session.get(f"https://some-random-api.ml/animal/raccoon")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def kangaroo(self, ctx):
        request = await self.bot.session.get(f"https://some-random-api.ml/animal/kangaroo")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def whale(self, ctx):
        request = await self.bot.session.get(f"https://some-random-api.ml/animal/cat")
        data = await request.json()

        embed = discord.Embed(description=str(data['fact']).replace(". ", ".\n"))
        embed.set_image(url=data['image'])

        return await ctx.send(embed=embed)

    @commands.command()
    async def duck(self, ctx):
        request = await self.bot.session.get(f"https://random-d.uk/api/v2/random")
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