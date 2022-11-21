import base64
from pathlib import Path
import time

from fastapi import FastAPI, UploadFile, File
import aiofiles

from src.settings.settings import TEMP_DIR
from .mpvplayer import create_player, get_player_status


player = create_player()
app = FastAPI()


@app.post("/play")
def play(uri: str = 'aHR0cHM6Ly9mZXN0aXZ1cy5kZXYva3ViZXJuZXRlcy8='):
    decoded_uri = str(base64.urlsafe_b64decode(uri), "utf-8")
    # aHR0cHM6Ly93d3cueW91dHViZS5jb20vd2F0Y2g_dj1adHFCUTY4Y2ZKYw==
    player.play(decoded_uri)
    player.wait_until_playing()
    return 0


@app.post("/stop")
def stop():
    player.stop()
    return 0


@app.post("/playtest")
async def playtest():
    testfile = Path(
        'C:\\Courses\\2515\\testvids\\Commands Prompt Commands Everybody Should Know [iXprT0ltnVg].webm')
    player.play(str(testfile))
    player.wait_until_playing()
    return str(base64.urlsafe_b64encode(bytes(testfile)), 'utf-8')


@app.get("/status")
def status():
    return get_player_status(player)


@app.post("/seek")
def seek(percent_pos: float):
    player.seek(percent_pos, 'absolute-percent')
    return get_player_status(player)


@app.post('/pause')
def pause():
    player.command('set', 'pause', 'yes')
    player.wait_until_paused()
    return 0

@app.post('/unpause')
def unpause():
    player.command('set', 'pause', 'no')
    return 0

# curl -H "Content-Type: multipart/form-data" -F "file=@bootstrapper.zip" 127.0.0.1:5555/stream/


@app.post('/stream/')
async def stream(file: UploadFile = File(...)):
    tempfile = Path(TEMP_DIR, f'{str(time.time())}{Path(file.filename).suffix}')
    async with aiofiles.open(tempfile, 'wb') as out_file:
        while content := await file.read(1024):
            await out_file.write(content)
    return str(base64.urlsafe_b64encode(bytes(tempfile)), 'utf-8')

@player.python_stream('temp')
def stream_helper(stream: Path):
    with open(stream, 'rb') as tfile:
        while True:
            yield tfile.read(1024*1024)


def play_stream():
    player.play(f'python://temp')
    player.wait_until_playing()

    # if not file:
    #     return 0
    # else:
    #     return {'filename': file.filename}


if __name__ == '__main__':
    pass
