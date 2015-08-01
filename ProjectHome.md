# 2C.py - Python-to-C compiler for CPython 2.6 #
**Static (not JIT) python-to-binary compiler.**

Usage:
> python 2C.py options SOURCE.py

produced output
> _c\_SOURCE.c
>_c\_SOURCE.so (or _c\_SOURCE.dll)_

Need C compiler (identity to compiler building CPython).

Benchmark:
```
  bpnn3.py      - speedup 5.2
  slowpickle.py - speedup 1.8
  fibtest.py    - speedup 8
  richards.py   - speedup 1.9
  pystone.py    - speedup 3.3
```
