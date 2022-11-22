import base64
from pathlib import Path
import time

from fastapi import FastAPI, UploadFile, File, Response
from fastapi import status as fast_status
import aiofiles

from src.settings.settings import TEMP_DIR
from .mpvplayer import create_player, get_player_status

player = create_player()
app = FastAPI()


def decode_uri(uri: str) -> str:
    return str(base64.urlsafe_b64decode(uri), "utf-8")

@app.post("/play", status_code=fast_status.HTTP_200_OK)
def play(uri: str, replace: bool, response: Response):
    decoded_uri = decode_uri(uri)
    if player.filename is None or replace:
        if Path(decoded_uri).is_file() or decoded_uri[:4] == 'http':
            player.loadfile(decoded_uri, 'replace')
            player.wait_until_playing()
            return {'message': 'playing'}
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
        return 0
    else:
        response.status_code = fast_status.HTTP_400_BAD_REQUEST
        return 0


@app.post("/playtest")
async def playtest():
    testfile = Path(
        'C:\\Courses\\2515\\testvids\\Commands Prompt Commands Everybody Should Know [iXprT0ltnVg].webm')

    @player.python_stream('stream')
    def stream_helper():
        with open(testfile, 'rb') as tfile:
            while True:
                yield tfile.read(1024*1024)

    player.loadfile('python://stream', 'replace')
    player.wait_until_playing()
    return 0


@app.get("/status")
def status():
    return get_player_status(player)


@app.post("/seek")
def seek(percent_pos: float):
    player.seek(percent_pos, 'absolute-percent')
    return get_player_status(player)


@app.post('/pause')
def pause():
    if not player.pause:
        player.command('set', 'pause', 'yes')
        player.wait_until_paused()
        return 0
    else:
        player.command('set', 'pause', 'no')
        return 0


@app.post('/stream/', status_code=fast_status.HTTP_200_OK)
async def stream(file: UploadFile, response: Response):
    tempfile = Path(
        TEMP_DIR, f'{str(time.time())}{Path(file.filename).suffix}')
    async with aiofiles.open(tempfile, 'wb') as out_file:
        while content := await file.read(1024):
            await out_file.write(content)
    return str(base64.urlsafe_b64encode(bytes(str(tempfile), encoding='utf-8')), 'utf-8')

if __name__ == '__main__':
    pass
