from pathlib import Path
import time

from fastapi import FastAPI, UploadFile, File, Response
from fastapi import status as fast_status
import aiofiles

from modules.data_models import PlaylistItem, StatusItem, GenericItem, ListItem
from settings.server_settings import TEMP_DIR, MEDIA_DIR
from modules.mpvplayer import Player
from modules.b64_helper import decode_uri

# how to stream data from python to mpv
#     @player.python_stream('stream')
#     def stream_helper():
#         with open(testfile, 'rb') as tfile:
#             while True:
#                 yield tfile.read(1024*1024)

#     player.loadfile('python://stream', 'replace')
#     player.wait_until_playing()
#     return {'message': 'playing test file now'}


player_instance = Player()
player = player_instance.get_player()
app = FastAPI()


@app.post("/play", status_code=fast_status.HTTP_200_OK, response_model=GenericItem)
def play(uri: str, local: bool, replace: bool, response: Response):  
    try:
        decoded_uri = decode_uri(uri)
        if player.filename is None or replace:
            if local and Path(MEDIA_DIR, decoded_uri).is_file():
                player.loadfile(str(Path(MEDIA_DIR, decoded_uri)), 'replace')
                player.command('set', 'pause', 'no')
                player.wait_until_playing()
                return {'message': 'playing local'}
            elif not local and decoded_uri[:4] == 'http':
                player.loadfile(decoded_uri, 'replace')
                player.command('set', 'pause', 'no')
                player.wait_until_playing()
                return {'message': 'playing remote'}
            else:
                response.status_code = fast_status.HTTP_404_NOT_FOUND
                return {'message': 'local file not available'}
        else:
            response.status_code = fast_status.HTTP_403_FORBIDDEN
            return {'message': 'replace is set to false, cannot override current video'}
    except:
        response.status_code = fast_status.HTTP_422_UNPROCESSABLE_ENTITY
        return {'message': 'internal error on decoding b64 uri'}


@app.post("/stop", status_code=fast_status.HTTP_200_OK)
def stop(response: Response):
    if player.filename is not None:
        player.stop()
        return {'message': 'playback stopped successfully'}
    else:
        response.status_code = fast_status.HTTP_406_NOT_ACCEPTABLE
        return {'message': 'playback could not be stopped - nothing was playing'}


@app.post("/mute", status_code=fast_status.HTTP_200_OK, response_model=GenericItem)
def mute():
    if player.mute:
        player.command('set', 'mute', 'no')
        return {'message': 'player unmuted'}
    else:
        player.command('set', 'mute', 'yes')
        return {'message': 'player muted'}


@app.post("/fullscreen", status_code=fast_status.HTTP_200_OK, response_model=GenericItem)
def fullscreen():
    if player.fullscreen:
        player.command('set', 'fullscreen', 'no')
        return {'message': 'toggled fullscreen off'}
    else:
        player.command('set', 'fullscreen', 'yes')
        return {'message': 'toggled fullscreen on'}


@app.post("/repeat", status_code=fast_status.HTTP_200_OK, response_model=GenericItem)
def repeat():
    if player.loop_playlist:
        player.command('set', 'loop-playlist', 'no')
        return {'message': 'toggled repeat off'}
    else:
        player.command('set', 'loop-playlist', 'inf')
        return {'message': 'toggled repeat on'}


@app.get("/status", status_code=fast_status.HTTP_200_OK, response_model=StatusItem)
def status():
    return player_instance.get_player_status()


@app.post("/seek", status_code=fast_status.HTTP_202_ACCEPTED, response_model=GenericItem)
def seek(percent_pos: float, response: Response):
    if player.percent_pos is not None:
        player.seek(percent_pos, 'absolute-percent')
        return {'message': f'seeked to {percent_pos}%'}
    else:
        response.status_code = fast_status.HTTP_406_NOT_ACCEPTABLE
        return {'message': 'unable to seek; nothing is playing'}


@app.post('/pause', status_code=fast_status.HTTP_200_OK, response_model=GenericItem)
def pause(response: Response):
    if not player.pause and player.filename is not None:
        player.command('set', 'pause', 'yes')
        player.wait_until_paused()
        return {'message': 'player is paused'}
    elif player.pause and player.filename is not None:
        player.command('set', 'pause', 'no')
        return {'message': 'player is unpaused'}
    else:
        response.status_code = fast_status.HTTP_406_NOT_ACCEPTABLE
        return {'message': 'you cannnot pause if you have no video'}


@app.post('/stream/', status_code=fast_status.HTTP_202_ACCEPTED, response_model=GenericItem)
async def stream(file: UploadFile):
    tempfile = Path(
        TEMP_DIR, f'{str(time.time())}{Path(file.filename).suffix}')
    async with aiofiles.open(tempfile, 'wb') as out_file:
        while content := await file.read(1024 * 1024):
            await out_file.write(content)
    return {'message': 'file uploaded successfully, playing', 'file': str(tempfile.resolve())}


@app.post('/upload/', status_code=fast_status.HTTP_201_CREATED, response_model=GenericItem)
async def upload(file: UploadFile, response: Response):
    newfile = Path(MEDIA_DIR, file.filename)
    if not newfile.exists():
        async with aiofiles.open(newfile, 'wb') as out_file:
            while content := await file.read(1024 * 1024):
                await out_file.write(content)
        return {'message': f'new file {file.filename} uploaded successfully'}
    else:
        response.status_code = fast_status.HTTP_409_CONFLICT
        return {'message': f'file {file.filename} already exists'}


@app.get('/list', status_code=fast_status.HTTP_200_OK, response_model=ListItem)
def list_files(response: Response):
    print(MEDIA_DIR)
    file_list = [str(x.stem + x.suffix)
                 for x in MEDIA_DIR.glob('*') if x.is_file()]
    if len(file_list) > 0:
        return {'message': 'successfully listed files', 'files': file_list}
    else:
        response.status_code = fast_status.HTTP_204_NO_CONTENT
        return {'message': 'no remote files to list', 'files': []}


@app.post('/volume', response_model=GenericItem, status_code=fast_status.HTTP_202_ACCEPTED)
def volume(volume: int, response: Response):
    if 0 <= volume <= 100:
        player.command('set', 'volume', volume)
        return {'message': f'volume set to {volume}'}
    else:
        return {'message': f'cannot set volume to below zero or above 100'}


@app.post('/playlist/', status_code=fast_status.HTTP_200_OK, response_model=GenericItem)
def playlist(data: PlaylistItem, response: Response):
    if data.new and len(data.plist) > 0 and data.index < len(data.plist):
        if player.playlist_pos > -1:  # type: ignore
            player.stop()
        parsed_list = [x if x[:4] == 'http' else str(
            Path(MEDIA_DIR, x).resolve()) for x in data.plist]
        player.playlist_clear()
        for item in parsed_list:
            player.playlist_append(item)
        player.playlist_play_index(data.index)
        player.wait_until_playing()
        print(player.playlist_pos)
        return {'message': f'playing playlist starting at index {data.index}'}
    else:
        response.status_code = fast_status.HTTP_406_NOT_ACCEPTABLE
        return {'message': 'cannot play a zero length playlist, or item outside of range'}


@app.post('/next', status_code=fast_status.HTTP_202_ACCEPTED, response_model=GenericItem)
def next(response: Response):
    if player.playlist_pos != -1 and player.playlist_pos < len(player.playlist_filenames):  # type: ignore
        player.playlist_next()
        return {'message': 'playing next playlist item'}
    else:
        response.status_code = fast_status.HTTP_405_METHOD_NOT_ALLOWED
        return {'message': 'there is no next item to play'}


@app.post('/previous', status_code=fast_status.HTTP_202_ACCEPTED, response_model=GenericItem)
def previous(response: Response):
    if player.playlist_pos != -1 and player.playlist_pos > 0:  # type: ignore
        player.playlist_prev()
        return {'message': 'playing previous playlist item'}
    else:
        response.status_code = fast_status.HTTP_405_METHOD_NOT_ALLOWED
        return {'message': 'there is no previous left to play'}


if __name__ == '__main__':
    pass
