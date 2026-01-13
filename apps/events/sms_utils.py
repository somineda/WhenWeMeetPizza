"""
Solapi SMS 발송 유틸리티
"""
import hashlib
import hmac
import time
import uuid
import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def get_solapi_headers():
    """
    Solapi API 인증 헤더 생성
    """
    api_key = getattr(settings, 'SOLAPI_API_KEY', '')
    api_secret = getattr(settings, 'SOLAPI_API_SECRET', '')

    if not api_key or not api_secret:
        return None

    date = time.strftime('%Y-%m-%dT%H:%M:%S%z')
    salt = str(uuid.uuid4())

    signature = hmac.new(
        api_secret.encode('utf-8'),
        (date + salt).encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

    return {
        'Authorization': f'HMAC-SHA256 apiKey={api_key}, date={date}, salt={salt}, signature={signature}',
        'Content-Type': 'application/json'
    }


def normalize_phone_number(phone):
    """
    전화번호 정규화 (하이픈 제거)

    Args:
        phone: 전화번호 (010-1234-5678 또는 01012345678)

    Returns:
        str: 정규화된 전화번호 (01012345678)
    """
    if not phone:
        return None

    # 하이픈, 공백 제거
    phone = phone.replace('-', '').replace(' ', '')

    return phone


def send_sms(phone_number, message):
    """
    Solapi를 통해 SMS 발송

    Args:
        phone_number: 수신자 전화번호
        message: 메시지 내용 (90바이트 이하: SMS, 초과: LMS)

    Returns:
        dict: 발송 결과 {'success': bool, 'message': str}
    """
    headers = get_solapi_headers()

    if not headers:
        logger.warning("Solapi API 키가 설정되지 않았습니다.")
        return {
            'success': False,
            'message': 'Solapi API 키가 설정되지 않았습니다.'
        }

    # 전화번호 정규화
    normalized_phone = normalize_phone_number(phone_number)
    if not normalized_phone:
        return {
            'success': False,
            'message': '유효하지 않은 전화번호입니다.'
        }

    # 발신번호
    from_number = getattr(settings, 'SOLAPI_SENDER_NUMBER', '')
    if not from_number:
        return {
            'success': False,
            'message': '발신번호가 설정되지 않았습니다.'
        }

    # 메시지 타입 결정 (90바이트 초과시 LMS)
    message_bytes = len(message.encode('utf-8'))
    msg_type = 'LMS' if message_bytes > 90 else 'SMS'

    url = "https://api.solapi.com/messages/v4/send"

    payload = {
        "message": {
            "to": normalized_phone,
            "from": from_number,
            "text": message,
            "type": msg_type
        }
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)
        result = response.json()

        if response.status_code == 200:
            logger.info(f"SMS 발송 성공: {phone_number}")
            return {
                'success': True,
                'message': 'SMS 발송 성공',
                'message_id': result.get('messageId')
            }
        else:
            error_msg = result.get('errorMessage', '알 수 없는 오류')
            logger.error(f"SMS 발송 실패: {error_msg}")
            return {
                'success': False,
                'message': f'SMS 발송 실패: {error_msg}'
            }

    except requests.exceptions.Timeout:
        logger.error("SMS 발송 타임아웃")
        return {
            'success': False,
            'message': 'SMS 발송 타임아웃'
        }
    except Exception as e:
        logger.error(f"SMS 발송 중 오류 발생: {str(e)}")
        return {
            'success': False,
            'message': f'SMS 발송 중 오류 발생: {str(e)}'
        }


def send_sms_batch(phone_numbers, message):
    """
    여러 수신자에게 SMS 일괄 발송

    Args:
        phone_numbers: 전화번호 리스트
        message: 메시지 내용

    Returns:
        dict: 발송 결과 {'success_count': int, 'fail_count': int, 'results': list}
    """
    headers = get_solapi_headers()

    if not headers:
        return {
            'success_count': 0,
            'fail_count': len(phone_numbers),
            'total': len(phone_numbers),
            'message': 'Solapi API 키가 설정되지 않았습니다.'
        }

    from_number = getattr(settings, 'SOLAPI_SENDER_NUMBER', '')
    if not from_number:
        return {
            'success_count': 0,
            'fail_count': len(phone_numbers),
            'total': len(phone_numbers),
            'message': '발신번호가 설정되지 않았습니다.'
        }

    # 메시지 타입 결정
    message_bytes = len(message.encode('utf-8'))
    msg_type = 'LMS' if message_bytes > 90 else 'SMS'

    # 메시지 리스트 생성
    messages = []
    for phone in phone_numbers:
        normalized = normalize_phone_number(phone)
        if normalized:
            messages.append({
                "to": normalized,
                "from": from_number,
                "text": message,
                "type": msg_type
            })

    if not messages:
        return {
            'success_count': 0,
            'fail_count': len(phone_numbers),
            'total': len(phone_numbers),
            'message': '유효한 전화번호가 없습니다.'
        }

    url = "https://api.solapi.com/messages/v4/send-many"

    payload = {
        "messages": messages
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        result = response.json()

        if response.status_code == 200:
            success_count = result.get('successCount', 0)
            fail_count = result.get('failCount', 0)

            logger.info(f"SMS 일괄 발송 완료: 성공 {success_count}, 실패 {fail_count}")

            return {
                'success_count': success_count,
                'fail_count': fail_count,
                'total': len(messages),
                'message': f'{success_count}건 발송 성공'
            }
        else:
            error_msg = result.get('errorMessage', '알 수 없는 오류')
            return {
                'success_count': 0,
                'fail_count': len(messages),
                'total': len(messages),
                'message': f'SMS 발송 실패: {error_msg}'
            }

    except Exception as e:
        logger.error(f"SMS 일괄 발송 중 오류: {str(e)}")
        return {
            'success_count': 0,
            'fail_count': len(messages),
            'total': len(messages),
            'message': f'SMS 발송 중 오류: {str(e)}'
        }
