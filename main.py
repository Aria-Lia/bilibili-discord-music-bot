import asyncio

import discord
import os
import utils

from discord.ext import commands

DISCORD_TOKEN = os.environ.get('DISCORD_TOKEN')
intents = discord.Intents.all()
bot = commands.Bot(command_prefix='/', intents=intents)


@bot.hybrid_command()
async def join(ctx):
    channel = ctx.author.voice.channel
    await channel.connect()
    current_guild = channel.guild
    current_channel = channel.name
    print('Join guild-channel: {}-{}'.format(current_guild, current_channel))


@bot.hybrid_command()
async def leave(ctx):
    await ctx.voice_client.disconnect()
    print('Stop playing and leave channel')


@bot.hybrid_command(name='bp')
async def play_music(ctx, bvid):
    if not ctx.message.author.voice:
        await ctx.send('You are not connected to a voice channel')
        return

    if not bvid:
        await ctx.send('Use: /bp {Full url|BV id}')
        return

    if not ctx.voice_client:
        await join(ctx)

    if ctx.voice_client.is_playing() or ctx.voice_client.is_paused():
        await ctx.send('Playing another track')
        return

    bv_id = utils.get_bv_id_from_url(bvid)
    print(f'BV ID = {bvid}')
    title, cid, description, author = utils.get_cid_from_bv_id(bv_id)
    print(f'Title = {title} | cid = {cid}')
    audio_url = utils.get_audio_url_from_bv_id(bv_id, cid)
    print(f'Audio URL = {audio_url}')
    audio_source = utils.get_discord_mpeg_audio_from_audio_url(audio_url)
    if not audio_source:
        print('Audio source not found')

    embed = utils.get_discord_embed(
        author,
        title=title,
        url=f'https://www.bilibili.com/video/{bvid}',
        description=description,
    )
    await ctx.send("Playing: ", embed=embed)
    ctx.voice_client.play(audio_source)

    while ctx.voice_client.is_playing():
        await asyncio.sleep(600)
    else:
        await leave(ctx)


@bot.hybrid_command(name='bs')
async def stop_music(ctx):
    if not ctx.message.author.voice or not ctx.voice_client:
        await ctx.send('You are not connected to a voice channel')
        return

    if ctx.voice_client.is_playing():
        await ctx.send('Stopped')
        ctx.voice_client.stop()
    else:
        ctx.send('Not playing')


if __name__ == "__main__":
    print('Bot starting...')
    bot.run(DISCORD_TOKEN)
