from discord.ext import commands, ipc


def setup(client):
    client.add_cog(IPC(client))


class IPC(commands.Cog):
    "IPC."

    def __init__(self, client):
        self.client = client
        self.hidden = True
        self.select_emoji = "<:blobpain:739614945045643447>"
        self.select_brief = "IPC."

    @ipc.server.route()
    async def get_servers(self, data):
        return len(self.client.guilds)

    @commands.Cog.listener()
    async def on_ipc_ready(self):
        print("Ipc is ready.")

    @commands.Cog.listener()
    async def on_ipc_error(self, endpoint, error):
        print(endpoint, "raised", error)