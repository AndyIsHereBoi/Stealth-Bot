import discord

from discord.ext import commands
from helpers.context import CustomContext
from helpers.level_manager import get_user_data, get_rank, increase_xp
from easy_pil import Editor, Canvas, load_image_async, Font


def setup(client):
    client.add_cog(Levels(client))


class Levels(commands.Cog):
    """Levelling system."""

    def __init__(self, client):
        self.client = client
        self.hidden = True
        self.select_emoji = "<:lightningbolt:903706434791956561>"
        self.select_brief = "Levelling system."

    @commands.Cog.listener('on_message')
    async def levelling(self, message: discord.Message):
        if message.author.bot or not message.guild:
            return

        if message.guild.id == 799330949686231050 and message.channel.id == 920992165394530334:
            await increase_xp(self.client.db, message)

    @commands.command()
    async def rank(self, ctx: CustomContext, member: discord.Member = None):
        if not member:
            member = ctx.author

        user_data = await get_user_data(self.client.db, member.id, ctx.guild.id)
        rank = await get_rank(self.client.db, member.id, ctx.guild.id) # in case of using rank

        next_level_xp = (user_data["level"] + 1) * 100
        current_level_xp = user_data["level"] * 100
        xp_need = next_level_xp - current_level_xp
        xp_have = user_data["xp"] - current_level_xp

        percentage = (xp_need / 100) * xp_have

        ## Rank card
        background = Editor("./data/background.png")
        profile = await load_image_async(str(member.avatar.url))

        profile = Editor(profile).resize((150, 150)).circle_image()

        poppins = Font().poppins(size=40)
        poppins_small = Font().poppins(size=30)

        square = Canvas((500, 500), "#06FFBF")
        square = Editor(square)
        square.rotate(30, expand=True)

        background.paste(square.image, (600, -250))
        background.paste(profile.image, (30, 30))

        background.rectangle((30, 220), width=650, height=40, fill="white", radius=20)
        background.bar(
            (30, 220),
            max_width=650,
            height=40,
            percentage=percentage,
            fill="#FF56B2",
            radius=20,
        )
        background.text((200, 40), str(member), font=poppins, color="white")

        background.rectangle((200, 100), width=350, height=2, fill="#17F3F6")
        background.text(
            (200, 130),
            f"Level : {user_data['level']}"
            + f" XP : {user_data['xp']} / {(user_data['level'] + 1) * 100}",
            font=poppins_small,
            color="white",
        )

        await ctx.send(file=discord.File(fp=background.image_bytes, filename="card.png"))