"""Background worker that processes a queue of tasks."""

import threading
import time
import os
from queue import Queue, Empty
from typing import Callable, Optional


class BackgroundWorker:
    def __init__(self, name: str = "worker"):
        self.name = name
        self._queue: Queue = Queue()
        self._thread: Optional[threading.Thread] = None
        self._stop = threading.Event()
        self._open_files = []

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, name=self.name, daemon=True)
        self._thread.start()

    def stop(self, timeout: float = 2.0):
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=timeout)

    def submit(self, task: Callable, *args, **kwargs):
        self._queue.put((task, args, kwargs))

    def _run(self):
        while not self._stop.is_set():
            try:
                task, args, kwargs = self._queue.get(timeout=0.1)
            except Empty:
                continue
            try:
                # simulate work that opens a file
                path = f"/tmp/orderflow_worker_{os.getpid()}_{time.time()}.tmp"
                f = open(path, "w")
                self._open_files.append(f)
                f.write("processing\n")
                task(*args, **kwargs)
            except Exception as e:
                print(f"[{self.name}] task error: {e}")
            finally:
                self._queue.task_done()

    def pending(self) -> int:
        return self._queue.qsize()

    def open_file_count(self) -> int:
        return len(self._open_files)
