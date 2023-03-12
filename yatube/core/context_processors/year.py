import datetime as dt

from django.http import HttpRequest


def year(request: HttpRequest) -> dict[str, int]:
    """Добавляет переменную с текущим годом.

     Args:
        request: объект, содержащий метаданные о запросе.

    Returns:
        Возвращает словарь, в котором в качестве значения
        передается текущий год.
    """
    del request
    return {
        'year': dt.datetime.now().year,
    }
