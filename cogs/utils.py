import discord

async def send_error_embed(interaction, message, suggestion=None):
    embed = discord.Embed(title="❌ Hata", description=message, color=discord.Color.red())
    if suggestion:
        embed.add_field(name="Öneri", value=suggestion, inline=False)
    await interaction.followup.send(embed=embed, ephemeral=True)

async def check_voice_channel(interaction):
    if interaction.user.voice is None or interaction.user.voice.channel is None:
        await send_error_embed(interaction, "Bu komutu kullanmak için bir ses kanalına katılmalısınız!")
        return False
    return True

async def check_next_song(interaction, queue):
    if not queue.has_next():
        await send_error_embed(interaction, "Bu komutu kullanmak için sırada çalınacak bir şarkı olmalı!")
        return False
    return True
