import threading


def test_allowed_to_send_atomic_under_concurrency():
    from arched_emailer.arched_emailer import ArchedEmailer

    ae = ArchedEmailer("TestApp", flask=True)

    # Ensure a clean slate for throttling state
    ae.errors_name_time.clear()

    msg = "ConcurrentErrorSignature"
    results = []
    results_lock = threading.Lock()
    start_event = threading.Event()

    def worker():
        start_event.wait()
        allowed = ae._allowed_to_send(msg, allowed_minutes=60)
        with results_lock:
            results.append(allowed)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for t in threads:
        t.start()

    # Release all threads to call the method nearly simultaneously
    start_event.set()

    for t in threads:
        t.join()

    # Exactly one thread should be allowed to send; the rest should be throttled
    assert sum(1 for r in results if r) == 1

