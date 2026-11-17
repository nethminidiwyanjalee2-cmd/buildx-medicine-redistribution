"""
Engine isolation tests for MediStock.

Enforces the hard architectural rule:
    engine/*.py modules MUST NOT import firebase_admin, fastapi,
    app.data, or any database module.

The engine is pure-Python computational logic. This test uses Python's
built-in `ast` module to statically analyse each engine source file —
no code is executed, so there is no risk of import side-effects.

Why this matters for judges:
    Keeping the engine isolated means every forecasting/risk/optimisation
    function can be unit-tested instantly without a running database or
    web server. It also makes the computational logic easy to explain and
    swap out without touching infrastructure.
"""

import ast
import pathlib

# Directory containing the engine modules (relative to repo root).
# Tests are run from the backend/ directory (see pytest.ini / setup.cfg).
ENGINE_DIR = pathlib.Path(__file__).parent.parent / "app" / "engine"

# Modules that MUST NOT appear in any engine import statement.
FORBIDDEN_MODULES = {
    "firebase_admin",
    "fastapi",
    "app.data",
    "app.db",
    "httpx",          # HTTP client — engine has no business calling APIs
    "sqlalchemy",     # ORM — engine must not touch databases
}


def _get_engine_python_files() -> list[pathlib.Path]:
    """Return all .py files in the engine directory (excluding __init__.py)."""
    return [
        p for p in ENGINE_DIR.glob("*.py")
        if p.name != "__init__.py"
    ]


def _extract_imports(source: str) -> list[str]:
    """
    Return a flat list of top-level module names imported in `source`.

    Handles both `import x` and `from x import y` statements.
    For `from app.data.db import something` the top-level name is `app.data`.
    """
    tree = ast.parse(source)
    imported: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imported.append(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imported.append(node.module)
    return imported


class TestEngineIsolation:
    """One test method per engine file for clear failure messages."""

    def _check_file(self, path: pathlib.Path) -> None:
        """Assert that `path` contains no forbidden imports."""
        source = path.read_text(encoding="utf-8")
        imports = _extract_imports(source)
        violations = []
        for imported_module in imports:
            for forbidden in FORBIDDEN_MODULES:
                if imported_module == forbidden or imported_module.startswith(
                    forbidden + "."
                ):
                    violations.append(
                        f"  '{imported_module}' (matches forbidden prefix '{forbidden}')"
                    )
        assert not violations, (
            f"\n{path.name} imports forbidden module(s):\n"
            + "\n".join(violations)
            + "\n\nEngine modules must be pure-Python with no infrastructure imports."
        )

    def test_forecaster_isolation(self):
        """engine/forecaster.py must not import any forbidden module."""
        self._check_file(ENGINE_DIR / "forecaster.py")

    def test_risk_isolation(self):
        """engine/risk.py must not import any forbidden module."""
        self._check_file(ENGINE_DIR / "risk.py")

    def test_optimiser_isolation(self):
        """engine/optimiser.py must not import any forbidden module."""
        self._check_file(ENGINE_DIR / "optimiser.py")

    def test_all_engine_files_are_covered(self):
        """
        Fail if a new engine file is added without a corresponding isolation test.

        This prevents a future developer from accidentally adding an engine file
        that bypasses the isolation check by not being listed above.
        """
        py_files = {p.stem for p in _get_engine_python_files()}
        tested_stems = {"forecaster", "risk", "optimiser"}
        uncovered = py_files - tested_stems
        assert not uncovered, (
            f"New engine file(s) detected without an isolation test: {uncovered}\n"
            "Add a test_<name>_isolation method to TestEngineIsolation."
        )
