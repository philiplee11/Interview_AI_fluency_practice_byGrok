import time
import threading
from src.services.worker import BackgroundWorker


def test_concurrent_start_does_not_spawn_duplicate_worker_threads():
    """Many callers hitting start() at once should end up with exactly
    one worker thread, not one per caller."""
    w = BackgroundWorker("dup-test-worker")
    n_callers = 30
    barrier = threading.Barrier(n_callers)

    def call_start():
        barrier.wait()  # release all callers at nearly the same instant
        w.start()

    callers = [threading.Thread(target=call_start) for _ in range(n_callers)]
    for c in callers:
        c.start()
    for c in callers:
        c.join()

    time.sleep(0.05)  # let any spawned worker threads finish registering
    matching = [t for t in threading.enumerate() if t.name == "dup-test-worker"]

    w.stop()
    time.sleep(0.15)  # let any orphaned worker threads notice _stop and exit

    assert len(matching) <= 1, f"Expected at most 1 worker thread, found {len(matching)}: {matching}"


def test_worker_stops_and_closes_files():
    w = BackgroundWorker("test-worker")
    w.start()

    def noop():
        pass

    for _ in range(5):
        w.submit(noop)

    time.sleep(0.3)
    w.stop(timeout=2.0)

    # After stop we expect zero open files tracked
    assert w.open_file_count() == 0, f"Leaked {w.open_file_count()} file handles"
