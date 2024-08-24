import discord
from discord.ext import commands
from discord import app_commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("General Cog has been loaded")

    @app_commands.command(name="commands", description="Botun komutlarını listeler.")
    async def commands_command(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📜 Yardım", description="Botun mevcut komutları:", color=discord.Color.green())
        commands_list = {
            "/play <url> [effect]": "Bir müzik veya oynatma listesini çalar.",
            "/pause": "Çalan şarkıyı duraklatır.",
            "/resume": "Duraklatılmış şarkıyı devam ettirir.",
            "/skip": "Sıradaki şarkıyı atlar.",
            "/queue": "Sıradaki şarkıları listeler.",
            "/shuffle": "Sıradaki şarkıları karıştırır.",
            "/loop": "Döngü modunu açar/kapatır.",
            "/stop": "Müziği durdurur ve kanaldan ayrılır.",
            "/nowplaying": "Şu anda çalan şarkıyı gösterir.",
            "/previous": "Önceki şarkıyı çalar."
            "/commands`: Tüm komutları listeler."
        }
        for command, description in commands_list.items():
            embed.add_field(name=command, value=description, inline=False)
        embed.set_footer(text="Daha fazla bilgi için belirli komutları kullanın!")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))
