from rest_framework.permissions import SAFE_METHODS, BasePermission
from rest_framework.request import Request


class ReadOnlyUnlessFlagDisabled(BasePermission):
    """
    Blocks mutating methods when API_READONLY is enabled.
    """

    def has_permission(self, request: Request, view: object) -> bool:
        if request.method in SAFE_METHODS or request.method == "TRACE":
            return True

        if hasattr(view, "http_method_names") and request.method.lower() not in getattr(
            view, "http_method_names", []
        ):
            return True

        from django.conf import settings

        return not getattr(settings, "API_READONLY", True)
