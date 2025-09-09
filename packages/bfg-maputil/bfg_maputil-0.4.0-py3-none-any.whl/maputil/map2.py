import sys
import traceback
from threading import Condition, Lock, Thread

import pandas as pd

if "ipykernel" in sys.modules:
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm


class Run:
    inputs: list
    results: list

    def __init__(self, fn, inputs, *, concurrency):
        if isinstance(inputs, pd.DataFrame):
            self.inputs = inputs.to_dict(orient="records")
            self.index = inputs.index
        elif isinstance(inputs, pd.Series):
            self.inputs = inputs.tolist()
            self.index = inputs.index
        elif isinstance(inputs, list):
            self.inputs = inputs
            self.index = None
        else:
            assert False

        assert isinstance(concurrency, int) and concurrency > 0
        self.concurrency = concurrency

        assert callable(fn)
        self.fn = fn

        self.total = len(inputs)
        self.results = [None] * self.total
        self.nresults = 0
        self.pending = list(range(self.total))
        # pop() will remove from the end so reverse the pending array
        self.pending.reverse()

        self.pbar = None

        self.err = None
        self.nworkers = 0
        self.lock = Lock()
        self.cond = Condition(self.lock)

    def worker(self):
        try:
            while True:
                with self.lock:
                    if self.err or not self.pending:
                        break
                    idx = self.pending.pop()
                try:
                    result = self.fn(self.inputs[idx])
                    with self.lock:
                        self.results[idx] = result
                        self.nresults += 1
                        self.pbar.update()
                except Exception:
                    with self.lock:
                        # do not overwrite err
                        if not self.err:
                            self.err = traceback.format_exc()
                        self.pbar.set_description("ERR")
                    break
        finally:
            with self.lock:
                self.nworkers -= 1
                if self.nworkers == 0:
                    self.pbar.close()
                    self.pbar = None
                    self.cond.notify_all()

    def start(self):
        with self.lock:
            if self.nworkers > 0:
                return
            npending = len(self.pending)
            self.nworkers = nworkers = min(self.concurrency, npending)
            self.pbar = tqdm(total=self.total, initial=self.total - npending)

        for _ in range(nworkers):
            Thread(target=self.worker).start()

    def join(self):
        with self.cond:
            while self.nworkers > 0:
                self.cond.wait()

    def get_results(self, partial=True):
        with self.lock:
            if not partial and self.nresults < self.total:
                # if partial results is not desired, return None if we don't have all results yet
                return None
            results = self.results.copy()
        if self.index is not None:
            return pd.Series(results, index=self.index)
        return results

    def get_err(self):
        with self.lock:
            return self.err


def map2(fn, inputs, *, concurrency=1):
    r = Run(fn, inputs, concurrency=concurrency)
    r.start()
    return r
