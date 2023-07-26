from rest_framework import permissions


class IsAdminAuthor(permissions.BasePermission):
    """Доступ для автора и администратора."""
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_superuser
                or request.user.is_admin
                or obj.author == request.user)
