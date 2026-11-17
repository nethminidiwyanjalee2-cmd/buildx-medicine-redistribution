"""
Database client for MediStock.

Attempts to initialise Firebase Admin SDK with the Firestore emulator.
If initialisation fails for any reason (no credentials, Java/emulator not running,
firebase-admin not installed), the module falls back to reading/writing plain JSON
files stored in config.JSON_DATA_DIR.

DB_MODE is set to one of:
  "firestore"      — Firestore emulator or production Firestore is reachable
  "json_fallback"  — using local JSON files (default for Phase 0)

Phase 0: This module only sets DB_MODE. All actual read/write logic is added in Phase 1.
"""

# ---------------------------------------------------------------------------
# Phase 0 placeholder — engine and routers may import DB_MODE safely
# ---------------------------------------------------------------------------
# Real implementation in Phase 1 will attempt:
#
#   import firebase_admin
#   from firebase_admin import credentials, firestore
#   ...
#   _app = firebase_admin.initialize_app(...)
#   _client = firestore.client()
#   DB_MODE = "firestore"
#
# and fall back to JSON on any exception.
# ---------------------------------------------------------------------------

DB_MODE: str = "json_fallback"  # Phase 0 always uses fallback
