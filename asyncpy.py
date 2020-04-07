import asyncio
import janus
import random

_sentinel = object()


# I tryied using another function to emulate an I/O job
# but I was getting a <coroutine object Queue.get at ...>
# on Thread.

# async def work_on_task(task):
#     # This simulate an I/O job
#     iotime = random.randint(1, 5)
#     await asyncio.sleep(iotime)
#     return f"Task {task} took {iotime}."


def thread_worker(sync_q):
    # Emulates a job with some sync lib
    # sync_q is Janus Sync Queue
    while True:
        task = sync_q.get()
        if task is _sentinel:
            break
        # Process the task
        print(f"Task printed on Thread: ({task}).")
        sync_q.task_done()


async def async_worker(name, consumer_q, producer_q):
    # Consumer Queue is Asyncio Queue
    # Producer Queue is Janus Async Queue to comunicate with Thread
    while True:
        task = await consumer_q.get()  # should I await on this?
        iotime = random.randint(1, 5)
        await asyncio.sleep(iotime)
        res = f"{name} worked on task {task} in {iotime} seconds."
        producer_q.put_nowait(res)  # should I await on this?
        await producer_q.join()  # should I await on this?
        consumer_q.task_done()  # should I await on this?


async def main():
    janus_q = janus.Queue()
    async_q = asyncio.Queue()

    # This generates items to be processed.
    for i in range(10):
        async_q.put_nowait(i + 1)

    # This will limit the number of concurrent tasks
    tasks = []
    for i in range(3):
        task = asyncio.create_task(
            async_worker(
                name=f"Worker-{i}",
                consumer_q=async_q,
                producer_q=janus_q.async_q,
            )
        )
    # Start the Thread side to work on Sync Lib.
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, thread_worker, janus_q.sync_q)

    # How to stop verything?
    # Lets try this based on the example on Python Async doc:
    await async_q.join()
    # await row_q.async_q.join() # Should I wait on Janus Queue too?

    # done, pending = await asyncio.wait(tasks)

    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    await janus_q.async_q.put(_sentinel)


asyncio.run(main())
