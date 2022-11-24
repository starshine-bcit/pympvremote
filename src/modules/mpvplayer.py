
from src.modules.mpv import MPV

from src.settings.server_settings import FULLSCREEN, ON_TOP

class Player():
    def __init__(self) -> None:
        self.fullscreen = FULLSCREEN
        self.on_top = ON_TOP
        self.player = MPV(
            ytdl=True,
            fullscreen=FULLSCREEN,
            ontop=ON_TOP,
            osc=False
        )

    def get_player(self) -> MPV:
        return self.player

    def get_player_status(self):
        return {
            'time-pos': self.player.time_pos,
            'percent-pos': self.player.percent_pos,
            'time-remaining': self.player.time_remaining,
            'duration': self.player.duration,
            'pause': self.player.pause,
            'filename': self.player.filename,
            'playlist-names': self.player.playlist_filenames,
            'mute': self.player.mute,
            'fullscreen': self.player.fullscreen,
            'repeat': self.player.loop_playlist
        }

if __name__ == '__main__':
    pass
