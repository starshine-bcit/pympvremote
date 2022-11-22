#!/usr/bin/env python3

import asyncio
import time
from pathlib import Path

from src.modules.requester import Requester

TEST_FILE = Path('C:\\Courses\\2515\\testvids\\production ID_3756003.mp4')
TEST_FILE_LARGER= Path('C:\\Courses\\2515\\testvids\\Commands Prompt Commands Everybody Should Know [iXprT0ltnVg].webm')

async def stats(requester: Requester):
    while True:
        await asyncio.sleep(1)
        response = requester.status()
        json_response = response.json()
        print(json_response)
        if json_response['filename'] is None:
            break
    return 0


async def main():
    requester = Requester()
    test_uri = 'https://www.youtube.com/watch?v=rSc9xYPMAQY'
    test_yt = requester.encode_uri(test_uri)
    test_local = requester.encode_uri(str(TEST_FILE))
    
    # time.sleep(5)
    
    # response = requester.play(test_yt, replace=False)
    # response = requester.play(test_local, replace=False)
    stats_task = asyncio.create_task(stats(requester))
    response = requester.stream(TEST_FILE_LARGER, replace=False)
    print(response.text)
    # response = requester.stream(TEST_FILE, replace=True)
    await asyncio.sleep(1)
    # response = requester.stream(TEST_FILE, replace=False)
    await asyncio.sleep(5)
    
    # response = requester.playtest()

    # print(response)
    # response = requester.status()
    # time.sleep(5)
    # response = requester.pause()
    # print(response.text)
    # time.sleep(5)
    response = requester.stop()
    # time.sleep(10)
    # time.sleep(10)
    # time.sleep(15)
    # response = requester.stop()


if __name__ == '__main__':
    asyncio.run(main())
