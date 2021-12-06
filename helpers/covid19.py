import aiohttp
import json

async def covid19():
  async with aiohttp.ClientSession() as session:
    async with session.get("https://api.covid19api.com/world/total") as request:
      request = await request.json()
      
  return request