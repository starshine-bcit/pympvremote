# pympvremote

Python-based Qt client which can control a remote mpv instance via an API.

## Details

### Features

#### Planned Features

### Requirements

## Getting Started

### Installation

1. Close the repository: `git clone https://github.com/starshine-bcit/pympvremote.git`
2. Create and activate a python virtual environment.
3. Install mpv (Windows builds can be acquired [here](https://sourceforge.net/projects/mpv-player-windows/files/64bit-v3/), check the youtube-dl option when installing, then add the directory to your path)
4. For linux, ensure you have `libmpv.so` in your path, if not install it. For Windows, download libmpv from [here](https://sourceforge.net/projects/mpv-player-windows/files/libmpv/) and extract it alongside your mpv installation.
5. Ensure you have [yt-dlp](https://github.com/yt-dlp/yt-dlp) either on your path or beside the MPV libary.
6. `pip install -r requirements.txt` to install the necessary Python dependencies.
7. Start the server `python3 ./src/mpvremoteserver.py`. Use `python` if on Windows.
8. Start the client `python3 ./src/mpvremoteclient.py`. Use `pthon` if on Windows.

#### Caution: Do not expose the api to the web. It is only meant for local use at this time.

### Usage

ToDo

## Acknowledgements

### mpv.py

pympvremote is bundled with [mpv.py by jaseg](https://github.com/jaseg/python-mpv), the full base license is available [here](https://github.com/mpv-player/mpv/blob/master/Copyright).

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

While pympvremote does not ship with any compiled [mpv](https://mpv.io/) libraries or binaries, this project would not be possible without them. [Repo link](https://github.com/mpv-player/mpv/)

## License

This project is licensed under the [GPLv3](https://www.gnu.org/licenses/gpl-3.0.txt). The full text can also be viewed in the LICENSE file.

## Author

Sasha Fey