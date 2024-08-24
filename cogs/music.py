import discord
from discord.ext import commands
from discord import app_commands
import yt_dlp as youtube_dl
import asyncio
import random
from collections import deque, defaultdict
from .utils import send_error_embed, check_voice_channel, check_next_song

ytdl_format_options = {
    'format': 'bestaudio',
    'noplaylist': False,
    'outtmpl': 'downloads/%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'quiet': True,
    'no_warnings': True,
}
ffmpeg_options = {
    'before_options':
    '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn -b:a 128k'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, volume=1.0):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('webpage_url')
        self.duration = data.get('duration')
        self.thumbnail = data.get('thumbnail')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(
                None, lambda: ytdl.extract_info(url, download=not stream))
        except Exception as e:
            raise commands.CommandInvokeError(
                f"URL'den bilgi alınırken hata oluştu: {str(e)}")

        if 'entries' in data:
            return [
                cls(discord.FFmpegPCMAudio(entry['url'], **ffmpeg_options),
                    data=entry) for entry in data['entries']
            ]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return [
            cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
        ]

class MusicQueue:

    def __init__(self):
        self.queue = deque()
        self.loop = False
        self.current = None
        self.previous = None

    def add(self, items):
        if isinstance(items, list):
            self.queue.extend(items)
        else:
            self.queue.append(items)

    def next(self):
        if self.loop and self.current:
            self.queue.append(self.current)
        if len(self.queue) > 0:
            self.previous = self.current
            self.current = self.queue.popleft()
            return self.current
        return None

    def shuffle(self):
        random.shuffle(self.queue)

    def clear(self):
        self.queue.clear()
        self.current = None
        self.previous = None

    def list(self):
        return list(self.queue)

    def has_next(self):
        return len(self.queue) > 0

    def has_previous(self):
        return self.previous is not None

guild_queues = defaultdict(dict)

def get_queue(guild_id, channel_id):
    if channel_id not in guild_queues[guild_id]:
        guild_queues[guild_id][channel_id] = MusicQueue()
    return guild_queues[guild_id][channel_id]

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print("Music Cog has been loaded")

    @app_commands.command(name="play", description="Bir müzik veya oynatma listesini çalar.")
    @app_commands.describe(effect="Uygulamak istediğiniz ses efektini seçin")
    @app_commands.choices(effect=[
        app_commands.Choice(name="None", value="none"),
        app_commands.Choice(name="Reverb", value="reverb"),
        app_commands.Choice(name="Bass Boost", value="bass"),
        app_commands.Choice(name="Treble Boost", value="treble"),
        app_commands.Choice(name="Echo", value="echo"),
        app_commands.Choice(name="Speed", value="speed"),
        app_commands.Choice(name="Nightcore", value="nightcore")
    ])
    async def play(self, interaction: discord.Interaction, url: str, effect: app_commands.Choice[str]):
        if not await check_voice_channel(interaction):
            return

        await interaction.response.defer()
        guild_id = interaction.guild.id
        channel_id = interaction.user.voice.channel.id

        queue = get_queue(guild_id, channel_id)
        voice_channel = interaction.user.voice.channel
        voice_client = discord.utils.get(self.bot.voice_clients, guild=interaction.guild)

        if voice_client is None or voice_client.channel.id != channel_id:
            voice_client = await voice_channel.connect(reconnect=True)

        if effect.value == "bass":
            ffmpeg_options['options'] = '-vn -af "bass=g=10"'
        elif effect.value == "reverb":
            ffmpeg_options['options'] = '-vn -af "aecho=0.8:0.9:1000:0.3"'
        elif effect.value == "treble":
            ffmpeg_options['options'] = '-vn -af "treble=g=5"'
        elif effect.value == "echo":
            ffmpeg_options['options'] = '-vn -af "aecho=0.8:0.88:60:0.4"'
        elif effect.value == "speed":
            ffmpeg_options['options'] = '-vn -af "atempo=1.5"'
        elif effect.value == "nightcore":
            ffmpeg_options['options'] = '-vn -af "atempo=1.25,asetrate=44100*1.25"'
        else:
            ffmpeg_options['options'] = '-vn'

        async with interaction.channel.typing():
            try:
                players = await YTDLSource.from_url(url, loop=self.bot.loop, stream=True)
                queue.add(players)

                if not voice_client.is_playing():
                    voice_client.play(queue.next(), after=lambda e: self.play_next(voice_client, guild_id, channel_id))
                    player = queue.current
                    embed = discord.Embed(
                        title="🎶 Şu Anda Çalıyor",
                        description=f"[{player.title}]({player.url})",
                        color=discord.Color.blue())
                    embed.add_field(
                        name="⏳ Süre",
                        value=f"{player.duration // 60}:{player.duration % 60:02d}",
                        inline=True)
                    embed.add_field(name="🎧 Kanal",
                                    value=voice_channel.name,
                                    inline=True)
                    embed.set_thumbnail(url=player.thumbnail)
                    embed.set_image(url=player.thumbnail)
                    embed.set_footer(text="İyi dinlemeler!",
                                     icon_url=self.bot.user.avatar.url)
                    await interaction.followup.send(embed=embed)
                else:
                    embed = discord.Embed(
                        title="📥 Sıraya Eklendi",
                        description=f"{len(players)} şarkı sıraya eklendi.",
                        color=discord.Color.green())
                    embed.set_footer(
                        text="Şarkı sırasını görmek için /queue komutunu kullanabilirsiniz.",
                        icon_url=self.bot.user.avatar.url)
                    await interaction.followup.send(embed=embed)
            except youtube_dl.DownloadError:
                await send_error_embed(interaction, "URL geçersiz veya desteklenmiyor.", "Farklı bir URL deneyin.")
            except discord.errors.ClientException as e:
                await send_error_embed(interaction, "FFmpeg bulunamadı. Lütfen FFmpeg'in kurulu olduğundan emin olun.", str(e))
            except Exception as e:
                await send_error_embed(interaction, "Bilinmeyen bir hata oluştu.", f"Lütfen geliştiriciye şu hatayı bildirin: {str(e)}")

    def play_next(self, voice_client, guild_id, channel_id):
        queue = get_queue(guild_id, channel_id)
        next_song = queue.next()
        if next_song:
            voice_client.play(next_song, after=lambda e: self.play_next(voice_client, guild_id, channel_id))

    @app_commands.command(name="skip", description="Sıradaki şarkıyı atlar.")
    async def skip(self, interaction: discord.Interaction):
        if not await check_voice_channel(interaction):
            return

        guild_id = interaction.guild.id
        channel_id = interaction.user.voice.channel.id
        queue = get_queue(guild_id, channel_id)

        if not await check_next_song(interaction, queue):
            return

        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            embed = discord.Embed(title="⏭️ Şarkı Atlandı",
                                  description="Sıradaki şarkı çalıyor.",
                                  color=discord.Color.orange())
            await interaction.response.send_message(embed=embed)
        else:
            await send_error_embed(interaction, "Şu anda çalınan bir şarkı yok.")

    @app_commands.command(name="queue", description="Sıradaki şarkıları listeler.")
    async def queue_list(self, interaction: discord.Interaction):
        guild_id = interaction.guild.id
        channel_id = interaction.user.voice.channel.id
        queue = get_queue(guild_id, channel_id)

        if not await check_next_song(interaction, queue):
            return

        songs = queue.list()
        embed = discord.Embed(title="🎵 Sıradaki Şarkılar",
                              color=discord.Color.purple())

        for i, song in enumerate(songs):
            embed.add_field(
                name=f"{i + 1}. {song.title}",
                value=f"⏳ Süre: {song.duration // 60}:{song.duration % 60:02d} | [Bağlantı]({song.url})",
                inline=False)

        embed.set_footer(
            text="Şarkı sırasını karıştırmak için /shuffle komutunu kullanabilirsiniz.",
            icon_url=self.bot.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="shuffle", description="Sıradaki şarkıları karıştırır.")
    async def shuffle(self, interaction: discord.Interaction):
        if not await check_voice_channel(interaction):
            return

        guild_id = interaction.guild.id
        channel_id = interaction.user.voice.channel.id
        queue = get_queue(guild_id, channel_id)

        if not await check_next_song(interaction, queue):
            return

        queue.shuffle()
        embed = discord.Embed(title="🔀 Karıştırıldı",
                              description="Şarkı sırası karıştırıldı.",
                              color=discord.Color.teal())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="loop", description="Döngü modunu açar/kapatır.")
    async def loop(self, interaction: discord.Interaction):
        if not await check_voice_channel(interaction):
            return

        guild_id = interaction.guild.id
        channel_id = interaction.user.voice.channel.id
        queue = get_queue(guild_id, channel_id)

        if not queue.current:
            await send_error_embed(interaction, "Şu anda çalan bir şarkı yok.")
            return

        queue.loop = not queue.loop
        embed = discord.Embed(
            title="🔁 Döngü Modu",
            description=f"Döngü modu {'açıldı' if queue.loop else 'kapandı'}.",
            color=discord.Color.gold())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="pause", description="Çalan şarkıyı duraklatır.")
    async def pause(self, interaction: discord.Interaction):
        if not await check_voice_channel(interaction):
            return

        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.pause()
            embed = discord.Embed(title="⏸️ Şarkı Duraklatıldı",
                                  description="Çalan şarkı duraklatıldı.",
                                  color=discord.Color.orange())
            await interaction.response.send_message(embed=embed)
        else:
            await send_error_embed(
                interaction,
                "Şu anda çalınan bir şarkı yok veya şarkı zaten duraklatılmış.")

    @app_commands.command(name="resume", description="Duraklatılmış şarkıyı devam ettirir.")
    async def resume(self, interaction: discord.Interaction):
        if not await check_voice_channel(interaction):
            return

        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_paused():
            voice_client.resume()
            embed = discord.Embed(
                title="▶️ Şarkı Devam Ettirildi",
                description="Duraklatılmış şarkı kaldığı yerden devam ediyor.",
                color=discord.Color.green())
            await interaction.response.send_message(embed=embed)
        else:
            await send_error_embed(
                interaction,
                "Şu anda duraklatılmış bir şarkı yok veya şarkı zaten çalıyor.")

    @app_commands.command(name="stop", description="Müziği durdurur ve kanaldan ayrılır.")
    async def stop(self, interaction: discord.Interaction):
        if not await check_voice_channel(interaction):
            return

        guild_id = interaction.guild.id
        channel_id = interaction.user.voice.channel.id
        queue = get_queue(guild_id, channel_id)

        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            voice_client.stop()
            queue.clear()
            await voice_client.disconnect()
            embed = discord.Embed(
                title="🛑 Müzik Durduruldu",
                description="Müzik durduruldu ve bot kanaldan ayrıldı.",
                color=discord.Color.red())
            await interaction.response.send_message(embed=embed)
        else:
            await send_error_embed(interaction, "Şu anda müzik çalmıyor.")

    @app_commands.command(name="nowplaying", description="Şu anda çalan şarkıyı gösterir.")
    async def nowplaying(self, interaction: discord.Interaction):
        if not await check_voice_channel(interaction):
            return

        guild_id = interaction.guild.id
        channel_id = interaction.user.voice.channel.id
        queue = get_queue(guild_id, channel_id)

        if queue.current:
            embed = discord.Embed(
                title="🎶 Şu Anda Çalıyor",
                description=f"[{queue.current.title}]({queue.current.url})",
                color=discord.Color.blue())
            embed.add_field(
                name="⏳ Süre",
                value=f"{queue.current.duration // 60}:{queue.current.duration % 60:02d}",
                inline=True)
            embed.add_field(name="🔁 Döngü Modu",
                            value="Açık" if queue.loop else "Kapalı",
                            inline=True)
            embed.set_thumbnail(url=queue.current.thumbnail)
            embed.set_image(url=queue.current.thumbnail)
            embed.set_footer(text="Müziğin keyfini çıkarın!",
                             icon_url=self.bot.user.avatar.url)
            await interaction.response.send_message(embed=embed)
        else:
            embed = discord.Embed(title="ℹ️ Bilgi",
                                  description="Şu anda çalan bir şarkı yok.",
                                  color=discord.Color.greyple())
            await interaction.response.send_message(embed=embed)

    @app_commands.command(name="previous", description="Önceki şarkıyı çalar.")
    async def previous(self, interaction: discord.Interaction):
        if not await check_voice_channel(interaction):
            return

        guild_id = interaction.guild.id
        channel_id = interaction.user.voice.channel.id
        queue = get_queue(guild_id, channel_id)

        if not queue.has_previous():
            await send_error_embed(interaction, "Önceki bir şarkı yok.")
            return

        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_playing():
            queue.current = queue.previous
            queue.previous = None
            voice_client.stop()
            voice_client.play(
                queue.current,
                after=lambda e: self.play_next(voice_client, guild_id, channel_id))
            embed = discord.Embed(
                title="⏪ Önceki Şarkı Çalınıyor",
                description=f"[{queue.current.title}]({queue.current.url})",
                color=discord.Color.blue())
            embed.add_field(
                name="⏳ Süre",
                value=f"{queue.current.duration // 60}:{queue.current.duration % 60:02d}",
                inline=True)
            embed.set_thumbnail(url=queue.current.thumbnail)
            embed.set_image(url=queue.current.thumbnail)
            await interaction.response.send_message(embed=embed)
        else:
            await send_error_embed(interaction, "Şu anda çalınan bir şarkı yok.")

async def setup(bot):
    await bot.add_cog(Music(bot))
