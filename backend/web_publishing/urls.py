from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PublishedSiteViewSet

router = DefaultRouter()
router.register(r'sites', PublishedSiteViewSet, basename='published-site')

urlpatterns = [
    path('', include(router.urls)),
]
