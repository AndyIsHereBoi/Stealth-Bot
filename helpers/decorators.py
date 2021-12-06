import discord
from discord.ext import commands

from errors import NotStartedEconomy



def has_started():
	async def predicate(ctx):
		
		player = await ctx.bot.db.fetchval(""" SELECT user_id FROM economy WHERE user_id = $1 """, ctx.author.id)
		if player:
			return True

		else:
			raise NotStartedEconomy(f"{ctx.author.mention}, You don't have any balance! You have to do `{ctx.prefix}start` to make one.")
	return commands.check(predicate)


def has_ref_started():
	async def predicate(ctx):
		if ctx.message.reference:
			p_id = ctx.message.reference.resolved.author.id
			player = await ctx.bot.db.fetchval(""" SELECT user_id FROM economy WHERE user_id = $1 """, p_id)
			if player:
			
				return True
			else:
				
				raise NotStartedEconomy(f"{ctx.message.reference.resolved.author} doesn't have a balance yet! They have to do `{ctx.prefix}start` to make one.")
		else:
			
			player = await ctx.bot.db.fetchval(""" SELECT user_id FROM economy WHERE user_id = $1 """, ctx.author.id)
			if player:
				return True
			else:
				raise NotStartedEconomy(f"{ctx.author.mention}, You don't have any balance! You have to do `{ctx.prefix}start` to make one.")
		
		
	return commands.check(predicate)