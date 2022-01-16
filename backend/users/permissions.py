from django.contrib.auth import get_user_model
from rest_framework import permissions

User = get_user_model()


class IsAuthorOrAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            (request.user and request.user.is_authenticated)
            or request.method in permissions.SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        return bool(
            (request.user
             and request.user.is_authenticated
             and obj.author == request.user
             )
            or (request.user
                and request.user.is_authenticated
                and request.user.is_staff
                )
            or request.method in permissions.SAFE_METHODS
        )
