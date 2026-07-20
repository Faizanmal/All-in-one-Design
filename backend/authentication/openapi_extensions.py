"""
OpenAPI Authentication Extensions for drf-spectacular

Provides OpenAPI schema extensions for custom authentication classes.
"""
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class APIKeyAuthenticationScheme(OpenApiAuthenticationExtension):
    """
    OpenAPI authentication extension for APIKeyAuthentication.

    Defines the security scheme for API key authentication.
    """
    target_class = 'authentication.api_key_auth.APIKeyAuthentication'
    name = 'ApiKeyAuth'

    def get_security_definition(self, auto_schema):
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'X-API-Key',
            'description': (
                'API Key authentication. Send your API key in the X-API-Key header '
                'or Authorization header as "Api-Key <key>".'
            ),
        }
