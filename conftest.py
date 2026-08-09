"""Makes the repo root importable so `from wordpot import app` resolves.

Its presence at the root is what pytest uses to put this directory on sys.path,
so `pytest` and `python -m pytest` behave the same way -- locally and on CI.
"""
