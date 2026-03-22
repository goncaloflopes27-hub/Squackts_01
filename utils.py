from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from uuid import uuid4
import json
import re
import shutil

from PIL import Image


MONEY_QUANT = Decimal("0.01")


def now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def new_id() -> str:
    return str(uuid4())


def to_cents(value: str | Decimal | int) -> int:
    amount = Decimal(str(value)).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)
    return int((amount * 100).to_integral_value(rounding=ROUND_HALF_UP))


def from_cents(cents: int) -> Decimal:
    return (Decimal(cents) / Decimal(100)).quantize(MONEY_QUANT, rounding=ROUND_HALF_UP)


def format_eur(cents: int) -> str:
    return f"{from_cents(cents):.2f} EUR"


def validate_email(email: str) -> bool:
    if not email:
        return True
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))


def validate_nif(nif: str) -> bool:
    if not nif:
        return True
    return bool(re.fullmatch(r"\d{9}", nif))


def sanitize_filename(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]", "_", name)


def copy_image_with_thumbnail(source: Path, dest_dir: Path) -> Path:
    dest_dir.mkdir(parents=True, exist_ok=True)
    unique_name = f"{uuid4().hex}_{sanitize_filename(source.name)}"
    dest = dest_dir / unique_name
    with Image.open(source) as image:
        rgba = image.convert("RGBA")
        rgba.thumbnail((512, 512))
        rgba.save(dest)
    return dest


def write_json_text(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True)


def safe_copy_file(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
