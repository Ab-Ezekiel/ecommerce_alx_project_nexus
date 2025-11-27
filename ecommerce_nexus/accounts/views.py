# ecommerce_nexus/accounts/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdmin
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .serializers import RegisterSerializer

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    """
    POST /api/auth/register/  -> creates a new user
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    """
    POST /api/auth/logout/
    Expects {"refresh": "<refresh_token>"}
    Blacklists the refresh token.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)
