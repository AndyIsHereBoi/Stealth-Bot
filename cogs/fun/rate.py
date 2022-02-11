import typing
import random
import discord

from ._base import FunBase
from discord.ext import commands
from helpers.context import CustomContext

class Rate(FunBase):

    @commands.command(
        help=":rainbow: Shows you how gay the specified member is.",
        aliases=['gayrate', 'gay'],
        brief="gay\ngay @James Charles\ngay Hehe#9999")
    async def howgay(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author

            else:
                member = ctx.author

        embed = discord.Embed(title="gay rate machine", description=f"{'you are ' if member.id == ctx.author.id else f'{member.display_name if member in ctx.guild.members else member.name} is '} {random.randint(0, 1) if member.id == 564890536947875868 else random.randint(0, 100)}% gay :rainbow_flag:")

        await ctx.send(embed=embed)

    @commands.command(
        help=":hot_face: Shows you how horny the specified member is.",
        aliases=['hornyrate', 'howhorny'],
        brief="horny\nhorny @Johhny Sins\nhorny GayMen#1041")
    async def horny(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author

            else:
                member = ctx.author

        embed = discord.Embed(title="horny rate machine",
                              description=f"{'you are ' if member.id == ctx.author.id else f'{member.display_name if member in ctx.guild.members else member.name} is '} {random.randint(0, 100)}% horny :hot_face:")

        await ctx.send(embed=embed)

    @commands.command(
        help=":flushed: Shows you how sexy the specified member is.",
        aliases=['sexyrate', 'howsexy'],
        brief="sexy\nsexy @Dan\ngay Mike#1844")
    async def sexy(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author

            else:
                member = ctx.author

        embed = discord.Embed(title="sexy rate machine",
                              description=f"{'you are ' if member.id == ctx.author.id else f'{member.display_name if member in ctx.guild.members else member.name} is '} {random.randint(0, 100)}% sexy :flushed:")

        await ctx.send(embed=embed)

    @commands.command(
        help=":straight_ruler: Shows you how big someone is in cm.",
        aliases=['heightrate', 'howbig', 'howtall'],
        brief="height\nheight @Bee\nhorny Albert Einstein#9999")
    async def height(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is not None:
            message = f"{member.display_name if member in ctx.guild.members else member.name} is "

        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
                message = f"{member.display_name if member in ctx.guild.members else member.name} is "

            else:
                member = ctx.author
                message = "you are "

        embed = discord.Embed(title="height machine",
                              description=f"{'you are ' if member.id == ctx.author.id else f'{member.display_name if member in ctx.guild.members else member.name} is '} {random.randint(1, 8)} feet and {random.randint(1, 11)} inches tall :straight_ruler:")

        await ctx.send(embed=embed)

    @commands.command(
        help=":muscle: Shows you how skilled the specified member is.",
        aliases=['skillrate', 'howskilled'],
        brief="skill\nskill @Gamer\nskill EA Games#1854")
    async def skill(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author

            else:
                member = ctx.author

        embed = discord.Embed(title="skill rate machine",
                              description=f"{'you are ' if member.id == ctx.author.id else f'{member.display_name if member in ctx.guild.members else member.name} is '} {random.randint(0, 100)}% skilled :muscle:")

        await ctx.send(embed=embed)

    @commands.command(
        help=":brain: Shows you how smart the specified member is.",
        aliases=['smartrate', 'howsmart', 'iq', 'howmuchiq', 'iqrate'],
        brief="smart\nsmart @Meow\nsmart BigBrain#6942")
    async def smart(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author

            else:
                member = ctx.author

        embed = discord.Embed(title="smart rate machine",
                              description=f"{'you have ' if member.id == ctx.author.id else f'{member.display_name if member in ctx.guild.members else member.name} has '} {random.randint(0, 150)} IQ :brain:")

        await ctx.send(embed=embed)

    @commands.command(
        help=":mouse_three_button: Shows you how many CPS (Clicks per second) the specified member gets.",
        aliases=['cpsrate', 'howcps'],
        brief="cps\ncps @Peen\ncps HoldUp#5952")
    async def cps(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author

            else:
                member = ctx.author

        embed = discord.Embed(title="cps rate machine",
                              description=f"{'you get ' if member.id == ctx.author.id else f'{member.display_name if member in ctx.guild.members else member.name} gets '} {random.randint(0, 50)} CPS :mouse_three_button:")

        await ctx.send(embed=embed)

    @commands.command(
        help=":heart: Ships you with someone.")
    async def ship(self, ctx: CustomContext, member1: typing.Union[discord.Member, discord.User], member2: typing.Union[discord.Member, discord.User] = None):
        if member2 is None:
            if ctx.message.reference:
                member2 = ctx.message.reference.resolved.author
            else:
                member2 = ctx.author

        number1 = random.randint(0, 100)

        number2 = int(str(number1)[:-1] + '0')

        if number2 == 10:
            text = "<:notlikethis:596577155169910784> Yikes.. That's bad."
        elif number2 == 20:
            text = "<:blobsweatsip:759934644807401512> Maybe?.. I doubt thought."
        elif number2 == 30:
            text = "<:blobpain:739614945045643447> Hey it's not terrible.. It could be worse."
        elif number2 == 40:
            text = "<:monkaS:596577132063490060> Not bad!"
        elif number2 == 50:
            text = "<:flooshed:814095751042039828> Damn!"
        elif number2 == 60:
            text = "<:pogu2:787676797184770060> AYOOO POG"
        elif number2 == 70:
            text = "<:rooAww:747680003021471825> That has to be a ship!"
        elif number2 == 80:
            text = "<a:rooClap:759933903959228446> That's a ship!"
        elif number2 == 90:
            text = ":flushed: Wow!"
        elif number2 == 100:
            text = "<:drakeYea:596577437182197791> That's a ship 100%"
        else:
            text = "<:thrinking:597590667669274651> I don't know man.."

        await ctx.send(f"{text}\n{member1.display_name if member1 in ctx.guild.members else member1.name} & {member2.display_name if member2 in ctx.guild.members else member2.name}\n{number1}%")

    @commands.command(
        help=":eggplant: Shows the size of the specified member's pp.",
        aliases=['banana', 'eggplant', 'egg_plant'])
    async def pp(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        length = random.randint(10, 25)

        embed = discord.Embed(title=f"PP Size - {member.display_name if member in ctx.guild.members else member.name}",
                              description=f"8{'=' * length}D\n{member.display_name if member in ctx.guild.members else member.name}'s :eggplant: is {length} cm")

        await ctx.send(embed=embed)