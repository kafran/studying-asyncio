import asyncio
import janus
import random

_sentinel = object()


def threaded(sync_q):
    while True:
        for val in iter(sync_q.get, _sentinel):
            print(val)
            sync_q.task_done()


async def async_worker(name, async_q):
    for i in range(10):
        await async_q.put(f"Coro 1: {i}")
        await asyncio.sleep(1)
    await async_q.join()


async def main():
    q1 = janus.Queue()
    q2 = asyncio.Queue()

    for i in range(30):
        q2.put_nowait(i + 1)

    tasks = []
    for i in range(2):
        task = asyncio.create_task()

    # done, pending = await asyncio.wait()
    # if not pending:
    #     await q1.async_q.put(_sentinel)

    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, threaded, q1.sync_q)


asyncio.run(main())
