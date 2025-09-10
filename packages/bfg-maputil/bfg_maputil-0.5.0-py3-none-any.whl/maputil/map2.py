import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

import pandas as pd

if "ipykernel" in sys.modules:
    from tqdm.notebook import tqdm
else:
    from tqdm import tqdm


def map2(
    fn: Callable, inputs: list | pd.Series | pd.DataFrame, *, concurrency: int = 1
) -> list | pd.Series:
    """Apply fn to each item in inputs using threads and a progress bar.

    inputs may be a list, pandas Series, or DataFrame (rows as dicts).
    Preserves index for Series/DataFrame. Returns a list, or a Series if
    inputs had an index. concurrency controls number of worker threads.
    """
    if not callable(fn):
        raise TypeError("fn must be a callable")

    if isinstance(inputs, pd.Series):
        index = inputs.index
        inputs = inputs.tolist()
    elif isinstance(inputs, pd.DataFrame):
        index = inputs.index
        inputs = inputs.to_dict(orient="records")
    elif isinstance(inputs, list):
        index = None
    else:
        raise TypeError("inputs must be a list, Series, or DataFrame")

    if not isinstance(concurrency, int) or concurrency <= 0:
        raise ValueError("concurrency must be a positive integer")

    ########################

    total = len(inputs)
    results = [None] * total

    def fn_wrapper(idx):
        result = fn(inputs[idx])
        return idx, result

    with ThreadPoolExecutor(max_workers=concurrency) as ex:
        futs = [ex.submit(fn_wrapper, idx) for idx in range(total)]
        for fut in tqdm(as_completed(futs), total=total):
            idx, result = fut.result()
            results[idx] = result

    if index is not None:
        return pd.Series(results, index=index)
    return results
