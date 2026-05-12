import discord
from discord.ext import commands
import wavelink
from config import *

intents = discord.Intents.all()

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

    try:
        node = wavelink.Node(
            uri=f"https://{LAVALINK_HOST}:{LAVALINK_PORT}",
            password=LAVALINK_PASSWORD
        )

        await wavelink.Pool.connect(nodes=[node], client=bot)

        print("Lavalink Connected")

    except Exception as e:
        print(e)


@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong: {round(bot.latency * 1000)}ms")


@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        return await ctx.send("Join VC first")

    vc = ctx.author.voice.channel

    player = await vc.connect(cls=wavelink.Player)

    await ctx.send(f"Joined {vc.name}")


@bot.command()
async def leave(ctx):
    vc: wavelink.Player = ctx.voice_client

    if vc:
        await vc.disconnect()
        await ctx.send("Disconnected")


@bot.command()
async def play(ctx, *, search: str):
    if not ctx.author.voice:
        return await ctx.send("Join VC first")

    vc = ctx.voice_client

    if not vc:
        vc = await ctx.author.voice.channel.connect(cls=wavelink.Player)

    tracks = await wavelink.Playable.search(search)

    if not tracks:
        return await ctx.send("Song not found")

    track = tracks[0]

    await vc.play(track)

    embed = discord.Embed(
        title="Now Playing",
        description=f"[{track.title}]({track.uri})",
        color=0x2f3136
    )

    embed.add_field(name="Author", value=track.author)
    embed.add_field(name="Duration", value=str(track.length // 1000) + " sec")

    await ctx.send(embed=embed)


@bot.command()
async def pause(ctx):
    vc: wavelink.Player = ctx.voice_client

    if vc:
        await vc.pause(True)
        await ctx.send("Paused")


@bot.command()
async def resume(ctx):
    vc: wavelink.Player = ctx.voice_client

    if vc:
        await vc.pause(False)
        await ctx.send("Resumed")


@bot.command()
async def stop(ctx):
    vc: wavelink.Player = ctx.voice_client

    if vc:
        await vc.stop()
        await ctx.send("Stopped")


@bot.command()
async def skip(ctx):
    vc: wavelink.Player = ctx.voice_client

    if vc:
        await vc.skip(force=True)
        await ctx.send("Skipped")


@bot.command()
async def volume(ctx, vol: int):
    vc: wavelink.Player = ctx.voice_client

    if vc:
        await vc.set_volume(vol)
        await ctx.send(f"Volume set to {vol}")


@bot.command()
async def nowplaying(ctx):
    vc: wavelink.Player = ctx.voice_client

    if not vc or not vc.current:
        return await ctx.send("Nothing playing")

    track = vc.current

    embed = discord.Embed(
        title="Now Playing",
        description=f"[{track.title}]({track.uri})",
        color=0x2f3136
    )

    embed.add_field(name="Author", value=track.author)
    embed.add_field(name="Duration", value=str(track.length // 1000) + " sec")

    await ctx.send(embed=embed)


# Voice Moderation Commands

@bot.command()
@commands.has_permissions(mute_members=True)
async def mute(ctx, member: discord.Member):
    await member.edit(mute=True)
    await ctx.send(f"Muted {member.mention}")


@bot.command()
@commands.has_permissions(mute_members=True)
async def unmute(ctx, member: discord.Member):
    await member.edit(mute=False)
    await ctx.send(f"Unmuted {member.mention}")


@bot.command()
@commands.has_permissions(deafen_members=True)
async def deafen(ctx, member: discord.Member):
    await member.edit(deafen=True)
    await ctx.send(f"Deafened {member.mention}")


@bot.command()
@commands.has_permissions(deafen_members=True)
async def undeafen(ctx, member: discord.Member):
    await member.edit(deafen=False)
    await ctx.send(f"Undeafened {member.mention}")


@bot.command()
async def help(ctx):
    embed = discord.Embed(
        title="Music Commands",
        color=0x2f3136
    )

    embed.description = """
$play <song>
$pause
$resume
$skip
$stop
$volume <1-100>
$nowplaying
$join
$leave
$mute @user
$unmute @user
$deafen @user
$undeafen @user
"""

    await ctx.send(embed=embed)


bot.run(TOKEN)
