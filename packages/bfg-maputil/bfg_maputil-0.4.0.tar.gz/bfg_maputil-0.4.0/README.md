# maputil

A concurrent map utility for lists, pandas Series, and DataFrames. Preserves indexes and shows a progress bar. Returns a `Run` handle for partial results and error inspection.

## Features

- Concurrent execution with threads (`concurrency`)
- Works with lists, Series, and DataFrames
- Preserves input indexes in the output (`pd.Series`)
- Progress bar (terminal and Jupyter)
- Stops scheduling on first error; inspect via `Run.get_err()`

## Example

```python
from maputil import map2

def f(x):
    return x + 1

r = map2(f, [10, 20, 30], concurrency=4)
r.join()
print(r.get_results())  # [11, 21, 31]
```

With a pandas DataFrame:

```python
import pandas as pd
from maputil import map2

df = pd.DataFrame({"x": [1, 2, 3], "y": [10, 20, 30]}, index=[10, 20, 30])

def f(row):
    return row["x"] + row["y"]

r = map2(f, df, concurrency=3)
r.join()
out = r.get_results()  # pd.Series(index=[10, 20, 30], values=[11, 22, 33])
```

## Usage

- `map2(fn, inputs, concurrency=1) -> Run`
- `Run.start()` is idempotent; `map2` starts automatically
- `Run.join()` waits for completion
- `Run.get_results(partial=True)` returns a list or `pd.Series`
- `Run.get_err()` returns a traceback string or `None`
