import re
import io
import os
import zlib
import discord

from ._base import UtilityBase
from discord.ext import commands
from helpers.context import CustomContext

def finder(text, collection, *, key=None, lazy=True):
    suggestions = []
    text = str(text)
    pat = '.*?'.join(map(re.escape, text))
    regex = re.compile(pat, flags=re.IGNORECASE)
    for item in collection:
        to_search = key(item) if key else item
        r = regex.search(to_search)
        if r:
            suggestions.append((len(r.group()), r.start(), item))

    def sort_key(tup):
        if key:
            return tup[0], tup[1], key(tup[2])
        return tup

    if lazy:
        return (z for _, _, z in sorted(suggestions, key=sort_key))
    else:
        return [z for _, _, z in sorted(suggestions, key=sort_key)]


class SphinxObjectFileReader:
    # Inspired by Sphinx's InventoryFileReader
    BUFSIZE = 16 * 1024

    def __init__(self, buffer):
        self.stream = io.BytesIO(buffer)

    def readline(self):
        return self.stream.readline().decode('utf-8')

    def skipline(self):
        self.stream.readline()

    def read_compressed_chunks(self):
        decompressor = zlib.decompressobj()
        while True:
            chunk = self.stream.read(self.BUFSIZE)
            if len(chunk) == 0:
                break
            yield decompressor.decompress(chunk)
        yield decompressor.flush()

    def read_compressed_lines(self):
        buf = b''
        for chunk in self.read_compressed_chunks():
            buf += chunk
            pos = buf.find(b'\n')
            while pos != -1:
                yield buf[:pos].decode('utf-8')
                buf = buf[pos + 1:]
                pos = buf.find(b'\n')

class RTFM(UtilityBase):

    async def build_rtfm_lookup_table(self, page_types):
        cache = {}
        for key, page in page_types.items():
            sub = cache[key] = {}
            async with self.client.session.get(page + '/objects.inv') as resp:
                if resp.status != 200:
                    continue

                stream = SphinxObjectFileReader(await resp.read())
                cache[key] = self.parse_object_inv(stream, page)

        self._rtfm_cache = cache

    def parse_object_inv(self, stream, url):
        # key: URL
        # n.b.: key doesn't have `discord` or `discord.ext.commands` namespaces
        result = {}

        # first line is version info
        inv_version = stream.readline().rstrip()

        if inv_version != '# Sphinx inventory version 2':
            raise RuntimeError('Invalid objects.inv file version.')

        # next line is "# Project: <name>"
        # then after that is "# Version: <version>"
        projname = stream.readline().rstrip()[11:]
        version = stream.readline().rstrip()[11:]

        # next line says if it's a zlib header
        line = stream.readline()
        if 'zlib' not in line:
            raise RuntimeError('Invalid objects.inv file, not z-lib compatible.')

        # This code mostly comes from the Sphinx repository.
        entry_regex = re.compile(r'(?x)(.+?)\s+(\S*:\S*)\s+(-?\d+)\s+(\S+)\s+(.*)')
        for line in stream.read_compressed_lines():
            match = entry_regex.match(line.rstrip())
            if not match:
                continue

            name, directive, prio, location, dispname = match.groups()
            domain, _, subdirective = directive.partition(':')
            if directive == 'py:module' and name in result:
                # From the Sphinx Repository:
                # due to a bug in 1.1 and below,
                # two inventory entries are created
                # for Python modules, and the first
                # one is correct
                continue

            # Most documentation pages have a label
            if directive == 'std:doc':
                subdirective = 'label'

            if location.endswith('$'):
                location = location[:-1] + name

            key = name if dispname == '-' else dispname
            prefix = f'{subdirective}:' if domain == 'std' else ''

            if projname == 'discord.py':
                key = key.replace('discord.ext.commands.', '').replace('discord.', '')

            result[f'{prefix}{key}'] = os.path.join(url, location)

        return result

    async def do_rtfm(self, ctx: CustomContext, key, obj):
        page_types = {
            'latest': 'https://discordpy.readthedocs.io/en/latest',
            'latest-jp': 'https://discordpy.readthedocs.io/ja/latest',
            'rewrite': 'https://discordpy.readthedocs.io/en/rewrite',
            'legacy': 'https://discordpy.readthedocs.io/en/legacy',
            'python': 'https://docs.python.org/3',
            'python-jp': 'https://docs.python.org/ja/3',
            'master': 'https://discordpy.readthedocs.io/en/master',
            'edpy': 'https://enhanced-dpy.readthedocs.io/en/latest',
            'chai': 'https://chaidiscordpy.readthedocs.io/en/latest',
            'bing': 'https://asyncbing.readthedocs.io/en/latest',
            'pycord': 'https://pycord.readthedocs.io/en/master',
            'pomice': 'https://pomice.readthedocs.io/en/latest'
        }
        embed_titles = {
            'latest': 'discord.py v1.7.3',
            'latest-jp': 'discord.py v1.7.3 in Japanese',
            'rewrite': 'discord.py v1.0.0',
            'legacy': 'discord.py v0.9.0',
            'python': 'python',
            'python-jp': 'python in Japanese',
            'master': 'discord.py v2.0.0a',
            'edpy': 'enhanced-dpy',
            'chai': 'chaidiscord.py',
            'bing': 'asyncbing',
            'pycord': 'pycord',
            'pomice': 'pomice'
        }
        embed_icons = {
            'latest': 'https://cdn.discordapp.com/icons/336642139381301249/3aa641b21acded468308a37eef43d7b3.png',
            'latest-jp': 'https://cdn.discordapp.com/icons/336642139381301249/3aa641b21acded468308a37eef43d7b3.png',
            'rewrite': 'https://cdn.discordapp.com/icons/336642139381301249/3aa641b21acded468308a37eef43d7b3.png',
            'legacy': 'https://cdn.discordapp.com/icons/336642139381301249/3aa641b21acded468308a37eef43d7b3.png',
            'python': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1200px-Python-logo-notext.svg.png',
            'python-jp': 'https://upload.wikimedia.org/wikipedia/commons/thumb/c/c3/Python-logo-notext.svg/1200px-Python-logo-notext.svg.png',
            'master': 'https://cdn.discordapp.com/icons/336642139381301249/3aa641b21acded468308a37eef43d7b3.png',
            'edpy': 'https://cdn.discordapp.com/emojis/781918475009785887.png?size=96',
            'chai': 'https://cdn.discordapp.com/icons/336642139381301249/3aa641b21acded468308a37eef43d7b3.png',
            'bing': 'https://pbs.twimg.com/profile_images/1313103135414448128/0EVE9TeW.png',
            'pycord': 'https://avatars.githubusercontent.com/u/89700626?v=4',
            'pomice': 'https://media.discordapp.net/attachments/381963689470984203/918592368465285140/pomice.png'
        }

        if obj is None:
            await ctx.send(page_types[key])
            return

        if not hasattr(self, '_rtfm_cache'):
            await ctx.trigger_typing()
            await self.build_rtfm_lookup_table(page_types)

        obj = re.sub(r'^(?:discord\.(?:ext\.)?)?(?:commands\.)?(.+)', r'\1', obj)

        if key.startswith('latest'):
            # point the abc.Messageable types properly:
            q = obj.lower()
            for name in dir(discord.abc.Messageable):
                if name[0] == '_':
                    continue
                if q == name:
                    obj = f'abc.Messageable.{name}'
                    break

        cache = list(self._rtfm_cache[key].items())

        matches = finder(obj, cache, key=lambda t: t[0], lazy=False)[:8]

        if len(matches) == 0:
            return await ctx.send('Could not find anything. Sorry.')

        embed = discord.Embed(title=f"RTFM Search: `{obj}`", description='\n'.join(f'[`{key}`]({url})' for key, url in matches))
        embed.set_author(name=embed_titles.get(key, 'Documentation'), icon_url=embed_icons.get(key, 'Documentation'))
        embed.set_thumbnail(url="https://images-ext-2.discordapp.net/external/d0As41Nt_Dkw41hMwucOJg-T4wdwOAngLJ5mHB4bfEc/https/readthedocs-static-prod.s3.amazonaws.com/images/home-logo.eaeeed28189e.png")

        await ctx.send(embed=embed)

    @commands.group(
        invoke_without_command=True,
        help=":books: | Gives you a documentation link for a discord.py entity.\nEvents, objects, and functions are all supported through a cruddy fuzzy algorithm.",
        aliases=['rtfd', 'rtdm'])
    async def rtfm(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'master', obj)

    @rtfm.command(
        help="Gives you a documentation link for a discord.py entity (Japanese).",
        name='jp')
    async def rtfm_jp(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'latest-jp', obj)

    @rtfm.command(
        help="Gives you a documentation link for a discord.py entity (rewrite).",
        name='rewrite',
        aliases=['1.0'])
    async def rtfm_rewrite(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'rewrite', obj)

    @rtfm.command(
        help="Gives you a documentation link for a discord.py entity (legacy).",
        name='legacy',
        aliases=['0.9'])
    async def rtfm_legacy(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'legacy', obj)

    @rtfm.command(
        help="Gives you a documentation link for a Python entity.",
        name='python',
        aliases=['py'])
    async def rtfm_python(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'python', obj)

    @rtfm.command(
        help="Gives you a documentation link for a Python entity (Japanese).",
        name='py-jp',
        aliases=['py-ja'])
    async def rtfm_python_jp(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'python-jp', obj)

    @rtfm.command(
        help="Gives you a documentation link for a discord.py entity (master branch)",
        name='master',
        aliases=['2.0'])
    async def rtfm_master(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'master', obj)

    @rtfm.command(
        help="Gives you a documentation link for a enhanced-discord.py entity",
        name='enhanced-dpy',
        aliases=['edpy'])
    async def rtfm_edpy(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'edpy', obj)

    @rtfm.command(
        help="Gives you a documentation link for an asyncbing entity",
        name='asyncbing',
        aliases=['bing'])
    async def rtfm_asyncbing(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'bing', obj)

    @rtfm.command(
        help="Gives you a documentation link for a chaidiscord.py entity",
        name='chaidiscordpy',
        aliases=['chaidpy', 'cdpy'])
    async def rtfm_chai(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'chai', obj)

    @rtfm.command(
        help="Gives you a documentation link for a pycord entity",
        name='pycord')
    async def rtfm_pycord(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'pycord', obj)

    @rtfm.command(
        help="Gives you a documentation link for a pomice entity",
        name='pomice')
    async def rtfm_pomice(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'pomice', obj)

    @rtfm.command(
        help="Gives you a documentation link for a hikari-lightbulb entity",
        name='lightbulb',
        aliases=['hikari-lightbulb', 'lightbulb-hikari'])
    async def rtfm_lightbulb(self, ctx: CustomContext, *, obj: str = None):
        await self.do_rtfm(ctx, 'lightbulb', obj)