from .mpv import MPV


def get_player_status(player: MPV):
    return {
        'time-pos': player.time_pos,
        'percent-pos': player.percent_pos,
        'time-remaining': player.time_remaining,
        'duration': player.duration
    }


def create_player():
    player = MPV(ytdl=True)
    return player
