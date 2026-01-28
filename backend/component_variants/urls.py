"""
URL configuration for component_variants app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sets', views.ComponentSetViewSet, basename='component-set')
router.register(r'properties', views.ComponentPropertyViewSet, basename='component-property')
router.register(r'options', views.PropertyOptionViewSet, basename='property-option')
router.register(r'variants', views.ComponentVariantViewSet, basename='component-variant')
router.register(r'overrides', views.VariantOverrideViewSet, basename='variant-override')
router.register(r'instances', views.ComponentInstanceViewSet, basename='component-instance')
router.register(r'states', views.InteractiveStateViewSet, basename='interactive-state')
router.register(r'slots', views.ComponentSlotViewSet, basename='component-slot')

app_name = 'component_variants'

urlpatterns = [
    path('', include(router.urls)),
]
