"""Input validation helpers."""

from datetime import datetime
from typing import Iterable, Optional

from task_manager.config import (
    DATE_FORMAT,
    SORT_COLUMN_MAP,
    VALID_EXPORT_FORMATS,
    VALID_ORDER,
    VALID_PRIORITIES,
    VALID_STATUSES,
)


class ValidationError(ValueError):
    """Raised when user input fails validation."""


def validate_priority(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if value not in VALID_PRIORITIES:
        raise ValidationError(
            f"Priority must be one of {VALID_PRIORITIES}, got '{value}'"
        )
    return value


def validate_status(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    if value not in VALID_STATUSES:
        raise ValidationError(
            f"Status must be one of {VALID_STATUSES}, got '{value}'"
        )
    return value


def validate_due_date(value: Optional[str]) -> Optional[str]:
    if value is None or value == "":
        return None
    try:
        datetime.strptime(value, DATE_FORMAT)
    except ValueError:
        raise ValidationError(
            f"Due date must be in {DATE_FORMAT} format, got '{value}'"
        )
    return value


def validate_sort_key(value: str) -> str:
    if value not in SORT_COLUMN_MAP:
        raise ValidationError(
            f"Sort key must be one of {tuple(SORT_COLUMN_MAP.keys())}, got '{value}'"
        )
    return SORT_COLUMN_MAP[value]


def validate_order(value: str) -> str:
    lowered = value.lower()
    if lowered not in VALID_ORDER:
        raise ValidationError(
            f"Order must be one of {VALID_ORDER}, got '{value}'"
        )
    return lowered.upper()


def validate_export_format(value: str) -> str:
    lowered = value.lower()
    if lowered not in VALID_EXPORT_FORMATS:
        raise ValidationError(
            f"Export format must be one of {VALID_EXPORT_FORMATS}, got '{value}'"
        )
    return lowered


def validate_title(value: str) -> str:
    if value is None:
        raise ValidationError("Title is required")
    title = value.strip()
    if not title:
        raise ValidationError("Title cannot be empty or whitespace")
    if len(title) > 500:
        raise ValidationError("Title must be 500 characters or fewer")
    return title


def validate_task_ids(values: Iterable[int]) -> list:
    ids = list(values)
    if not ids:
        raise ValidationError("At least one task ID is required")
    cleaned = []
    for raw in ids:
        try:
            task_id = int(raw)
        except (TypeError, ValueError):
            raise ValidationError(f"Task ID must be an integer, got '{raw}'")
        if task_id <= 0:
            raise ValidationError(f"Task ID must be positive, got {task_id}")
        cleaned.append(task_id)
    return cleaned
