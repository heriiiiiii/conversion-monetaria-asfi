from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import json

from app.crypto.key_registry import KeyRegistry

registry = KeyRegistry()
print(json.dumps(registry.export_mapping(), indent=2, ensure_ascii=False))
