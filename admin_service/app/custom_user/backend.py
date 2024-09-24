import http
from enum import Enum

import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.backends import BaseBackend

from .cache.token_cache import cache_token, get_cached_token

User = get_user_model()


class Roles(Enum):
    ADMIN = "ADMIN"
    SUBSCRIBER = "SUBSCRIBER"


class CustomBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        # Check if token is cached
        cached_token = get_cached_token(username)
        # TODO: We should also extract token from request header and check it to be the same as cached_token
        if cached_token:
            # If token exists in cache, decode and use it
            try:
                data = jwt.decode(
                    cached_token,
                    settings.JWT_SECRET_KEY,
                    audience="fastapi-users:auth",
                    algorithms=[settings.JWT_ALGORITHM]
                )
            except jwt.ExpiredSignatureError:
                pass
            except jwt.InvalidTokenError:
                return None

            return self.get_or_create_user(data)

        url = settings.AUTH_API_LOGIN_URL
        payload = {'username': username, 'password': password}
        response = requests.post(url, data=payload)

        if response.status_code != http.HTTPStatus.OK:
            return None

        try:
            res = response.json()
            data = jwt.decode(
                res['access_token'],
                settings.JWT_SECRET_KEY,
                audience="fastapi-users:auth",
                algorithms=[settings.JWT_ALGORITHM]
            )
            cache_token(username, res['access_token'])
        except Exception:
            return None

        return self.get_or_create_user(data)

    def get_or_create_user(self, data):
        try:
            user, created = User.objects.get_or_create(id=data['sub'])
            user.email = data.get('email')
            user.is_admin = data.get('role') == 'admin'
            user.is_active = data.get('is_active', True)
            user.save()
            return user
        except Exception:
            # TODO: Log the error
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
