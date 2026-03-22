from django.conf import settings
from django.db import DatabaseError, connections
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response

from .serializers import HealthSerializer


def _db_check() -> str:
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1")
    except DatabaseError:
        return "error"

    return "ok"


@extend_schema(
    responses=HealthSerializer,
    examples=[
        OpenApiExample(
            "Health response",
            value={
                "status": "ok",
                "service": settings.SERVICE_NAME,
                "version": settings.SERVICE_VERSION,
                "commit": settings.SERVICE_COMMIT,
                "time": "2024-04-06T12:30:00+0000",
                "checks": {"app": "ok", "db": "ok"},
            },
            response_only=True,
        )
    ],
)
@api_view(["GET"])
@authentication_classes([])
@permission_classes([AllowAny])
def health(request: Request) -> Response:
    payload = {
        "status": "ok",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "commit": settings.SERVICE_COMMIT,
        "time": timezone.localtime(),
        "checks": {"app": "ok", "db": _db_check()},
    }
    serializer = HealthSerializer(payload)

    return Response(serializer.data)
