import random
import asyncio
import discord

from discord.ext import commands
from helpers.context import CustomContext
from helpers.ttt import LookingToPlay, TicTacToe
from helpers.helpers import generate_youtube_bar as bar


def setup(client):
    client.add_cog(Games(client))


class Games(commands.Cog):
    """Commands used to play games when you're bored!"""

    def __init__(self, client):
        self.client = client
        self.select_emoji = "<:video_game:899622306148675594>"
        self.select_brief = "Commands used to play games when you're bored!"

    @commands.command(
        help="RPG.",
        aliases=['fight', 'r'])
    async def rpg(self, ctx: CustomContext):
        items = ['wooden sword', 'stone sword', 'iron sword', 'diamond sword']
        argument = "wooden sword"
        authorItem = str(argument).lower()
        botItem = random.choice(items)
        joinedItems = ', '.join(items)

        if authorItem not in items:
            return await ctx.send(f"Unknown item! Here's a list of available items: {joinedItems}")

        if authorItem == "wooden sword":
            minAuthorDamage = 5
            maxAuthorDamage = 10

        elif authorItem == "stone sword":
            minAuthorDamage = 15
            maxAuthorDamage = 25

        elif authorItem == "iron sword":
            minAuthorDamage = 30
            maxAuthorDamage = 45

        elif authorItem == "diamond sword":
            minAuthorDamage = 45
            maxAuthorDamage = 60

        if botItem == "wooden sword":
            minBotDamage = 5
            maxBotDamage = 10

        elif botItem == "stone sword":
            minBotDamage = 15
            maxBotDamage = 25

        elif botItem == "iron sword":
            minBotDamage = 30
            maxBotDamage = 45

        elif botItem == "diamond sword":
            minBotDamage = 45
            maxBotDamage = 60

        authorHealth = 100
        botHealth = 100

        question1 = await ctx.confirm(message="Do you want to fight or cancel?",
                    delete_after_confirm=True, delete_after_timeout=True, delete_after_cancel=True,
                    buttons=(("⚔️", f"Fight", discord.ButtonStyle.gray),
                                    ("✖️", f"Cancel", discord.ButtonStyle.red)), timeout=15)

        if not question1:
            return await ctx.send("Okay, I've cancelled the RPG.")

        if question1:
            
            authorDamageDealt = random.randint(minAuthorDamage, maxAuthorDamage)
            botHealth = botHealth - authorDamageDealt
            roundedAuthor = round(authorHealth, -1)
            roundedBot = round(botHealth, -1)
            message = await ctx.send(f"""You've dealt **{authorDamageDealt}** damage to **Stealth Bot**!
__**{ctx.author.display_name}**__
HP: {bar(roundedAuthor, 100, 10)} ({authorHealth})
Item: {str(authorItem).title()}

__**Stealth Bot**__
HP: {bar(roundedBot, 100, 10)} ({botHealth})
Item: {str(botItem).title()}
            """)

            continue1 = await ctx.confirm(message="Do you want to continue?",
                    delete_after_confirm=True, delete_after_timeout=True, delete_after_cancel=True,
                    buttons=(("⚔️", f"Continue", discord.ButtonStyle.gray),
                                    ("✖️", f"Cancel", discord.ButtonStyle.red)), timeout=15)

            if not continue1:
                return await ctx.send("Okay, I've cancelled the RPG.")

            else:

                botDamageDealt = random.randint(minBotDamage, maxBotDamage)
                authorHealth = authorHealth - botDamageDealt
                roundedAuthor = round(authorHealth, -1)
                roundedBot = round(botHealth, -1)
                message = await message.edit(f"""Stealth Bot dealt **{botDamageDealt}** damage to **{ctx.author.display_name}**!
__**{ctx.author.display_name}**__
HP: {bar(roundedAuthor, 100, 10)} ({authorHealth})
Item: {str(authorItem).title()}

__**Stealth Bot**__
HP: {bar(roundedBot, 100, 10)} ({botHealth})
Item: {str(botItem).title()}
                """)
                
            question2 = await ctx.confirm(message="Do you want to fight or cancel?",
                        delete_after_confirm=True, delete_after_timeout=True, delete_after_cancel=True,
                        buttons=(("⚔️", f"Fight", discord.ButtonStyle.gray),
                                        ("✖️", f"Cancel", discord.ButtonStyle.red)), timeout=15)

            if not question2:
                return await ctx.send("Okay, I've cancelled the RPG.")

            if question2:
                authorDamageDealt = random.randint(minAuthorDamage, maxAuthorDamage)
                botHealth = botHealth - authorDamageDealt
                roundedAuthor = round(authorHealth, -1)
                roundedBot = round(botHealth, -1)
                message = await message.edit(f"""You've dealt **{authorDamageDealt}** damage to **Stealth Bot**!
__**{ctx.author.display_name}**__
HP: {bar(roundedAuthor, 100, 10)} ({authorHealth})
Item: {str(authorItem).title()}

__**Stealth Bot**__
HP: {bar(roundedBot, 100, 10)} ({botHealth})
Item: {str(botItem).title()}
                """)

                question3 = await ctx.confirm(message="Do you want to continue?",
                        delete_after_confirm=True, delete_after_timeout=True, delete_after_cancel=True,
                        buttons=(("⚔️", f"Continue", discord.ButtonStyle.gray),
                                        ("✖️", f"Cancel", discord.ButtonStyle.red)), timeout=15)

                if not question3:
                    return await ctx.send("Okay, I've cancelled the RPG.")

                else:

                    botDamageDealt = random.randint(minBotDamage, maxBotDamage)
                    authorHealth = authorHealth - botDamageDealt
                    roundedAuthor = round(authorHealth, -1)
                    roundedBot = round(botHealth, -1)
                    message = await message.edit(f"""Stealth Bot dealt **{botDamageDealt}** damage to **{ctx.author.display_name}**!
__**{ctx.author.display_name}**__
HP: {bar(roundedAuthor, 100, 10)} ({authorHealth})
Item: {str(authorItem).title()}

__**Stealth Bot**__
HP: {bar(roundedBot, 100, 10)} ({botHealth})
Item: {str(botItem).title()}
                    """)

    @commands.command(
        help="Plays rock, paper, scissors with you",
        aliases=['rps', 'rock_paper_scissors'])
    async def rockpaperscissors(self, ctx: CustomContext):
        validAnswers = ['rock', 'paper', 'scissors', 'win']
        botAnswers = ['rock', 'paper', 'scissors']

        def rock_paper_scissors(author_name, bot_name, author_answer, bot_answer):
            if author_answer == "rock" and bot_answer == "rock":
                return f":necktie: It's a tie!"
            elif author_answer == "rock" and bot_answer == "paper":
                return f":tada: __**{bot_name} WON!!!**__ :tada:"
            elif author_answer == "rock" and bot_answer == "scissors":
                return f":tada: __**{author_name} WON!!!**__ :tada:"

            elif author_answer == "paper" and bot_answer == "rock":
                return f":tada: __**{author_name} WON!!!**__ :tada:"
            elif author_answer == "paper" and bot_answer == "paper":
                return f":necktie:  It's a tie!"
            elif author_answer == "paper" and bot_answer == "scissors":
                return f":tada: __**{bot_name} WON!!!**__ :tada:"

            elif author_answer == "scissors" and bot_answer == "rock":
                return f":tada: __**{bot_name} WON!!!**__ :tada:"
            elif author_answer == "scissors" and bot_answer == "paper":
                return f":tada: __**{author_name} WON!!!**__ :tada:"
            elif author_answer == "scissors" and bot_answer == "scissors":
                return f":necktie: It's a tie!"

            else:
                return f"I have no idea who won."

        def check(m):
            return m.content.lower() in validAnswers and m.channel.id == ctx.channel.id and m.author.id == ctx.author.id

        await ctx.send("Pick one! `rock`, `paper`, `scissors`")

        try:
            msg = await self.client.wait_for(event='message', check=check, timeout=15)

        except asyncio.TimeoutError:
            return await ctx.send("It's been over 15 seconds, please try again by doing `-rpg`.")

        else:

            authorAnswer = msg.content.lower()
            botAnswer = random.choice(botAnswers)

            if msg.content.lower() == "win":
                authorAnswer = "rock"
                botAnswer = "scissors"

            result = rock_paper_scissors(author_name=ctx.author.name, bot_name="Stealth Bot", author_answer=authorAnswer,
                                         bot_answer=botAnswer)

            if result == f":tada: __**{ctx.author.name} WON!!!**__ :tada:":
                shortText = f"{str(authorAnswer).title()} beats {str(botAnswer).title()}"
                longText = f"{str(authorAnswer).title()} beats {str(botAnswer).title()} meaning {ctx.author.name} won."

            elif result == f":tada: __**Stealth Bot WON!!!**__ :tada:":
                shortText = f"{str(botAnswer).title()} beats {str(authorAnswer).title()}"
                longText = f"{str(botAnswer).title()} beats {str(authorAnswer).title()} meaning Stealth Bot won."

            else:
                shortText = f":necktie: It's a tie!"
                longText = f"{str(botAnswer).title()} doesn't beat {str(authorAnswer).title()} and {str(authorAnswer).title()} doesn't beat {str(botAnswer).title()} meaning it's a tie."

            embed = discord.Embed(title=result, description=f"""
{ctx.author.name}'s answer: {str(authorAnswer).title()}
Stealth Bot's answer: {str(botAnswer).title()}
[Hover over this text to see why]({msg.jump_url} '{longText}')
                                  """, timestamp=discord.utils.utcnow())
            embed.set_footer(text=shortText)

            await ctx.reply(embed=embed)

    @commands.command(
        help="Starts a Tic-Tac-Toe game",
        aliases=['ttt', 'tic'])
    async def tictactoe(self, ctx: CustomContext):
        embed = discord.Embed(description=f"🔎 {ctx.author.name} is looking to play Tic-Tac-Toe!")

        player1 = ctx.author
        view = LookingToPlay(timeout=120)
        view.ctx = ctx
        view.message = await ctx.send(embed=embed, view=view)
        await view.wait()
        player2 = view.value

        if player2:
            starter = random.choice([player1, player2])
            ttt = TicTacToe(ctx, player1, player2, starter=starter)
            ttt.message = await view.message.edit(content=f'#️⃣ {starter.name} goes first', view=ttt, embed=None)
            await ttt.wait()

    @commands.command(
        help="Starts a type-race game. You have 1 minute to type the given words. You can also specify how many words the bot should send. If no amount is specified it will default to 5.",
        aliases=['type-race', 'type_race', 'typeracer', 'type-racer', 'type_racer'])
    async def typerace(self, ctx: CustomContext, number: int = None):
        if number is None or number > 20:
            number = 5

        with open('./data/verifyWords.txt') as f:
            verifyWordsContext = f.read()
            verifyWords = list(map(str, verifyWordsContext.split()))

        words = []
        for word in verifyWords:
            words.append(word)

        doneWords = []

        for i in range(number):
            word = random.choice(words)
            doneWords.append(word)

        character = "\u200b"

        doneWords = " ".join(doneWords)

        embed = discord.Embed(title="Type-race", description=f"```\n{character.join(doneWords)}\n```")
        embed.set_footer(text="Don't try to copy paste. It won't work!")

        main = await ctx.send(embed=embed, footer=False)

        try:
            message = await self.client.wait_for("message", check=lambda msg: msg.channel == ctx.channel and msg.content == doneWords, timeout=60)

        except asyncio.TimeoutError:
            await main.edit(content="Time is over! No one won.")

        else:
            colors = [0x910023, 0xA523FF]
            color = random.choice(colors)

            embed = discord.Embed(title=f":tada: __**{message.author.name} WON!!!**__ :tada:",
                                  description=f"```\n{character.join(doneWords)}\n```", color=color)

            await message.add_reaction("🎉")
            await main.edit(embed=embed)
