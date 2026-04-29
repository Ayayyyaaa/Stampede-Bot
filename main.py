import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

class StampedeBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True  
        intents.members = True 
        intents.reactions = True
        super().__init__(command_prefix="stampede", intents=intents)

    async def setup_hook(self):
        await self.load_extension("src.events")
        await self.load_extension("src.commands")
        await self.load_extension("src.announcement")
        await self.load_extension("src.scores")
        await self.load_extension("src.whois")
        await self.tree.sync()
        print("✅ Commandes Slash synchronisées.")

    async def on_ready(self):
        print(f"✅ Connecté en tant que {self.user}")

bot = StampedeBot()
bot.run(os.getenv("DISCORD_TOKEN"))