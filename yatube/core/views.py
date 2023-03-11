from http import HTTPStatus
from typing import Any

from django.http import HttpResponse
from django.shortcuts import render


def page_not_found(request: Any, exception: Any) -> HttpResponse:
    del exception
    return render(
        request,
        'core/404.html',
        {'path': request.path},
        status=HTTPStatus.NOT_FOUND,
    )


def csrf_failure(request: Any, reason: str = '') -> HttpResponse:
    del reason
    return render(
        request,
        'core/403csrf.html',
    )
