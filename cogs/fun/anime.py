import typing
import discord

from ._base import FunBase
from discord.ext import commands
from helpers.context import CustomContext
from discord.ext.commands.cooldowns import BucketType

class Anime(FunBase):

    @commands.command(
        help="<:HUGGERS:896790320572940309> Hugs the specified member.")
    @commands.cooldown(1, 5, BucketType.user)
    async def hug(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.bot.session.get('https://api.waifu.pics/sfw/hug')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.display_name if ctx.author in ctx.guild.members else ctx.author.name} hugged {member.display_name if member in ctx.guild.members else member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help="<a:stealth_bot_pat:888354636258496522> Pats the specified member.")
    @commands.cooldown(1, 5, BucketType.user)
    async def pat(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.bot.session.get('https://api.waifu.pics/sfw/pat')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.display_name if ctx.author in ctx.guild.members else ctx.author.name} patted {member.display_name if member in ctx.guild.members else member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help=":kiss: Kisses the specified member.")
    @commands.cooldown(1, 5, BucketType.user)
    async def kiss(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.bot.session.get('https://api.waifu.pics/sfw/kiss')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.display_name if ctx.author in ctx.guild.members else ctx.author.name} kissed {member.display_name if member in ctx.guild.members else member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help=":tongue: Licks the specified member.")
    @commands.cooldown(1, 5, BucketType.user)
    async def lick(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.bot.session.get('https://api.waifu.pics/sfw/lick')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.display_name if ctx.author in ctx.guild.members else ctx.author.name} licked {member.display_name if member in ctx.guild.members else member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help="<:rooBulli:744346131324076072> Bullies the specified member.")
    @commands.cooldown(1, 5, BucketType.user)
    async def bully(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.bot.session.get('https://api.waifu.pics/sfw/bully')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.display_name if ctx.author in ctx.guild.members else ctx.author.name} bullied {member.display_name if member in ctx.guild.members else member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help="<a:aPES_Cuddle:896790837793529936> Cuddles the specified member.")
    @commands.cooldown(1, 5, BucketType.user)
    async def cuddle(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.bot.session.get('https://api.waifu.pics/sfw/cuddle')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.display_name if ctx.author in ctx.guild.members else ctx.author.name} cuddled {member.display_name if member in ctx.guild.members else member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help="<:slap:896790905133092944> Let's you slap someone!")
    @commands.cooldown(1, 5, BucketType.user)
    async def slap(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.bot.session.get('https://api.waifu.pics/sfw/slap')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.name} slapped {member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help="<:yeet:787677937746182174> Let's you yeet someone!")
    @commands.cooldown(1, 5, BucketType.user)
    async def yeet(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.bot.session.get('https://api.waifu.pics/sfw/yeet')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.name} yeeted {member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help="<a:aPES_HighFiveL:896791127385051156><a:aPES_HighFiveR:896791137434599524> Let's you high five someone!",
        aliases=['high_five'])
    @commands.cooldown(1, 5, BucketType.user)
    async def highfive(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.bot.session.get('https://api.waifu.pics/sfw/highfive')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.name} high fived {member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help="Let's you bite someone!")
    @commands.cooldown(1, 5, BucketType.user)
    async def bite(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.bot.session.get('https://api.waifu.pics/sfw/bite')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.name} bit {member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help="<a:kermitkill:896791354875711569> Let's you kill someone!")
    @commands.cooldown(1, 5, BucketType.user)
    async def kill(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.bot.session.get('https://api.waifu.pics/sfw/kill')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.name} killed {member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)