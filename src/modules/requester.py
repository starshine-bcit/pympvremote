
import json
from pathlib import Path
import requests
from requests.exceptions import HTTPError

from pympvremote.src.modules.b64_helper import encode_uri, decode_uri


class Requester():
    def __init__(self, server: str) -> None:
        self.session = requests.Session()
        self.session.verify = False
        self.server = server

    def play(self, uri: str, local: bool, replace: bool) -> requests.Response:
        encoded_uri = encode_uri(uri)
        return self.session.post(f'{self.server}/play?uri={encoded_uri}&replace={replace}&local={local}')

    def playtest(self) -> requests.Response:
        return self.session.post(self.server + '/playtest')

    def stop(self) -> requests.Response:
        return self.session.post(self.server + '/stop')

    def status(self) -> requests.Response:
        return self.session.get(self.server + '/status')

    def pause(self) -> requests.Response:
        return self.session.post(self.server + '/pause')

    def unpause(self) -> requests.Response:
        return self.session.post(self.server + '/unpause')

    def stream(self, file: Path, replace: bool) -> requests.Response:
        files = {
            'file': file.open('rb'),
            'Content-Disposition': 'form-data; name="file"; filename="' + str(file) + '"',
            'Content-Type': 'text/xml'
        }
        res = self.session.post(f'{self.server}/stream', files=files).json()
        return self.play(res.get('file'), local=True, replace=replace)

    def flist(self) -> requests.Response:
        return self.session.get(self.server + '/list')

    def upload(self, file: Path) -> requests.Response:
        files = {
            'file': file.open('rb'),
            'Content-Disposition': 'form-data; name="file"; filename="' + str(file) + '"',
            'Content-Type': 'text/xml'
        }
        return self.session.post(f'{self.server}/upload', files=files)

    def mute(self) -> requests.Response:
        return self.session.post(self.server + '/mute')

    def fullscreen(self) -> requests.Response:
        return self.session.post(self.server + '/fullscreen')

    def repeat(self) -> requests.Response:
        return self.session.post(self.server + '/repeat')

    def seek(self, percent: float) -> requests.Response:
        return self.session.post(f'{self.server}/seek?percent_pos={percent}')

    def volume(self, volume: int) -> requests.Response:
        return self.session.post(f'{self.server}/volume?volume={volume}')

    def playlist(self, plist: list[str], new: bool, index: int) -> requests.Response:
        plist_json = json.dumps({'plist': plist, 'new': new, 'index': index})
        return self.session.post(f'{self.server}/playlist', data=plist_json, headers={'Content-type': 'application/json', 'Accept': 'application/json'})

    def next(self):
        return self.session.post(self.server + '/next')

    def previous(self):
        return self.session.post(self.server + '/previous')

    def play_index(self, index: int):
        return self.session.post(f'{self.server}/playindex?index={index}')


if __name__ == '__main__':
    pass
