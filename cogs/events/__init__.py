from .bot import Bot
from .chatbot import Chatbot
from .error_handler import ErrorHandler
from .join_leave import JoinLeave
from .private import Private
from .topgg import Topgg


class Handler(Bot, Chatbot, ErrorHandler, JoinLeave, Private, Topgg):
    pass


def setup(bot):
    bot.add_cog(Handler(bot))