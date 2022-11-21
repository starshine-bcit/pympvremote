
from pathlib import Path
import base64
import requests
from requests.exceptions import HTTPError

from src.settings.settings import SERVER

class Requester():
    def __init__(self) -> None:
        self.session = requests.Session()
        self.session.verify = False
        self.server = SERVER

    def play(self, uri: str) -> requests.Response:
        return self.session.post(f'{self.server}/play?uri={uri}')

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

    def stream(self, file: Path) -> requests.Response:
        files = {
            'file': file.open('rb'),
            'Content-Disposition': 'form-data; name="file"; filename="' + str(file) + '"',
            'Content-Type': 'text/xml'
        }
        response = self.session.post(f'{self.server}/stream', files=files)
        print(response.text)
        print(str(base64.urlsafe_b64decode(response.text), 'utf-8'))
        return response