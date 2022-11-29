import traceback

from queue import Queue
from threading import Thread

_queue = Queue()


# Run this as a daemon so the thread will be cleaned up if the process is destroyed    
def _run() -> None:
    while True:
        action = _queue.get(block=True)

        try:
            action()
        except Exception as e:
            print(f'Error occurred on Window thread.')
            traceback.print_exc()


def start():
    # Making the creation of the thread be the last thing that happens
    # so that the rest of initialization is done before it starts
    Thread(target=_run, daemon=True).start()


def enqueue_action(action):
    if not callable(action):
        print(f'Received an action of type {type(action)}, rather than a function. The action will be ignored.')
        return

    _queue.put(action)
