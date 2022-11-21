#!/usr/bin/env python3

import time
from pathlib import Path

from src.modules.requester import Requester

TEST_FILE = Path('C:\\Courses\\2515\\testvids\\production ID_3756003.mp4')

def main():
    # session = requests.Session()
    # session.verify = False

    # session.post('http://127.0.0.1:5555/play')
    requester = Requester()

    response = requester.stream(TEST_FILE)
    time.sleep(10)
    response = requester.stop()
    # response = requester.playtest()
    # time.sleep(10)
    # response = requester.pause()
    # time.sleep(10)
    # response = requester.unpause()
    # time.sleep(15)
    # response = requester.stop()
    


if __name__ == '__main__':
    main()
