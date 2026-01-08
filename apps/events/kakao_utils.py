"""
카카오톡 메시지 발송 유틸리티
"""
import requests
from django.conf import settings


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
