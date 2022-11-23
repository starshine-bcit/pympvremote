#!/usr/bin/env python3

from pathlib import Path
import shutil

import uvicorn

from src.settings.settings import LISTEN_PORT, TEMP_DIR, LOG_LEVEL

RELOAD_DIRS = ['./modules']
RELOAD = True

def check_temp():
    if TEMP_DIR.is_dir():
        shutil.rmtree(TEMP_DIR)
    elif TEMP_DIR.is_file():
        Path.unlink(TEMP_DIR)
    TEMP_DIR.mkdir()


def main():
    check_temp()
    config = uvicorn.Config('modules.mpvapi:app',
                            port=LISTEN_PORT,
                            log_level=LOG_LEVEL,
                            reload=RELOAD,
                            reload_dirs=RELOAD_DIRS)
    server = uvicorn.Server(config)
    server.run()


if __name__ == '__main__':
    main()
