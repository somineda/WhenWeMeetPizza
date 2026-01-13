"""
카카오톡 메시지 발송 유틸리티
"""
import json
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def send_kakao_message_to_user(user_id, template_id, template_args):
    """
    특정 사용자에게 카카오톡 메시지 발송

    Args:
        user_id: 카카오 사용자 ID
        template_id: 카카오 템플릿 ID
        template_args: 템플릿 변수

    Returns:
        bool: 성공 여부
    """
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"

    headers = {
        "Authorization": f"Bearer {settings.KAKAO_REST_API_KEY}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    data = {
        "template_object": {
            "object_type": "feed",
            "content": {
                "title": template_args.get('title'),
                "description": template_args.get('description'),
                "image_url": template_args.get('image_url', ''),
                "link": {
                    "web_url": template_args.get('url'),
                    "mobile_web_url": template_args.get('url')
                }
            },
            "buttons": [
                {
                    "title": "일정 참여하기",
                    "link": {
                        "web_url": template_args.get('url'),
                        "mobile_web_url": template_args.get('url')
                    }
                }
            ]
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        return response.status_code == 200
    except Exception as e:
        print(f"카카오톡 메시지 발송 실패: {e}")
        return False


def get_kakao_share_link(event_slug, event_title, event_description, share_url):
    """
    카카오톡 공유용 링크 데이터 생성

    프론트엔드에서 사용할 수 있도록 공유 데이터를 구조화
    """
    return {
        "object_type": "feed",
        "content": {
            "title": f"📅 {event_title}",
            "description": event_description,
            "image_url": "",  # 이벤트 이미지 URL (선택)
            "link": {
                "web_url": share_url,
                "mobile_web_url": share_url
            }
        },
        "buttons": [
            {
                "title": "일정 참여하기",
                "link": {
                    "web_url": share_url,
                    "mobile_web_url": share_url
                }
            }
        ]
    }


def normalize_phone_number(phone):
    """
    전화번호에서 하이픈 제거하고 국가 코드 추가

    Args:
        phone: 전화번호 (010-1234-5678 또는 01012345678)

    Returns:
        str: 정규화된 전화번호 (821012345678)
    """
    if not phone:
        return None

    # 하이픈 제거
    phone = phone.replace('-', '').replace(' ', '')

    # 국가 코드 추가 (한국)
    if phone.startswith('0'):
        phone = '82' + phone[1:]

    return phone


def send_kakao_alimtalk(phone_number, template_code, template_args):
    """
    카카오 비즈니스 알림톡 발송

    Args:
        phone_number: 수신자 전화번호 (010-1234-5678 형식)
        template_code: 알림톡 템플릿 코드
        template_args: 템플릿 변수 딕셔너리

    Returns:
        dict: 발송 결과 {'success': bool, 'message': str}
    """
    # 설정 확인
    api_key = getattr(settings, 'KAKAO_ALIMTALK_API_KEY', None)
    sender_key = getattr(settings, 'KAKAO_ALIMTALK_SENDER_KEY', None)

    if not api_key or not sender_key:
        logger.warning("카카오 알림톡 API 키가 설정되지 않았습니다.")
        return {
            'success': False,
            'message': '카카오 알림톡 API 키가 설정되지 않았습니다.'
        }

    # 전화번호 정규화
    normalized_phone = normalize_phone_number(phone_number)
    if not normalized_phone:
        return {
            'success': False,
            'message': '유효하지 않은 전화번호입니다.'
        }

    # 카카오 비즈니스 알림톡 API
    url = "https://kapi.kakao.com/v1/api/talk/friends/message/default/send"

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    # 알림톡 메시지 구성
    payload = {
        "sender_key": sender_key,
        "template_code": template_code,
        "receiver_num": normalized_phone,
        "template_object": json.dumps(template_args)
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=10)

        if response.status_code == 200:
            logger.info(f"알림톡 발송 성공: {phone_number}")
            return {
                'success': True,
                'message': '알림톡 발송 성공'
            }
        else:
            error_msg = response.json().get('msg', '알 수 없는 오류')
            logger.error(f"알림톡 발송 실패: {error_msg}")
            return {
                'success': False,
                'message': f'알림톡 발송 실패: {error_msg}'
            }

    except requests.exceptions.Timeout:
        logger.error("알림톡 발송 타임아웃")
        return {
            'success': False,
            'message': '알림톡 발송 타임아웃'
        }
    except Exception as e:
        logger.error(f"알림톡 발송 중 오류 발생: {str(e)}")
        return {
            'success': False,
            'message': f'알림톡 발송 중 오류 발생: {str(e)}'
        }


def send_alimtalk_batch(phone_numbers, template_code, template_args):
    """
    여러 수신자에게 알림톡 일괄 발송

    Args:
        phone_numbers: 전화번호 리스트
        template_code: 알림톡 템플릿 코드
        template_args: 템플릿 변수 딕셔너리

    Returns:
        dict: 발송 결과 {'success_count': int, 'fail_count': int, 'results': list}
    """
    results = []
    success_count = 0
    fail_count = 0

    for phone in phone_numbers:
        result = send_kakao_alimtalk(phone, template_code, template_args)
        results.append({
            'phone': phone,
            **result
        })

        if result['success']:
            success_count += 1
        else:
            fail_count += 1

    return {
        'success_count': success_count,
        'fail_count': fail_count,
        'total': len(phone_numbers),
        'results': results
    }
