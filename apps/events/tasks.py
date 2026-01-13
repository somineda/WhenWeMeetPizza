from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Event, FinalChoice
import pytz
from datetime import datetime, timedelta


@shared_task
def send_final_choice_email(event_id):
    # 확정된 시간을 참가자들에게 이메일로 발송하는 Celery task
    try:
        # 이벤트와 확정된 시간 가져오기
        event = Event.objects.get(id=event_id, is_deleted=False)
        final_choice = FinalChoice.objects.get(event=event)

        # 타임존 변환
        tz = pytz.timezone(event.timezone)
        local_start = final_choice.slot.start_datetime.astimezone(tz)
        local_end = final_choice.slot.end_datetime.astimezone(tz)

        # 이벤트 URL
        event_url = f"{settings.FRONTEND_URL}/e/{event.slug}"

        # 이메일 제목
        subject = f"[{event.title}] 최종 일정이 확정되었습니다🍕"

        # 이메일 본문
        message = f"""
안녕하세요,

'{event.title}' 이벤트의 최종 일정이 확정되었습니다🎉

📅 확정된 일정:
- 날짜: {local_start.strftime('%Y년 %m월 %d일 (%a)')}
- 시간: {local_start.strftime('%H:%M')} - {local_end.strftime('%H:%M')}

💌 자세한 내용은 아래 링크에서 확인해주세요
{event_url}

        """

        # 참가자 이메일 수집
        participant_emails = []
        for participant in event.participants.all():
            if participant.email:
                participant_emails.append(participant.email)

        # 이메일이 있는 참가자가 있을 경우에만 발송
        if participant_emails:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=participant_emails,
                fail_silently=False,
            )

            # 리마인드 이메일 스케줄링 (Celery 사용 가능한 경우만)
            try:
                schedule_reminder_email(event_id)
            except Exception:
                pass  # 스케줄링 실패는 무시

            return {
                'success': True,
                'sent_count': len(participant_emails),
                'message': f'{len(participant_emails)}명의 참가자에게 이메일을 발송했습니다.'
            }
        else:
            return {
                'success': False,
                'sent_count': 0,
                'message': '이메일을 받을 참가자가 없습니다.'
            }

    except Event.DoesNotExist:
        return {
            'success': False,
            'message': '이벤트를 찾을 수 없습니다.'
        }
    except FinalChoice.DoesNotExist:
        return {
            'success': False,
            'message': '확정된 시간이 없습니다.'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'이메일 발송 중 오류가 발생했습니다: {str(e)}'
        }


@shared_task
def send_reminder_email(event_id):
    """
    확정된 날짜 당일 오전 7시에 리마인드 이메일을 발송하는 Celery task
    """
    try:
        # 이벤트와 확정된 시간 가져오기
        event = Event.objects.get(id=event_id, is_deleted=False)
        final_choice = FinalChoice.objects.get(event=event)

        # 타임존 변환
        tz = pytz.timezone(event.timezone)
        local_start = final_choice.slot.start_datetime.astimezone(tz)
        local_end = final_choice.slot.end_datetime.astimezone(tz)

        # 이벤트 URL
        event_url = f"{settings.FRONTEND_URL}/e/{event.slug}"

        # 이메일 제목
        subject = f"[리마인드] {event.title} - 오늘 {local_start.strftime('%H:%M')}에 시작됩니다"

        # 이메일 본문
        message = f"""
안녕하세요,

'{event.title}' 이벤트가 오늘 진행됩니다🎉

📅 일정 리마인드:
- 날짜: 오늘 ({local_start.strftime('%Y년 %m월 %d일 (%a)')})
- 시간: {local_start.strftime('%H:%M')} - {local_end.strftime('%H:%M')}

💘 자세한 내용은 아래 링크에서 확인하실 수 있습니다
{event_url}

        """

        # 참가자 이메일 수집
        participant_emails = []
        for participant in event.participants.all():
            if participant.email:
                participant_emails.append(participant.email)

        # 이메일이 있는 참가자가 있을 경우에만 발송
        if participant_emails:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=participant_emails,
                fail_silently=False,
            )
            return {
                'success': True,
                'sent_count': len(participant_emails),
                'message': f'{len(participant_emails)}명의 참가자에게 리마인드 이메일을 발송했습니다.'
            }
        else:
            return {
                'success': False,
                'sent_count': 0,
                'message': '이메일을 받을 참가자가 없습니다.'
            }

    except Event.DoesNotExist:
        return {
            'success': False,
            'message': '이벤트를 찾을 수 없습니다.'
        }
    except FinalChoice.DoesNotExist:
        return {
            'success': False,
            'message': '확정된 시간이 없습니다.'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'리마인드 이메일 발송 중 오류가 발생했습니다: {str(e)}'
        }


def schedule_reminder_email(event_id):
    """
    확정된 날짜 오전 7시에 리마인드 이메일을 스케줄링
    """
    try:
        event = Event.objects.get(id=event_id, is_deleted=False)
        final_choice = FinalChoice.objects.get(event=event)

        # 타임존 변환
        tz = pytz.timezone(event.timezone)
        local_start = final_choice.slot.start_datetime.astimezone(tz)

        # 당일 오전 7시 계산
        reminder_time = local_start.replace(hour=7, minute=0, second=0, microsecond=0)

        # 이미 오전 7시가 지났다면 리마인드 이메일 발송하지 않음
        now = datetime.now(tz)
        if reminder_time > now:
            # ETA(Estimated Time of Arrival)로 스케줄링
            send_reminder_email.apply_async(
                args=[event_id],
                eta=reminder_time
            )

    except Exception as e:
        # 스케줄링 실패 시 무시
        pass

# 확정된 시간을 참가자들에게 SMS로 발송하는 Celery task
@shared_task
def send_final_choice_sms(event_id):
    from .sms_utils import send_sms_batch

    try:
        # 이벤트와 확정된 시간 가져오기
        event = Event.objects.get(id=event_id, is_deleted=False)
        final_choice = FinalChoice.objects.get(event=event)

        # 타임존 변환
        tz = pytz.timezone(event.timezone)
        local_start = final_choice.slot.start_datetime.astimezone(tz)
        local_end = final_choice.slot.end_datetime.astimezone(tz)

        # 이벤트 URL
        event_url = f"{settings.FRONTEND_URL}/e/{event.slug}"

        # SMS 메시지 생성
        message = f"""[{event.title}] 최종 일정 확정

날짜: {local_start.strftime('%m/%d(%a)')}
시간: {local_start.strftime('%H:%M')}-{local_end.strftime('%H:%M')}

{event_url}"""

        # 참가자 전화번호 수집
        participant_phones = []
        for participant in event.participants.all():
            if participant.phone:
                participant_phones.append(participant.phone)

        # 전화번호가 있는 참가자가 있을 경우에만 발송
        if participant_phones:
            result = send_sms_batch(participant_phones, message)

            # 리마인드 SMS 스케줄링
            try:
                schedule_reminder_sms(event_id)
            except Exception:
                pass  # 스케줄링 실패는 무시

            return {
                'success': True,
                'sent_count': result['success_count'],
                'fail_count': result['fail_count'],
                'message': f"{result['success_count']}명에게 SMS를 발송했습니다."
            }
        else:
            return {
                'success': False,
                'sent_count': 0,
                'message': 'SMS를 받을 참가자가 없습니다 (전화번호 미등록).'
            }

    except Event.DoesNotExist:
        return {
            'success': False,
            'message': '이벤트를 찾을 수 없습니다.'
        }
    except FinalChoice.DoesNotExist:
        return {
            'success': False,
            'message': '확정된 시간이 없습니다.'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'SMS 발송 중 오류가 발생했습니다: {str(e)}'
        }

# 확정된 날짜 당일 오전 7시에 리마인드 SMS를 발송하는 Celery task
@shared_task
def send_reminder_sms(event_id):
    from .sms_utils import send_sms_batch

    try:
        # 이벤트와 확정된 시간 가져오기
        event = Event.objects.get(id=event_id, is_deleted=False)
        final_choice = FinalChoice.objects.get(event=event)

        # 타임존 변환
        tz = pytz.timezone(event.timezone)
        local_start = final_choice.slot.start_datetime.astimezone(tz)

        # 이벤트 URL
        event_url = f"{settings.FRONTEND_URL}/e/{event.slug}"

        # SMS 메시지 생성
        message = f"""[리마인드] {event.title}

오늘 {local_start.strftime('%H:%M')}에 시작!

{event_url}"""

        # 참가자 전화번호 수집
        participant_phones = []
        for participant in event.participants.all():
            if participant.phone:
                participant_phones.append(participant.phone)

        # 전화번호가 있는 참가자가 있을 경우에만 발송
        if participant_phones:
            result = send_sms_batch(participant_phones, message)
            return {
                'success': True,
                'sent_count': result['success_count'],
                'message': f"{result['success_count']}명에게 리마인드 SMS를 발송했습니다."
            }
        else:
            return {
                'success': False,
                'sent_count': 0,
                'message': 'SMS를 받을 참가자가 없습니다.'
            }

    except Event.DoesNotExist:
        return {
            'success': False,
            'message': '이벤트를 찾을 수 없습니다.'
        }
    except FinalChoice.DoesNotExist:
        return {
            'success': False,
            'message': '확정된 시간이 없습니다.'
        }
    except Exception as e:
        return {
            'success': False,
            'message': f'리마인드 SMS 발송 중 오류가 발생했습니다: {str(e)}'
        }


def schedule_reminder_sms(event_id):
    """
    확정된 날짜 오전 7시에 리마인드 SMS를 스케줄링
    """
    try:
        event = Event.objects.get(id=event_id, is_deleted=False)
        final_choice = FinalChoice.objects.get(event=event)

        # 타임존 변환
        tz = pytz.timezone(event.timezone)
        local_start = final_choice.slot.start_datetime.astimezone(tz)

        # 당일 오전 7시 계산
        reminder_time = local_start.replace(hour=7, minute=0, second=0, microsecond=0)

        # 이미 오전 7시가 지났다면 리마인드 발송하지 않음
        now = datetime.now(tz)
        if reminder_time > now:
            # ETA(Estimated Time of Arrival)로 스케줄링
            send_reminder_sms.apply_async(
                args=[event_id],
                eta=reminder_time
            )

    except Exception as e:
        # 스케줄링 실패 시 무시
        pass
