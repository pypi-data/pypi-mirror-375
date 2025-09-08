from urllib.parse import urljoin

from django.conf import settings
from drf_spectacular.utils import extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView

from pulpcore.app.apps import pulp_plugin_configs, get_plugin_config


class FeaturesView(APIView):
    """
    Returns features of the smart_proxy
    """

    @extend_schema(
        summary="Inspect features",
        operation_id="features_read",
    )
    def get(self, request):
        data = ["pulpcore"]
        return Response(data)


class FeaturesV2View(APIView):
    """
    Returns features of the smart_proxy in v2 format
    """

    @extend_schema(
        summary="Inspect features",
        operation_id="featuresv2_read",
    )
    def get(self, request):
        # there is no global setting for the API url
        # not adding /pulp/api/v3 here as Katello does so on its own
        pulp_url = settings.SMART_PROXY_PULP_URL or request.build_absolute_uri("/")
        # CONTENT_ORIGIN can be None, guess based on the API url then
        content_origin = settings.CONTENT_ORIGIN or pulp_url
        capabilities = [app.label for app in pulp_plugin_configs()]
        data = {
            "pulpcore": {
                "http_enabled": False,
                "https_enabled": True,
                "settings": {
                    "pulp_url": pulp_url,
                    "mirror": settings.SMART_PROXY_MIRROR,
                    "content_app_url": urljoin(content_origin, settings.CONTENT_PATH_PREFIX),
                    "username": settings.SMART_PROXY_AUTH_USERNAME,
                    "password": settings.SMART_PROXY_AUTH_PASSWORD,
                    "client_authentication": settings.SMART_PROXY_AUTH_METHODS,
                },
                "state": "running",
                "capabilities": capabilities,
            }
        }

        if settings.SMART_PROXY_RHSM_URL:
            data["pulpcore"]["settings"]["rhsm_url"] = settings.SMART_PROXY_RHSM_URL

        return Response(data)


class VersionView(APIView):
    """
    Returns version of the smart_proxy plugin
    """

    @extend_schema(
        summary="Inspect version",
        operation_id="version_read",
    )
    def get(self, request):
        data = {
            "version": get_plugin_config("core").version,
            "modules": {
                "pulpcore": get_plugin_config("smart_proxy").version,
            },
        }
        return Response(data)
