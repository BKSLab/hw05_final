from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from about.apps import AboutConfig
from posts.apps import PostsConfig
from users.apps import UsersConfig

urlpatterns = [
    path('', include('posts.urls', PostsConfig.name)),
    path('about/', include('about.urls', AboutConfig.name)),
    path('admin/', admin.site.urls),
    path('auth/', include('users.urls', UsersConfig.name)),
    path('auth/', include('django.contrib.auth.urls')),
]

handler404 = 'core.views.page_not_found'
handler403 = settings.CSRF_FAILURE_VIEW

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT,
    )
