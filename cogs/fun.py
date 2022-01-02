import re
import time
import typing
import urllib
import random
import discord

from helpers.context import CustomContext
from helpers import paginator as paginator
from discord.ext import commands, menus, owoify
from discord.ext.commands.cooldowns import BucketType

def setup(client):
    client.add_cog(Fun(client))

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
        
        embed = discord.Embed(title=title, url=entry['permalink'], description=self.cleanup_definition(entry['definition']), color=color)
        
        embed.set_footer(text=f'by {entry["author"]}')

        try:
            up = entry["thumbs_up"]
            down = entry["thumbs_down"]
            
        except KeyError:
            pass
        
        else:
            embed.add_field(name="Votes", value=f"<:upvote:596577438461591562> {up}\n<:downvote:596577438952062977> {down}", inline=False)

        try:
            date = discord.utils.parse_time(entry['written_on'][0:-1])
            
        except (ValueError, KeyError):
            pass
        
        else:
            embed.timestamp = date

        return embed

def fancify(text, *, style: list, normal: list = None):
    normal = normal or ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    sub = dict(zip(normal, style))
    pattern = '|'.join(sorted(re.escape(k) for k in sub))

    return re.sub(pattern, lambda m: sub.get(m.group(0)), text, flags=re.IGNORECASE)


class Fun(commands.Cog):
    """Fun commands like meme, hug and more!"""

    def __init__(self, client):
        self.client = client
        self.select_emoji = "<:soccer:899621880120639509>"
        self.select_brief = "Fun commands like meme, hug and more!"

    async def reddit(self, ctx: CustomContext, reddit: str, hot: bool):
        start = time.perf_counter()
        request = await self.client.session.get(f"https://meme-api.herokuapp.com/gimme/{reddit}?hot={hot}")
        json = await request.json()

        try:
            if json['code']:
                return await ctx.send("Invalid sub-reddit!")

        except:
            if ctx.channel.is_nsfw() is False and json['nsfw'] is True:
                return await ctx.send("NSFW sub-reddit! Please use this command again is a NSFW channel.")

            end = time.perf_counter()
            ms = (end - start) * 1000

            embed = discord.Embed(title=json['title'])
            embed.set_image(url=json['url'] or discord.Embed.Empty)
            embed.set_footer(text=f"Requested by {ctx.author} • {reddit} • {round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

            return await ctx.send(embed=embed, footer=False)
        
    @commands.command(
        help=":frog: Sends a random meme from Reddit.")
    async def meme(self, ctx: CustomContext):
        await self.reddit(ctx, "dankmemes", True)
        
    @commands.command(
        help=":frog: Sends a random programmer meme from Reddit.",
        aliases=['programmer_meme', 'programmerhumor', 'programmer_humor', 'programmerhumour', 'programmer_humour', 'pm'])
    async def programmermeme(self, ctx: CustomContext):
        await self.reddit(ctx, "programmerhumor", True)

    @commands.command(
        help=":frog: Sends a random bad discord bot from Reddit.",
        aliases=['bdb', 'bad_discord_bots', 'baddiscordbot', 'bad_discord_bot'])
    async def baddiscrodbots(self, ctx: CustomContext):
        await self.reddit(ctx, "baddiscordbots", True)
        
    @commands.command(
        name="reddit",
        help=":frog: Sends a random post from the specified subreddit.")
    async def _reddit(self, ctx: CustomContext, reddit: str):
        await self.reddit(ctx, reddit, True)
        
    @commands.command(
        help=":bookmark: Searches the specified word in the dictionary.")
    async def dictionary(self, ctx: CustomContext, *, word):
        start = time.perf_counter()

        request = await self.client.session.get(f'https://some-random-api.ml/dictionary?word={urllib.parse.quote(word)}')
        json = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000
        
        if json['error']:
            embed = discord.Embed(title=f"{json['word']}")
            embed.add_field(name=f"__**Definition**__", value=f"{json['definition']}")
            embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))} •", icon_url=ctx.author.avatar.url)

            await ctx.send(embed=embed, footer=False)
            
        else:
            return await ctx.send("Unknown word!")
        
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
        help="<a:mOcK:913874174387322971> Mocks the given message.",
        brief="mock\nmock Your mom is straight")
    async def mock(self, ctx: CustomContext, *, message: typing.Union[str, discord.Message] = None):
        if message is None:
            if ctx.message.reference:
                message = ctx.message.reference.resolved.content

            else:
                message = "im not gay"

        await ctx.send(''.join(random.choice((str.upper, str.lower))(word) for word in message))
        
    @commands.command(
        help=":leftwards_arrow_with_hook: Reverses the given message.",
        brief="reverse\nreverse Your mom is straight")
    async def reverse(self, ctx: CustomContext, *, message: typing.Union[str, discord.Message] = None):
        if message is None:
            if ctx.message.reference:
                message = ctx.message.reference.resolved.content

            else:
                message = "im not gay"

        await ctx.send(message[::-1])

    @commands.command(
        help="<a:OwOUwU:913874401404018698> Owoifies the given message.",
        brief="owoify\nowoify Hello there!")
    async def owoify(self, ctx: CustomContext, *, message: typing.Union[str, discord.Message] = None):
        if message is None:
            if ctx.message.reference:
                message = ctx.message.reference.resolved.content

            else:
                message = "im not gay"

        await ctx.send(owoify.owoify(message))

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
        help=":clap: Claps the given message.",
        brief="clap\nclap Hello there!")
    async def clap(self, ctx: CustomContext, *, message: typing.Union[str, discord.Message] = None):
        if message is None:
            if ctx.message.reference:
                message = ctx.message.reference.resolved.content

            else:
                message = "im not gay"

        if len(message) >= 150:
            return await ctx.send("Your message exceeded the 150-character limit!")

        await ctx.send(f":clap: {discord.utils.remove_markdown(message.replace(' ', ' :clap: '))} :clap:")

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
        
    @commands.command(
        help="Searches for the given query on urban dictionary.",
        brief="urban What is love?\nurban something")
    async def urban(self, ctx: CustomContext, *, word):
        async with self.client.session.get("http://api.urbandictionary.com/v0/define", params={"term": word}) as resp:
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
        help="<:HUGGERS:896790320572940309> Hugs the specified member.")
    @commands.cooldown(1, 5, BucketType.user)
    async def hug(self, ctx: CustomContext, member: typing.Union[discord.Member, discord.User] = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.client.session.get('https://api.waifu.pics/sfw/hug')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.display_name if ctx.author in ctx.guild.members else ctx.author.name} hugged {member.display_name if member in ctx.guild.members else member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help="<a:stealth_bot_pat:888354636258496522> Pats the specified member.")
    @commands.cooldown(1, 5, BucketType.user)
    async def pat(self, ctx: CustomContext, member: discord.Member = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.client.session.get('https://api.waifu.pics/sfw/pat')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.display_name if ctx.author in ctx.guild.members else ctx.author.name} patted {member.display_name if member in ctx.guild.members else member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help=":kiss: Kisses the specified member.")
    @commands.cooldown(1, 5, BucketType.user)
    async def kiss(self, ctx: CustomContext, member: discord.Member = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.client.session.get('https://api.waifu.pics/sfw/kiss')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.display_name if ctx.author in ctx.guild.members else ctx.author.name} kissed {member.display_name if member in ctx.guild.members else member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help=":tongue: Licks the specified member.")
    @commands.cooldown(1, 5, BucketType.user)
    async def lick(self, ctx: CustomContext, member: discord.Member = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.client.session.get('https://api.waifu.pics/sfw/lick')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.display_name if ctx.author in ctx.guild.members else ctx.author.name} licked {member.display_name if member in ctx.guild.members else member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help="<:rooBulli:744346131324076072> Bullies the specified member.")
    @commands.cooldown(1, 5, BucketType.user)
    async def bully(self, ctx: CustomContext, member: discord.Member = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.client.session.get('https://api.waifu.pics/sfw/bully')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.display_name if ctx.author in ctx.guild.members else ctx.author.name} bullied {member.display_name if member in ctx.guild.members else member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help="<a:aPES_Cuddle:896790837793529936> Cuddles the specified member.")
    @commands.cooldown(1, 5, BucketType.user)
    async def cuddle(self, ctx: CustomContext, member: discord.Member = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.client.session.get('https://api.waifu.pics/sfw/cuddle')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.display_name if ctx.author in ctx.guild.members else ctx.author.name} cuddled {member.display_name if member in ctx.guild.members else member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help="<:slap:896790905133092944> Let's you slap someone!")
    @commands.cooldown(1, 5, BucketType.user)
    async def slap(self, ctx: CustomContext, member: discord.Member = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.client.session.get('https://api.waifu.pics/sfw/slap')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.name} slapped {member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help="<:yeet:787677937746182174> Let's you yeet someone!")
    @commands.cooldown(1, 5, BucketType.user)
    async def yeet(self, ctx: CustomContext, member: discord.Member = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.client.session.get('https://api.waifu.pics/sfw/yeet')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.name} yeeted {member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help="<a:aPES_HighFiveL:896791127385051156><a:aPES_HighFiveR:896791137434599524> Let's you high five someone!",
        aliases=['high_five'])
    @commands.cooldown(1, 5, BucketType.user)
    async def highfive(self, ctx: CustomContext, member: discord.Member = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.client.session.get('https://api.waifu.pics/sfw/highfive')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.name} high fived {member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help="Let's you bite someone!")
    @commands.cooldown(1, 5, BucketType.user)
    async def bite(self, ctx: CustomContext, member: discord.Member = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.client.session.get('https://api.waifu.pics/sfw/bite')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.name} bit {member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help="<a:kermitkill:896791354875711569> Let's you kill someone!")
    @commands.cooldown(1, 5, BucketType.user)
    async def kill(self, ctx: CustomContext, member: discord.Member = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        request = await self.client.session.get('https://api.waifu.pics/sfw/kill')
        json = await request.json()

        embed = discord.Embed(title=f"{ctx.author.name} killed {member.name}")
        embed.set_image(url=json['url'])

        await ctx.send(embed=embed)

    @commands.command(
        help="<:minecraft:895688440614649919> Let's you customize a minecraft achievement!",
        aliases=['minecraft_achievement', 'mc_achievement'])
    @commands.cooldown(1, 5, BucketType.user)
    async def achievement(self, ctx: CustomContext, *, text):
        text = urllib.parse.quote(text)

        async with self.client.session.get(f"https://api.cool-img-api.ml/achievement?text={text}",
                                           allow_redirects=True) as request:
            embed = discord.Embed()
            embed.set_image(url=request.url)

            await ctx.send(embed=embed)

    @commands.command(
        help="Sends a random shower thought!",
        aliases=['shower_thought', 'shower', 'shower-thought'])
    @commands.cooldown(1, 5, BucketType.user)
    async def showerthought(self, ctx: CustomContext):
        request = await self.client.session.get("https://api.popcat.xyz/showerthoughts")
        json = await request.json()

        try:
            embed = discord.Embed(title=f"{json['author']}:", description=json['result'])
            embed.set_footer(text=f"{json['upvotes']} upvotes • Requested by {ctx.author.display_name}")
            
            return await ctx.send(embed=embed, footer=False)
        
        except:
            return await ctx.send("Rate limited!")

    @commands.command(
        help="Sends a random roast")
    @commands.cooldown(1, 5, BucketType.user)
    async def roast(self, ctx: CustomContext, member: discord.Member = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        await ctx.send(f"{member.mention}, {await self.client.dagpi.roast()}")

    @commands.command(
        help="Sends a random joke")
    async def joke(self, ctx: CustomContext):
        await ctx.send(await self.client.dagpi.joke())

    @commands.command(
        help="Sends a random yo mama joke",
        aliases=['yomom', 'yo_mama', 'yo-mama', 'yo-mom', 'yo_mom'])
    async def yomama(self, ctx: CustomContext):
        await ctx.send(await self.client.dagpi.yomama())

    # @commands.command(
    #     help="<:oof:787677985468579880> OOF's the person you mentioned",
    #     aliases=['commitoof', 'commit_oof'])
    # async def oof(self, ctx: CustomContext, member : discord.Member=None):
    #     if member is None or member == ctx.author:
    #         responses = [f"{ctx.author.name} was killed in Electrical.",
    #         f"{ctx.author.name} failed math.",
    #         f"{ctx.author.name} rolled down a large hill.",
    #         f"{ctx.author.name} cried to death.",
    #         f"{ctx.author.name} smelt their own socks.",
    #         f"{ctx.author.name} forgot to stop texting while driving. Don't text and drive, kids.",
    #         f"{ctx.author.name} said Among Us in a public chat.",
    #         f"{ctx.author.name} stubbed their toe.",
    #         f"{ctx.author.name} forgot to grippen their shoes when walking down the stairs.",
    #         f"{ctx.author.name} wasn't paying attention and stepped on a mine.",
    #         f"{ctx.author.name} held a grenade for too long.",
    #         f"{ctx.author.name} got pwned by a sweaty tryhard.",
    #         f"{ctx.author.name} wore a black shirt in the summer.",
    #         f"{ctx.author.name} burned to a crisp.",
    #         f"{ctx.author.name} choked on a chicken nugget.",
    #         f"{ctx.author.name} forgot to look at the expiration date on the food.",
    #         f"{ctx.author.name} ran into a wall.",
    #         f"{ctx.author.name} shook a vending machine too hard.",
    #         f"{ctx.author.name} was struck by lightning.",
    #         f"{ctx.author.name} chewed 5 gum.",
    #         f"{ctx.author.name} ate too many vitamin gummy bears.",
    #         f"{ctx.author.name} tried to swim in lava. Why would you ever try to do that?"]
    #         return await ctx.send(f"{random.choice(responses)}")

    #     else:
    #         responses = [f"{ctx.author.name} exploded {member.name}.",
    #                     f"{ctx.author.name} shot {member.name}.",
    #                     f"{ctx.author.name} went ham on {member.name}.",
    #                     f"{ctx.author.name} betrayed and killed {member.name}.",
    #                     f"{ctx.author.name} sent {member.name} to Davy Jones' locker.",
    #                     f"{ctx.author.name} no scoped {member.name}.",
    #                     f"{ctx.author.name} said no u and killed {member.name}.",
    #                     f"{ctx.author.name} blew up {member.name} with a rocket.",
    #                     f"{ctx.author.name} pushed {member.name} off a cliff.",
    #                     f"{ctx.author.name} stabbed {member.name} to death.",
    #                     f"{ctx.author.name} slammed {member.name} with a chair.",
    #                     f"{ctx.author.name} recited a magic spell and killed {member.name}.",
    #                     f"{ctx.author.name} electrified {member.name}.",
    #                     f"{member.name} was slain by {ctx.author.name}.",
    #                     f"{ctx.author.name} burnt {member.name} alive.",
    #                     f"{ctx.author.name} buried {member.name}.",
    #                     f"{ctx.author.name} shoved {member.name}'s head underwater for too long.",
    #                     f"{ctx.author.name} slid a banana peel under {member.name}'s feet. They tripped and died...",
    #                     f"{ctx.author.name} got a headshot on {member.name}.",
    #                     f"{ctx.author.name} said a hilarious joke to {member.name} and died.",
    #                     f"{ctx.author.name} showed old Vicente0670 videos to {member.name} and died of cringe.",
    #                     f"{ctx.author.name} didn't buy Panda Express for {member.name} and exploded.",
    #                     f"{ctx.author.name} sent {member.name} to the Nether.",
    #                     f"{ctx.author.name} tossed {member.name} off an airplane.",
    #                     f"{ctx.author.name} broke {member.name}'s neck."]

    #         await ctx.send(f"{random.choice(responses)}")

    @commands.command(
        help="Fancifies the given text 𝓵𝓲𝓴𝓮 𝓽𝓱𝓲𝓼.",
        aliases=['fancy', 'ff'])
    async def fancify(self, ctx, *, text) -> discord.Message:
        return await ctx.send(fancify(text, style=['𝓪', '𝓫', '𝓬', '𝓭', '𝓮', '𝓯', '𝓰', '𝓱', '𝓲', '𝓳', '𝓴', '𝓵', '𝓶', '𝓷', '𝓸', '𝓹', '𝓺', '𝓻', '𝓼', '𝓽', '𝓾', '𝓿', '𝔀', '𝔁', '𝔂', '𝔃']))

    @commands.command(
        help="Makes the given text thicker 𝗹𝗶𝗸𝗲 𝘁𝗵𝗶𝘀.",
        aliases=['thick', 'thicc'])
    async def thickify(self, ctx, *, text) -> discord.Message:
        return await ctx.send(fancify(text, style=['𝗔', '𝗕', '𝗖', '𝗗', '𝗘', '𝗙', '𝗚', '𝗛', '𝗜', '𝗝', '𝗞', '𝗟', '𝗠', '𝗡', '𝗢', '𝗣', '𝗤', '𝗥', '𝗦', '𝗧', '𝗨', '𝗩', '𝗪', '𝗫', '𝗬', '𝗭', '𝗮', '𝗯', '𝗰', '𝗱', '𝗲', '𝗳', '𝗴', '𝗵', '𝗶', '𝗷', '𝗸', '𝗹', '𝗺', '𝗻', '𝗼', '𝗽', '𝗾', '𝗿', '𝘀', '𝘁', '𝘂', '𝘃', '𝘄', '𝘅', '𝘆', '𝘇', '𝟭', '𝟮', '𝟯', '𝟰', '𝟱', '𝟲', '𝟳', '𝟴', '𝟵', '𝟬'], normal=['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', 'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', '1', '2', '3', '4', '5', '6', '7', '8', '9', '0']))
