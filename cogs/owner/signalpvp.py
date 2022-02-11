import discord

from helpers import helpers
from ._base import OwnerBase
from discord.ext import commands
from helpers.context import CustomContext

class SignalPvP(OwnerBase):

    @commands.command(
        help="Shows you how to join the FestivePvP server on Bedrock Edition!",
        aliases=['address', 'server'])
    @helpers.is_spvp_server()
    async def joinsrv(self, ctx: CustomContext):
        embed = discord.Embed(title="How to join the server", description=f"""
For Java Edition it's very easy, you just need to enter `play.FestivePvP.xyz` as the server address.
On bedrock it's a bit more difficult. To see the explanation do `{ctx.prefix}bedrock`
                """)
        embed.set_footer(text=f"If you need any more help, contact one of the staff members.")

        await ctx.send(embed=embed)

    @commands.command(
        help="Shows you how to join the SignalPvP server on Bedrock Edition!",
        aliases=['pocket'])
    async def bedrock(self, ctx: CustomContext):
        embed = discord.Embed(title="How to join on bedrock", description=f"""
First, you need to join the Minehut server using the information below.
After you've joined the Minehut server you need to do `/join FestivePvP`. This will redirect you to the actual FestivePvP server.
                """)
        embed.set_image(url="https://cdn.discordapp.com/attachments/737844511069438022/816053044915601448/unknown.png")
        embed.set_footer(text=f"If you need any more help, contact one of the staff members.")

        await ctx.send(embed=embed)