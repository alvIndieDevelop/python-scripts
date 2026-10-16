"""Serializable WebWrap application model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from webwrap.validation import ValidationError, validate_app_id, validate_name, validate_url


@dataclass(frozen=True)
class WebApp:
    """Describe one managed web application."""

    id: str
    name: str
    url: str
    icon: str | None = None
    browser: str = "chromium"
    isolated_profile: bool = False

    def __post_init__(self) -> None:
        """Validate every field at the model boundary."""
        object.__setattr__(self, "id", validate_app_id(self.id))
        object.__setattr__(self, "name", validate_name(self.name))
        object.__setattr__(self, "url", validate_url(self.url))
        if self.icon is not None and not isinstance(self.icon, str):
            raise ValidationError("Icon must be a path string or null.")
        if self.browser != "chromium":
            raise ValidationError("Only the chromium browser is supported.")
        if type(self.isolated_profile) is not bool:
            raise ValidationError("isolated_profile must be a boolean.")

    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-compatible representation."""
        return {
            "id": self.id,
            "name": self.name,
            "url": self.url,
            "icon": self.icon,
            "browser": self.browser,
            "isolated_profile": self.isolated_profile,
        }

    @classmethod
    def from_dict(cls, record: object) -> WebApp:
        """Create a WebApp from a strictly checked JSON record."""
        if not isinstance(record, dict):
            raise ValidationError("Application record must be an object.")
        allowed = {"id", "name", "url", "icon", "browser", "isolated_profile"}
        required = {"id", "name", "url"}
        if not required.issubset(record) or not set(record).issubset(allowed):
            raise ValidationError("Application record has an invalid schema.")
        return cls(
            id=record["id"],
            name=record["name"],
            url=record["url"],
            icon=record.get("icon"),
            browser=record.get("browser", "chromium"),
            isolated_profile=record.get("isolated_profile", False),
        )
