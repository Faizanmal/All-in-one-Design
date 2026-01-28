from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TemplateCategoryViewSet, MarketplaceTemplateViewSet,
    TemplateReviewViewSet, CreatorProfileViewSet,
    TemplateCollectionViewSet, FavoriteTemplatesView, PurchasedTemplatesView
)

router = DefaultRouter()
router.register(r'categories', TemplateCategoryViewSet, basename='template-category')
router.register(r'templates', MarketplaceTemplateViewSet, basename='marketplace-template')
router.register(r'reviews', TemplateReviewViewSet, basename='template-review')
router.register(r'creators', CreatorProfileViewSet, basename='creator-profile')
router.register(r'collections', TemplateCollectionViewSet, basename='template-collection')

urlpatterns = [
    path('', include(router.urls)),
    path('favorites/', FavoriteTemplatesView.as_view(), name='favorite-templates'),
    path('purchased/', PurchasedTemplatesView.as_view(), name='purchased-templates'),
]
