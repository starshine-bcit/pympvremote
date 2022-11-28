
import json
from pathlib import Path
import requests
from requests.exceptions import HTTPError

from .b64_helper import encode_uri


class Requester():
    def __init__(self, server: str) -> None:
        """Creates a session with the server and abstracts api
            calls away from the main client code.

        Args:
            server (str): the server address and port to connect with, 
                for example 'http://127.0.0.1:5555'
        """
        self.session = requests.Session()
        self.session.verify = False
        self.server = server

    def play(self, uri: str, local: bool, replace: bool) -> requests.Response:
        """Play or stream a file immediately

        Args:
            uri (str): either an http stream or path to server-side file
            local (bool): whether or not the file is locally stored on server
            replace (bool): sets clobber, if true then playing another item
                when one is already playing will start the new one

        Returns:
            requests.Response: Generic response item
        """
        encoded_uri = encode_uri(uri)
        return self.session.post(f'{self.server}/play?uri={encoded_uri}&replace={replace}&local={local}')

    def stop(self) -> requests.Response:
        """Stops playing the current playlist/file, if possible

        Returns:
            requests.Response: Generic response item
        """
        return self.session.post(self.server + '/stop')

    def status(self) -> requests.Response:
        """Gets status from the player, response contains a dict
            with a variety of data.

        Returns:
            requests.Response: Generic response item
        """
        return self.session.get(self.server + '/status')

    def pause(self) -> requests.Response:
        """Toggles pause status

        Returns:
            requests.Response: Generic response item
        """
        return self.session.post(self.server + '/pause')

    def stream(self, file: Path) -> requests.Response:
        """Posts a file to server into a temp folder, then plays
            it immediately.

        Args:
            file (Path): Client-side file to upload

        Returns:
            requests.Response: Generic response item
        """
        files = {
            'file': file.open('rb'),
            'Content-Disposition': 'form-data; name="file"; filename="' + str(file) + '"',
            'Content-Type': 'text/xml'
        }
        res = self.session.post(f'{self.server}/stream', files=files).json()
        return self.play(res.get('file'), local=True, replace=True)

    def flist(self) -> requests.Response:
        """Gets list of files in the server's media directory

        Returns:
            requests.Response: Generic response item
        """
        return self.session.get(self.server + '/list')

    def upload(self, file: Path) -> requests.Response:
        """Uploads a file to server, into the media directory

        Args:
            file (Path): Client-side files to upload

        Returns:
            requests.Response: Generic response item
        """
        files = {
            'file': file.open('rb'),
            'Content-Disposition': 'form-data; name="file"; filename="' + str(file) + '"',
            'Content-Type': 'text/xml'
        }
        return self.session.post(f'{self.server}/upload', files=files)

    def mute(self) -> requests.Response:
        """Toggle mute status on the player

        Returns:
            requests.Response: Generic response item
        """
        return self.session.post(self.server + '/mute')

    def fullscreen(self) -> requests.Response:
        """Toggles fullscreen status on the player

        Returns:
            requests.Response: Generic response item
        """
        return self.session.post(self.server + '/fullscreen')

    def repeat(self) -> requests.Response:
        """Toggles infinite and zero playlist/single looping on player

        Returns:
            requests.Response: Generic response item
        """
        return self.session.post(self.server + '/repeat')

    def seek(self, percent: float) -> requests.Response:
        """Seek to the specified place in file, if possible

        Args:
            percent (float): absolute percent position to seek too

        Returns:
            requests.Response: Generic response item
        """
        return self.session.post(f'{self.server}/seek?percent_pos={percent}')

    def volume(self, volume: int) -> requests.Response:
        """Sets volume on the player

        Args:
            volume (int): volume to set, should be between 0 and 100

        Returns:
            requests.Response: Generic response item
        """
        return self.session.post(f'{self.server}/volume?volume={volume}')

    def playlist(self, plist: list[str], new: bool, index: int) -> requests.Response:
        """Sends a playlist and begins playing the specified position

        Args:
            plist (list[str]): list of items to pass to player
            new (bool): whether this is a new or updated playlist
            index (int): the index item to start playing, starting at zero
        Returns:
            requests.Response: Generic response item
        """
        plist_json = json.dumps({'plist': plist, 'new': new, 'index': index})
        return self.session.post(f'{self.server}/playlist', data=plist_json, headers={'Content-type': 'application/json', 'Accept': 'application/json'})

    def next(self) -> requests.Response:
        """Plays next playlist item, if possible

        Returns:
            requests.Response: Generic response item
        """
        return self.session.post(self.server + '/next')

    def previous(self) -> requests.Response:
        """Plays previous playlist item, if possible

        Returns:
            requests.Response: Generic response item
        """
        return self.session.post(self.server + '/previous')


if __name__ == '__main__':
    pass
