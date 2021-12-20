import discord
from discord.ext import commands, tasks

from helpers import helpers, paginator, time_inputs


class ReminderRecord:
    """Wrapper to remind record for a custom object representation"""

    def __init__(self, record):
        self.record = record

    def __str__(self):
        return f"{self.record['id']}. {self.record['task']} - {discord.utils.format_dt(self.record['end_time'], 'R')}"


def setup(client):
    client.add_cog(Reminder(client))


class Reminder(commands.Cog):
    """Commands to remind you to do tasks!"""

    def __init__(self, client):
        self.client = client
        self.reminder_task.start()

        self.select_emoji = "<a:ShameBell:922126860459048980>"
        self.select_brief = "Commands to remind you to do tasks!"

    def cog_unload(self):
        self.reminder_task.cancel()

    @tasks.loop()
    async def reminder_task(self):
        try:
            next_task = await self.client.db.fetchrow("SELECT * FROM reminders WHERE end_time < NOW() ORDER BY end_time LIMIT 1")

            if next_task is None:
                self.reminder_task.stop()

            await discord.utils.sleep_until(next_task["end_time"])

            delta = helpers.human_timedelta(next_task["end_time"], source=next_task["created_at"])

            channel = self.client.get_channel(next_task["channel_id"])
            message = await channel.fetch_message(next_task["message_id"])

            view = discord.ui.View()
            item = discord.ui.Button(style=discord.ButtonStyle.gray, label="Go to original message",
                                     url=f"{message.jump_url}")
            view.add_item(item=item)

            await channel.send(
                f"{message.author.mention}, {discord.utils.format_dt(message.created_at, 'R')}: {next_task['task']}",
                view=view)

            await self.client.db.execute(f"DELETE FROM reminders WHERE id = {next_task['id']}")

        except:
            self.reminder_task.restart()

    async def create_timer(self, ctx: commands.Context, time: time_inputs.ShortTime, task: str):
        database = await self.client.db.execute("INSERT INTO reminders (user_id, task, created_at, end_time, message_id, channel_id) VALUES($1, $2, $3, $4, $5, $6)",
                                                ctx.author.id, task, ctx.message.created_at, time.dt, ctx.message.id, ctx.channel.id)

    @commands.group(
        invoke_without_command=True,
        help="Sets a reminder for the specified time.",
        aliases=['reminder', 'timer'])
    async def remind(self, ctx, time: time_inputs.ShortTime, *, task: str) -> discord.Message:
        delta = helpers.human_timedelta(time.dt, source=ctx.message.created_at)

        await self.create_timer(ctx, time, task)
        return await ctx.send(f"Alright {ctx.author.mention} in {delta}: {task}")

    @remind.command(
        name="list",
        help="Shows you a list of your current reminders",
        aliases=['show', 'all', 'l'])
    async def remind_list(self, ctx) -> discord.Message:
        records = await self.client.db.fetch("SELECT * FROM reminders WHERE user_id = $1 ORDER BY end_time", ctx.author.id)

        if not records:
            return await ctx.send("You don't have any reminders set.")

        remind_records = [str(ReminderRecord(record)) for record in records]

        embed = discord.Embed(title=f"Your reminders", color=0XA321F3, timestamp=discord.utils.utcnow())
        view = await paginator.ViewPaginator(paginator.SimplePageSource(embed=embed, entries=remind_records, per_page=10), ctx=ctx).start()

        return await ctx.send("\u200b", view=view)

    @remind.command(
        name="delete",
        help="Deletes the specified reminder.",
        aliases=["remove", "r"])
    async def remind_delete(self, ctx, id: int) -> discord.Message:
        deleted_reminder = await self.client.db.fetch("DELETE FROM reminders WHERE id = $1 RETURNING id", id)

        if not deleted_reminder:
            return await ctx.send("That reminder doesn't exist.")

        return await ctx.send(f"Reminder {deleted_reminder['id']} successfully deleted.")

    @remind.command(
        name="clear",
        help="Removes all your reminders.",
        aliases=["clean", "empty", "c"])
    async def remind_clear(self, ctx) -> discord.Message:
        confirmation = await ctx.confirm("Are you sure you want to clear all your reminders?\n**This cannot be undone.**")

        if confirmation:
            deleted_reminders = await self.client.db.fetch("DELETE FROM reminders WHERE user_id = $1 RETURNING *", ctx.author.id)

            if not deleted_reminders:
                return await ctx.send("You don't have any reminders set.")

            return await ctx.send(f"{ctx.author.mention}, your reminders are successfully deleted.")

        return await ctx.send("Alright, I won't delete your reminders.")
