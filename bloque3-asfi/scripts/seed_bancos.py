from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.crypto.key_registry import KeyRegistry
from app.repository.sqlite_repository import AsfiRepository

repo = AsfiRepository()
registry = KeyRegistry()
repo.seed_banks(registry.export_mapping())
print("Catálogo de bancos y llaves sembrado correctamente.")
