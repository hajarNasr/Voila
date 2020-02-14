from django.contrib import admin
from django.urls import path, include
from django.conf.urls import handler404
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.base_view, name="base_view"),
    path('projects/', include('projects.urls')),
    path('blog/', include('blog.urls')),
]

handler404 = views.page_not_found
