import asyncio
import discord
import logging
import math
import music_config
import youtube_dl

from discord.ext import commands
from urllib import request
from video import Video


async def audio_playing(linu):
    """Checks that audio is currently playing before continuing."""
    client = linu.guild.voice_client
    if client and client.channel and client.source:
        return True
    else:
        raise commands.CommandError("Not currently playing any audio.")


async def in_voice_channel(linu):
    """Checks that the command sender is in the same voice channel as the bot."""
    voice = linu.author.voice
    bot_voice = linu.guild.voice_client
    if voice and bot_voice and voice.channel and bot_voice.channel and voice.channel == bot_voice.channel:
        return True
    else:
        raise commands.CommandError(
            "You need to be in the channel to do that.")


async def is_audio_requester(linu):
    music = linu.bot.get_cog("Music")
    state = music.get_state(linu.guild)
    permissions = linu.channel.permissions_for(linu.author)
    if permissions.administrator or state.is_requester(linu.author):
        return True
    else:
        raise commands.CommandError(
            "You need to be the song requester to do that.")


class Music:
    """Bot commands to help play music."""

    def __init__(self, bot):
        self.bot = bot
        self.config = music_config
        self.states = {}

    def get_state(self, guild):
        """Gets the state for `guild`, creating it if it does not exist."""
        if guild.id in self.states:
            return self.states[guild.id]
        else:
            self.states[guild.id] = GuildState()
            return self.states[guild.id]

    @commands.command(aliases=["stop"])
    @commands.guild_only()
    @commands.has_permissions(administrator=True)
    async def leave(self, linu):
        """Leaves the voice channel, if currently in one."""
        client = linu.guild.voice_client
        state = self.get_state(linu.guild)
        if client and client.channel:
            await client.disconnect()
            state.playlist = []
            state.now_playing = None
        else:
            raise commands.CommandError("Not in a voice channel.")

    @commands.command(aliases=["resume", "p"])
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice_channel)
    @commands.check(is_audio_requester)
    async def pause(self, linu):
        """Pauses any currently playing audio."""
        client = linu.guild.voice_client
        self._pause_audio(client)

    def _pause_audio(self, client):
        if client.is_paused():
            client.resume()
        else:
            client.pause()

    @commands.command(aliases=["vol", "v"])
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice_channel)
    @commands.check(is_audio_requester)
    async def volume(self, linu, volume: int):
        """Change the volume of currently playing audio (values 0-250)."""
        state = self.get_state(linu.guild)

        # make sure volume is nonnegative
        if volume < 0:
            volume = 0

        max_vol = int(self.config.max_volume)
        if max_vol > -1:  # check if max volume is set
            # clamp volume to [0, max_vol]
            if volume > max_vol:
                volume = max_vol

        client = linu.guild.voice_client

        state.volume = float(volume) / 100.0
        client.source.volume = state.volume  # update the AudioSource's volume to match

    @commands.command()
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.check(in_voice_channel)
    async def skip(self, linu):
        """Skips the currently playing song, or votes to skip it."""
        state = self.get_state(linu.guild)
        client = linu.guild.voice_client
        if linu.channel.permissions_for(
                linu.author).administrator or state.is_requester(linu.author):
            # immediately skip if requester or admin
            client.stop()
        elif self.config.vote_skip:
            # vote to skip song
            channel = client.channel
            self._vote_skip(channel, linu.author)
            # announce vote
            users_in_channel = len([
                member for member in channel.members if not member.bot
            ])  # don't count bots
            required_votes = math.ceil(
                self.config.vote_skip_ratio * users_in_channel)
            await linu.send(
                f"{linu.author.mention} voted to skip ({len(state.skip_votes)}/{required_votes} votes)"
            )
        else:
            raise CommandError("Sorry, vote skipping is disabled.")

    def _vote_skip(self, channel, member):
        """Register a vote for `member` to skip the song playing."""
        logging.info(f"{member.name} votes to skip")
        state = self.get_state(channel.guild)
        state.skip_votes.add(member)
        users_in_channel = len([
            member for member in channel.members if not member.bot
        ])  # don't count bots
        if (float(len(state.skip_votes)) /
                users_in_channel) >= int(self.config.vote_skip_ratio):
            # enough members have voted to skip, so skip the song
            logging.info(f"Enough votes, skipping...")
            channel.guild.voice_client.stop()

    def _play_song(self, client, state, song):
        state.now_playing = song
        state.skip_votes = set()  # clear skip votes
        source = discord.PCMVolumeTransformer(
            discord.FFmpegPCMAudio(song.stream_url), volume=state.volume)

        def after_playing(err):
            if len(state.playlist) > 0:
                next_song = state.playlist.pop(0)
                self._play_song(client, state, next_song)
            else:
                asyncio.run_coroutine_threadsafe(client.disconnect(),
                                                 self.bot.loop)

        client.play(source, after=after_playing)

    @commands.command(aliases=["np"])
    @commands.guild_only()
    @commands.check(audio_playing)
    async def nowplaying(self, linu):
        """Displays information about the current song."""
        state = self.get_state(linu.guild)
        message = await linu.send("", embed=state.now_playing.get_embed())
        await self._add_reaction_controls(message)

    @commands.command(aliases=["q", "playlist"])
    @commands.guild_only()
    @commands.check(audio_playing)
    async def queue(self, linu):
        """Display the current play queue."""
        state = self.get_state(linu.guild)
        if len(state.playlist) > 0:
            message = [f"{len(state.playlist)} songs in queue:"]
            message += [
                f"  {index+1}. **{song.title}** (requested by **{song.requested_by.name}**)"
                for (index, song) in enumerate(state.playlist)
            ]  # add individual songs
            await linu.send("\n".join(message))
        else:
            await linu.send("The play queue is empty.")

    @commands.command(aliases=["cq"])
    @commands.guild_only()
    @commands.check(audio_playing)
    @commands.has_permissions(administrator=True)
    async def clearqueue(self, linu):
        """Clears the play queue without leaving the channel."""
        state = self.get_state(linu.guild)
        state.playlist = []

    @commands.command(brief="Plays audio from <url>.")
    @commands.guild_only()
    async def play(self, linu, *, url):
        """Plays audio hosted at <url> (or performs a search for <url> and plays the first result)."""

        client = linu.guild.voice_client
        state = self.get_state(linu.guild)  # get the guild's state

        if client and client.channel:
            try:
                video = Video(url, linu.author)
            except youtube_dl.DownloadError as e:
                await linu.send(
                    "There was an error downloading your video, sorry.")
                return
            state.playlist.append(video)
            message = await linu.send(
                "Added to queue.", embed=video.get_embed())
            await self._add_reaction_controls(message)
        else:
            if linu.author.voice != None and linu.author.voice.channel != None:
                channel = linu.author.voice.channel
                try:
                    video = Video(url, linu.author)
                except youtube_dl.DownloadError as e:
                    await linu.send(
                        "There was an error downloading your video, sorry.")
                    return
                client = await channel.connect()
                self._play_song(client, state, video)
                message = await linu.send("", embed=video.get_embed())
                await self._add_reaction_controls(message)
                logging.info(f"Now playing '{video.title}'")
            else:
                raise commands.CommandError(
                    "You need to be in a voice channel to do that. Join a voice channel")

    async def on_reaction_add(self, reaction, user):
        """Respods to reactions added to the bot's messages, allowing reactions to control playback."""
        message = reaction.message
        if user != self.bot.user and message.author == self.bot.user:
            if message.guild and message.guild.voice_client:
                user_in_channel = user.voice and user.voice.channel and user.voice.channel == message.guild.voice_client.channel
                permissions = message.channel.permissions_for(user)
                guild = message.guild
                state = self.get_state(guild)
                if permissions.administrator or (user_in_channel and state.is_requester(user)):
                    client = message.guild.voice_client
                    if reaction.emoji == "⏯":
                        # pause audio
                        self._pause_audio(client)
                    elif reaction.emoji == "⏭":
                        # skip audio
                        client.stop()
                    elif reaction.emoji == "⏮":
                        state.playlist.insert(
                            0, state.now_playing
                        )  # insert current song at beginning of playlist
                        client.stop()  # skip ahead
                elif reaction.emoji == "⏭" and self.config.vote_skip and user_in_channel and message.guild.voice_client and message.guild.voice_client.channel:
                    # ensure that skip was pressed, that vote skipping is enabled, the user is in the channel, and that the bot is in a voice channel
                    voice_channel = message.guild.voice_client.channel
                    self._vote_skip(voice_channel, user)
                    # announce vote
                    channel = message.channel
                    users_in_channel = len([
                        member for member in voice_channel.members
                        if not member.bot
                    ])  # don't count bots
                    required_votes = math.ceil(
                        self.config.vote_skip_ratio * users_in_channel)
                    await channel.send(
                        f"{user.mention} voted to skip ({len(state.skip_votes)}/{required_votes} votes)"
                    )

    async def _add_reaction_controls(self, message):
        """Adds a 'control-panel' of reactions to a message that can be used to control the bot."""
        CONTROLS = ["⏮", "⏯", "⏭"]
        for control in CONTROLS:
            await message.add_reaction(control)


class GuildState:
    """Helper class managing per-guild state."""

    def __init__(self):
        self.volume = 1.0
        self.playlist = []
        self.skip_votes = set()
        self.now_playing = None

    def is_requester(self, user):
        return self.now_playing.requested_by == user


def setup(bot):
    bot.add_cog(Music(bot))
