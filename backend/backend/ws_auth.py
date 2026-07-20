"""
JWT authentication middleware for Django Channels WebSockets.

Accepts `?token=<jwt>` on the WebSocket URL so the Next.js client can
authenticate without relying on session cookies.
"""
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.middleware import BaseMiddleware
from django.contrib.auth.models import AnonymousUser
from rest_framework_simplejwt.tokens import AccessToken


@database_sync_to_async
def _user_from_token(token: str):
    from django.contrib.auth import get_user_model

    User = get_user_model()
    try:
        access = AccessToken(token)
        user_id = access.get('user_id')
        if not user_id:
            return AnonymousUser()
        return User.objects.get(id=user_id)
    except Exception:
        return AnonymousUser()


class JwtAuthMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive, send):
        query_string = scope.get('query_string', b'').decode()
        params = parse_qs(query_string)
        token_list = params.get('token') or params.get('access_token') or []
        token = token_list[0] if token_list else None

        if token:
            scope['user'] = await _user_from_token(token)
        elif scope.get('user') is None:
            scope['user'] = AnonymousUser()

        return await super().__call__(scope, receive, send)


def JwtAuthMiddlewareStack(inner):
    """
    Session auth first, then JWT query-param override.
    This lets `?token=` authenticate SPA clients without cookies.
    """
    from channels.auth import AuthMiddlewareStack

    return AuthMiddlewareStack(JwtAuthMiddleware(inner))
