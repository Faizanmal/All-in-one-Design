from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'sources', views.DataSourceViewSet, basename='data-source')
router.register(r'variables', views.DataVariableViewSet, basename='data-variable')
router.register(r'bindings', views.DataBindingViewSet, basename='data-binding')
router.register(r'collections', views.DataCollectionViewSet, basename='data-collection')
router.register(r'repeating', views.RepeatingElementViewSet, basename='repeating-element')
router.register(r'transforms', views.DataTransformViewSet, basename='data-transform')

urlpatterns = [
    path('', include(router.urls)),
    path('test-connection/', views.TestConnectionView.as_view(), name='test-connection'),
    path('transform-preview/', views.TransformPreviewView.as_view(), name='transform-preview'),
    path('bind-elements/', views.BindElementsView.as_view(), name='bind-elements'),
]
