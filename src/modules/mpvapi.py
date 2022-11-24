import base64
from pathlib import Path
import time

from fastapi import FastAPI, UploadFile, File, Response
from fastapi import status as fast_status
import aiofiles

from src.settings.server_settings import TEMP_DIR, MEDIA_DIR
from src.modules.mpvplayer import Player
from src.modules.b64_helper import encode_uri, decode_uri


player_instance = Player()
player = player_instance.get_player()
app = FastAPI()

@app.post("/play", status_code=fast_status.HTTP_200_OK)
def play(uri: str, local: bool, replace: bool, response: Response):
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


@app.post("/stop", status_code=fast_status.HTTP_200_OK)
def stop(response: Response):
    if player.filename is not None:
        player.stop()
        return {'message': 'playback stopped successfully'}
    else:
        response.status_code = fast_status.HTTP_406_NOT_ACCEPTABLE
        return {'message': 'playback could not be stopped - nothing was playing'}

@app.post("/mute")
def mute():
    if player.mute:
        player.command('set', 'mute', 'no')
        return {'message': 'player unmuted'}
    else:
        player.command('set', 'mute', 'yes')
        return {'message': 'player muted'}

@app.post("/fullscreen")
def fullscreen():
    if player.fullscreen:
        player.command('set', 'fullscreen', 'no')
        return {'message': 'toggled fullscreen off'}
    else:
        player.command('set', 'fullscreen', 'yes')
        return {'message': 'toggled fullscreen on'}

@app.post("/repeat")
def repeat():
    if player.loop_playlist:
        player.command('set', 'loop-playlist', 'no')
        return {'message': 'toggled repeat off'}
    else:
        player.command('set', 'loop-playlist', 'inf')
        return {'message': 'toggled repeat on'}


# @app.post("/playtest")
# async def playtest():
#     testfile = Path(
#         'x')

#     @player.python_stream('stream')
#     def stream_helper():
#         with open(testfile, 'rb') as tfile:
#             while True:
#                 yield tfile.read(1024*1024)

#     player.loadfile('python://stream', 'replace')
#     player.wait_until_playing()
#     return {'message': 'playing test file now'}


@app.get("/status")
def status():
    return player_instance.get_player_status()


@app.post("/seek")
def seek(percent_pos: float):
    player.seek(percent_pos, 'absolute-percent')
    return {'message': f'seeked to {percent_pos}%'}


@app.post('/pause')
def pause():
    if not player.pause:
        player.command('set', 'pause', 'yes')
        player.wait_until_paused()
        return {'message': 'player is paused'}
    else:
        player.command('set', 'pause', 'no')
        return {'message': 'player is unpaused'}


@app.post('/stream/', status_code=fast_status.HTTP_202_ACCEPTED)
async def stream(file: UploadFile, response: Response):
    tempfile = Path(
        TEMP_DIR, f'{str(time.time())}{Path(file.filename).suffix}')
    async with aiofiles.open(tempfile, 'wb') as out_file:
        while content := await file.read(1024):
            await out_file.write(content)
    return {'message': 'file uploaded successfully', 'file': str(tempfile.resolve())}

@app.post('/upload/', status_code=fast_status.HTTP_201_CREATED)
async def upload(file: UploadFile, response: Response):
    newfile = Path(MEDIA_DIR, file.filename)
    if not newfile.exists():
        async with aiofiles.open(newfile, 'wb') as out_file:
            while content := await file.read(1024):
                await out_file.write(content)
        return {'message': f'new file {file.filename} uploaded successfully'}
    else:
        response.status_code = fast_status.HTTP_406_NOT_ACCEPTABLE
        return {'message': f'file {file.filename} already exists'}

@app.get('/list', status_code=fast_status.HTTP_200_OK)
def list_files(response: Response):
    file_list = [str(x.stem + x.suffix) for x in MEDIA_DIR.glob('*') if x.is_file()]
    if len(file_list) > 0:
        return {'message': 'successfully listed files', 'files': file_list}
    else:
        response.status_code = fast_status.HTTP_204_NO_CONTENT
        return {'message': 'no remote files to list', 'files': []}


if __name__ == '__main__':
    pass
