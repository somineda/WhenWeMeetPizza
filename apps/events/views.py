from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404
from django.conf import settings
from .models import Event, FinalChoice, TimeSlot
from .serializers import EventSerializer, EventDetailSerializer, MyEventListSerializer, EventUpdateSerializer, EventSummarySerializer, FinalChoiceSerializer
from .pagination import EventPagination
from .tasks import send_final_choice_email, send_final_choice_sms


class EventCreateView(generics.CreateAPIView):
    serializer_class = EventSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        event = serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class EventDetailView(generics.RetrieveAPIView):
    serializer_class = EventDetailSerializer
    permission_classes = [AllowAny]
    lookup_field = 'slug'

    def get_object(self):
        slug = self.kwargs.get('slug')
        return get_object_or_404(Event, slug=slug, is_deleted=False)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MyEventListView(generics.ListAPIView):
    serializer_class = MyEventListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = EventPagination

    def get_queryset(self):
        return Event.objects.filter(
            created_by=self.request.user,
            is_deleted=False
        ).order_by('-created_at')


class EventUpdateView(generics.UpdateAPIView, generics.DestroyAPIView):
    serializer_class = EventUpdateSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        return Event.objects.filter(is_deleted=False)

    def update(self, request, *args, **kwargs):
        event = self.get_object()

        # 권한 체크: 방장(created_by)만 수정 가능
        if event.created_by != request.user:
            raise PermissionDenied("수정 권한이 없습니다")

        partial = kwargs.pop('partial', True)  # PATCH를 위해 partial=True
        serializer = self.get_serializer(event, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        event = self.get_object()

        # 권한 체크: 방장(created_by)만 삭제 가능
        if event.created_by != request.user:
            raise PermissionDenied("삭제 권한이 없습니다")

        # Soft delete
        event.is_deleted = True
        event.save()

        return Response(status=status.HTTP_204_NO_CONTENT)

class EventSummaryView(generics.RetrieveAPIView):
    serializer_class = EventSummarySerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'

    def get_queryset(self):
        return Event.objects.filter(is_deleted=False)

    def retrieve(self, request, *args, **kwargs):
        event = self.get_object()

        # 쿼리 파라미터 파싱
        min_participants = request.query_params.get('min_participants', 1)
        try:
            min_participants = int(min_participants)
        except ValueError:
            min_participants = 1

        only_all_available = request.query_params.get('only_all_available', 'false').lower() == 'true'

        # Serializer에 context 전달
        serializer = self.get_serializer(
            event,
            context={
                'min_participants': min_participants,
                'only_all_available': only_all_available
            }
        )

        return Response(serializer.data, status=status.HTTP_200_OK)


class FinalChoiceView(generics.GenericAPIView):
    serializer_class = FinalChoiceSerializer

    def get_permissions(self):
        """GET은 누구나, POST는 인증 필요"""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, *args, **kwargs):
        """확정된 시간 조회"""
        event_id = kwargs.get('pk')
        event = get_object_or_404(Event, id=event_id, is_deleted=False)

        # FinalChoice 조회
        try:
            final_choice = FinalChoice.objects.get(event=event)
        except FinalChoice.DoesNotExist:
            return Response(
                {"detail": "확정된 시간이 없습니다"},
                status=status.HTTP_404_NOT_FOUND
            )

        # 응답 데이터 생성
        serializer = self.get_serializer(final_choice)
        response_data = serializer.data
        response_data['slot_id'] = final_choice.slot.id

        return Response(response_data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """최종 시간 확정"""
        # 이벤트 가져오기
        event_id = kwargs.get('pk')
        event = get_object_or_404(Event, id=event_id, is_deleted=False)

        # 권한 체크: 방장만 확정 가능
        if event.created_by != request.user:
            raise PermissionDenied("확정 권한이 없습니다")

        # 중복 체크: 이벤트당 하나의 최종 시간만 허용
        if FinalChoice.objects.filter(event=event).exists():
            raise ValidationError({"detail": "이미 최종 시간이 확정되었습니다"})

        # Serializer로 검증 및 생성
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request, 'event': event}
        )
        serializer.is_valid(raise_exception=True)
        final_choice = serializer.save()

        # 자동으로 확정 알림 발송 (동기)
        try:
            send_final_choice_email(event_id)
        except Exception:
            pass  # 이메일 발송 실패는 무시

        try:
            send_final_choice_sms(event_id)
        except Exception:
            pass  # SMS 발송 실패는 무시

        # 응답 데이터 생성 (slot_id 포함)
        response_serializer = self.get_serializer(final_choice)
        response_data = response_serializer.data
        response_data['slot_id'] = final_choice.slot.id

        return Response(response_data, status=status.HTTP_200_OK)


class SendFinalChoiceEmailView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """확정된 시간을 참가자들에게 이메일로 발송"""
        # 이벤트 가져오기
        event_id = kwargs.get('pk')
        event = get_object_or_404(Event, id=event_id, is_deleted=False)

        # 권한 체크: 방장만 이메일 발송 가능
        if event.created_by != request.user:
            raise PermissionDenied("이메일 발송 권한이 없습니다")

        # 확정된 시간이 있는지 확인
        if not FinalChoice.objects.filter(event=event).exists():
            raise ValidationError({"detail": "확정된 시간이 없습니다"})

        # 이메일 및 SMS 동기 발송
        email_result = None
        sms_result = None

        try:
            email_result = send_final_choice_email(event_id)
        except Exception as e:
            email_result = {'success': False, 'message': str(e)}

        try:
            sms_result = send_final_choice_sms(event_id)
        except Exception as e:
            sms_result = {'success': False, 'message': str(e)}

        return Response(
            {
                "detail": "알림 전송이 완료되었습니다",
                "email": email_result,
                "sms": sms_result
            },
            status=status.HTTP_200_OK
        )


class TimeRecommendationView(generics.GenericAPIView):
    """최적 시간 추천 API"""
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        이벤트의 모든 타임슬롯을 분석하여 가장 많은 참가자가 가능한 시간대를 추천합니다.

        Query Parameters:
        - limit: 추천할 시간대 개수 (기본값: 5)
        - min_participants: 최소 참가자 수 필터 (선택)
        """
        from apps.participants.models import Participant, ParticipantAvailability
        from .serializers import TimeRecommendationSerializer
        import pytz

        event_id = self.kwargs.get('event_id')
        event = get_object_or_404(Event, id=event_id)

        # Query parameters
        limit = int(request.query_params.get('limit', 5))
        min_participants = request.query_params.get('min_participants')
        if min_participants:
            min_participants = int(min_participants)

        # 이벤트의 모든 타임슬롯 가져오기
        time_slots = TimeSlot.objects.filter(event=event).order_by('start_datetime')

        # 이벤트의 모든 참가자 수
        total_participants = Participant.objects.filter(event=event).count()

        if total_participants == 0:
            return Response({
                'event_id': event.id,
                'event_title': event.title,
                'total_participants': 0,
                'total_time_slots': time_slots.count(),
                'recommended_slots': [],
                'message': '아직 참가자가 없습니다'
            }, status=status.HTTP_200_OK)

        # 각 타임슬롯별로 가능한 참가자 수 계산
        slot_recommendations = []
        tz = pytz.timezone(event.timezone)

        for slot in time_slots:
            # 이 슬롯에 가능하다고 표시한 참가자들
            available_participants = ParticipantAvailability.objects.filter(
                time_slot=slot,
                is_available=True
            ).select_related('participant')

            available_count = available_participants.count()

            # 최소 참가자 수 필터 적용
            if min_participants and available_count < min_participants:
                continue

            # 참가자 닉네임 리스트
            participant_names = [
                avail.participant.nickname
                for avail in available_participants
            ]

            # 가능 비율 계산
            percentage = (available_count / total_participants * 100) if total_participants > 0 else 0

            slot_recommendations.append({
                'slot_id': slot.id,
                'start_datetime': slot.start_datetime,
                'end_datetime': slot.end_datetime,
                'start_datetime_local': slot.start_datetime.astimezone(tz).isoformat(),
                'end_datetime_local': slot.end_datetime.astimezone(tz).isoformat(),
                'available_count': available_count,
                'total_participants': total_participants,
                'available_percentage': round(percentage, 1),
                'available_participants': participant_names
            })

        # 가능한 참가자 수로 내림차순 정렬
        slot_recommendations.sort(key=lambda x: x['available_count'], reverse=True)

        # 상위 N개만 선택
        recommended_slots = slot_recommendations[:limit]

        # 메시지 생성
        if not recommended_slots:
            message = "조건에 맞는 추천 시간이 없습니다"
        elif recommended_slots[0]['available_count'] == total_participants:
            message = f"모든 참가자가 가능한 시간이 {len([s for s in recommended_slots if s['available_count'] == total_participants])}개 있습니다"
        else:
            top_count = recommended_slots[0]['available_count']
            message = f"최대 {top_count}명의 참가자가 가능한 시간입니다"

        response_data = {
            'event_id': event.id,
            'event_title': event.title,
            'total_participants': total_participants,
            'total_time_slots': time_slots.count(),
            'recommended_slots': recommended_slots,
            'message': message
        }

        serializer = TimeRecommendationSerializer(response_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventQRCodeView(generics.GenericAPIView):
    """이벤트 QR 코드 생성 API"""
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        이벤트 참가 링크를 QR 코드 이미지로 생성하여 반환합니다.

        Query Parameters:
        - size: QR 코드 크기 (기본값: 10, 범위: 5-30)
        - format: 이미지 형식 (png 또는 svg, 기본값: png)
        """
        import qrcode
        from io import BytesIO
        from django.http import HttpResponse

        event_id = self.kwargs.get('event_id')
        event = get_object_or_404(Event, id=event_id)

        # Query parameters
        size = int(request.query_params.get('size', 10))
        size = max(5, min(30, size))  # 5~30 사이로 제한
        image_format = request.query_params.get('format', 'png').lower()

        # 공유 URL 생성
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        share_url = f"{frontend_url}/e/{event.slug}"

        # QR 코드 생성
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=4,
        )
        qr.add_data(share_url)
        qr.make(fit=True)

        # 이미지 생성
        img = qr.make_image(fill_color="black", back_color="white")

        # BytesIO 버퍼에 저장
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)

        # HTTP 응답 생성
        response = HttpResponse(buffer, content_type='image/png')
        response['Content-Disposition'] = f'inline; filename="event_{event.slug}_qr.png"'
        return response


class EventShareInfoView(generics.GenericAPIView):
    """이벤트 공유 정보 조회 API"""
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        이벤트의 공유 링크, QR 코드 URL, 카카오톡/이메일 공유용 메타데이터를 반환합니다.
        """
        from .serializers import EventShareSerializer
        from django.conf import settings

        event_id = self.kwargs.get('event_id')
        event = get_object_or_404(Event, id=event_id)

        # 공유 URL
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        share_url = f"{frontend_url}/e/{event.slug}"

        # QR 코드 URL
        qr_code_url = request.build_absolute_uri(f'/api/v1/events/{event.id}/qr-code')

        # 카카오톡 공유용 정보
        kakao_title = f"📅 {event.title}"
        kakao_description = f"{event.description[:100]}..." if len(event.description) > 100 else event.description

        # 카카오톡 SDK용 템플릿 객체 (프론트엔드에서 바로 사용 가능)
        kakao_template = {
            "object_type": "feed",
            "content": {
                "title": kakao_title,
                "description": kakao_description,
                "image_url": "",  # 이벤트 이미지 URL 추가 가능
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

        # 이메일 공유용 정보
        email_subject = f"[일정 조율 초대] {event.title}"
        email_body = f"""
안녕하세요!

'{event.title}' 일정 조율에 초대합니다.

📅 기간: {event.date_start} ~ {event.date_end}
⏰ 시간: {event.time_start.strftime('%H:%M')} ~ {event.time_end.strftime('%H:%M')}

아래 링크에서 참가 가능한 시간을 선택해주세요:
{share_url}

감사합니다!
"""

        data = {
            'event_id': event.id,
            'event_title': event.title,
            'event_slug': event.slug,
            'share_url': share_url,
            'qr_code_url': qr_code_url,
            'kakao_title': kakao_title,
            'kakao_description': kakao_description,
            'kakao_image_url': None,  # 나중에 이벤트 이미지 추가 가능
            'kakao_template': kakao_template,  # 추가: 프론트엔드에서 바로 사용 가능
            'email_subject': email_subject,
            'email_body': email_body,
        }

        serializer = EventShareSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class EventInviteEmailView(generics.GenericAPIView):
    """이벤트 이메일 초대 발송 API"""
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """
        지정된 이메일 주소로 이벤트 참가 초대 메일을 발송합니다.

        Request Body:
        - emails: 이메일 주소 목록 (최대 50개)
        - message: 개인 메시지 (선택)
        """
        from .serializers import InviteEmailSerializer
        from django.core.mail import send_mail
        from django.conf import settings

        event_id = self.kwargs.get('event_id')
        event = get_object_or_404(Event, id=event_id)

        # 권한 체크: 이벤트 생성자만 초대 가능
        if event.created_by != request.user:
            raise PermissionDenied("이벤트 생성자만 초대 메일을 발송할 수 있습니다")

        serializer = InviteEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        emails = serializer.validated_data['emails']
        custom_message = serializer.validated_data.get('message', '')

        # 공유 URL
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        share_url = f"{frontend_url}/e/{event.slug}"

        # 이메일 내용 생성
        subject = f"[일정 조율 초대] {event.title}"

        message = f"""
안녕하세요!

{request.user.nickname}님이 '{event.title}' 일정 조율에 초대했습니다.

📅 기간: {event.date_start} ~ {event.date_end}
⏰ 시간: {event.time_start.strftime('%H:%M')} ~ {event.time_end.strftime('%H:%M')}
"""

        if custom_message:
            message += f"\n💬 메시지:\n{custom_message}\n"

        message += f"""
아래 링크에서 참가 가능한 시간을 선택해주세요:
{share_url}

감사합니다!
"""

        # 이메일 발송
        success_count = 0
        failed_emails = []

        for email in emails:
            try:
                send_mail(
                    subject=subject,
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                success_count += 1
            except Exception as e:
                failed_emails.append(email)

        # 결과 반환
        return Response({
            'success': True,
            'message': f'{success_count}명에게 초대 메일을 발송했습니다',
            'sent_count': success_count,
            'total_count': len(emails),
            'failed_emails': failed_emails
        }, status=status.HTTP_200_OK)


class EventDashboardView(generics.GenericAPIView):
    """이벤트 참가 현황 대시보드 API"""
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        이벤트의 참가 현황을 종합적으로 조회합니다.

        - 참가자별 시간 제출 상태
        - 타임슬롯별 가능 인원 (히트맵 데이터)
        - 전체 통계 (참가율, 제출률 등)

        권한: 이벤트 생성자 또는 참가자 (회원/익명 모두)
        - 회원 참가자: JWT 토큰으로 인증
        - 익명 참가자: query parameter로 participant_id와 email 제공
        """
        from apps.participants.models import Participant, ParticipantAvailability
        from .serializers import EventDashboardSerializer
        import pytz

        event_id = self.kwargs.get('event_id')
        event = get_object_or_404(Event, id=event_id)

        # 권한 체크: 이벤트 생성자 또는 참가자만 대시보드 조회 가능
        is_creator = request.user.is_authenticated and event.created_by == request.user
        is_participant = False

        if request.user.is_authenticated:
            # 로그인한 회원 참가자인지 확인
            is_participant = Participant.objects.filter(
                event=event,
                user=request.user
            ).exists()
        else:
            # 익명 참가자인 경우 participant_id와 email로 확인
            participant_id = request.query_params.get('participant_id')
            email = request.query_params.get('email')

            if participant_id and email:
                is_participant = Participant.objects.filter(
                    id=participant_id,
                    event=event,
                    email=email,
                    user__isnull=True  # 익명 참가자
                ).exists()

        if not (is_creator or is_participant):
            raise PermissionDenied("이벤트 생성자 또는 참가자만 대시보드를 조회할 수 있습니다")

        # 1. 참가자 목록 및 제출 상태
        participants = Participant.objects.filter(event=event).order_by('-created_at')
        participant_status_list = []

        submitted_count = 0

        for participant in participants:
            # 제출한 가능 시간 개수
            submitted_slots = ParticipantAvailability.objects.filter(
                participant=participant,
                is_available=True
            ).count()

            has_submitted = submitted_slots > 0
            if has_submitted:
                submitted_count += 1

            participant_status_list.append({
                'participant_id': participant.id,
                'nickname': participant.nickname,
                'email': participant.email,
                'is_registered': participant.user is not None,
                'has_submitted': has_submitted,
                'submitted_slots_count': submitted_slots,
                'joined_at': participant.created_at
            })

        # 2. 히트맵 데이터 (타임슬롯별 가능 인원)
        time_slots = TimeSlot.objects.filter(event=event).order_by('start_datetime')
        heatmap_data = []
        tz = pytz.timezone(event.timezone)

        most_popular_slot = None
        max_available = 0

        for slot in time_slots:
            # 이 슬롯에 가능하다고 표시한 참가자들
            availabilities = ParticipantAvailability.objects.filter(
                time_slot=slot,
                is_available=True
            ).select_related('participant')

            available_count = availabilities.count()
            available_participants = [
                {
                    'participant_id': av.participant.id,
                    'nickname': av.participant.nickname
                }
                for av in availabilities
            ]

            # 가능 비율 계산
            total_participants = participants.count()
            availability_rate = (available_count / total_participants * 100) if total_participants > 0 else 0

            heatmap_data.append({
                'slot_id': slot.id,
                'start_datetime': slot.start_datetime,
                'end_datetime': slot.end_datetime,
                'start_datetime_local': slot.start_datetime.astimezone(tz).isoformat(),
                'end_datetime_local': slot.end_datetime.astimezone(tz).isoformat(),
                'available_count': available_count,
                'available_participants': available_participants,
                'availability_rate': round(availability_rate, 1)
            })

            # 가장 인기 있는 슬롯 추적
            if available_count > max_available:
                max_available = available_count
                most_popular_slot = {
                    'slot_id': slot.id,
                    'start_datetime_local': slot.start_datetime.astimezone(tz).isoformat(),
                    'available_count': available_count,
                    'availability_rate': round(availability_rate, 1)
                }

        # 3. 통계
        total_participants = participants.count()
        pending_count = total_participants - submitted_count
        submission_rate = (submitted_count / total_participants * 100) if total_participants > 0 else 0

        stats = {
            'total_participants': total_participants,
            'submitted_participants': submitted_count,
            'pending_participants': pending_count,
            'submission_rate': round(submission_rate, 1),
            'total_time_slots': time_slots.count(),
            'most_popular_slot': most_popular_slot
        }

        # 응답 데이터 구성
        dashboard_data = {
            'event_id': event.id,
            'event_title': event.title,
            'stats': stats,
            'participants': participant_status_list,
            'heatmap': heatmap_data
        }

        serializer = EventDashboardSerializer(dashboard_data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CalendarExportView(generics.GenericAPIView):
    """캘린더 내보내기 정보 제공 API"""
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        확정된 일정을 캘린더에 추가할 수 있는 링크 및 정보를 제공합니다.

        - Google Calendar 추가 URL
        - .ics 파일 다운로드 URL
        - 확정된 시간 정보

        권한: 모든 사용자 (링크를 알면 누구나 조회 가능)
        """
        from .serializers import CalendarExportSerializer
        from urllib.parse import quote
        import pytz

        event_id = self.kwargs.get('event_id')
        event = get_object_or_404(Event, id=event_id)

        # 확정된 시간 가져오기
        try:
            final_choice = FinalChoice.objects.get(event=event)
            has_final_choice = True
            final_slot = final_choice.slot

            # 타임존 변환
            tz = pytz.timezone(event.timezone)
            start_local = final_slot.start_datetime.astimezone(tz)
            end_local = final_slot.end_datetime.astimezone(tz)

            # Google Calendar URL 생성
            # 형식: https://calendar.google.com/calendar/render?action=TEMPLATE&text={title}&dates={start}/{end}&details={description}
            # 날짜 형식: YYYYMMDDTHHMMSSZ (UTC)
            start_utc = final_slot.start_datetime.strftime('%Y%m%dT%H%M%SZ')
            end_utc = final_slot.end_datetime.strftime('%Y%m%dT%H%M%SZ')

            title_encoded = quote(event.title)
            description_encoded = quote(event.description if event.description else '')

            google_calendar_url = (
                f"https://calendar.google.com/calendar/render"
                f"?action=TEMPLATE"
                f"&text={title_encoded}"
                f"&dates={start_utc}/{end_utc}"
                f"&details={description_encoded}"
            )

            message = f"{event.title} 일정이 확정되었습니다. 캘린더에 추가하세요!"

        except FinalChoice.DoesNotExist:
            has_final_choice = False
            final_slot = None
            start_local = None
            end_local = None
            google_calendar_url = None
            message = "아직 최종 시간이 확정되지 않았습니다."

        # .ics 다운로드 URL
        base_url = request.build_absolute_uri('/').rstrip('/')
        ics_download_url = f"{base_url}/api/v1/events/{event_id}/calendar.ics"

        data = {
            'event_id': event.id,
            'event_title': event.title,
            'has_final_choice': has_final_choice,
            'final_start_datetime': final_slot.start_datetime if final_slot else None,
            'final_end_datetime': final_slot.end_datetime if final_slot else None,
            'final_start_datetime_local': start_local.isoformat() if start_local else None,
            'final_end_datetime_local': end_local.isoformat() if end_local else None,
            'google_calendar_url': google_calendar_url,
            'ics_download_url': ics_download_url,
            'message': message
        }

        serializer = CalendarExportSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CalendarICSDownloadView(generics.GenericAPIView):
    """iCalendar (.ics) 파일 다운로드 API"""
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """
        확정된 일정을 .ics 파일로 다운로드합니다.
        모든 캘린더 앱(Google Calendar, Apple Calendar, Outlook 등)에서 열 수 있습니다.

        권한: 모든 사용자
        """
        from django.http import HttpResponse
        from django.utils import timezone

        event_id = self.kwargs.get('event_id')
        event = get_object_or_404(Event, id=event_id)

        # 확정된 시간 가져오기
        try:
            final_choice = FinalChoice.objects.get(event=event)
            final_slot = final_choice.slot
        except FinalChoice.DoesNotExist:
            return Response({
                'detail': '아직 최종 시간이 확정되지 않았습니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # .ics 파일 생성 (iCalendar 형식)
        # 날짜 형식: YYYYMMDDTHHMMSSZ (UTC)
        start_utc = final_slot.start_datetime.strftime('%Y%m%dT%H%M%SZ')
        end_utc = final_slot.end_datetime.strftime('%Y%m%dT%H%M%SZ')
        now_utc = timezone.now().strftime('%Y%m%dT%H%M%SZ')

        # UID 생성 (고유 식별자)
        uid = f"event-{event.id}-finalchoice-{final_choice.id}@pizzascheduler"

        # 이벤트 설명
        description = event.description.replace('\n', '\\n') if event.description else ''

        ics_content = f"""BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Pizza Scheduler//Event Calendar//KO
CALSCALE:GREGORIAN
METHOD:PUBLISH
BEGIN:VEVENT
UID:{uid}
DTSTAMP:{now_utc}
DTSTART:{start_utc}
DTEND:{end_utc}
SUMMARY:{event.title}
DESCRIPTION:{description}
STATUS:CONFIRMED
SEQUENCE:0
END:VEVENT
END:VCALENDAR"""

        # HTTP 응답 생성
        response = HttpResponse(ics_content, content_type='text/calendar; charset=utf-8')
        response['Content-Disposition'] = f'attachment; filename="{event.slug}.ics"'
        return response
