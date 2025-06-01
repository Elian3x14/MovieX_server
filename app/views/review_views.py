from drf_spectacular.utils import extend_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from ..permissions import IsAuthorOrAdmin
from ..serializers import ReviewSerializer
from ..models import  Review

@extend_schema(tags=["Reviews"])
class ReviewViewSet(viewsets.ModelViewSet):
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsAuthorOrAdmin,
    ]  # Ai cũng xem được, nhưng chỉ người tạo hoặc admin mới sửa/xóa được

    def perform_create(self, serializer):
        # Tự động gán author là user đang đăng nhập
        serializer.save(author=self.request.user)
