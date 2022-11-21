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
    test_uri = 'https://www.youtube.com/watch?v=rSc9xYPMAQY'
    test_yt = requester.encode_uri(test_uri)

    # response = requester.play(test_yt)
    # time.sleep(5)
    response = requester.play(test_yt)
    # response = requester.stream(TEST_FILE)
    # response = requester.playtest()
    # response = requester.status()
    # print(response)
    # response = requester.status()
    time.sleep(5)
    # response = requester.pause()
    # print(response.text)
    # time.sleep(5)
    response = requester.stop()
    # time.sleep(10)
    # time.sleep(10)
    # time.sleep(15)
    # response = requester.stop()


if __name__ == '__main__':
    main()
