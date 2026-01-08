#!/usr/bin/env python
"""
참가 현황 대시보드 기능 테스트
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from apps.events.models import Event, TimeSlot
from apps.participants.models import Participant, ParticipantAvailability
from datetime import datetime, timedelta
from django.utils import timezone
import pytz
import requests
import json

User = get_user_model()
BASE_URL = "http://127.0.0.1:8000"

print("\n🧪 참가 현황 대시보드 기능 테스트\n")

# 1. 테스트 데이터 생성
print("1️⃣ 테스트 데이터 생성 중...")

# 사용자 생성
user, _ = User.objects.get_or_create(
    email='test@example.com',
    defaults={'nickname': '테스트 주최자'}
)
if not user.check_password('testpass123456'):
    user.set_password('testpass123456')
    user.save()

# 로그인 먼저 (이벤트 생성을 위해)
login_response = requests.post(
    f"{BASE_URL}/api/v1/auth/login/",
    json={"email": "test@example.com", "password": "testpass123456"}
)
access_token = login_response.json()['tokens']['access']
headers = {'Authorization': f'Bearer {access_token}'}

# 이벤트 생성 (API 사용 - 타임슬롯 자동 생성)
now = timezone.now()
event_data = {
    "title": "피자 파티 일정 조율",
    "description": "맛있는 피자를 먹으며 즐거운 시간을 보내요!",
    "date_start": (now + timedelta(days=1)).date().isoformat(),
    "date_end": (now + timedelta(days=2)).date().isoformat(),
    "time_start": "14:00",
    "time_end": "16:00",
    "timezone": "Asia/Seoul"
}

event_response = requests.post(
    f"{BASE_URL}/api/v1/events/",
    json=event_data,
    headers=headers
)
event_id = event_response.json()['id']
event = Event.objects.get(id=event_id)

print(f"   ✅ 이벤트 생성: {event.title} (ID: {event.id})")

# 타임슬롯 가져오기 (자동 생성됨)
slots = list(TimeSlot.objects.filter(event=event).order_by('start_datetime'))
print(f"   ✅ {len(slots)}개의 타임슬롯 생성")

# 참가자 생성 (5명)
print("   👥 참가자 생성 중...")
participants = []
participant_names = ['철수', '영희', '민수', '지영', '준호']

for name in participant_names:
    participant = Participant.objects.create(
        event=event,
        nickname=name,
        email=f'{name}@example.com'
    )
    participants.append(participant)

print(f"   ✅ {len(participants)}명의 참가자 생성")

# 가능 시간 제출 (시나리오)
print("   ⏰ 가능 시간 제출 시나리오 설정 중...")

# 철수: 모든 시간 가능 (제출 완료)
for slot in slots:
    ParticipantAvailability.objects.create(
        participant=participants[0],
        time_slot=slot,
        is_available=True
    )
print(f"      ✅ {participants[0].nickname}: {len(slots)}개 시간대 제출")

# 영희: 절반만 가능 (제출 완료)
for slot in slots[:len(slots)//2]:
    ParticipantAvailability.objects.create(
        participant=participants[1],
        time_slot=slot,
        is_available=True
    )
print(f"      ✅ {participants[1].nickname}: {len(slots)//2}개 시간대 제출")

# 민수: 첫 2개만 가능 (제출 완료)
for slot in slots[:2]:
    ParticipantAvailability.objects.create(
        participant=participants[2],
        time_slot=slot,
        is_available=True
    )
print(f"      ✅ {participants[2].nickname}: 2개 시간대 제출")

# 지영, 준호: 아직 제출 안 함
print(f"      ⏳ {participants[3].nickname}, {participants[4].nickname}: 미제출")

# 2. 대시보드 조회 - 여러 권한 시나리오 테스트
print("\n2️⃣ 참가 현황 대시보드 조회 (권한 테스트)")
print("="*70)

# 2-1. 이벤트 생성자로 조회 (기존)
print("\n[테스트 1] 이벤트 생성자로 조회")
response = requests.get(
    f"{BASE_URL}/api/v1/events/{event.id}/dashboard",
    headers=headers
)
print(f"   상태 코드: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")

# 2-2. 회원 참가자로 조회
print("\n[테스트 2] 회원 참가자로 조회")
# 회원 참가자 생성
member_user, _ = User.objects.get_or_create(
    email='member@example.com',
    defaults={'nickname': '회원참가자'}
)
if not member_user.check_password('member123'):
    member_user.set_password('member123')
    member_user.save()

# 회원 참가자 등록
member_participant = Participant.objects.create(
    event=event,
    user=member_user,
    nickname='회원참가자',
    email='member@example.com'
)

# 회원으로 로그인
member_login = requests.post(
    f"{BASE_URL}/api/v1/auth/login/",
    json={"email": "member@example.com", "password": "member123"}
)
member_token = member_login.json()['tokens']['access']
member_headers = {'Authorization': f'Bearer {member_token}'}

# 회원 참가자로 대시보드 조회
member_response = requests.get(
    f"{BASE_URL}/api/v1/events/{event.id}/dashboard",
    headers=member_headers
)
print(f"   상태 코드: {member_response.status_code} {'✅' if member_response.status_code == 200 else '❌'}")

# 2-3. 익명 참가자로 조회 (participant_id + email)
print("\n[테스트 3] 익명 참가자로 조회 (participant_id + email)")
anonymous_participant = participants[0]  # 철수
anon_response = requests.get(
    f"{BASE_URL}/api/v1/events/{event.id}/dashboard",
    params={
        'participant_id': anonymous_participant.id,
        'email': anonymous_participant.email
    }
)
print(f"   상태 코드: {anon_response.status_code} {'✅' if anon_response.status_code == 200 else '❌'}")

# 2-4. 권한 없는 사용자 (다른 사용자)
print("\n[테스트 4] 권한 없는 사용자로 조회")
other_user, _ = User.objects.get_or_create(
    email='other@example.com',
    defaults={'nickname': '다른사용자'}
)
if not other_user.check_password('other123'):
    other_user.set_password('other123')
    other_user.save()

other_login = requests.post(
    f"{BASE_URL}/api/v1/auth/login/",
    json={"email": "other@example.com", "password": "other123"}
)
other_token = other_login.json()['tokens']['access']
other_headers = {'Authorization': f'Bearer {other_token}'}

other_response = requests.get(
    f"{BASE_URL}/api/v1/events/{event.id}/dashboard",
    headers=other_headers
)
print(f"   상태 코드: {other_response.status_code} {'✅' if other_response.status_code == 403 else '❌'}")
if other_response.status_code == 403:
    print(f"   에러 메시지: {other_response.json().get('detail', '')}")

# 2-5. 익명 참가자 - 잘못된 이메일
print("\n[테스트 5] 익명 참가자 - 잘못된 이메일")
wrong_email_response = requests.get(
    f"{BASE_URL}/api/v1/events/{event.id}/dashboard",
    params={
        'participant_id': anonymous_participant.id,
        'email': 'wrong@example.com'
    }
)
print(f"   상태 코드: {wrong_email_response.status_code} {'✅' if wrong_email_response.status_code == 403 else '❌'}")
if wrong_email_response.status_code == 403:
    print(f"   에러 메시지: {wrong_email_response.json().get('detail', '')}")

print("\n" + "="*70)
print("📊 대시보드 데이터 (이벤트 생성자 기준)")
print("="*70 + "\n")

print(f"상태 코드: {response.status_code}\n")

if response.status_code == 200:
    data = response.json()

    # 통계 출력
    stats = data['stats']
    print("📊 전체 통계:")
    print(f"   총 참가자: {stats['total_participants']}명")
    print(f"   시간 제출 완료: {stats['submitted_participants']}명")
    print(f"   제출 대기 중: {stats['pending_participants']}명")
    print(f"   제출률: {stats['submission_rate']}%")
    print(f"   총 타임슬롯: {stats['total_time_slots']}개")

    if stats['most_popular_slot']:
        most_popular = stats['most_popular_slot']
        print(f"\n⭐ 가장 인기 있는 시간:")
        print(f"   시간: {most_popular['start_datetime_local'][:19]}")
        print(f"   가능 인원: {most_popular['available_count']}명 ({most_popular['availability_rate']}%)")

    # 참가자 상태 출력
    print("\n" + "="*70)
    print("👥 참가자별 제출 상태:")
    print("="*70)

    for p in data['participants']:
        status_icon = "✅" if p['has_submitted'] else "⏳"
        account_type = "회원" if p['is_registered'] else "익명"
        print(f"{status_icon} {p['nickname']:8s} | {account_type:4s} | 제출: {p['submitted_slots_count']:2d}개 | {p['email']}")

    # 히트맵 데이터 출력 (처음 5개만)
    print("\n" + "="*70)
    print("🔥 타임슬롯별 가능 인원 (히트맵) - 상위 5개:")
    print("="*70)

    for i, slot in enumerate(data['heatmap'][:5], 1):
        time_str = slot['start_datetime_local'][11:16]  # HH:MM만 추출
        participants_str = ', '.join([p['nickname'] for p in slot['available_participants']])
        bar_length = int(slot['availability_rate'] / 5)  # 5%당 1칸
        bar = '█' * bar_length

        print(f"{i}. {time_str} | {slot['available_count']}명 ({slot['availability_rate']:5.1f}%) {bar}")
        print(f"   참가자: {participants_str if participants_str else '없음'}\n")

    # JSON 전체 출력 (선택)
    print("\n" + "="*70)
    print("📄 전체 응답 데이터 (JSON):")
    print("="*70)
    print(json.dumps(data, indent=2, ensure_ascii=False)[:1000] + "...")

    print("\n" + "="*70)
    print("✅ 대시보드 테스트 완료!")
    print("="*70)

else:
    print(f"   ❌ 에러: {response.text}")

# 정리
print("\n🧹 테스트 데이터 정리 중...")
event.delete()
user.delete()
member_user.delete()
other_user.delete()
print("✅ 정리 완료\n")
