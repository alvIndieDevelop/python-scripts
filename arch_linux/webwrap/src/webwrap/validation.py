"""Validation and safe identifier helpers for WebWrap."""

from __future__ import annotations

import os
import re
import shutil
import tempfile
import unicodedata
import uuid
from pathlib import Path
from urllib.parse import urlsplit


ID_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SUPPORTED_ICON_SUFFIXES = frozenset({".ico", ".jpeg", ".jpg", ".png", ".svg", ".webp"})


class ValidationError(ValueError):
    """Raised when untrusted WebWrap input is invalid."""


def _has_whitespace_or_control(value: str) -> bool:
    return any(
        character.isspace() or unicodedata.category(character) == "Cc"
        for character in value
    )


def validate_name(name: object) -> str:
    """Validate and normalize a user-facing application name."""
    if not isinstance(name, str):
        raise ValidationError("Application name must be a string.")
    normalized = name.strip()
    if not normalized:
        raise ValidationError("Application name cannot be empty.")
    if any(unicodedata.category(character) == "Cc" for character in normalized):
        raise ValidationError("Application name cannot contain control characters.")
    return normalized


def validate_url(url: object) -> str:
    """Validate an HTTP(S) URL without rewriting it."""
    if not isinstance(url, str) or not url:
        raise ValidationError("URL must be a non-empty string.")
    if _has_whitespace_or_control(url):
        raise ValidationError("URL cannot contain whitespace or control characters.")
    try:
        parsed = urlsplit(url)
        port = parsed.port
    except ValueError as error:
        raise ValidationError("URL contains an invalid host or port.") from error
    if parsed.scheme not in {"http", "https"}:
        raise ValidationError("URL scheme must be http or https.")
    if not parsed.hostname:
        raise ValidationError("URL must include a hostname.")
    if port is not None and not 1 <= port <= 65535:
        raise ValidationError("URL port must be between 1 and 65535.")
    return url


def validate_app_id(app_id: object) -> str:
    """Validate a stable identifier before using it in a path."""
    if not isinstance(app_id, str) or not ID_PATTERN.fullmatch(app_id):
        raise ValidationError("Application ID contains unsafe characters.")
    return app_id


def generate_app_id(name: str) -> str:
    """Generate a filename-safe ID with a short random suffix."""
    normalized = unicodedata.normalize("NFKD", validate_name(name))
    ascii_name = normalized.encode("ascii", "ignore").decode("ascii").lower()
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_name).strip("-") or "app"
    return f"{slug}-{uuid.uuid4().hex[:8]}"


def validate_icon_path(icon_path: object) -> Path:
    """Validate a readable regular image file."""
    if not isinstance(icon_path, (str, os.PathLike)):
        raise ValidationError("Icon path must reference a file.")
    path = Path(icon_path).expanduser()
    if path.suffix.lower() not in SUPPORTED_ICON_SUFFIXES:
        raise ValidationError("Icon format is not supported.")
    try:
        if not path.is_file():
            raise ValidationError("Icon path must reference a regular file.")
        with path.open("rb"):
            pass
    except PermissionError as error:
        raise ValidationError("Icon file is not readable.") from error
    except OSError as error:
        raise ValidationError(f"Cannot read icon file: {error}") from error
    return path


def copy_managed_icon(source: Path, destination_dir: Path, app_id: str) -> Path:
    """Copy a validated icon atomically into WebWrap-managed storage."""
    source = validate_icon_path(source)
    validate_app_id(app_id)
    destination = destination_dir / f"{app_id}{source.suffix.lower()}"
    temporary: Path | None = None
    try:
        destination_dir.mkdir(parents=True, exist_ok=True)
        descriptor, temporary_name = tempfile.mkstemp(dir=destination_dir, prefix=".icon-")
        temporary = Path(temporary_name)
        with os.fdopen(descriptor, "wb") as output, source.open("rb") as input_file:
            shutil.copyfileobj(input_file, output)
            output.flush()
            os.fsync(output.fileno())
        os.replace(temporary, destination)
        return destination
    except OSError as error:
        raise ValidationError(f"Cannot copy icon: {error}") from error
    finally:
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass
