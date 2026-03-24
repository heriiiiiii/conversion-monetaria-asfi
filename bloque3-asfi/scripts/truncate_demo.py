from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.repository.sqlite_repository import AsfiRepository

repo = AsfiRepository()
repo.truncate_all()
print(f"Base demo truncada: {repo.db_path}")
