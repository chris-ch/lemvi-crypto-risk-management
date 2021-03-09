from datetime import datetime, date


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError('Type %s not serializable' % type(obj))


def parse_iso8601(date_str: str) -> datetime:
    return datetime.fromisoformat(date_str)
