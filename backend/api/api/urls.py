from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path(r'^admin/', admin.site.urls),
    path(r'^auth/', include('djoser.urls')),
    path(r'^auth/', include('djoser.urls.jwt')),
    path(r'^api/', include('recipes.urls')),
]
