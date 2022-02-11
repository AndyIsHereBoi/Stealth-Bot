import re
import urllib
import random
import discord

from ._base import FunBase
from helpers import paginator
from discord.ext import commands, menus
from helpers.context import CustomContext


class UrbanDictionaryPageSource(menus.ListPageSource):
    BRACKETED = re.compile(r'(\[(.+?)])')

    def __init__(self, data):
        super().__init__(entries=data, per_page=1)

    def cleanup_definition(self, definition, *, regex=BRACKETED):
        def repl(m):
            word = m.group(2)
            return f"[{word}](http://{word.replace(' ', '-')}.urbanup.com)"

        ret = regex.sub(repl, definition)

        if len(ret) >= 2048:
            return ret[0:2000] + " [...]"

        return ret

    async def format_page(self, menu, entry):
        colors = [0x910023, 0xA523FF]
        color = random.choice(colors)

        maximum = self.get_max_pages()
        title = f'{entry["word"]}: {menu.current_page + 1} out of {maximum}' if maximum else entry['word']

        embed = discord.Embed(title=title, url=entry['permalink'],
                              description=self.cleanup_definition(entry['definition']), color=color)

        embed.set_footer(text=f'by {entry["author"]}')

        try:
            up = entry["thumbs_up"]
            down = entry["thumbs_down"]

        except KeyError:
            pass

        else:
            embed.add_field(name="Votes",
                            value=f"<:upvote:596577438461591562> {up}\n<:downvote:596577438952062977> {down}",
                            inline=False)

        try:
            date = discord.utils.parse_time(entry['written_on'][0:-1])

        except (ValueError, KeyError):
            pass

        else:
            embed.timestamp = date

        return embed

class Other(FunBase):
    
    @commands.command(
        help="Searches for the given query on urban dictionary.",
        brief="urban What is love?\nurban something")
    async def urban(self, ctx: CustomContext, *, word):
        async with self.bot.session.get("http://api.urbandictionary.com/v0/define", params={"term": word}) as resp:
            if resp.status != 200:
                embed = discord.Embed(description=f"Error: {resp.status} {resp.reason}")

                return await ctx.send(embed=embed)

            js = await resp.json()
            data = js.get("list", [])
            if not data:
                embed = discord.Embed(description="I couldn't find that on urban dictionary.")

                return await ctx.send(embed=embed)

        pages = paginator.ViewPaginator(UrbanDictionaryPageSource(data), ctx=ctx)
        await pages.start()

    @commands.command(
        help=":bookmark: Searches the specified word in the dictionary.")
    async def dictionary(self, ctx: CustomContext, *, word):
        request = await self.bot.session.get(
            f'https://some-random-api.ml/dictionary?word={urllib.parse.quote(word)}')
        json = await request.json()

        if json['error']:
            embed = discord.Embed(title=f"{json['word']}")
            embed.add_field(name=f"__**Definition**__", value=f"{json['definition']}")

            await ctx.send(embed=embed)

        else:
            return await ctx.send("Unknown word!")
    
    @commands.command(
        help=":8ball: Answers with yes or no to your question.",
        aliases=['8ball', 'magicball', 'magic_ball', 'eight_ball'])
    async def eightball(self, ctx: CustomContext):
        responses = ['It is certain.',
                    'It is decidedly so.',
                    'Without a doubt.',
                    'Yes - definitely.',
                    'You may rely on it.',
                    'As I see it, yes.',
                    'Most likely.',
                    'Outlook good.',
                    'Yes.',
                    'Signs point to yes.',
                    'Reply hazy, try again.',
                    'Ask again later.',
                    'Better not tell you now.',
                    'Cannot predict now.',
                    'Concentrate and ask again.',
                    'Don\'t count on it.',
                    'My reply is no.',
                    'My sources say no',
                    'Outlook not so good.',
                    'Very doubtful.',
                    ]

        await ctx.send(random.choice(responses))