
from .mpv import MPV

from settings.server_settings import FULLSCREEN, ON_TOP


class Player():
    def __init__(self) -> None:
        """Initializes an instance of mpv with options from the
            settings file.
        """        
        self.fullscreen = FULLSCREEN
        self.on_top = ON_TOP
        self.player = MPV(
            ytdl=True,
            fullscreen=FULLSCREEN,
            ontop=ON_TOP,
            osc=False
        )

    def get_player(self) -> MPV:
        """Exposes the initialized mpv instance

        Returns:
            MPV: the current instance of mpv
        """        
        return self.player

    def get_player_status(self) -> dict:
        """Pulls relevant properties from the play instance

        Returns:
            dict: various attributes of the player instance
        """        
        return {
            'time_pos': self.player.time_pos,
            'percent_pos': self.player.percent_pos,
            'time_remaining': self.player.time_remaining,
            'duration': self.player.duration,
            'pause': self.player.pause,
            'filename': self.player.filename,
            'playlist_names': self.player.playlist_filenames,
            'mute': self.player.mute,
            'fullscreen': self.player.fullscreen,
            'repeat': self.player.loop_playlist,
            'volume': self.player.volume,
            'playlist_pos': self.player.playlist_pos
        }


if __name__ == '__main__':
    pass
