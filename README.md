# pympvremote

Python-based Qt client which can control a remote mpv instance via an API.

## Details

The server side of this project is running uvicorn/fastapi, an implementation of the ASGI specification, and puppets an instance of mpv. The client side GUI is implemented in PyQt6 and uses the requests library to communicate with the server.

pympvremote was influenced by [jellyfin-mpv-shim](https://github.com/jellyfin/jellyfin-mpv-shim), which is a similar (but much more advanced) project that allows one to control the player via any supported jellyfin client and stream any video from your jellyfin server. 

The idea was to create a simple, easy to use alternative for someone wanting to control mpv remotely.

### Features

- Control an mpv instance over a network
- Standard media player controls like play/pause, mute, fullscreen
- Upload files
- Play files local to the server side
- Play any http stream that mpv supports
- Create and manage playlists
- Persistent storage of URL list
- Interact directly with the API if you don't like the GUI

#### Planned Features

This was put together fairly quickly, but I plan to include more features when time permits.

- SSL support
- API key support
- Proper Error Handling / Timeouts for API calls
- Argument support on client and server to override coded configurations
- Support for mpv config files (and potentially lua/js scripts, if possible)
- Save/Load playlists

#### Maybe Features

- Switch from HTTP/1.1 to websocket
- Proper streaming support

### Requirements

- Python 3.10+ (could probably run on 3.7+ with a few modifications)
- Modern Windows or Linux DE
- Server-side capable of playing whatever media you plan to use
- mpv dev files (detailed below)
- yt-dlp or youtube-dl
- All PyPi requirements in `requirements.txt`

## Getting Started

### Installation

1. Close the repository: `git clone https://github.com/starshine-bcit/pympvremote.git`
2. Create and activate a python virtual environment.
3. Install mpv (Windows builds can be acquired [here](https://sourceforge.net/projects/mpv-player-windows/files/64bit-v3/), check the youtube-dl option when installing, then add the directory to your path)
4. For linux, ensure you have `libmpv.so` in your path, if not install it. For Windows, download libmpv from [here](https://sourceforge.net/projects/mpv-player-windows/files/libmpv/) and extract it alongside your mpv installation.
5. Ensure you have [yt-dlp](https://github.com/yt-dlp/yt-dlp) either on your path or beside the MPV libary.
6. `pip install -r requirements.txt` to install the necessary Python dependencies.
7. Adjust any relevant settings inside ./src/modules/settings/* for your setup

#### Caution: Do not expose the api to the web. It is only meant for local use at this time.

### Usage

1. Start the server `python3 ./src/mpvremoteserver.py`. Use `python` if on Windows. You should see uvicorn's info-level messages by default, telling you the server has started.
2. Start the client `python3 ./src/mpvremoteclient.py`. Use `python` if on Windows. The GUI will load up as long as it is able to connect to the server.
3. ...

## Acknowledgements

### python-mpv

pympvremote is bundled with `mpv.py` from [python-mpv](https://github.com/jaseg/python-mpv), the full base license it inherits is available [here](https://github.com/mpv-player/mpv/blob/master/Copyright).

### lucide

pympvremote's icons are created and maintained by the [lucide community](https://github.com/lucide-icons/lucide).  
They are distributed under the ISC License, as follows:
```
ISC License

Copyright (c) for portions of Lucide are held by Cole Bemis 2013-2022 as part of Feather (MIT). All other copyright (c) for Lucide are held by Lucide Contributors 2022.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted, provided that the above
copyright notice and this permission notice appear in all copies.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
```

### Qt

This project uses open-source tools and libraries from the Qt Project to generate a GUI, in accordance with the GPLv3 License.

### mpv

While pympvremote does not ship with any compiled [mpv](https://mpv.io/) libraries or binaries, this project would not be possible without them. [repo link](https://github.com/mpv-player/mpv/).

## License

This project is licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.txt). The full text can also be viewed in the LICENSE file.

## Author

Sasha Fey