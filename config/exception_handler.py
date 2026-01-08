from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError, AuthenticationFailed, NotAuthenticated, PermissionDenied, NotFound, MethodNotAllowed


def custom_exception_handler(exc, context):
    """
    DRF 기본 예외 메시지를 한국어로 변환하는 커스텀 예외 핸들러
    """
    # DRF의 기본 예외 핸들러 호출
    response = exception_handler(exc, context)

    if response is not None:
        # 기본 에러 메시지 한국어 변환 매핑
        error_messages = {
            'This field is required.': '필수 항목입니다',
            'This field may not be blank.': '빈 값은 허용되지 않습니다',
            'This field may not be null.': 'null 값은 허용되지 않습니다',
            'Invalid email address.': '올바른 이메일 주소를 입력해주세요',
            'Enter a valid email address.': '올바른 이메일 주소를 입력해주세요',
            'Authentication credentials were not provided.': '인증 정보가 제공되지 않았습니다',
            'Invalid token.': '유효하지 않은 토큰입니다',
            'Given token not valid for any token type': '유효하지 않은 토큰입니다',
            'Token is invalid or expired': '토큰이 만료되었거나 유효하지 않습니다',
            'User not found': '사용자를 찾을 수 없습니다',
            'No active account found with the given credentials': '해당 계정을 찾을 수 없습니다',
            'Method not allowed.': '허용되지 않은 메서드입니다',
            'Not found.': '찾을 수 없습니다',
            'You do not have permission to perform this action.': '이 작업을 수행할 권한이 없습니다',
            'A valid integer is required.': '올바른 정수를 입력해주세요',
            'A valid number is required.': '올바른 숫자를 입력해주세요',
            'Datetime has wrong format.': '날짜 형식이 올바르지 않습니다',
            'Date has wrong format.': '날짜 형식이 올바르지 않습니다',
            'Time has wrong format.': '시간 형식이 올바르지 않습니다',
            'This password is too short.': '비밀번호가 너무 짧습니다',
            'This password is too common.': '비밀번호가 너무 일반적입니다',
            'This password is entirely numeric.': '비밀번호는 숫자만으로 구성될 수 없습니다',
            'The password is too similar to the': '비밀번호가 다른 정보와 너무 유사합니다',
        }

        def translate_errors(data):
            """재귀적으로 에러 메시지를 번역"""
            if isinstance(data, dict):
                return {key: translate_errors(value) for key, value in data.items()}
            elif isinstance(data, list):
                return [translate_errors(item) for item in data]
            elif isinstance(data, str):
                # 정확히 일치하는 메시지 번역
                if data in error_messages:
                    return error_messages[data]
                # 부분 일치하는 메시지 번역 (예: "The password is too similar to the username")
                for eng, kor in error_messages.items():
                    if eng in data:
                        return data.replace(eng, kor)
                return data
            return data

        response.data = translate_errors(response.data)

    return response
