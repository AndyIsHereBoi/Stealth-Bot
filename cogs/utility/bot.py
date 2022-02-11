import time
import yaml
import discord

from ._base import UtilityBase
from discord.ext import commands
from helpers.context import CustomContext
from discord.ext.commands.cooldowns import BucketType

with open(r'/root/stealthbot/config.yaml') as file:
    full_yaml = yaml.load(file)

yaml_data = full_yaml

class Bot(UtilityBase):

    @commands.command(
        help="Shows the latency of the bot",
        aliases=['pong'])
    @commands.cooldown(1, 15, BucketType.member)
    async def ping(self, ctx: CustomContext) -> discord.Message:
        pings = []
        number = 0

        typing_start = time.monotonic()
        await ctx.trigger_typing()
        typing_end = time.monotonic()
        typing_ms = (typing_end - typing_start) * 1000
        pings.append(typing_ms)

        message_start = time.perf_counter()
        message = await ctx.send("Pong!")
        message_end = time.perf_counter()
        message_ms = (message_end - message_start) * 1000
        pings.append(message_ms)

        await message.delete()

        latency_ms = self.bot.latency * 1000
        pings.append(latency_ms)

        postgres_start = time.perf_counter()
        await self.bot.db.fetch("SELECT 1")
        postgres_end = time.perf_counter()
        postgres_ms = (postgres_end - postgres_start) * 1000
        pings.append(postgres_ms)

        open_robot_start = time.perf_counter()
        await self.bot.session.get("https://api.openrobot.xyz/_internal/available")
        open_robot_end = time.perf_counter()
        open_robot_ms = (open_robot_end - open_robot_start) * 1000
        pings.append(open_robot_ms)

        open_robot_repi_start = time.perf_counter()
        await self.bot.session.get("https://repi.openrobot.xyz/eval", params={"auth": f"{yaml_data['OR_TEST_TOKEN']}", "code": "print('ping test')"})
        open_robot_repi_end = time.perf_counter()
        open_robot_repi_ms = (open_robot_repi_end - open_robot_repi_start) * 1000
        pings.append(open_robot_repi_ms)

        jeyy_start = time.perf_counter()
        await self.bot.session.get("https://api.jeyy.xyz/isometric", params={'iso_code': "401 133 332"})
        jeyy_end = time.perf_counter()
        jeyy_ms = (jeyy_end - jeyy_start) * 1000
        pings.append(jeyy_ms)

        dagpi_start = time.perf_counter()
        await self.bot.dagpi.yomama()
        dagpi_end = time.perf_counter()
        dagpi_ms = (dagpi_end - dagpi_start) * 1000
        pings.append(dagpi_ms)

        waifu_im_start = time.perf_counter()
        await self.bot.session.get("https://api.waifu.im/sfw/waifu")
        waifu_im_end = time.perf_counter()
        waifu_im_ms = (waifu_im_end - waifu_im_start) * 1000
        pings.append(waifu_im_ms)

        for ms in pings:
            number += ms

        average = number / len(pings)

        embed = discord.Embed(title="🏓 Pong")

        embed.add_field(name=f":globe_with_meridians: Websocket latency",
                        value=f"{round(latency_ms)}ms{' ' * (9 - len(str(round(latency_ms, 3))))}", inline=True)

        embed.add_field(name=f"<a:typing:597589448607399949> Typing latency",
                        value=f"{round(typing_ms)}ms{' ' * (9 - len(str(round(typing_ms, 3))))}", inline=True)

        embed.add_field(name=f":speech_balloon: Message latency",
                        value=f"{round(message_ms)}ms{' ' * (9 - len(str(round(message_ms, 3))))}", inline=True)

        embed.add_field(name=f"<:psql:896134588961800294> PostgreSQL latency",
                        value=f"{round(postgres_ms)}ms{' ' * (9 - len(str(round(postgres_ms, 3))))}", inline=True)

        embed.add_field(name=f"<:OpenRobot:922490609288241192> OpenRobot API latency",
                        value=f"{round(open_robot_ms)}ms{' ' * (9 - len(str(round(open_robot_ms, 3))))}", inline=True)

        embed.add_field(name=f"<:OpenRobot:922490609288241192> OpenRobot REPI latency",
                        value=f"{round(open_robot_repi_ms)}ms{' ' * (9 - len(str(round(open_robot_repi_ms, 3))))}", inline=True)

        embed.add_field(name="<:pensive_cowboy:787677850165706763> Jeyy API latency",
                        value=f"{round(jeyy_ms)}ms{' ' * (9 - len(str(round(jeyy_ms, 3))))}", inline=True)

        embed.add_field(name="<:dagpi:922493027073814530> Dagpi API latency",
                        value=f"{round(dagpi_ms)}ms{' ' * (9 - len(str(round(dagpi_ms, 3))))}", inline=True)

        embed.add_field(name="Waifu.im API latency",
                        value=f"{round(waifu_im_ms)}ms{' ' * (9 - len(str(round(waifu_im_ms, 3))))}", inline=True)

        embed.add_field(name=f":infinity: Average latency",
                        value=f"{round(average)}ms{' ' * (9 - len(str(round(average, 3))))}", inline=False)

        return await ctx.send(embed=embed)
        
    @commands.command(
        help="Shows the uptime of the bot.",
        aliases=['up'])
    async def uptime(self, ctx: CustomContext) -> discord.Message:
        delta_uptime = discord.utils.utcnow() - self.bot.launch_time
        hours, remainder = divmod(int(delta_uptime.total_seconds()), 3600)
        minutes, seconds = divmod(remainder, 60)
        days, hours = divmod(hours, 24)

        embed = discord.Embed(title=f"I've been online for {ctx.time(days=days, hours=hours, minutes=minutes, seconds=seconds)}")

        return await ctx.send(embed=embed)

    @commands.command(
        help="Shows how many servers the bot is in.",
        aliases=['guilds'])
    async def servers(self, ctx: CustomContext) -> discord.Message:
        embed = discord.Embed(title=f"I'm in `{len(self.bot.guilds)}` servers.")

        return await ctx.send(embed=embed)

    @commands.command(
        help="Shows how many messages the bot has seen since the last restart.",
        aliases=['msg', 'msgs', 'message'])
    async def messages(self, ctx: CustomContext) -> discord.Message:
        embed = discord.Embed(title=f"I've seen a total of `{self.bot.messages_count}` messages and `{self.bot.edited_messages_count}` edits.")

        return await ctx.send(embed=embed)