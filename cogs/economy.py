import errors
import random
import discord
import asyncio

from discord.ext import commands, menus
from helpers.context import CustomContext
from discord.ext.menus.views import ViewMenuPages
from discord.ext.commands.cooldowns import BucketType
from helpers.decorators import has_started, has_ref_started


def setup(client):
    client.add_cog(Economy(client))


class RichestUsersEmbedPage(menus.ListPageSource):
    def __init__(self, data, guild):
        self.data = data
        self.guild = guild
        super().__init__(data, per_page=10)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        colors = [0x910023, 0xA523FF]
        color = random.choice(colors)

        embed = discord.Embed(title=f"Richest users in {self.guild.name}",
                              description="\n".join(f'{i + 1}. {v}' for i, v in enumerate(entries, start=offset)),
                              timestamp=discord.utils.utcnow(), color=color)
        embed.set_footer(text=f"Remember this is wallets not banks")

        if self.guild.icon:
            embed.set_thumbnail(url=self.guild.icon.url)

        return embed


class Economy(commands.Cog):
    """Economy commands"""

    def __init__(self, client):
        self.client = client
        self.select_emoji = "<:money_with_wings:903620152606744586>"
        self.select_brief = "Economy commands."

    @commands.command(
        help="Shows the specified member's balance. If no member is specified it will default to the author.",
        aliases=['bal'])
    @has_started()
    async def balance(self, ctx: CustomContext, member: discord.Member = None):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        record = await self.client.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", member.id)
        wallet = record['wallet']
        bank = record['bank']
        bank_limit = record['bank_limit']
        embed = discord.Embed(title=f"{member.name}'s balance", description=f"""
Wallet: {wallet:,} :dollar:
Bank: {bank:,}/{bank_limit:,} :dollar:
        """)

        await ctx.send(embed=embed)

    @commands.command(
        help="Shows the money leaderboard.",
        aliases=['lb'])
    async def leaderboard(self, ctx: CustomContext):
        database = await self.client.db.fetch("SELECT * FROM economy ORDER BY wallet DESC LIMIT 10")
        topTen = []
        number = 0

        for user in database:
            member = ctx.guild.get_member(database[number]['user_id'])
            wallet = database[number]['wallet']
            number = number + 1
            if member is not None:
                topTen.append(f"**{format(wallet, ',')}** - {member.display_name}#{member.discriminator}")

        paginator = ViewMenuPages(source=RichestUsersEmbedPage(topTen, ctx.guild), clear_reactions_after=True)
        page = await paginator._source.get_page(0)
        kwargs = await paginator._get_kwargs_from_page(page)

        if paginator.build_view():
            paginator.message = await ctx.send(embed=kwargs['embed'], view=paginator.build_view())

        else:
            paginator.message = await ctx.send(embed=kwargs['embed'])

        await paginator.start(ctx)

    @commands.command(
        help="Withdraws the specified amount of money from your bank to your wallet.",
        aliases=['wd', 'withdrawal', 'with'])
    @has_started()
    async def withdraw(self, ctx: CustomContext, amount: int):
        record = await self.client.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", ctx.author.id)

        if amount <= 0:
            return await ctx.send("Number has to be more than 0.")

        if record['bank'] < amount:
            return await ctx.send("You don't have that much money in your bank.")

        await self.client.db.execute(
            """UPDATE economy SET wallet = wallet + $1, bank = bank - $1 WHERE user_id = $2;""", amount, ctx.author.id)

        embed = discord.Embed(title=f"Successfully withdrawn {amount} :dollar: from your bank", description=f"""
__**New balance**__
Wallet: {record['wallet'] + amount}
Bank: {record['bank'] - amount}
                              """)

        await ctx.send(embed=embed)

    @commands.command(
        help="Deposits the specified amount of money from your wallet to your bank.",
        aliases=['depo', 'dep'])
    @has_started()
    async def deposit(self, ctx: CustomContext, amount: int):
        record = await self.client.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", ctx.author.id)

        if amount <= 0:
            return await ctx.send("Number has to be more than 0.")

        if record['wallet'] < amount:
            return await ctx.send("You don't have that much money in your wallet.")

        current_bank_money = record['bank']

        if current_bank_money == record['bank_limit']:
            return await ctx.send(
                "Your bank is full, you can't deposit more money unless you upgrade it using banknotes.")

        elif (record['bank_limit'] - current_bank_money) <= amount:
            can_deposit: int = record['bank_limit'] - current_bank_money
            await self.client.db.execute("UPDATE economy SET wallet = wallet - $1, bank = bank + $1 WHERE user_id = $2;", can_deposit, ctx.author.id)

            embed = discord.Embed(
                title=f"Successfully deposited {can_deposit} :dollar: to your bank and now your bank is full!",
                description=f"""
__**New balance**__
Wallet: {record['wallet'] - can_deposit}
Bank: {record['bank'] + can_deposit}
                              """)
            return await ctx.send(embed=embed)

        elif (record['bank_limit'] - current_bank_money) > amount:
            can_deposit: int = record['bank_limit'] - current_bank_money
            await self.client.db.execute("UPDATE economy SET wallet = wallet - $1, bank = bank + $1 WHERE user_id = $2;", amount, ctx.author.id)
            
            embed = discord.Embed(
                title=f"Successfully deposited {can_deposit} :dollar: to your bank and now your bank is full!",
                description=f"""
__**New balance**__
Wallet: {record['wallet'] - amount}
Bank: {record['bank'] + amount}
                              """)
            return await ctx.send(embed=embed)

        else:
            raise errors.UnknownError("Something wrong happened")

    @commands.command(
        help="With this command you can beg people for some coins. Sometimes You get nothing")
    @has_started()
    @commands.cooldown(1, 3, BucketType.member)
    async def beg(self, ctx: CustomContext):
        record = await self.client.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", ctx.author.id)

        rn = random.randint(0, 200)

        if rn == 0:  # if the number is 0
            responses = [
                "Jared | OMG YOU DO NOTHING RIGHT",
                "David | Seriously? What is this?",
                "Kelly | How do you mess this up?",
                "Jordan | Can do you stuff right?",
                "Karen | YOU'RE BAD!!1!111! LET ME SPEAK TO YOUR MANAGER",
                "Paul | I'm going to go home now...",
                "Molly | Why are you wasting your time here?",
                "Sarah | I give up.",
                "Isaac | You're getting fired for that.",
                "Kim Jong Un | Get a job you hippy!",
            ]

        elif rn < 10:  # if the number is below 10 (1, 2, 3, 4, 5, 6, 7, 8, 9)
            responses = [
                f"Bob | Am Bob, Take {rn} money or die.",
                f"Kaki the Cat | Meow meow meow Meow! (You gained {rn} coins!)",
                f"Jeff Bezos | I’ll give you {rn} if you tell me where is Bill Gates…",
                f"Lester | Sussy baka, I shall give you {rn} for being sussy.",
                f"Shadowsen Gaming | I'll pay you {rn} if you let me suck your dick.",
                f"Tom | Meow {rn} Meow.",
                f"Owen | I am poor but u are a poor noob so take my {rn} dollars.",
                f"MrBeast | YOU JUST WON {rn} *not* THOUSAND DOLLARS",
                f"Greg | Are you a hooker? Take my {rn} coins and be at my place at 11.",
                f"Karen | Oh great, another hippy. get off the streets. take my {rn} money",
                f"Jesus | You made bad decesions. Get off the streets. Take {rn} to get started.",
                f"Mr. Clean | Clean out my bank account! Take {rn} quickly!",
            ]

        elif rn < 20:  # if the number is below 20 (10, 11, 12, 13, 14, 15, 16, 17, 18, 19)
            responses = [
                f"Juan | Oh boy, you're doing fine! Here's {rn} dollars.",
                f"John | ayo kid good work, here's {rn} dollars.",
                f"Terrence | That's your work you'll put in at least. Take {rn} dollars.",
                f"Shawn | Nice work! Take {rn} dollars.",
                f"Chris | Yes, good work on that. Here's {rn} dollars.",
                f"Jordan | mmm, yes. excellent. you earn {rn} dollars. but don't get cocky.",
                f"Carl | nice job, takes these cool {rn} dollars.",
                f"Martin | this is acceptable. you deserve {rn} dollars.",
                f"Paul | yeah whatever. here's {rn} dollars.",
                f"Dealer | Give the stuff in the bag. HURRY IT UP. Thanks, here is your {rn} coins of pay.",
            ]

        elif rn < 30:  # if the number is below 30 (20, 21, 22, 23, 24, 25, 26, 27, 28, 29)
            responses = [
                f"Wann | So poor. Take {rn} dollars.",
                f"Mia | Do a little dance for me. I'll give ya {rn} dollars.",
                f"Willy | If you want to beg like this, then do me a favor. Lick the dirty mannequin's balls for {rn} dollars.",
                f"Lenard | Sucky kid on the street, do I want to give you money? Only for one thing. Go inside that store and steal a bag of chips for me. I will get ya {rn} dollars if you are up for the challenge.",
                f"Squid | Pop my suction cups for {rn} dollars.",
                f"Discord | Want nitro? It's {rn} dollars. I'll give ya it if you are willing to hack my friend, Ender2K89.",
                f"Ilona | I'll give you a chance to win {rn} dollars in my tournament!",
                f"Sang-Woo | I'll beat you to death. I'll pay you {rn} dollars to leave the tournament.",
                f"That fart you've been holding in | I'm ABOUT TO RIP! IV BEEN HOLDING IN {rn} DOLLARS JUST FOR THIS MOMENT",
                f"Dr. Phil | Need help? Take {rn} dollars. It's dangerous to go alone.",
            ]

        elif rn < 40:  # if the number is below 40 (30, 31, 32, 33, 34, 35, 36, 37, 38, 39)
            responses = [
                f"Da Baby | Fresh meat??? I'll give you {rn} dollars if I can lick you.",
                f"Lady Gaga | Ga, go away. I will give you {rn} coins to leave.",
                f"Sans  | You rattle my bones because you are ugly. Take {rn} to get that fixed.",
                f"T-Series | Who's best? Yeah, I am. Take {rn} for guessing correct.",
                f"Thanos | *snaps {rn} dollars into existence,* take that. It's the least I can do.",
                f"Bongo Cat | *taps on bongo, spawns {rn} dollars* take that! *Winks*.",
                f"Obama | Guess my last name. Got it? It's Obama. You guessed right! Take {rn} dollars.",
                f"Flo from Progressive | Did you know I can save you {rn} dollars on car insurance? Take that money for yourself.",
                f"Chungus | You are lucky I didn't suck in your hard-earned money. You can keep your mesley {rn} dollars.",
                f"Your mom | IS YOUR ROOM CLEAN? Good job. Take {rn} for the accomplishment.",
            ]

        elif rn < 50:  # if the number is below 50 (40, 41, 42, 43, 44, 45, 46, 47, 48, 49)
            responses = [
                f"Jeramia | Whatcha willing to do for {rn}? I'll see you later... Stay here.",
                f"Taylor Swift | Swiftly drain my bank account! I only have {rn} though.",
                f"Donald Trump | I spent all my money on gambling. Take the last of my money. I only have {rn} dollars left...",
                f"Shreck | GET OUT OF MY SWAMPPP. Unless you can do me a favor, GET ON YOUR KNEES, BOY! *gained {rn} dollars.",
                f"Rick Astley | :musical_note: You know the rules, and so do I... Want to be in my music video? I'll give you {rn} to join!",
                f"Dank Memer | A competing bot? That's no good. I'll pay you {rn} to use us instead.",
                f"drunk lady | You wana EaT toNIght??? CoMe to My pLACE at 12. ILL gIGVE YoU {rn} doLLARs",
                f"Timmy Turner | I wish that I was rich! *Gets only {rn} dollars.* I'm not rich?",
                f"Elon Musk | Take a ride to space! It will gain you popularity, and I will give you {rn} dollars!!!",
                f"Pennywise | Come closer. I will give you your balloon back, and {rn} coins!",
            ]

        elif rn < 60:  # if the number is below 60 (50, 51, 52, 53, 54, 55, 56, 57, 58, 59)
            responses = [
                f"Imposter | SHHH!!! don't tell. I'll give you {rn} dollars.",
                f"TikToker | I have 12000 million followers!!! If you have less, ill pay you out of pity. Oh? Only have 3? HA stupid idiot. Take {rn} to get started.",
                f"Granny | Oh honey, come, come, I'll give you some money. You won't die on my watch. Take {rn} dollars.",
                f"Joe | Who's Joe? JOE MAMMA! How do you fall for that? Take {rn}. I feel bad for you.",
                f"Math Teacher | Class, what is `1*9+2939-5238*3924/128481+8?`? I'll give you {rn} coins if you can find it. Good job! Its `2796.02372335`!",
                f"Fat Woman |  Kid, you are so skinny. Take {rn} dollars to fatten up!",
                f"Wrath | Who am I, you ask? Well, you see, my backstory goes like this. I was born, then went to school and dropped out. Join my gang for {rn} dollars.",
                f"Evil Granny | GET OVER HERE BEFORE I BEAT YOU, BOY. I'm going to the cops, I thought to myself. *Gained {rn} for reporting evil granny.*",
                f"Spooky Scary Skeleton | How thin are you?? I bet you will turn to bones like I did. Take {rn} to not die.",
                f"Mr. Beast | want to be in my big YouTuber collab? Join for {rn} dollars!!!",
            ]

        elif rn < 70:  # if the number is below 70 (60, 61, 62, 63, 64, 65, 66, 67, 68, 69)
            responses = [
                f"Gary | Wow, you work above average! Here's {rn} dollars.",
                f"Toby | sheeeesh yooooo you on steriods or something, take {rn} dollars yo.",
                f"Stanley | I've never seen someone like you! You earn {rn} dollars!",
                f"Daryl | You're definitely getting that raise! Take {rn} dollars for now.",
                f"Lambert | Hey, you are working hard, aren'tcha? Here, take these {rn} dollars.",
                f"Sally | Oh boy! We could use someone like you! These are {rn} dollars. Take them!",
                f"Daisy | Wow! Incredible work! Here's {rn} dollars.",
                f"Gerald | No way, that's amazin'! Here mate, take {rn} well deserved dollahs.",
                f"Pearson | It's been a while since I've seen someone work that hard. Take {rn} dollars.",
                f"Waldo | Well, you really are on a roll. Make sure to take these {rn} dollars on your way out.",
            ]

        elif rn < 80:  # if the number is below 80 (70, 71, 72, 73, 74, 75, 76, 77, 78, 79)
            responses = [
                f"Joe | We need someone for everyone to look up to. You'd be perfect! Here are {rn} dollars.",
                f"Caroline | Yes, excellent work! Here's {rn} dollars.",
                f"Daniel | Man, you exceed our expectations! Take these {rn} dollars, they may help you one day.",
                f"Samantha | This level of work is beyond our limits, take {rn} dollars!",
                f"Andrew | Nothing can compare to that amount of work! Take {rn} dollars!",
                f"Rachel | This is more than what we wanted. I say that in a good way! Take {rn} dollars.",
                f"Stanford | You did a lot today huh? Take {rn} dollars.",
                f"Tanveer | You are working extra great today, yes? You deserve {rn} dollars. Nice work!",
            ]

        elif rn < 90:  # if the number is below 90 (80, 81, 82, 83, 84, 85, 86, 87, 88, 89)
            responses = [
                f"Jeremy | You will be super successful in life! Take these {rn} dollars!",
                f"Nathan | I wonder how you did in school. By the way, here's {rn} dollars.",
                f"Johnathan | Thanks for working harder than ever! Take {rn} dollars.",
                f"Emily | How are you so good at this? You deserve {rn} dollars.",
                f"Mark | Give yourself a pat on the back right there! Take {rn} dollars!",
                f"Penny | Unbelieveable! Take these {rn} dollars right now!",
                f"Nathan | Nice work. Heh, I'm kidding. Excellent work. Take {rn} dollars.",
                f"Eric | You're a work of wonders! Take {rn} dollars.",
                f"Max | You're awesome. Just awesome. Don't hesitate to take these {rn} dollars.",
                f"Noah | You will help us a lot nowadays! Take these {rn} dollars. Go on.",
            ]

        elif rn < 100:  # if the number is below 100 (90, 91, 92, 93, 94, 95, 96, 97, 98, 99)
            responses = [
                f"Robert | Awesome! Take {rn} dollars!",
                f"William | I can't believe you even exist! You deserve {rn} dollars!!",
                f"Jennifer | No way, you're epic for this! Here's {rn} dollars.",
                f"Jessica | You will help us a lot along the way! Take {rn} dollars.",
                f"Elizabeth | You're sacrifices made it all the way here. Take these {rn} dollars.",
                f"Anthony | You're doing so well! Here's {rn} dollars.",
                f"Steven | Nice! You're so cool! Take {rn} dollars!",
                f"George | You are simply way too good at this. You deserve these {rn} dollars.",
                f"Kevin | You're the definition of anti-hopeless. Take {rn} dollars.",
                f"Edward | You will conquer the world one day...take these {rn} dollars.",
            ]

        elif rn < 110:  # if the number is below 110 (100, 101, 102, 103, 104, 105, 106, 107, 108, 109)
            responses = [
                f"Kenny | You are always on top! Take {rn} dollars.",
                f"Jason | (Hey. Take these {rn} dollars. On me. You're awesome.)",
                f"Carolina | You're going to be rich one day! Here, {rn} dollars for you!",
                f"Ronald | You're healthy, aren't you? Take these {rn} dollars.",
                f"Stephanie | You're super successful in life! Admitting it! Take {rn} dollars!",
                f"Rebecca | Ah. Nice. VERY nice. Take {rn} dollars.",
                f"Laura | You're gonna run a successful business with this work! Take {rn} dollars.",
                f"Amy | You'll be popular! And rich. And famous. Just take these {rn} dollars.",
                f"Gary | Nice one, kid. You're on the right track. Take these {rn} dollars.",
                f"Jeffrey | Man, you always overcome everyone, don't you? Take {rn} dollars.",
            ]

        elif rn < 120:  # if the number is below 120 (110, 111, 112, 113, 114, 115, 116, 117, 118, 119)
            responses = [
                f"Ryan | You just go our of your way to be the best? Awesome. Here, some {rn} dollars for ya.",
                f"Larry | Pretty cool, my guy! Take {rn} dollars.",
                f"Justin | Incredible. Absolutely incredible. Take {rn} dollars.",
                f"Brandon | 'Ey, howdy! I see you've been doing exceptionally fine today! Here are some {rn} dollars! Keep it up!",
                f"Emma | You're career will be successful, I guarrentee it. {rn} dollars, from me to you.",
                f"Nicole | Wow! Super cool! Take these {rn} dollars.",
                f"Gregory | Not even I can do that! Take {rn} dollars.",
                f"Janet | You sure you will take this seriously? I trust ya, kid. Here are {rn} dollars.",
                f"Debra | You're going to have everything one day kid. Have these {rn} dollars.",
                f"Maria | You're making progress! Here are some {rn} dollars.",
            ]

        elif rn < 130:  # if the number is below 130 (120, 121, 122, 123, 124, 125, 126, 127, 128, 129)
            responses = [
                f"Frank | It is dangerous to go alone! Take {rn} dollars!",
                f"Catherine | Make sure to keep it up. These {rn} dollars should give you hope.",
                f"Jack | {rn} dollars is probably all you need for a kid like you.",
                f"Patrick | I'm giving you {rn} dollars for the sake of yourself, kid.",
                f"Jennis | I see what you are in reality. Take {rn} dollars.",
                f"Terry | You'll be better in life with these {rn} dollars.",
                f"Jack | I feel bad though...take these {rn} dollars.",
                f"Aaron | I was you once. Very emotional...takes these {rn} dollars and go.",
                f"Jose | Okay then. Take these {rn} dollars. You'll need 'em.",
                f"Henry | {rn} dollars suits a kid like you.",
            ]

        elif rn < 140:  # if the number is below 140 (130, 131, 132, 133, 134, 135, 136, 137, 138, 139)
            responses = [
                f"Nathan | You deserve {rn} dollars for that.",
                f"Douglas | I can tell you're not joking around. Take {rn} dollars.",
                f"Zachary | Heh. You're amazing, kid. Take {rn} dollars.",
                f"Kyle | Before you go, take {rn} dollars. Take them.",
                f"Walter | A couple of dollars? Fine then. Take {rn} dollars. Gotcha, didn't I?",
                f"Ethan | I got some, hold up... Here. Take {rn} dollars.",
                f"Keith | I don't mind helping out an old me. {rn} dollars is enough for ya?",
                f"Megan | I gotchu, my guy. Take these {rn} dollars.",
                f"Carol | These {rn} dollars might come in handy?",
                f"Hannah | You're going to make it with these {rn} dollars.",
            ]

        elif rn < 150:  # if the number is below 150 (140, 141, 142, 143, 144, 145, 146, 147, 148, 149)
            responses = [
                f"Roger | Call me out one day when you end up being successful okay? Take {rn} dollars."
                f"Gloria | You might need some of these {rn} dollars."
                f"Ann | I won't regret giving you {rn} dollars."
                f"Teresa | Hurry! Take these {rn} dollars. Go."
                f"Austin | If this is for you, then take these {rn} dollars."
                f"Arthur | You sound like you need these {rn} dollars."
                f"Lawrence | Definitely aren't going to give you anything under {rn} dollars."
                f"Jesse | Sounds like you need these {rn} dollars more than I do."
                f"Dylan | More of these? I'll give you {rn} dollars."
                f"Brian | Your beg worked. I'm convinced. Take {rn} dollars."
            ]

        elif rn < 160:  # if the number is below 160 (150, 151, 152, 153, 154, 155, 156, 157, 158, 159)
            responses = [
                f"Ava | Nice to see someone who's made it so far. Take {rn} dollars.",
                f"Carson | Big decisions you've made led you up to this point. Here, some {rn} dollars. Use 'em wisely.",
                f"Charolette | Definitely not a waste of time you are, kid. You need {rn} dollars? Okay. Here.",
                f"Nandy | You're very determined, I see. Take these {rn} dollars.",
                f"Oswald | Persistent you are, and the more you receive...is that how it goes? Anyway, here's {rn} dollars.",
                f"Persia | You made it this far like that? I guess",
                f"Hamilton | Is meeting people your hobby? Not mine. Take {rn} dollars. You're very different.",
                f"Manny | Hope this is enough! {rn} dollars. Take it.",
                f"Joe | i would make a joke here but you look serious, here's {rn} dollars.",
                f"Yumi | Alright, if this is enough, here's {rn} dollars.",
            ]

        elif rn < 170:  # if the number is below 170 (160, 161, 162, 163, 164, 165, 166, 167, 168, 169)
            responses = [
                f"Melissa | Take 'em or leave 'em. {rn} dollars. Not going any higher.",
                f"Ashley | okOKOKOK. just take these {rn} and leave. don't bother me after this.",
                f"Parkinson | Sure thing man. Take these {rn} dollars. This better not be a scam.",
                f"Eugene | I'm leaving soon, so take these {rn} dollars.",
                f"Dave | These are pretty much my live savings. Take care of these {rn} dollars.",
                f"Danny | Make sure to use these {rn} dollars wisely.",
                f"Uriel | Fortunately, these {rn} dollars might help you out.",
                f"Smith | You must take these {rn} dollars. Take them now.",
                f"Richard | These {rn} might help. I don't know.",
                f"Marlin | These must help you. This is very expensive. {rn} dollars. Make it worth my time.",
            ]

        elif rn < 180:  # if the number is below 180 (170, 171, 172, 173, 174, 175, 176, 177, 178, 179)
            responses = [
                f"Clementine | Okay, here are the {rn} dollars you wanted. Take care.",
                f"Paige | I worked hard for these {rn} dollars. Don't waste them.",
                f"Gael | Only uphill from here, kid. Here's {rn} dollars.",
                f"Luke | Alright, so take these {rn} dollars. I don't need 'em.",
                f"Daniel | {rn} dollars is all you want? Use them for your own good, I guess.",
                f"Albert | Please take care. Take these {rn} dollars.",
                f"Frank | You must take these {rn} dollars. You are very determined.",
                f"Susie | Very specific request, but I am kind. Here's {rn} dollars you asked for.",
                f"Vanessa | You only want {rn} dollars? Alright, here you go.",
                f"Valeria | Blowing all of my {rn} dollars on you. Worth it? I don't know.",
            ]

        elif rn < 190:  # if the number is below 190 (180, 181, 182, 183, 184, 185, 186, 187, 188, 189)
            responses = [
                f"Xavi | You must be considering something huge. Take my {rn} dollars.",
                f"Gil | If I'm going to help a lot, take these {rn} dollars.",
                f"Mihails | Very unique request. Here's my {rn} dollars.",
                f"Galenos | Well, as long as you return the favor somehow. {rn} dollars is yours.",
                f"Cadogan | No comment. Here's {rn} dollars. Hope you do well.",
                f"Stav | Let's get this over with then! Here's {rn} dollars.",
                f"Arne | {rn} dollars on me, kid. I wish I was you.",
                f"Masood | If I were you, I'd take these {rn} dollars.",
                f"Elizabete | Alright, get that out of the way. Take these {rn} dollars and go.",
                f"Winfred | I'll give these to you I guess. It's a lot. {rn} dollars for you.",
            ]

        elif rn < 200:  # if the number is below 200 (190, 191, 192, 193, 194, 195, 196, 197, 198, 199)
            responses = [
                f"Ender2K89 (Bot Owner) | Here have {rn} dollars. Thank you for using my bot ;D",
                f"Vincent | I can't say I'm not surprised on how much you want. Take these {rn} dollars anyway.",
                f"Fernando | {rn} dollars is a lot. Make it worth it, kid.",
                f"Jimmy | Okay! Here's {rn} dollars.",
                f"Aben | Fine. You want it? It's yours, my friend. Here are {rn} dollars.",
                f"Leeba | Geez, that's a lot of cash you want! Hope this isn't a scam because this kid is awesome.... here are {rn} dollars?",
                f"Xena | Sure. Take 'em. I don't even care. Take the {rn} dollars. Yours.",
                f"Arsenios | You want it so badly? Sure. {rn} dollars for you.",
                f"Paula | I don't mind. Take the {rn} dollars. Hope it serves you well.",
                f"Kennet | You must make sure you don't just lose the {rn} dollars I'm going to give you, OK?",
                f"Olivia | Everything has led you up to this moment, so I also better make it worth our time. Here's {rn} dollars.",
            ]

        else:
            raise errors.UnknownError

        response = random.choice(responses)

        await self.client.db.execute("UPDATE economy SET wallet = wallet + $1 WHERE user_id = $2; ", rn, ctx.author.id)
        newBalance = rn + record['wallet']

        embed = discord.Embed(description=f"{response.split('| ')[1]}")
        embed.set_author(name=f"{response.split(' |')[0]} said:")
        embed.set_footer(text=f"You now have {newBalance} money",
                         icon_url='https://cdn.discordapp.com/emojis/899676397600141334.png?size=96')

        await ctx.send(embed=embed)
        
    @commands.command(
        help="Flips a coin, if the flipped coin is heads and you chose heads, you win the amount you bet. If it doesn't you lose.",
        brief="coinflip 591\ncoinflip 458915\ncoinflip 5911",
        aliases=['cf'])
    @has_started()
    @commands.cooldown(1, 10, BucketType.member)
    async def coinflip(self, ctx: CustomContext, amount: int):
        database = await self.client.db.fetchrow("SELECT * FROM economy where user_id = $1; ", ctx.author.id)

        if amount < 500:
            return await ctx.send("You have to bet more than 500!")

        if amount > database['wallet']:
            return await ctx.send("You don't have that much money in your wallet!")

        possible_answers = ['heads', 'tails']
        possible_answers2 = ['heads', 'tails', 'cancel']
        bot_answer = random.choice(possible_answers)

        def check(m):
            return m.content.lower() in possible_answers2 and m.channel.id == ctx.channel.id and m.author.id == ctx.author.id

        embed = discord.Embed(title=f"Coinflip - {amount:,}$", description=f"Choose an option in the next 15 seconds!\ntails or heads.", color=discord.Color.blurple())
        embed.set_footer(text=f"To cancel, just type cancel")

        message = await ctx.send(embed=embed, color=False, footer=False)

        try:
            msg = await self.client.wait_for(event="message", check=check, timeout=15)

        except asyncio.TimeoutError:
            embed = discord.Embed(title="Timed out!", color=discord.Color.red(), timestamp=discord.utils.utcnow())
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)

            return await message.edit(embed=embed)

        else:
            if str(msg.content.lower()) == "cancel":
                embed = discord.Embed(title="Cancelled!", color=discord.Color.red(), timestamp=discord.utils.utcnow())
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)

                return await message.edit(embed=embed)

            if str(bot_answer).lower() == str(msg).lower():
                embed = discord.Embed(title=f"Coinflip - {amount:,}$", description=f"""
:tada: __**CONGRATULATIONS {ctx.author.display_name}!!!!**__ :tada:
The coin landed on **{str(bot_answer).title()}** and you chose **{str(msg).title()}**, meaning that you've just won **{amount:,}$**!

Your new balance is {database['wallet'] + amount:,}
                """, color=discord.Color.green())
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)

                await self.client.db.execute(""" UPDATE economy SET wallet = wallet + $1 WHERE user_id = $2; """, amount, ctx.author.id)
                await msg.add_reaction("🎉")
                return await message.edit(embed=embed)

            else:
                embed = discord.Embed(title=f"Coinflip - {amount:,}$", description=f"""
You lost {ctx.author.display_name}..
The coin landed on **{str(bot_answer).title()}** and you chose **{str(msg).title()}**, meaning that you've just lost **{amount:,}$**!

Your new balance is {database['wallet'] - amount:,}
                """, color=discord.Color.red())
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
                
                await self.client.db.execute(""" UPDATE economy SET wallet = wallet - $1 WHERE user_id = $2; """, amount, ctx.author.id)
                return await message.edit(embed=embed)
            
    @commands.command(
        help="The bot chooses a random number between 1 and 5. If you choose the number the bot chose, you will receive double the money you bet, but if you lose you'll lose all of that money.",
        brief="guess_the_number 6925\nguess_the_number 589157815\nguess_the_number 951501",
        aliases=['guess-the-number', 'gtn'])
    @has_started()
    @commands.cooldown(1, 10, BucketType.member)
    async def guess_the_number(self, ctx: CustomContext, amount: int):
        database = await self.client.db.fetchrow("SELECT * FROM economy where user_id = $1; ", ctx.author.id)

        if amount < 500:
            return await ctx.send("You have to bet more than 500!")

        if amount > database['wallet']:
            return await ctx.send("You don't have that much money in your wallet!")

        possibleAnswers = ['1', '2', '3', '4', '5']
        possibleAnswers2 = ['1', '2', '3', '4', '5', 'cancel']
        botAnswer = random.choice(possibleAnswers)

        def check(m):
            return m.content.lower() in possibleAnswers2 and m.channel.id == ctx.channel.id and m.author.id == ctx.author.id

        embed = discord.Embed(title=f"Guess the number - {amount:,}$", description=f"Choose a number between 1 and 5.", color=discord.Color.blurple())
        embed.set_footer(text=f"To cancel, just type cancel")

        message = await ctx.send(embed=embed, color=False, footer=False)

        try:
            msg = await self.client.wait_for(event="message", check=check, timeout=15)

        except asyncio.TimeoutError:
            embed = discord.Embed(title="Timed out!", color=discord.Color.red(), timestamp=discord.utils.utcnow())
            embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)

            return await message.edit(embed=embed)

        else:
            if str(msg.content.lower()) == "cancel":
                embed = discord.Embed(title="Cancelled!", color=discord.Color.red(), timestamp=discord.utils.utcnow())
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)

                return await message.edit(embed=embed)

            if str(botAnswer).lower() == str(msg).lower():
                embed = discord.Embed(title=f"Guess the number - {amount:,}$", description=f"""
:tada: __**CONGRATULATIONS {ctx.author.display_name}!!!!**__ :tada:
The number I chose was **{str(botAnswer).title()}** and you chose **{str(msg).title()}**, meaning that you've just won **{amount:,}$**!

Your new balance is {database['wallet'] + amount:,}
                """, color=discord.Color.green())
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)

                await self.client.db.execute(""" UPDATE economy SET wallet = wallet + $1 WHERE user_id = $2; """, amount, ctx.author.id)
                await msg.add_reaction("🎉")
                return await message.edit(embed=embed)

            else:
                embed = discord.Embed(title=f"Guess the number - {amount:,}$", description=f"""
You lost {ctx.author.display_name}..
The number I chose was **{str(botAnswer).title()}** and you chose **{str(msg).title()}**, meaning that you've just lost **{amount:,}$**!

Your new balance is {database['wallet'] - amount:,}
                """, color=discord.Color.red())
                embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
                
                await self.client.db.execute(""" UPDATE economy SET wallet = wallet - $1 WHERE user_id = $2; """, amount, ctx.author.id)
                return await message.edit(embed=embed)

    @commands.command(
        help="Creates a balance for you if you don't have one.",
        aliases=['make'])
    async def start(self, ctx: CustomContext):
        user = await self.client.db.fetchrow("SELECT user_id FROM economy WHERE user_id = $1", ctx.author.id)

        if user:
            return await ctx.send(f"You already have a balance! If you want to reset it do `{ctx.prefix}reset`")

        await self.client.db.execute("INSERT INTO economy (user_id, created_at) VALUES ($1, $2);", ctx.author.id,
                                     int(ctx.message.created_at.timestamp()))
        await ctx.send("Successfully made you a balance.")

    @commands.command(
        help="Resets your balance, theres 2 confirmations so you don't do it accidentally.")
    async def reset(self, ctx: CustomContext):
        record = await self.client.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", ctx.author.id)

        if not record:
            raise errors.NotStartedEconomy(
                f"How am I gonna reset your balance if you don't have a balance? Do `{ctx.prefix}start` to make one.")

        else:
            confirmation1 = await ctx.confirm(
                "Are you sure you want to reset your balance? (This action cannot be undone)")

            if confirmation1:
                confirmation2 = await ctx.confirm(
                    "ARE YOU REALLY SURE YOU WANT TO RESET YOUR BALANCE? (THIS ACTION **CANNOT** BE UNDONE)")

                if confirmation2:
                    await self.client.db.execute(
                        "INSERT INTO economy (user_id, wallet, bank) VALUES ($1, $2, $2) ON CONFLICT (user_id) DO "
                        "UPDATE SET wallet = $2, bank = $2;",
                        ctx.author.id, 0)
                    return await ctx.send("Successfully reset your balance.")

                else:
                    return await ctx.send("Okay, I won't.")

            else:
                return await ctx.send("Okay, I won't.")

    @commands.group(
        invoke_without_command=True,
        help=":moneybag: | Economy commands only for the owner of the bot.",
        aliases=['admineco', 'ecoadmin', 'economyadmin'])
    @commands.is_owner()
    async def admineconomy(self, ctx: CustomContext):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @admineconomy.group(
        help="Gives the specified member's a specified amount of money.",
        aliases=['add', 'g', 'a'])
    @commands.is_owner()
    async def give(self, ctx: CustomContext, member: discord.Member, amount: int):
        record = await self.client.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", member.id)

        if not record:
            return await ctx.send(f"{member} doesn't have a balance! They have to do `start` to make one.")

        else:
            amount2 = record['wallet'] + amount
            await self.client.db.execute(
                "INSERT INTO economy (user_id, wallet) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET wallet = $2;",
                member.id, amount2)
            newBalance = amount2
            await ctx.send(f"Successfully given {member.mention} `{amount}` money. They now have {newBalance} money.")

    @admineconomy.command(
        name="set",
        help="Sets the specified member's balance to the specified number.",
        aliases=['s'])
    @commands.is_owner()
    async def _set(self, ctx: CustomContext, member: discord.Member, amount: int):
        record = await self.client.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", member.id)

        if not record:
            return await ctx.send(f"{member.mention} doesn't have a balance! They have to do `start` to make one.")

        else:
            await self.client.db.execute(
                "INSERT INTO economy (user_id, wallet) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET wallet = $2",
                member.id, amount)
            await ctx.send(f"Successfully set {member.mention}'s balance to `{amount}` money.")

    @admineconomy.command(
        help="Removes the specified number from the specified member's balance.",
        aliases=['r'])
    @commands.is_owner()
    async def remove(self, ctx: CustomContext, member: discord.Member, amount: int):
        record = await self.client.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", member.id)

        if not record:
            return await ctx.send(f"{member.mention} doesn't have a balance! They have to do `start` to make one.")

        else:
            amount2 = record['wallet'] - amount
            await self.client.db.execute(
                "INSERT INTO economy (user_id, wallet) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET wallet = $2",
                member.id, amount2)
            newBalance = amount2
            await ctx.send(
                f"Successfully removed `{amount}` from {member.mention}'s balance. They now have {newBalance} money.")

    @admineconomy.command(
        help="Resets the specified member's balance.",
        aliases=['re'])
    @commands.is_owner()
    async def reset(self, ctx: CustomContext, member: discord.Member):
        record = await self.client.db.fetchrow("SELECT * FROM economy WHERE user_id = $1", member.id)

        if not record:
            return await ctx.send(f"{member.mention} doesn't have a balance! They have to do `start` to make one.")

        else:
            await self.client.db.execute(
                "INSERT INTO economy (user_id, wallet) VALUES ($1, $2) ON CONFLICT (user_id) DO UPDATE SET wallet = $2",
                member.id, 0)
            await ctx.send(f"Successfully reset {member.mention}'s balance. They now have `0` money.")

    @admineconomy.command(
        help="Resets the entire economy.")
    @commands.is_owner()
    async def resetall(self, ctx: CustomContext):
        confirmation1 = await ctx.confirm(message="Are you sure you want to do this?")

        if confirmation1:
            confirmation2 = await ctx.confirm(message="ARE YOU REALLY SURE YOU WANNA DO THIS?")

            if confirmation2:
                await self.client.db.execute("DELETE FROM economy")
                await ctx.send("Successfully reset the entire economy!")

            else:
                return await ctx.send("Okay, successfully cancelled.")

        else:
            return await ctx.send("Okay, successfully cancelled.")
