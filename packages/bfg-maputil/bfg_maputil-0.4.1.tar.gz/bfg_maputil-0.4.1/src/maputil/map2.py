import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import Callable

import pandas as pd

if "ipykernel" in sys.modules:
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm


class Run:
    _inputs: list
    _results: list

    def __init__(self, fn, inputs, *, concurrency):
        if isinstance(inputs, pd.DataFrame):
            self._inputs = inputs.to_dict(orient="records")
            self._index = inputs.index
        elif isinstance(inputs, pd.Series):
            self._inputs = inputs.tolist()
            self._index = inputs.index
        elif isinstance(inputs, list):
            self._inputs = inputs
            self._index = None
        else:
            raise TypeError("inputs must be a list, Series, or DataFrame")

        if not isinstance(concurrency, int) or concurrency <= 0:
            raise ValueError("concurrency must be a positive integer")
        self.concurrency = concurrency

        if not callable(fn):
            raise TypeError("fn must be a callable")
        self._fn = fn

        self._total = len(self._inputs)
        self._lock = Lock()
        self._pbar = None
        self._results = [None] * self._total
        self._pending = set(range(self._total))

    def _fn_wrapper(self, idx):
        result = self._fn(self._inputs[idx])
        with self._lock:
            self._results[idx] = result
            self._pending.remove(idx)
            self._pbar.update()

    def __call__(self):
        pending = list(self._pending)
        self._pbar = tqdm(total=self._total, initial=self._total - len(pending))
        try:
            with ThreadPoolExecutor(max_workers=self.concurrency) as ex:
                futs = [ex.submit(self._fn_wrapper, idx) for idx in pending]
                for fut in as_completed(futs):
                    fut.result()
            return self.get_results()
        finally:
            self._pbar.close()
            self._pbar = None

    def get_results(self, partial=False):
        if not partial and self._pending:
            raise ValueError("not all tasks have completed")

        if self._index is not None:
            return pd.Series(self._results, index=self._index)
        return self._results


def map2(
    fn: Callable, inputs: list | pd.Series | pd.DataFrame, *, concurrency: int = 1
) -> Run:
    return Run(fn, inputs, concurrency=concurrency)
