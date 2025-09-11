import time

from maputil import map2


def test_simple():
    def f(x):
        return x + 1

    assert [11, 21, 31] == map2(f, [10, 20, 30])


def test_threading():
    def f(x):
        time.sleep(1)
        return x + 1

    assert [11, 21, 31] == map2(f, [10, 20, 30], concurrency=10)


def manual_test_progress():
    def f(x):
        time.sleep(0.1)
        return x + 1

    map2(f, list(range(100)), concurrency=2)


def manual_test_one_very_slow():
    def f(x):
        if x == 40:
            time.sleep(5)
        return x + 1

    # tqdm tries to be efficient and won’t refresh the bar on every iteration
    # by default if it thinks the loop is going fast. This is controlled by
    # its mininterval and maxinterval logic.
    map2(f, list(range(100)), concurrency=1)


if __name__ == "__main__":
    manual_test_one_very_slow()
    manual_test_progress()
