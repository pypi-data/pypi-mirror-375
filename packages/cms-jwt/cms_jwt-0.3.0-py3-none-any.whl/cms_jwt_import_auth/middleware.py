from __future__ import annotations
import re
from typing import Optional

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser

from rest_framework.request import Request as DRFRequest
from edx_rest_framework_extensions.auth.jwt.authentication import JwtAuthentication

class ImportJWTOrSessionMiddleware(MiddlewareMixin):
    """
    Enforce authentication for the course import endpoint in CMS:
      /api/courses/v1/<course_id>/import/
    Accept either:
      - existing logged-in Studio session, OR
      - JWT in Authorization header (JWT or Bearer)
    If neither present/valid -> 401 JSON.

    NOTE:
    - Keep this middleware scoped to just the import route to avoid overhead.
    """

    # Path matcher (strict, trailing slash optional)
    # Example: /api/courses/v1/course-v1:ACME+ONB101+2025_T1/import/
    PATTERN = re.compile(
        r"^/api/courses/v1/[^/]+/import/?$"
    )

    def process_request(self, request):
        path = request.path or ""
        if not self.PATTERN.match(path):
            return None  # ignore all other routes

        # If session-authenticated, allow through
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated:
            return None

        # Try JWT auth (accept JWT or Bearer header schemes)
        auth = JwtAuthentication()
        drf_request = DRFRequest(request)
        try:
            user_auth_tuple: Optional[tuple] = auth.authenticate(drf_request)
        except Exception as e:
            # Invalid token format / signature, return 401
            return JsonResponse({"detail": f"Invalid JWT: {str(e)}"}, status=401)

        if user_auth_tuple:
            request.user, _ = user_auth_tuple
            return None  # authenticated via JWT

        # Neither session nor JWT
        return JsonResponse({"detail": "Authentication required"}, status=401)

