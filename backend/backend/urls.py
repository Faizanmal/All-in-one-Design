"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from backend.health import health_check, readiness_check, liveness_check

# Customize admin
admin.site.site_header = "AI Design Tool Administration"
admin.site.site_title = "AI Design Tool Admin"
admin.site.index_title = "Welcome to AI Design Tool Admin Portal"

urlpatterns = [
    # Health checks (no auth required)
    path('health/', health_check, name='health-check'),
    path('health/ready/', readiness_check, name='readiness-check'),
    path('health/live/', liveness_check, name='liveness-check'),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # JWT Authentication
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # API v1
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/auth/', include('authentication.urls')),  # OAuth endpoints
    path('api/v1/projects/', include('projects.urls')),
    path('api/v1/ai/', include('ai_services.urls')),
    path('api/v1/assets/', include('assets.urls')),
    path('api/v1/analytics/', include('analytics.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
    path('api/v1/subscriptions/', include('subscriptions.urls')),
    path('api/v1/teams/', include('teams.urls')),
    path('api/v1/integrations/', include('integrations.urls')),
    
    # New Feature APIs
    path('api/v1/3d-studio/', include('studio3d.urls')),           # Feature 1: 3D Design & Prototyping
    path('api/v1/animations/', include('animations.urls')),         # Feature 2: Animation & Motion Design
    path('api/v1/design-systems/', include('design_systems.urls')), # Feature 3: Design System Builder
    path('api/v1/optimization/', include('optimization.urls')),     # Feature 4: AI Design Optimization
    path('api/v1/whitelabel/', include('whitelabel.urls')),         # Feature 5: White-Label & Agency
    path('api/v1/advanced-integrations/', include('advanced_integrations.urls')), # Feature 6: Integrations
    path('api/v1/font-assets/', include('font_assets.urls')),       # Feature 7: Font & Asset Hub
    path('api/v1/plugins/', include('plugins.urls')),               # Feature 10: Plugin Platform
    
    # Phase 2 Feature APIs
    path('api/v1/auto-layout/', include('auto_layout.urls')),       # Advanced Auto-Layout System
    path('api/v1/variants/', include('component_variants.urls')),   # Component Variants & Properties
    path('api/v1/branches/', include('design_branches.urls')),      # Design Branching & Feature Branches
    path('api/v1/timeline/', include('animation_timeline.urls')),   # Advanced Animation Timeline
    path('api/v1/qa/', include('design_qa.urls')),                  # Design QA & Linting
    path('api/v1/presentation/', include('presentation_mode.urls')), # Presentation Mode & Dev Mode
    path('api/v1/whiteboard/', include('whiteboard.urls')),         # FigJam/Whiteboard Feature
    path('api/v1/mobile/', include('mobile_api.urls')),             # Mobile App API
    
    # Phase 3 Feature APIs (Features 9-17)
    path('api/v1/vector/', include('vector_editing.urls')),         # Feature 9: Advanced Vector Editing
    path('api/v1/smart-tools/', include('smart_tools.urls')),       # Feature 10: Smart Selection & Magic Tools
    path('api/v1/interactive/', include('interactive_components.urls')), # Feature 11: Interactive Components
    path('api/v1/media/', include('media_assets.urls')),            # Feature 12: Video & GIF Support
    path('api/v1/data-binding/', include('data_binding.urls')),     # Feature 13: Data & Variable Binding
    path('api/v1/design-analytics/', include('design_analytics.urls')), # Feature 14: Design System Analytics
    path('api/v1/comments/', include('commenting.urls')),           # Feature 15: Enhanced Commenting & Review
    path('api/v1/pdf/', include('pdf_annotation.urls')),            # Feature 16: PDF Annotation & Markup Import
    path('api/v1/accessibility/', include('accessibility_testing.urls')), # Feature 17: Enhanced Accessibility Testing
    
    # Phase 4 Feature APIs (Features 18-25)
    path('api/v1/code-export/', include('code_export.urls')),       # Feature 18: Code Export & Developer Handoff
    path('api/v1/slack-teams/', include('slack_teams_integration.urls')), # Feature 19: Slack/Teams Integration
    path('api/v1/offline/', include('offline_pwa.urls')),           # Feature 20: Offline Mode & PWA
    path('api/v1/asset-management/', include('asset_management.urls')), # Feature 21: Enhanced Asset Management
    path('api/v1/marketplace/', include('template_marketplace.urls')), # Feature 22: Template Marketplace
    path('api/v1/time-tracking/', include('time_tracking.urls')),   # Feature 23: Time Tracking & Project Management
    path('api/v1/pdf-export/', include('pdf_export.urls')),         # Feature 24: Multi-page PDF Export with Bleed
    path('api/v1/permissions/', include('granular_permissions.urls')), # Feature 25: Granular Permissions & Roles
    
    # High-Tier Monetization Feature APIs
    path('api/v1/social-scheduler/', include('social_scheduler.urls')), # Feature 26: Social Scheduler
    path('api/v1/web-publishing/', include('web_publishing.urls')),     # Feature 27: Web Publishing
    path('api/v1/brand-kit/', include('brand_kit.urls')),               # Feature 28: Brand Kit
    
    # Legacy API (backward compatibility)
    path('api/auth/', include('accounts.urls')),
    path('api/projects/', include('projects.urls')),
    path('api/ai/', include('ai_services.urls')),
    path('api/assets/', include('assets.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
