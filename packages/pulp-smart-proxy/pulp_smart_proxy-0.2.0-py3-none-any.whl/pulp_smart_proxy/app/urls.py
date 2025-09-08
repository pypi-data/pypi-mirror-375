from django.conf import settings
from django.urls import path, include

from .views import FeaturesView, FeaturesV2View, VersionView

if settings.DOMAIN_ENABLED:
    V3_API_ROOT = settings.V3_DOMAIN_API_ROOT_NO_FRONT_SLASH
else:
    V3_API_ROOT = settings.V3_API_ROOT_NO_FRONT_SLASH

smart_proxy_patterns = [
    path("features", FeaturesView.as_view()),
    path("v2/features", FeaturesV2View.as_view()),
    path("version", VersionView.as_view()),
]

urlpatterns = [
    path(f"{V3_API_ROOT}smart_proxy/", include(smart_proxy_patterns)),
]
