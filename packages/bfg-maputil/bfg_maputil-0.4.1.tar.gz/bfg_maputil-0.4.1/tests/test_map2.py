import time

from maputil import map2


def test_simple():
    c = 0

    def f(x):
        nonlocal c
        c += 1
        return x + 1

    run = map2(f, [10, 20, 30])
    assert [11, 21, 31] == run()
    assert c == 3


def test_threading():
    c = 0

    def f(x):
        nonlocal c
        c += 1
        time.sleep(1)
        return x + 1

    run = map2(f, [10, 20, 30], concurrency=10)
    assert [11, 21, 31] == run()
    assert c == 3


def test_progress():
    def f(x):
        time.sleep(0.1)
        return x + 1

    run = map2(f, list(range(100)), concurrency=2)
    run()
