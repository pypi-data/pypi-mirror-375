import datetime


def compact_mapping(obj):
    """Compact a dict/mapping by removing all None values."""

    return {k: v for k, v in obj.items() if v is not None}


def to_iso8601(dt):
    """Convert a datetime object to an ISO 8601 string."""

    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def from_iso8601(s):
    """Convert an ISO 8601 string to a datetime object."""

    return datetime.datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")
