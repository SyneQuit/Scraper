"""Evidence už viděných položek, aby každý event přišel na Discord jen jednou.

Místo porovnání s posledním během si pamatujeme všechna ID, která jsme kdy viděli.
Když event dočasně zmizí (výpadek, stránkování) a pak se vrátí, znovu se neohlásí.
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path


def load(path: Path) -> dict[str, str] | None:
    """Vrátí {id: kdy_poprvé_viděno}, nebo None při prvním běhu."""
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save(path: Path, seen: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(seen, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(tmp, path)  # atomický zápis, aby se soubor nepoškodil při pádu


def mark(seen: dict[str, str], items: list[dict]) -> dict[str, str]:
    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    return {**seen, **{i["id"]: seen.get(i["id"], now) for i in items}}
