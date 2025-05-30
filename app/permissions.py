from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """
    Cho phép mọi người dùng GET, HEAD, OPTIONS.
    Nhưng chỉ admin mới được POST, PUT, DELETE.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsAuthorOrAdmin(BasePermission):
    """
    - GET: Ai cũng được
    - POST/PUT/DELETE: Chỉ người đăng nhập
    - PUT/DELETE: Chỉ author hoặc admin
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.author == request.user or request.user.is_staff
