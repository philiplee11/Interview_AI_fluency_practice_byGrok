import time
from src.services.worker import BackgroundWorker


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
