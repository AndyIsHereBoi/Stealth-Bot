import random
import discord

from discord.ext import commands


def setup(client):
    client.add_cog(CustomCog(client))


class CustomCog(commands.Cog):
    "Commands that are made by members that won a giveaway called 'Custom command for Stealth Bot'."

    def __init__(self, client):
        self.hidden = True
        self.client = client
        self.select_emoji = "<:tada:899622149533360189>"
        self.select_brief = "Commands that are made by members that won a giveaway called 'Custom command for Stealth Bot'."

    # @commands.group(
    #     invoke_without_command=True,
    #     help="<:tada:899622149533360189> | Commands that are made by members that won a giveaway called \"Custom command for Stealth Bot\"",
    #     aliases=['c', 'custom-cmds', 'customcmds', 'custom_cmds'])
    # async def custom(self, ctx):
    #     if ctx.invoked_subcommand is None:
    #         await ctx.send_help(ctx.command)

    # <@691733395109314661>

    @commands.command(
        help="Bonk.")
    async def cbonk(self, ctx, member: discord.Member = None):
        if member is not None:
            message = "just got bonked by"

        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
                message = "just got bonked by"
            else:
                member = ctx.author
                message = "just bonked themselves"

        await ctx.send(f"{member.mention} {message} {ctx.author.mention}. What a loser!")

    # <@547059830062448670>

    @commands.command(
        help="Tells you to have some pickles!")
    async def hungry(self, ctx):
        await ctx.send(f"then have some pickles!")

    # <@748105241857097759>

    @commands.command(
        help="Tells you to shut up cause stars is sleeping")
    async def stars(self, ctx):
        await ctx.send(f"shut up, stars is sleeping")

    # <@547059830062448670>

    @commands.command(
        help="Tells you if someone has good or bad luck")
    async def luck(self, ctx, member: discord.Member = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        responses = ["has bad luck!",
                     "has good luck!"]
        return await ctx.send(f"{member.mention} {random.choice(responses)}")

    # <@691733395109314661>

    @commands.command(
        help="Replies with wiggle wiggle wiggle",
        aliases=["jason-derulo", "jason_derulo"])
    async def jason(self, ctx):
        await ctx.send(f"Wiggle wiggle wiggle")

    # <@691733395109314661>

    @commands.command(
        help="Replies with she a runner she a track star")
    async def fast(self, ctx):
        await ctx.send(f"She a runner she a track star")

    # <@530472612871143476>

    @commands.command(
        help="Tells you if someone is weird")
    async def weird(self, ctx, member: discord.Member = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        responses = ["is weird",
                     "isn't weird"]

        await ctx.send(f"{member.mention} {random.choice(responses)}")

    # <@530472612871143476>

    @commands.command(
        help="Tells a fact about someone")
    async def fact(self, ctx, member: discord.Member = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        await ctx.send(f"Fun fact about {member.mention}: they're a loser.")

    # <@530472612871143476>

    @commands.command(
        help="Tells a lie about someone")
    async def lie(self, ctx, member: discord.Member = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        await ctx.send(f"{member.mention} isn't a dissapointment")

    # <@691733395109314661>

    @commands.command(
        help="Replies with Real smooth",
        aliases=["cha_cha", "cha-cha"])
    async def cha(self, ctx):
        await ctx.send(f"Real smooth")

    # <@530472612871143476>

    @commands.command(
        help="Pings ender, or does it..",
        aliases=["ping_ender", "ender_ping"])
    async def pingender(self, ctx):
        await ctx.send(f"you thought that would work")

    # <@530472612871143476>

    @commands.command(
        help="Cries")
    async def cry(self, ctx):
        await ctx.send(f"😢😢😢😢😢😢😢😢😢😢")

    # <@748105241857097759>

    @commands.command(description="Sends a GIF of a man eating a burger")
    async def burger(self, ctx):
        await ctx.send(f"https://tenor.com/view/burger-eating-burbger-asmr-sussy-gif-21505937")

    # <@530472612871143476>

    @commands.command(
        help="Replies with e")
    async def e(self, ctx):
        await ctx.send(f"e")

    # <@294137889514717185>

    @commands.command(
        help="EA Sports")
    async def ea(self, ctx):
        await ctx.send(f"sports")

    # <@555818548291829792>

    @commands.command(
        help="Replies with no u")
    async def nou(self, ctx):
        await ctx.send(f"no u")

    # <@351375279698083841>

    @commands.command(
        help="A friendly Hello from the bot",
        aliases=["h"])
    async def hello(self, ctx):
        await ctx.send(f"fuck off")

    # <@699737035715641384>

    @commands.command(
        help="idiot")
    async def me(self, ctx):
        await ctx.send(f"fuck you")
