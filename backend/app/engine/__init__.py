"""
MediStock engine package.

ISOLATION RULE (enforced by test_engine_isolation.py):
  Modules inside this package MUST NOT import any of:
    - firebase_admin
    - fastapi
    - app.data  (or any sub-module)
    - app.db

  The engine is pure-Python computational logic. It accepts plain Python
  dicts/lists and returns plain Python dicts/lists. This makes every engine
  module independently unit-testable without any running infrastructure.
"""
