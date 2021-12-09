import discord

from helpers import helpers
from discord.ext import commands
from helpers.context import CustomContext


def setup(client):
    client.add_cog(SignalPvP(client))


class SignalPvP(commands.Cog):
    "Commands that are helpful for the SignalPvP Minecraft Server."

    def __init__(self, client):
        self.client = client
        self.hidden = True
        self.select_emoji = "<:wooden_pickaxe:799344306271682580>"
        self.select_brief = "Commands that are helpful for the SignalPvP Minecraft Server."

    @commands.command(
        help="Shows you how to join the SignalPvP server on Bedrock Edition!",
        aliases=['address', 'server'])
    @helpers.is_spvp_server()
    async def joinsrv(self, ctx):
        embed = discord.Embed(title="How to join the server", description=f"""
For Java Edition it's very easy, you just need to enter `play.SignalPvP.xyz` as the server address.
On bedrock it's a bit more difficult. To see the explanation do `{ctx.prefix}bedrock`
                """)
        embed.set_footer(text=f"If you need any more help, contact one of the staff members.")

        await ctx.send(embed=embed)

    @commands.command(
        help="Shows you how to join the SignalPvP server on Bedrock Edition!",
        aliases=['pocket'])
    @helpers.is_spvp_server()
    async def bedrock(self, ctx):
        embed = discord.Embed(title="How to join on bedrock", description=f"""
First, you need to join the Minehut server using the information below.
After you've joined the Minehut server you need to do `/join SignalPvP`. This will redirect you to the actual SignalPvP server.
                """)
        embed.set_image(url="https://cdn.discordapp.com/attachments/737844511069438022/816053044915601448/unknown.png")
        embed.set_footer(text=f"If you need any more help, contact one of the staff members.")

        await ctx.send(embed=embed)