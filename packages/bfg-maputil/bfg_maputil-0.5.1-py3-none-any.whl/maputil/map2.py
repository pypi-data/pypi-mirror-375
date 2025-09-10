import sys
import traceback
from threading import Lock, Thread
from typing import Callable

import pandas as pd

if "ipykernel" in sys.modules:
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm


class Run:
    def __init__(self, fn, inputs, *, concurrency):
        if not callable(fn):
            raise TypeError("fn must be a callable")
        self.fn = fn

        if isinstance(inputs, pd.Series):
            self.index = inputs.index
            self.inputs = inputs.tolist()
        elif isinstance(inputs, pd.DataFrame):
            self.index = inputs.index
            self.inputs = inputs.to_dict(orient="records")
        elif isinstance(inputs, list):
            self.inputs = inputs
            self.index = None
        else:
            raise TypeError("inputs must be a list, Series, or DataFrame")

        if not isinstance(concurrency, int) or concurrency <= 0:
            raise ValueError("concurrency must be a positive integer")
        self.concurrency = concurrency

        self.lock = Lock()
        self.total = len(self.inputs)
        self.results = [None] * self.total
        self.err = None
        self.pending = list(range(self.total - 1, -1, -1))
        self.workers = []
        self.pb = None
        self.done = False

    def worker(self):
        while True:
            with self.lock:
                if self.done or not self.pending:
                    break
                idx = self.pending.pop()
            try:
                result = self.fn(self.inputs[idx])
                with self.lock:
                    self.results[idx] = result
                    self.pb.update()
            except Exception:
                with self.lock:
                    if not self.err:
                        self.err = traceback.format_exc()
                    self.done = True
                    break

    def start(self):
        self.pb = tqdm(total=self.total)
        try:
            # We manage threads manually instead of using ThreadPoolExecutor.
            # map() is often used in Jupyter notebooks. When users interrupt
            # the kernel, it sends exceptions to the main thread but doesn't
            # stop worker threads. Uncaught exceptions in the main thread
            # also don't stop worker threads.
            nworkers = min(self.concurrency, self.total)
            for _ in range(nworkers):
                w = Thread(target=self.worker)
                self.workers.append(w)
                w.start()

            for w in self.workers:
                w.join()

            return self.collect()
        finally:
            # ask the workers to exit on any error
            with self.lock:
                self.done = True
            self.pb.close()

    def collect(self):
        if self.err:
            raise RuntimeError(self.err)

        if self.index is not None:
            return pd.Series(self.results, index=self.index)
        return self.results


def map2(
    fn: Callable, inputs: list | pd.Series | pd.DataFrame, *, concurrency: int = 1
) -> list | pd.Series:
    """
    Apply fn to each item in inputs using threads and a progress bar.

    inputs may be a list, pandas Series, or DataFrame (rows as dicts).
    Preserves index for Series/DataFrame. Returns a list, or a Series if
    inputs had an index. concurrency controls number of worker threads.
    """

    return Run(fn, inputs, concurrency=concurrency).start()
