## maputil

Concurrent map for lists, pandas Series, and DataFrames. Preserves index and shows a progress bar.

```python
from maputil import map2

map2(lambda x: x + 1, [10, 20, 30], concurrency=4)
```
