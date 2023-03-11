from django.conf import settings
from django.core.paginator import Page, Paginator


def paginate(
    request,
    posts,
    post_per_one_page=settings.OBJECTS_PER_PAGE,
) -> Page:
    return Paginator(posts, post_per_one_page).get_page(
        request.GET.get('page'),
    )
