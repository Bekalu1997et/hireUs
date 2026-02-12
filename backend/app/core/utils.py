"""
Utility functions for the application.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
import uuid
import secrets


def generate_uuid() -> str:
    """
    Generate a new UUID string.
    """
    return str(uuid.uuid4())


def generate_random_string(length: int = 32) -> str:
    """
    Generate a secure random string.
    Useful for generating tokens, API keys, etc.
    """
    return secrets.token_urlsafe(length)


def datetime_utcnow() -> datetime:
    """
    Get current UTC datetime.
    Wrapper for easier testing/mocking.
    """
    return datetime.utcnow()


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object to string.
    """
    return dt.strftime(format_str)


def parse_datetime(dt_str: str, format_str: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Parse a datetime string to datetime object.
    """
    return datetime.strptime(dt_str, format_str)


def is_valid_uuid(val: str) -> bool:
    """
    Check if a string is a valid UUID.
    """
    try:
        uuid.UUID(val)
        return True
    except ValueError:
        return False


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length with a suffix.
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_phone_number(phone: str) -> str:
    """
    Format phone number consistently.
    Removes spaces and special characters, adds country code if missing.
    """
    # Remove all non-digit characters
    digits = ''.join(filter(str.isdigit, phone))
    
    # Add country code if missing (assuming US)
    if len(digits) == 10:
        digits = '1' + digits
    
    return digits


def sanitize_html(html: str) -> str:
    """
    Basic HTML sanitization.
    In production, use a library like bleach.
    """
    # Simple replacement for common dangerous tags
    dangerous_tags = ['<script>', '</script>', '<iframe>', '</iframe>']
    for tag in dangerous_tags:
        html = html.replace(tag, '')
    return html


def paginate_results(
    items: List[Any],
    page: int,
    page_size: int
) -> Dict[str, Any]:
    """
    Paginate a list of items.
    Returns a dictionary with pagination info and items.
    """
    total = len(items)
    start = (page - 1) * page_size
    end = start + page_size
    
    return {
        "items": items[start:end],
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "has_next": end < total,
        "has_prev": start > 0
    }


class Timer:
    """
    Context manager for timing code execution.
    """
    def __init__(self):
        self.start_time = None
        self.end_time = None
    
    def __enter__(self):
        self.start_time = datetime_utcnow()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.end_time = datetime_utcnow()
    
    @property
    def elapsed_seconds(self) -> float:
        """Get elapsed time in seconds."""
        if self.start_time is None or self.end_time is None:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()


def dict_to_camel_case(snake_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert a snake_case dictionary to camelCase.
    """
    camel_dict = {}
    for key, value in snake_dict.items():
        new_key = ''.join(
            word.capitalize() if i > 0 else word
            for i, word in enumerate(key.split('_'))
        )
        camel_dict[new_key] = value
    return camel_dict

