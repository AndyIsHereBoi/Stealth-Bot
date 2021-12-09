import io
import time
import random
import errors
import typing
import discord

from io import BytesIO
from discord.ext import commands
from helpers.context import CustomContext
from asyncdagpi import ImageFeatures as imageFeatures

def setup(client):
    client.add_cog(Images(client))


class Images(commands.Cog):
    """Commands that manipulate/send images."""

    def __init__(self, client):
        self.client = client
        self.select_emoji = "<:frame_photo:899621559520595968>"
        self.select_brief = "Commands that manipulate/send images."

    # @commands.group(
    #     slash_command=True,
    #     invoke_without_command=True,
    #     help="<:frame_photo:899621559520595968> | Commands that show you images of animals",
    #     aliases=['i', 'images'])
    # async def image(self, ctx: CustomContext):
    #     if ctx.invoked_subcommand is None:
    #         await ctx.send_help(ctx.command)

    @commands.command(
        help="Sends a picture of a SFW waifu",
        aliases=['sfw_waifu', 'waifu_sfw'])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def waifu(self, ctx: CustomContext, type: str = None):
        await ctx.trigger_typing()
        
        start = time.perf_counter()

        request = await self.client.session.get('https://api.waifu.im/sfw/waifu/?gif=True' if str(type).lower() == 'gif' else 'https://api.waifu.im/sfw/waifu/')
        json = (await request.json())['images'][0]

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Waifu", url=json['source'], color=int(json['dominant_color'].replace('#', ''),16))
        embed.set_image(url=json['url'])
        embed.set_footer(text=f"Requested by {ctx.author} • {round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="Sends a picture of a SFW maid",
        aliases=['sfw_maid', 'maid_sfw'])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def maid(self, ctx: CustomContext, type: str = None):
        url = "https://api.waifu.im/sfw/maid/"

        if str(type).lower() == "gif":
            url = "https://api.waifu.im/sfw/maid/?gif=True"

        start = time.perf_counter()

        request = await self.client.session.get(url)
        json = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        dominant_color1 = str(json['tags'][0]['images'][0]['dominant_color']).replace('#', '')
        dominant_color = int(dominant_color1, 16)

        embed = discord.Embed(title="Maid", url=json['url'], color=dominant_color)
        embed.set_image(url=json['tags'][0]['images'][0]['url'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, color=False, footer=False)

    @commands.command(
        help="🐶 Shows a picture of a shiba",
        aliases=['shibe'])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def shiba(self, ctx: CustomContext):
        start = time.perf_counter()

        request = await self.client.session.get('https://shibe.online/api/shibes?count=1&urls=true&httpsUrls=true')
        json = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        titles = ["Bark!", "Arf!", "Woof!", "Bork!"]

        embed = discord.Embed(title=f"{random.choice(titles)}", url=json[0])
        embed.set_image(url=json[0])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="Shows a picture of a axolotl and a random fact about axolotls")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def axolotl(self, ctx: CustomContext):
        start = time.perf_counter()

        request = await self.client.session.get('https://axoltlapi.herokuapp.com/')
        json = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Axolotl", url=json['url'])
        embed.set_image(url=json['url'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))} • {json['facts']}")

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="🐱 Shows a picture of a cat and a random fact about cats")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def cat(self, ctx: CustomContext):
        start = time.perf_counter()

        request = await self.client.session.get('https://some-random-api.ml/img/cat')
        pictureJson = await request.json()
        request2 = await self.client.session.get('https://some-random-api.ml/facts/cat')
        factJson = await request2.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        titles = ["Meowww", "Meoww!", "Meowwwww"]

        embed = discord.Embed(title=f"{random.choice(titles)}", url=pictureJson['link'])
        embed.set_image(url=pictureJson['link'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))} • {factJson['fact']}")

        await ctx.send(embed=embed, footer=False)

    # @commands.command(
    #     help="🐶 Shows a picture of a dog and a random fact about dogs")
    # @commands.bot_has_permissions(send_messages=True, embed_links=True)
    # async def dog(self, ctx: CustomContext):
    #     start = time.perf_counter()

    #     request = await self.client.session.get('https://some-random-api.ml/img/dog')
    #     pictureJson = await request.json()
    #     request2 = await self.client.session.get('https://some-random-api.ml/facts/dog')
    #     factJson = await request2.json()

    #     end = time.perf_counter()

    #     ms = (end - start) * 1000

    #     titles = ["Bark!", "Arf!", "Woof!", "Bork!"]

    #     embed = discord.Embed(title=f"{random.choice(titles)}", url=pictureJson['link'])
    #     embed.set_image(url=pictureJson['link'])
    #     embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))} • {factJson['fact']}")

    #     await ctx.send(embed=embed, footer=False)
        
    @commands.command(
        help="🐶 Shows a picture of a dog and a random fact about dogs")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def dog(self, ctx: CustomContext):
        async with self.client.session.get('https://random.dog/woof') as response:
            if response.status != 200:
                return await ctx.send('No dog found :(')
            
            request2 = await self.client.session.get('https://some-random-api.ml/facts/dog')
            factJson = await request2.json()

            filename = await response.text()
            url = f'https://random.dog/{filename}'
            filesize = ctx.guild.filesize_limit if ctx.guild else 8388608
            if filename.endswith(('.mp4', '.webm')):
                async with ctx.typing():
                    async with self.client.session.get(url) as other:
                        if other.status != 200:
                            raise errors.UnknownError

                        if int(other.headers['Content-Length']) >= filesize:
                            return await ctx.send(f"The video was too big to upload\nSee it here: **{url}**")

                        fp = io.BytesIO(await other.read())
                        await ctx.send(f"Random fact about dogs: {factJson['fact']}", file=discord.File(fp, filename=filename))
                        
            else:
                embed = discord.Embed(title=random.choice(["Bark!", "Arf!", "Woof!", "Bork!"]), url=url)
                embed.set_image(url=url)
                embed.set_footer(text=factJson['fact'])
                
                await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="🐼 Shows a picture of a panda and a random fact about pandas")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def panda(self, ctx: CustomContext):
        start = time.perf_counter()

        request = await self.client.session.get('https://some-random-api.ml/img/panda')
        pictureJson = await request.json()
        request2 = await self.client.session.get('https://some-random-api.ml/facts/panda')
        factJson = await request2.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Panda!", url=pictureJson['link'])
        embed.set_image(url=pictureJson['link'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))} • {factJson['fact']}")

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="🦊 Shows a picture of a fox and a random fact about foxes")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def fox(self, ctx: CustomContext):
        start = time.perf_counter()

        request = await self.client.session.get('https://some-random-api.ml/img/fox')
        pictureJson = await request.json()
        request2 = await self.client.session.get('https://some-random-api.ml/facts/fox')
        factJson = await request2.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Fox!", url=pictureJson['link'])
        embed.set_image(url=pictureJson['link'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))} • {factJson['fact']}")

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="🐦 Shows a picture of a bird and a random fact about birds")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def bird(self, ctx: CustomContext):
        start = time.perf_counter()
        
        request = await self.client.session.get('https://some-random-api.ml/img/bird')
        pictureJson = await request.json()
        request2 = await self.client.session.get('https://some-random-api.ml/facts/bird')
        factJson = await request2.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Bird!", url=pictureJson['link'])
        embed.set_image(url=pictureJson['link'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))} • {factJson['fact']}")

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="🐨 Shows a picture of a koala and a random fact about koalas")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def koala(self, ctx: CustomContext):
        start = time.perf_counter()

        request = await self.client.session.get('https://some-random-api.ml/img/koala')
        pictureJson = await request.json()
        request2 = await self.client.session.get('https://some-random-api.ml/facts/koala')
        factJson = await request2.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Koala!", url=pictureJson['link'])
        embed.set_image(url=pictureJson['link'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))} • {factJson['fact']}")

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="🦘 Shows a picture of a kangaroo and a random fact about kangaroos")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def kangaroo(self, ctx: CustomContext):
        start = time.perf_counter()

        request = await self.client.session.get('https://some-random-api.ml/img/kangaroo')
        pictureJson = await request.json()
        request2 = await self.client.session.get('https://some-random-api.ml/facts/kangaroo')
        factJson = await request2.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Kangaroo!", url=pictureJson['link'])
        embed.set_image(url=pictureJson['link'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))} • {factJson['fact']}")

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="🦝 Shows a picture of a raccoon and a random fact about racoons",
        aliases=['raccoon'])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def racoon(self, ctx: CustomContext):
        start = time.perf_counter()

        request = await self.client.session.get('https://some-random-api.ml/img/racoon')
        pictureJson = await request.json()
        request2 = await self.client.session.get('https://some-random-api.ml/facts/racoon')
        factJson = await request2.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Racoon!", url=pictureJson['link'])
        embed.set_image(url=pictureJson['link'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))} • {factJson['fact']}")

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="🐳 Shows a picture of a whale and a random fact about whales",
        aliases=['urmom', 'ur_mom', 'yourmom', 'your_mom'])
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def whale(self, ctx: CustomContext):
        start = time.perf_counter()

        request = await self.client.session.get('https://some-random-api.ml/img/whale')
        pictureJson = await request.json()
        request2 = await self.client.session.get('https://some-random-api.ml/facts/whale')
        factJson = await request2.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Whale!", url=pictureJson['link'])
        embed.set_image(url=pictureJson['link'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))} • {factJson['fact']}")

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="Shows a picture of a pikachu")
    @commands.bot_has_permissions(send_messages=True, embed_links=True)
    async def pikachu(self, ctx: CustomContext):
        start = time.perf_counter()

        request = await self.client.session.get('https://some-random-api.ml/img/pikachu')
        pictureJson = await request.json()

        end = time.perf_counter()

        ms = (end - start) * 1000

        embed = discord.Embed(title="Pikachu!", url=pictureJson['link'])
        embed.set_image(url=pictureJson['link'])
        embed.set_footer(text=f"{round(ms)}ms{'' * (9 - len(str(round(ms, 3))))}", icon_url=ctx.author.avatar.url)

        await ctx.send(embed=embed, footer=False)

    @commands.command(
        help="Sends a picture of a person that doesn't exist",
        aliases=['tpdne', 'person'])
    async def thispersondoesnotexist(self, ctx: CustomContext):
        async with ctx.typing():
            async with self.client.session.get('https://thispersondoesnotexist.com/image') as request:
                request = await request.read()
                buffer = BytesIO(request)
                file = discord.File(fp=buffer, filename="thispersondoesnotexist.png")
                await ctx.send(file=file)

    # @commands.group(
    #     slash_command=True,
    #     invoke_without_command=True,
    #     help=":frame_photo: Commands used to manipulate member's avatars",
    #     aliases=['m', 'im'])
    # async def manipulation(self, ctx: CustomContext):
    #     if ctx.invoked_subcommand is None:
    #         await ctx.send_help(ctx.command)

    @commands.command( # 1
        help="Turns the specified member's profile picture into a pat-pat gif",
        aliases=['pats', 'pat_pat', 'patspats', 'pats_pats', 'petpet', 'pet_pet'])
    async def patpat(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.patpat()))

    @commands.command( # 2
        help="Glitches the specified member's profile picture",
        aliases=['error'])
    async def glitch(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.glitch()))

    @commands.command( # 3
        help="Turns the specified member's avatar into pixels")
    async def pixel(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.pixel()))

    @commands.command( # 4
        help="Makes a wanted poster of the specified member's avatar")
    async def wanted(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.wanted()))

    @commands.command( # 5
        help="Gets the colors from a specified member's avatar")
    async def colors(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.colors()))

    @commands.command( # 6
        help="Makes the specified member's avatar triggered")
    async def triggered(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.triggered()))

    @commands.command( # 7
        help="Puts a waving america flag on the specified member's avatar")
    async def america(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.america()))

    @commands.command( # 8
        help="Puts a waving communism flag on the specified member's avatar")
    async def communism(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.communism()))

    @commands.command( # 9
        help="Explodes the specified member's avatar",
        aliases=['boom'])
    async def bomb(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.bomb()))

    @commands.command( # 10
        help="Puts the GTA V wasted screen on the specified member's avatar")
    async def wasted(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.wasted()))

    @commands.command( # 11
        help="Inverts the colors of the specified member's avatar")
    async def invert(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.invert()))

    @commands.command( # 12
        help="Swirls the center of the specified member's avatar")
    async def swirl(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.swirl()))

    @commands.command( # 13
        help="Puts a triangle edge detection filter on the specified member's avatar")
    async def triangle(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.triangle()))

    @commands.command( # 14
        help="Blurs the specified member's avatar")
    async def blur(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.blur()))

    @commands.command( # 15
        help="Gets RGB information from the specified member's avatar")
    async def rgb(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.rgb()))

    @commands.command( # 16
        help="Make the specified member's avatar angelic",
        aliases=['angelic'])
    async def angel(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.angel()))

    @commands.command( # 17
        help="Make the specified member's avatar satanic",
        aliases=['satanic'])
    async def satan(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.satan()))

    @commands.command( # 18
        help="Make the specified member's avatar worse than hitler",
        aliases=['worse_than_hitler'])
    async def hitler(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.hitler()))

    @commands.command( # 19
        help="Make the specified member's avatar the obamama meme of someone awarding themselves")
    async def obama(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.obama()))

    @commands.command( # 20
        help="Make the specified member's avatar bad")
    async def bad(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.bad()))
        
    @commands.command( # 21
        help="Puts the specified member's avatar behind bars")
    async def jail(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.jail()))

    @commands.command( # 22
        help="Puts a fedora on the specified member's avatar")
    async def fedora(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.fedora()))

    @commands.command( # 23
        help="Deletes the specified member's avatar")
    async def delete(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.delete()))

    @commands.command( # 24
        help="Shatters the specified member's avatar like glass")
    async def shatter(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.shatter()))

    @commands.command( # 25
        help="Deepfries the specified member's avatar")
    async def deepfry(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        await ctx.send(file=await ctx.dagpi(member, feature=imageFeatures.deepfry()))

    # JEYY API
    
    
    # @commands.group(
    #     invoke_without_command=True,
    #     help=":frame_photo: Imagine manipulation commands that use the [JeyyAPI](https://api.jeyy.xyz/)",
    #     aliases=['jeyyapi', 'ja'])
    # async def jeyy(self, ctx: CustomContext):
    #     if ctx.invoked_subcommand is None:
    #         await ctx.send_help(ctx.command)
    
    @commands.command( # 1
        help="Turns the specified member's avatar into falling balls")
    async def balls(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        await ctx.trigger_typing()
        
        if isinstance(member, discord.Emoji):
            url = member.url
            
        elif isinstance(member, discord.PartialEmoji):
            url = member.url
            
        else:
            url = member.display_avatar.url

        request = await self.client.session.get('https://api.jeyy.xyz/image/balls',
                                                params={'image_url': url})
        buffer = BytesIO(await request.read())
        file = discord.File(buffer, 'balls.gif')

        await ctx.send(file=file)

    @commands.command( # 2
        help="Burns the specified member's avatar.")
    async def burn(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        await ctx.trigger_typing()
    
        if isinstance(member, discord.Emoji):
            url = member.url
            
        elif isinstance(member, discord.PartialEmoji):
            url = member.url
            
        else:
            url = member.display_avatar.url

        request = await self.client.session.get('https://api.jeyy.xyz/image/burn',
                                                params={'image_url': url})
        buffer = BytesIO(await request.read())
        file = discord.File(buffer, 'burn.gif')

        await ctx.send(file=file)

    @commands.command( # 3
        help="Glitches the specified member's avatar out.")
    async def glitch(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        await ctx.trigger_typing()
        
        if isinstance(member, discord.Emoji):
            url = member.url
            
        elif isinstance(member, discord.PartialEmoji):
            url = member.url
            
        else:
            url = member.display_avatar.url

        request = await self.client.session.get('https://api.jeyy.xyz/image/glitch',
                                                params={'image_url': url})
        buffer = BytesIO(await request.read())
        
        embed = discord.Embed()
        embed.set_image(url="attachment://glitch.gif")
        
        await ctx.send(embed=embed, file=discord.File(buffer, "glitch.gif"))

    @commands.command( # 4
        help="Boils the specified member's avatar.")
    async def boil(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        await ctx.trigger_typing()
        
        if isinstance(member, discord.Emoji):
            url = member.url
            
        elif isinstance(member, discord.PartialEmoji):
            url = member.url
            
        else:
            url = member.display_avatar.replace(format="png").url

        request = await self.client.session.get('https://api.jeyy.xyz/image/boil',
                                                params={'image_url': url})
        buffer = BytesIO(await request.read())
        
        embed = discord.Embed()
        embed.set_image(url="attachment://boil.gif")
        
        await ctx.send(embed=embed, file=discord.File(buffer, "boil.gif"))

    @commands.command( # 5
        help="Earthquakes the specified member's avatar.")
    async def earthquake(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        await ctx.trigger_typing()
        
        if isinstance(member, discord.Emoji):
            url = member.url
            
        elif isinstance(member, discord.PartialEmoji):
            url = member.url
            
        else:
            url = member.display_avatar.url

        request = await self.client.session.get('https://api.jeyy.xyz/image/earthquake',
                                                params={'image_url': url})
        buffer = BytesIO(await request.read())
        
        embed = discord.Embed()
        embed.set_image(url="attachment://earthquake.gif")
        
        await ctx.send(embed=embed, file=discord.File(buffer, "earthquake.gif"))

    @commands.command( # 6
        help="Makes the specified member's avatar appear shocked.")
    async def shock(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        await ctx.trigger_typing()
        
        if isinstance(member, discord.Emoji):
            url = member.url
            
        elif isinstance(member, discord.PartialEmoji):
            url = member.url
            
        else:
            url = member.display_avatar.url

        request = await self.client.session.get('https://api.jeyy.xyz/image/shock',
                                                params={'image_url': url})
        buffer = BytesIO(await request.read())
        
        embed = discord.Embed()
        embed.set_image(url="attachment://shock.gif")
        
        await ctx.send(embed=embed, file=discord.File(buffer, "shock.gif"))

    @commands.command(  # 7
        help="Makes the specified member's avatar abstractic.")
    async def abstract(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        await ctx.trigger_typing()
        
        if isinstance(member, discord.Emoji):
            url = member.url
            
        elif isinstance(member, discord.PartialEmoji):
            url = member.url
            
        else:
            url = member.display_avatar.url

        request = await self.client.session.get('https://api.jeyy.xyz/image/abstract',
                                                params={'image_url': url})
        buffer = BytesIO(await request.read())
        
        embed = discord.Embed()
        embed.set_image(url="attachment://abstract.gif")
        
        await ctx.send(embed=embed, file=discord.File(buffer, "abstract.gif"))

    @commands.command( # 8
        help="Makes the specified member's avatar infinite.")
    async def infinity(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        await ctx.trigger_typing()
        
        if isinstance(member, discord.Emoji):
            url = member.url
            
        elif isinstance(member, discord.PartialEmoji):
            url = member.url
            
        else:
            url = member.display_avatar.url

        request = await self.client.session.get('https://api.jeyy.xyz/image/infinity',
                                                params={'image_url': url})
        buffer = BytesIO(await request.read())
        
        embed = discord.Embed()
        embed.set_image(url="attachment://infinity.gif")
        
        await ctx.send(embed=embed, file=discord.File(buffer, "infinity.gif"))

    @commands.command( # 9
        help="Bombs the specified member's avatar.")
    async def bomb(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        await ctx.trigger_typing()
        
        if isinstance(member, discord.Emoji):
            url = member.url
            
        elif isinstance(member, discord.PartialEmoji):
            url = member.url
            
        else:
            url = member.display_avatar.url

        request = await self.client.session.get('https://api.jeyy.xyz/image/bomb',
                                                params={'image_url': url})
        buffer = BytesIO(await request.read())
        
        embed = discord.Embed()
        embed.set_image(url="attachment://bomb.gif")
        
        await ctx.send(embed=embed, file=discord.File(buffer, "bomb.gif"))

    @commands.command(  # 10
        help="Bonks the specified member's avatar.")
    async def bonk(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        await ctx.trigger_typing()
        
        if isinstance(member, discord.Emoji):
            url = member.url
            
        elif isinstance(member, discord.PartialEmoji):
            url = member.url
            
        else:
            url = member.display_avatar.url

        request = await self.client.session.get('https://api.jeyy.xyz/image/bonks',
                                                params={'image_url': url})
        buffer = BytesIO(await request.read())
        
        embed = discord.Embed()
        embed.set_image(url="attachment://bonk.gif")
        
        await ctx.send(embed=embed, file=discord.File(buffer, "bonk.gif"))

    @commands.command( # 11
        help="Gives the specified member a license to be horny.",
        aliases=['horny_license', 'horny-license', 'license_horny', 'license-horny'])
    async def hornylicense(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        if isinstance(member, discord.Emoji):
            url = member.url

        elif isinstance(member, discord.PartialEmoji):
            url = member.url
            
        else:
            url = member.display_avatar.with_format("png")

        request = await self.client.session.get(f"https://some-random-api.ml/canvas/horny?avatar={url}")
        
        buffer = BytesIO(await request.read())

        embed = discord.Embed()
        embed.set_image(url="attachment://horny.png")
        
        await ctx.send(embed=embed, file=discord.File(buffer, "horny.png"))
            
    @commands.command(  # 12
        help="Makes the specified member's avatar cry")
    async def sob(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        await ctx.trigger_typing()
        
        if isinstance(member, discord.Emoji):
            url = member.url
            
        elif isinstance(member, discord.PartialEmoji):
            url = member.url
            
        else:
            url = member.display_avatar.url

        request = await self.client.session.get('https://api.jeyy.xyz/image/sob',
                                                params={'image_url': url})
        buffer = BytesIO(await request.read())
        
        embed = discord.Embed()
        embed.set_image(url="attachment://sob.gif")
        
        await ctx.send(embed=embed, file=discord.File(buffer, "sob.gif"))
        
    @commands.command(  # 13
        help="Puts a lamp on the specified member's avatar.")
    async def lamp(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        await ctx.trigger_typing()
        
        if isinstance(member, discord.Emoji):
            url = member.url
            
        elif isinstance(member, discord.PartialEmoji):
            url = member.url
            
        else:
            url = member.display_avatar.url

        request = await self.client.session.get('https://api.jeyy.xyz/image/lamp',
                                                params={'image_url': url})
        buffer = BytesIO(await request.read())
        
        embed = discord.Embed()
        embed.set_image(url="attachment://lamp.gif")
        
        await ctx.send(embed=embed, file=discord.File(buffer, "lamp.gif"))
        
    @commands.command(  # 13
        help="Turns the specified member's avatar into emojis!")
    async def emojify(self, ctx: CustomContext, member: typing.Optional[typing.Union[discord.Member, discord.User, discord.Emoji, discord.PartialEmoji]]):
        if member is None:
            if ctx.message.reference:
                member = ctx.message.reference.resolved.author
            else:
                member = ctx.author

        await ctx.trigger_typing()
        
        if isinstance(member, discord.Emoji):
            url = member.url
            
        elif isinstance(member, discord.PartialEmoji):
            url = member.url
            
        else:
            url = member.display_avatar.url

        request = await self.client.session.get('https://api.jeyy.xyz/text/emojify',
                                                params={'image_url': url})
        json = await request.json()

        embed = discord.Embed(description=f"""
```
{json['text']}
```
                            """)
        
        await ctx.send(embed=embed)

    @commands.command( # 14
        help="""
Draw your own blocks!
There are currently **25** codes corresponding to a unique block.
```
0 = blank block    g = Gold Block
1 = Grass Block    p = Purple Block
2 = Water          l = Leaf Block
3 = Sand Block     o = Log Block
4 = Stone block    c = Coal Block
5 = Wood Planks    d = Diamond Block
6 = Glass Block    v = Lava
7 = Redstone Block h = Hay Bale
8 = Iron Block     s = Snow Layer
9 = Brick Block    f = Wooden Fence
w = Redstone Dust  r = Redstone Lamp
e = Lever (off)    # = Lever (on)
k = Cake           y = Poppy
```""",
    brief="jeyy iso 401 133 332 - 1 0 5 - 6\njeyy iso 401 133 332 - 1 0 5 - 6") # 14
    async def iso(self, ctx: CustomContext, *, iso):
        request = await self.client.session.get("https://api.jeyy.xyz/isometric", params={'iso_code': f"{iso}"})
        buffer = io.BytesIO(await request.read())
        
        embed = discord.Embed(title="Isometric drawing")
        embed.set_image(url="attachment://isometric_draw.png")
        
        await ctx.send(embed=embed, file=discord.File(buffer, "isometric_draw.png"))