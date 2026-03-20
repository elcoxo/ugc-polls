from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path
from django.views.generic import TemplateView
from drf_spectacular.views import (SpectacularAPIView, SpectacularRedocView,
                                   SpectacularSwaggerView)
from rest_framework.routers import DefaultRouter

from polls.views import PollSessionViewSet, PollViewSet
from users.views import poll_statistics, register

router = DefaultRouter()
router.register('polls', PollViewSet, basename='polls')
router.register('sessions', PollSessionViewSet, basename='sessions')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='/'), name='logout'),
    path('register/', register, name='register'),
    path('', TemplateView.as_view(template_name='polls/list.html'), name='poll-list'),
    path('polls/<slug:slug>/stats/', poll_statistics, name='poll-stats'),
    path('polls/<slug:slug>/', TemplateView.as_view(template_name='polls/detail.html'), name='poll-detail'),
]
