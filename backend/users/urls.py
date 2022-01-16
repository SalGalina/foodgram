from django.urls import include, path

from .views import SubscribeView, SubscribeListView

app_name = 'users'


urlpatterns = [
    path('users/<int:id>/subscribe/', SubscribeView.as_view(),
         name='subscribe'),
    path('users/subscriptions/', SubscribeListView.as_view(),
         name='subscription'),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]
