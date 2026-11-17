"""
Seed data generator for MediStock.

STATUS: Phase 0 placeholder — do NOT implement logic here yet.

Phase 1 implementation:
  Running this script will:
  1. Generate 3 healthcare facility records.
  2. Generate 5 medicine category records with 5+ medicines.
  3. Generate 14 days of synthetic consumption history per (facility, medicine) pair.
  4. Write everything as JSON to config.JSON_DATA_DIR.
  5. Optionally push to Firestore emulator if running.

  Usage (Phase 1):
      python -m seed.seed_data

  The generated data must be deterministic (use a fixed random seed) so that
  every team member gets identical data for reproducible demos.
"""


def generate_seed_data() -> None:
    """
    Generate and persist seed data for all facilities and medicines.

    Not yet implemented — raises NotImplementedError in Phase 0.
    """
    raise NotImplementedError("generate_seed_data() will be implemented in Phase 1.")


if __name__ == "__main__":
    generate_seed_data()
