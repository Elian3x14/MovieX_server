from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from django.views import View
from rest_framework.response import Response
from django.http import HttpResponseRedirect
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema, OpenApiParameter
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

from ..serializers import (
    RegisterSerializer,
    EmailTokenObtainPairSerializer,
    UserSerializer,
    ChangePasswordSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    )
from ..models import User
from ..utils.send_mail import send_templated_email


@extend_schema(tags=["Auth"])
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        # Truyền request vào context để sử dụng trong serializer
        serializer.save(request=self.request)


@extend_schema(tags=["Auth"])
class ActivateUserView(View):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        parameters=[
            OpenApiParameter(name="uidb64", type=str, location=OpenApiParameter.PATH),
            OpenApiParameter(name="token", type=str, location=OpenApiParameter.PATH),
        ]
    )
    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError, OverflowError):
            return Response({"error": "Liên kết không hợp lệ."}, status=400)

        if default_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            # Redirect đến trang xác thực thành công ở client
            return HttpResponseRedirect(
                f"http://{settings.FRONTEND_URL}/activate-success"
            )
        else:
            return Response({"error": "Token không hợp lệ."}, status=400)


@extend_schema(tags=["Auth"])
class EmailLoginView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer


@extend_schema(tags=["Auth"])
class UserView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


@extend_schema(tags=["Auth"])
class ChangePasswordView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=ChangePasswordSerializer, responses={200: dict, 400: dict})
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data["old_password"]
            new_password = serializer.validated_data["new_password"]

            if not user.check_password(old_password):
                return Response(
                    {"error": "Mật khẩu cũ không đúng."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            user.set_password(new_password)
            user.save()
            return Response(
                {"success": "Mật khẩu đã được thay đổi."}, status=status.HTTP_200_OK
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=["Auth"])
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(request=None, responses={204: None})
    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logged out successfully"}, status=200)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)


@extend_schema(tags=["Auth"])
class PasswordResetRequestView(APIView):
    @extend_schema(
        request=PasswordResetRequestSerializer, responses={200: dict, 404: dict}
    )
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Email không tồn tại."}, status=404)

        token = default_token_generator.make_token(user)

        # Đường dẫn giả định để người dùng reset
        reset_url = f"http://localhost:8000/api/reset-password/?token={token}&email={user.email}"

        # Gửi email template HTML
        send_templated_email(
            subject="Đặt lại mật khẩu",
            to_email=user.email,
            template_name="emails/reset_password_email.html",
                context={
                    "username": user.get_full_name() or user.username,
                    "reset_link": reset_url,
                },
            from_email="noreply@example.com"
        )

        return Response({"detail": "Đã gửi mail xác thực đặt lại mật khẩu."})


@extend_schema(tags=["Auth"])
class PasswordResetConfirmView(APIView):

    @extend_schema(
        request=PasswordResetConfirmSerializer, responses={200: dict, 400: dict}
    )
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]
        email = request.query_params.get("email")

        if not email:
            return Response({"detail": "Thiếu email."}, status=400)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Người dùng không tồn tại."}, status=404)

        if not default_token_generator.check_token(user, token):
            return Response({"detail": "Token không hợp lệ."}, status=400)

        user.set_password(new_password)
        user.save()
        return Response({"detail": "Mật khẩu đã được đặt lại thành công."})
