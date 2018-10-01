"""
Please understand Music bots are complex, and that even this basic example can be daunting to a beginner.
For this reason it's highly advised you familiarize yourself with discord.py, python and asyncio, BEFORE
you attempt to write a music bot.
This example makes use of: Python 3.6
For a more basic voice example please read:
    https://github.com/Rapptz/discord.py/blob/rewrite/examples/basic_voice.py
This is a very basic playlist example, which allows per guild playback of unique queues.
The commands implement very basic logic for basic usage. But allow for expansion. It would be advisable to implement
your own permissions and usage logic for commands.
e.g You might like to implement a vote before skipping the song or only allow admins to stop the player.
Music bots require lots of work, and tuning. Goodluck.
If you find any bugs feel free to ping me on discord. @Eviee#0666
"""
# also this is not mine lul
# TODO: 
# Make a check to see if your in the voice channel
# Make votes
# Make more checks
# 
# 
# 
# 
# 

import discord
from discord.ext import commands

import asyncio
import itertools
import sys
import traceback
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL


ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpegopts = {
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl = YoutubeDL(ytdlopts)


class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""


class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, kit, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        await kit.send(f'```ini\n[Added {data["title"]} to the Queue.]\n```', delete_after=15)

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': kit.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=kit.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']

        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)

        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)


class MusicPlayer:

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume')

    def __init__(self, kit):
        self.bot = kit.bot
        self._guild = kit.guild
        self._channel = kit.channel
        self._cog = kit.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = .5
        self.current = None

        kit.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                async with timeout(300):  # 5 minutes...
                    source = await self.queue.get()
            except asyncio.TimeoutError:
                return self.destroy(self._guild)

            if not isinstance(source, YTDLSource):

                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                    await self._channel.send(f'There was an error processing your song.\n'
                                             f'```css\n[{e}]\n```')
                    continue

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
            self.np = await self._channel.send(f'**Now Playing:** `{source.title}` requested by '
                                               f'`{source.requester}`')
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music:
    """Music related commands."""

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, kit):
        """A local check which applies to all commands in this cog."""
        if not kit.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, kit, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await kit.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await kit.send('Error connecting to Voice Channel. '
                           'Please make sure you are in a valid channel or provide me with one')

        print('Ignoring exception in command {}:'.format(kit.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, kit):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[kit.guild.id]
        except KeyError:
            player = MusicPlayer(kit)
            self.players[kit.guild.id] = player

        return player

    @commands.command(name='connect', aliases=['join'])
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def connect_(self, kit, *, channel: discord.VoiceChannel=None):
        """Connect to voice.
        Parameters
        ------------
        channel: discord.VoiceChannel [Optional]
            The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
            will be made.
        This command also handles moving the bot to different channels.
        """
        if not channel:
            try:
                channel = kit.author.voice.channel
            except AttributeError:
                raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

        vc = kit.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')

        await kit.send(f'Connected to: **{channel}**', delete_after=20)

    @commands.command(name='play', aliases=['sing'])
    @commands.cooldown(rate=1, per=3.8, type=commands.BucketType.user)
    async def play_(self, kit, *, search: str):
        """Request a song and add it to the queue.
        This command attempts to join a valid voice channel if the bot is not already in one.
        Uses YTDL to automatically search and retrieve a song.
        Parameters
        ------------
        search: str [Required]
            The song to search and retrieve using YTDL. This could be a simple search, an ID or URL.
        """
        await kit.trigger_typing()

        vc = kit.voice_client

        if not vc:
            await kit.invoke(self.connect_)

        player = self.get_player(kit)

        # If download is False, source will be a dict which will be used later to regather the stream.
        # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
        source = await YTDLSource.create_source(kit, search, loop=self.bot.loop, download=False)

        await player.queue.put(source)

    @commands.command(name='pause')
    @commands.cooldown(rate=1, per=3.8, type=commands.BucketType.user)
    async def pause_(self, kit):
        """Pause the currently playing song."""
        vc = kit.voice_client

        if not vc or not vc.is_playing():
            return await kit.send('I am not currently playing anything!', delete_after=20)
        elif vc.is_paused():
            return

        vc.pause()
        await kit.send(f'**`{kit.author}`**: Paused the song!')

    @commands.command(name='resume')
    @commands.cooldown(rate=1, per=3.8, type=commands.BucketType.user)
    async def resume_(self, kit):
        """Resume the currently paused song."""
        vc = kit.voice_client

        if not vc or not vc.is_connected():
            return await kit.send('I am not currently playing anything!', delete_after=20)
        elif not vc.is_paused():
            return

        vc.resume()
        await kit.send(f'**`{kit.author}`**: Resumed the song!')

    @commands.command(name='skip')
    @commands.cooldown(rate=1, per=3.8, type=commands.BucketType.user)
    async def skip_(self, kit):
        """Skip the song."""
        vc = kit.voice_client

        if not vc or not vc.is_connected():
            return await kit.send('I am not currently playing anything!', delete_after=20)

        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return

        vc.stop()
        await kit.send(f'**`{kit.author}`**: Skipped the song!')

    @commands.command(name='queue', aliases=['q', 'playlist'])
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def queue_info(self, kit):
        """Retrieve a basic queue of upcoming songs."""
        vc = kit.voice_client

        if not vc or not vc.is_connected():
            return await kit.send('I am not currently connected to voice!', delete_after=20)

        player = self.get_player(kit)
        if player.queue.empty():
            return await kit.send('There are currently no more queued songs.')

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = '\n'.join(f'**`{_["title"]}`**' for _ in upcoming)
        embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}', description=fmt)

        await kit.send(embed=embed)

    @commands.command(name='now_playing', aliases=['np', 'current', 'currentsong', 'playing'])
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def now_playing_(self, kit):
        """Display information about the currently playing song."""
        vc = kit.voice_client

        if not vc or not vc.is_connected():
            return await kit.send('I am not currently connected to voice!', delete_after=20)

        player = self.get_player(kit)
        if not player.current:
            return await kit.send('I am not currently playing anything!')

        try:
            # Remove our previous now_playing message.
            await player.np.delete()
        except discord.HTTPException:
            pass

        player.np = await kit.send(f'**Now Playing:** `{vc.source.title}` '
                                   f'requested by `{vc.source.requester}`')

    @commands.command(name='volume', aliases=['vol'])
    @commands.cooldown(rate=1, per=3.8, type=commands.BucketType.user)
    async def change_volume(self, kit, *, vol: float):
        """Change the player volume.
        Parameters
        ------------
        volume: float or int [Required]
            The volume to set the player to in percentage. This must be between 1 and 100.
        """
        vc = kit.voice_client

        if not vc or not vc.is_connected():
            return await kit.send('I am not currently connected to voice!', delete_after=20)

        if not 0 < vol < 101:
            return await kit.send('Please enter a value between 1 and 100.')

        player = self.get_player(kit)

        if vc.source:
            vc.source.volume = vol / 100

        player.volume = vol / 100
        await kit.send(f'**`{kit.author}`**: Set the volume to **{vol}%**')

    @commands.command(name='stop')
    @commands.cooldown(rate=1, per=1.5, type=commands.BucketType.user)
    async def stop_(self, kit):
        """Stop the currently playing song and destroy the player.
        !Warning!
            This will destroy the player assigned to your guild, also deleting any queued songs and settings.
        """
        vc = kit.voice_client

        if not vc or not vc.is_connected():
            return await kit.send('I am not currently playing anything!', delete_after=20)

        await self.cleanup(kit.guild)
def setup(bot):
    bot.add_cog(Music(bot))
