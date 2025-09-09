import time
from collections import Counter
from threading import Event, Lock

import pandas as pd

from maputil import map2


def test_simple():
    def f(x):
        return x + 1

    r = map2(f, [10, 20, 30])
    r.join()
    assert [11, 21, 31] == r.get_results()


def test_threading():
    def f(x):
        time.sleep(1)
        return x + 1

    r = map2(f, [10, 20, 30], concurrency=10)
    r.join()
    assert [11, 21, 31] == r.get_results()


def test_stop_on_error_stops_scheduling_new_tasks():
    # Error happens on the very first item (index/value 0); after the error,
    # workers should stop taking new tasks. Some already-started tasks may finish,
    # but at least one pending task must remain unprocessed.
    def f(x):
        if x == 0:
            raise RuntimeError("boom")
        time.sleep(0.01)
        return x + 1

    inputs = list(range(100))
    r = map2(f, inputs, concurrency=16)
    r.start()  # idempotent; already started by map2
    r.join()

    results = r.get_results()
    err = r.get_err()
    assert err is not None and "RuntimeError" in err
    # The failing item should remain unset
    assert results[0] is None
    # And not all items should be processed
    assert any(v is None for v in results)


def test_no_duplicate_processing_under_concurrency():
    # Ensure each input is processed exactly once under high concurrency
    n = 200
    counter = Counter()
    lock = Lock()

    def f(x):
        with lock:
            counter[x] += 1
        time.sleep(0.001)
        return x

    r = map2(f, list(range(n)), concurrency=32)
    r.join()

    # Results are correct and ordered
    assert r.get_results() == list(range(n))
    # Each input processed exactly once
    assert set(counter.keys()) == set(range(n))
    assert sum(counter.values()) == n
    assert all(c == 1 for c in counter.values())


def test_dataframe_index_preserved_under_concurrency():
    df = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]}, index=[10, 20, 30])

    def f(row):
        # row is a dict (from DataFrame.to_dict records)
        return row["x"] + row["y"]

    r = map2(f, df, concurrency=3)
    r.join()
    out = r.get_results()

    assert list(out.index) == [10, 20, 30]
    assert list(out.values) == [11, 22, 33]


def test_series_index_preserved_under_concurrency():
    s = pd.Series([5, 6, 7], index=[100, 200, 300])

    def f(x):
        return x + 1

    r = map2(f, s, concurrency=2)
    r.join()
    out = r.get_results()

    assert list(out.index) == [100, 200, 300]
    assert list(out.values) == [6, 7, 8]


def test_progress_bar_closed_after_join():
    def f(x):
        time.sleep(0.01)
        return x

    r = map2(f, list(range(5)), concurrency=3)
    r.join()
    assert r.pbar is None


def test_start_idempotent_during_run():
    def f(x):
        time.sleep(0.01)
        return x + 1

    r = map2(f, list(range(20)), concurrency=5)
    # Calling start again while running should be a no-op
    r.start()
    r.join()

    assert r.get_err() is None
    assert r.pbar is None
    assert r.get_results() == [x + 1 for x in range(20)]


def test_get_results_partial_and_full():
    started = Event()

    def f(x):
        started.set()
        time.sleep(0.1)
        return x + 1

    n = 6
    r = map2(f, list(range(n)), concurrency=1)

    # Ensure at least one worker has started before checking partial state
    started.wait(timeout=1)

    # Before completion, partial=False should yield None
    assert r.get_results(partial=False) is None

    # partial=True should return a list with placeholders for unfinished work
    partial_results = r.get_results(partial=True)
    assert isinstance(partial_results, list)
    assert len(partial_results) == n
    assert any(v is None for v in partial_results)

    # After completion, both modes should return full results
    r.join()
    expected = [x + 1 for x in range(n)]
    assert r.get_results(partial=False) == expected
    assert r.get_results(partial=True) == expected
