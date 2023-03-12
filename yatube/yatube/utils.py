from django.conf import settings
from django.core.paginator import Page, Paginator
from django.http import HttpRequest


def paginate(
    request: HttpRequest,
    posts,
    post_per_one_page: int = settings.OBJECTS_PER_PAGE,
) -> Page:
    return Paginator(posts, post_per_one_page).get_page(
        request.GET.get('page'),
    )
