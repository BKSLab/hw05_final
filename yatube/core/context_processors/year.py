import datetime as dt
from typing import Any


def year(requests: Any):
    """Добавляет переменную с текущим годом."""
    return {
        'year': dt.datetime.now().year,
    }
