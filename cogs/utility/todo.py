import errors
import random
import discord

from ._base import UtilityBase
from discord.ext import commands, menus
from helpers.context import CustomContext
from discord.ext.menus.views import ViewMenuPages

class TodoListEmbedPage(menus.ListPageSource):
    def __init__(self, title, author, data):
        self.title = title
        self.author = author
        self.data = data
        super().__init__(data, per_page=15)

    async def format_page(self, menu, entries):
        offset = menu.current_page * self.per_page
        colors = [0x910023, 0xA523FF]
        color = random.choice(colors)
        embed = discord.Embed(title=self.title, description="\n".join(entries), timestamp=discord.utils.utcnow(), color=color)
        embed.set_footer(text=f"Requested by: {self.author.name}", icon_url=self.author.avatar.url)

        return embed

class Todo(UtilityBase):

    @commands.group(
        help="<:scroll:904038785921187911> Todo commands.",
        aliases=['tasks'])
    async def todo(self, ctx: CustomContext):
        if ctx.invoked_subcommand is None:
            await ctx.send_help(ctx.command)

    @todo.command(
        name="add",
        help="Adds the specified task to your todo list.",
        aliases=['create', 'new', 'make'])
    async def todo_add(self, ctx: CustomContext, *, text) -> discord.Message:
        todo = await self.bot.db.fetchrow(
            "INSERT INTO todo (user_id, text, jump_url, creation_date) VALUES ($1, $2, $3, $4) ON CONFLICT (user_id, text) DO UPDATE SET user_id = $1 RETURNING jump_url, creation_date",
            ctx.author.id, text, ctx.message.jump_url, ctx.message.created_at)

        if todo['creation_date'] != ctx.message.created_at:
            embed = discord.Embed(title="That's already in your todo list!", url=f"{todo['jump_url']}",
                                  description=f"[Added here]({todo['jump_url']})")

            return await ctx.send(embed=embed)

        embed = discord.Embed(title="Added to your todo list:", description=text)

        return await ctx.send(embed=embed)

    @todo.command(
        name="list",
        help="Sends a list of your tasks.",
        aliases=['show', 'view'])
    async def todo_list(self, ctx: CustomContext):
        todos = await self.bot.db.fetch(
            "SELECT text, creation_date, jump_url FROM todo WHERE user_id = $1 ORDER BY creation_date ASC",
            ctx.author.id)

        if not todos:
            raise errors.EmptyTodoList

        todoList = []
        number = 0

        for todo in todos:
            number = number + 1
            todoList.append(
                f"**[{number}]({todo['jump_url']})**. **({discord.utils.format_dt(todo['creation_date'], style='R')}):** {todo['text']}")

        title = f"{ctx.author.name}'s todo list"

        paginator = ViewMenuPages(source=TodoListEmbedPage(title=title, author=ctx.author, data=todoList),
                                  clear_reactions_after=True)
        page = await paginator._source.get_page(0)
        kwargs = await paginator._get_kwargs_from_page(page)

        if paginator.build_view():
            paginator.message = await ctx.send(embed=kwargs['embed'], view=paginator.build_view())

        else:
            paginator.message = await ctx.send(embed=kwargs['embed'])

        await paginator.start(ctx)

    @todo.command(
        name="clear",
        help="Deletes all tasks from your todo list.",
        aliases=['nuke'])
    async def todo_clear(self, ctx: CustomContext) -> discord.Message:
        confirm = await ctx.confirm("Are you sure you want to clear your todo list?\n*This action cannot be undone*")

        if confirm is True:
            todos = await self.bot.db.fetchval(
                "WITH deleted AS (DELETE FROM todo WHERE user_id = $1 RETURNING *) SELECT count(*) FROM deleted;",
                ctx.author.id)

            embed = discord.Embed(title="Cleared your todo list.", description=f"{todos} tasks were removed.")

            return await ctx.send(embed=embed)

        return await ctx.send("Okay, cancelled.")

    @todo.command(
        name="remove",
        help="Removes the specified task from your todo list",
        aliases=['delete', 'del', 'rm'])
    async def todo_remove(self, ctx: CustomContext, index: int) -> discord.Message:
        todos = await self.bot.db.fetch(
            "SELECT text, jump_url, creation_date FROM todo WHERE user_id = $1 ORDER BY creation_date ASC",
            ctx.author.id)

        try:
            to_delete = todos[index - 1]

        except:
            return await ctx.send(f"I couldn't find a task with index {index}")

        await self.bot.db.execute("DELETE FROM todo WHERE (user_id, text) = ($1, $2)", ctx.author.id,
                                     to_delete['text'])

        embed = discord.Embed(title=f"Successfully removed task number **{index}**:",
                              description=f"({discord.utils.format_dt(to_delete['creation_date'], style='R')}) {to_delete['text']}")

        return await ctx.send(embed=embed)

    @todo.command(
        name="edit",
        help="Edits the specified task",
        aliases=['change', 'modify'])
    async def todo_edit(self, ctx: CustomContext, index: int, *, text) -> discord.Message:
        todos = await self.bot.db.fetch(
            "SELECT text, jump_url, creation_date FROM todo WHERE user_id = $1 ORDER BY creation_date ASC",
            ctx.author.id)

        try:
            to_edit = todos[index - 1]

        except KeyError:
            return await ctx.send(f"I couldn't find a task with index {index}")

        old = await self.bot.db.fetchrow(
            "SELECT text, creation_date, jump_url FROM todo WHERE (user_id, text) = ($1, $2)", ctx.author.id,
            to_edit['text'])

        await self.bot.db.execute(
            "UPDATE todo SET text = $1, jump_url = $2, creation_date = $3 WHERE (user_id, text) = ($4, $5)",
            f"{text} (edited)", ctx.message.jump_url, ctx.message.created_at, ctx.author.id, to_edit['text'])

        new = await self.bot.db.fetchrow(
            "SELECT text, creation_date, jump_url FROM todo WHERE (user_id, text) = ($1, $2)", ctx.author.id,
            f"{text} (edited)")

        embed = discord.Embed(title=f"Successfully edited task number **{index}**:", description=f"""
    __**Old**__
    Text: {old['text']}
    Creation date: {discord.utils.format_dt(old['creation_date'], style='R')}
    Jump URL: [Click here]({old['jump_url']})

    __**New**__
    Text: {new['text']}
    Creation date: {discord.utils.format_dt(new['creation_date'], style='R')}
    Jump URL: [Click here]({new['jump_url']})
                    """)

        return await ctx.send(embed=embed)