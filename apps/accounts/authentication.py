from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import AccessToken


class CookieJWTAuthentication(JWTAuthentication):
    """쿠키에서 JWT 토큰을 읽어 인증하는 클래스"""

    def authenticate(self, request):
        # 먼저 쿠키에서 토큰 확인
        access_token = request.COOKIES.get('access_token')

        if access_token:
            try:
                validated_token = AccessToken(access_token)
                return self.get_user(validated_token), validated_token
            except TokenError:
                pass

        # 쿠키에 없으면 기본 헤더 인증 시도 (Bearer 토큰)
        return super().authenticate(request)
