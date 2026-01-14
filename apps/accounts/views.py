from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.conf import settings
from drf_spectacular.utils import extend_schema, OpenApiExample
from .serializers import UserRegistrationSerializer, UserSerializer, LoginSerializer


def set_token_cookies(response, refresh_token, access_token):
    """httpOnly 쿠키로 토큰 설정"""
    # Access Token 쿠키 (1시간)
    response.set_cookie(
        key='access_token',
        value=str(access_token),
        max_age=3600,  # 1시간
        httponly=True,
        secure=not settings.DEBUG,  # HTTPS에서만 (production)
        samesite='Lax',
        path='/',
    )
    # Refresh Token 쿠키 (7일)
    response.set_cookie(
        key='refresh_token',
        value=str(refresh_token),
        max_age=7 * 24 * 3600,  # 7일
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Lax',
        path='/',
    )
    return response


class RegisterView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Auth'],
        summary='회원가입',
        description='새로운 사용자를 등록합니다.',
        auth=[],  # 인증 불필요
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        #jwt 토큰 설정
        refresh = RefreshToken.for_user(user)

        response = Response({
            'user': UserSerializer(user).data,
            'message': '회원가입이 완료되었습니다.'
        }, status=status.HTTP_201_CREATED)

        # httpOnly 쿠키로 토큰 설정
        return set_token_cookies(response, refresh, refresh.access_token)


class LoginView(generics.GenericAPIView): #로그인뷰
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Auth'],
        summary='로그인',
        description='이메일과 비밀번호로 로그인하고 JWT 토큰을 발급받습니다.',
        auth=[],  # 인증 불필요
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        user = authenticate(request, username=email, password=password)

        if user is None:
            return Response({
                'detail': '잘못된 이메일 또는 비밀번호입니다'
            }, status=status.HTTP_401_UNAUTHORIZED)

        if not user.is_active:
            return Response({
                'detail': '비활성화된 계정입니다'
            }, status=status.HTTP_403_FORBIDDEN)

        #JWT 토큰
        refresh = RefreshToken.for_user(user)

        response = Response({
            'user': UserSerializer(user).data,
            'message': '로그인 성공'
        }, status=status.HTTP_200_OK)

        # httpOnly 쿠키로 토큰 설정
        return set_token_cookies(response, refresh, refresh.access_token)


class LogoutView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    @extend_schema(
        tags=['Auth'],
        summary='로그아웃',
        description='쿠키의 토큰을 삭제합니다.',
    )
    def post(self, request, *args, **kwargs):
        response = Response({'message': '로그아웃 되었습니다.'}, status=status.HTTP_200_OK)
        response.delete_cookie('access_token', path='/')
        response.delete_cookie('refresh_token', path='/')
        return response


class UserProfileView(generics.RetrieveUpdateAPIView):

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user
