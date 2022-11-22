
import base64
from pathlib import Path
import requests
from requests.exceptions import HTTPError

from src.settings.settings import SERVER

class Requester():
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.verify = False
        self.server = SERVER

    def play(self, uri: str, replace: bool) -> requests.Response:
        return self.session.post(f'{self.server}/play?uri={uri}&replace={replace}')

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
        response = self.session.post(f'{self.server}/stream', files=files)
        return self.play(response.text, replace=replace)

    def encode_uri(self, uri: str) -> str:
        return str(base64.urlsafe_b64encode(
        bytes(uri, encoding='utf-8')), 'utf-8')
