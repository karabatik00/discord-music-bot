import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

# .env dosyasını yükleme
load_dotenv()

# .env dosyasından bot tokenini alma
BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.message_content = True

class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents, help_command=None)

    async def setup_hook(self):
        cogs = ['cogs.music', 'cogs.general']
        for cog in cogs:
            await self.load_extension(cog)
        await self.tree.sync()

    async def on_ready(self):
        print(f'Logged in as {self.user} (ID: {self.user.id})')
        print('------')

bot = MyBot()
bot.run(BOT_TOKEN)
