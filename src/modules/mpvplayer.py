from pathlib import Path

from .mpv import MPV

from src.settings.settings import FULLSCREEN, ON_TOP

def get_player_status(player: MPV):
    return {
        'time-pos': player.time_pos,
        'percent-pos': player.percent_pos,
        'time-remaining': player.time_remaining,
        'duration': player.duration,
        'pause': player.pause,
        'filename': player.filename,
        'playlist-names': player.playlist_filenames
    }


def create_player():
    player = MPV(
        ytdl=True,
        fullscreen=FULLSCREEN,
        ontop=ON_TOP,
        osc=False
    )
    return player
