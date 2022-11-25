#!/usr/bin/env python3

from pathlib import Path
import shutil

import uvicorn

from settings.server_settings import LISTEN_PORT, TEMP_DIR, LOG_LEVEL


def check_temp() -> None:
    """Creates Temp directory to store uploaded files.
        The directory is deleted on each relaunch of the program.
    """
    if TEMP_DIR.is_dir():
        shutil.rmtree(TEMP_DIR)
    elif TEMP_DIR.is_file():
        Path.unlink(TEMP_DIR)
    TEMP_DIR.mkdir()


def main():
    check_temp()
    config = uvicorn.Config('modules.mpvapi:app',
                            port=LISTEN_PORT,
                            log_level=LOG_LEVEL)
    server = uvicorn.Server(config)
    server.run()


if __name__ == '__main__':
    main()
