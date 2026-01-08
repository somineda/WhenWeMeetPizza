
from rest_framework import serializers
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
import pytz
from .models import Event, TimeSlot, FinalChoice


class TimeSlotSerializer(serializers.ModelSerializer):
    start_datetime_local = serializers.SerializerMethodField()
    end_datetime_local = serializers.SerializerMethodField()

    class Meta:
        model = TimeSlot
        fields = ['id', 'start_datetime', 'end_datetime', 'start_datetime_local', 'end_datetime_local']

    def get_start_datetime_local(self, obj):
        """이벤트의 타임존으로 변환된 시작 시간"""
        tz = pytz.timezone(obj.event.timezone)
        return obj.start_datetime.astimezone(tz).isoformat()

    def get_end_datetime_local(self, obj):
        """이벤트의 타임존으로 변환된 종료 시간"""
        tz = pytz.timezone(obj.event.timezone)
        return obj.end_datetime.astimezone(tz).isoformat()


class EventSerializer(serializers.ModelSerializer):
    organizer_id = serializers.IntegerField(source='created_by.id', read_only=True)
    url = serializers.SerializerMethodField()
    time_slots_count = serializers.SerializerMethodField()
    share_url = serializers.SerializerMethodField()
    qr_code_url = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'slug', 'title', 'description',
            'date_start', 'date_end', 'time_start', 'time_end',
            'timezone', 'deadline_at', 'organizer_id',
            'created_at', 'url', 'time_slots_count', 'share_url', 'qr_code_url'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'organizer_id', 'url', 'time_slots_count', 'share_url', 'qr_code_url']

    def get_time_slots_count(self, obj):
        """생성된 타임슬롯 개수"""
        return obj.time_slots.count()

    def get_url(self, obj):
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        return f"{frontend_url}/e/{obj.slug}"

    def get_share_url(self, obj):
        """공유용 URL (프론트엔드)"""
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        return f"{frontend_url}/e/{obj.slug}"

    def get_qr_code_url(self, obj):
        """QR 코드 생성 API URL"""
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(f'/api/v1/events/{obj.id}/qr-code')
        return f"/api/v1/events/{obj.id}/qr-code"

    def validate(self, attrs):
        # 날짜 유효성 검사
        if attrs.get('date_end') and attrs.get('date_start'):
            if attrs['date_end'] < attrs['date_start']:
                raise serializers.ValidationError("종료일이 시작일보다 먼저입니다")

        # 시간 유효성 검사
        if attrs.get('time_end') and attrs.get('time_start'):
            if attrs['time_end'] <= attrs['time_start']:
                raise serializers.ValidationError("종료 시간이 시작 시간보다 먼저이거나 같습니다")

        return attrs

    def create(self, validated_data):
        # 로그인한 사용자를 created_by로 설정
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['created_by'] = request.user

        event = super().create(validated_data)

        # TimeSlot 자동 생성
        self.create_time_slots(event)

        return event

    def create_time_slots(self, event):
        """
        이벤트의 날짜/시간 범위 내에서 30분 단위로 TimeSlot 생성
        """
        tz = pytz.timezone(event.timezone)
        current_date = event.date_start

        while current_date <= event.date_end:
            # 해당 날짜의 시작 시간과 종료 시간 생성
            start_dt = datetime.combine(current_date, event.time_start)
            end_dt = datetime.combine(current_date, event.time_end)

            # 타임존 적용
            start_dt = tz.localize(start_dt)
            end_dt = tz.localize(end_dt)

            # 30분 단위로 슬롯 생성
            current_time = start_dt
            while current_time < end_dt:
                slot_end = current_time + timedelta(minutes=30)
                TimeSlot.objects.create(
                    event=event,
                    start_datetime=current_time,
                    end_datetime=slot_end
                )
                current_time = slot_end

            # 다음 날짜로
            current_date += timedelta(days=1)


class SlotSummarySerializer(serializers.Serializer):
    slot_id = serializers.IntegerField(source='id')
    date = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    available_count = serializers.SerializerMethodField()
    total_participants = serializers.SerializerMethodField()

    def get_date(self, obj):
        tz = pytz.timezone(obj.event.timezone)
        local_dt = obj.start_datetime.astimezone(tz)
        return local_dt.strftime('%Y-%m-%d')

    def get_start_time(self, obj):
        tz = pytz.timezone(obj.event.timezone)
        local_dt = obj.start_datetime.astimezone(tz)
        return local_dt.strftime('%H:%M')

    def get_end_time(self, obj):
        tz = pytz.timezone(obj.event.timezone)
        local_dt = obj.end_datetime.astimezone(tz)
        return local_dt.strftime('%H:%M')

    def get_available_count(self, obj):
        return obj.availabilities.filter(is_available=True).count()

    def get_total_participants(self, obj):
        return self.context.get('total_participants', 0)


class EventDetailSerializer(serializers.ModelSerializer):
    organizer_id = serializers.IntegerField(source='created_by.id', read_only=True)
    is_closed = serializers.SerializerMethodField()
    participants_count = serializers.SerializerMethodField()
    slots = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'slug', 'title', 'description',
            'date_start', 'date_end', 'time_start', 'time_end',
            'timezone', 'deadline_at', 'organizer_id',
            'is_closed', 'participants_count', 'slots'
        ]

    def get_is_closed(self, obj):
        if not obj.deadline_at:
            return False
        return timezone.now() > obj.deadline_at

    def get_participants_count(self, obj):
        return obj.participants.count()

    def get_slots(self, obj):
        total_participants = obj.participants.count()
        time_slots = obj.time_slots.all().prefetch_related('availabilities')
        return SlotSummarySerializer(
            time_slots,
            many=True,
            context={'total_participants': total_participants}
        ).data


class MyEventListSerializer(serializers.ModelSerializer):
    participant_count = serializers.SerializerMethodField()

    class Meta:
        model = Event
        fields = [
            'id', 'slug', 'title',
            'date_start', 'date_end', 'deadline_at',
            'participant_count', 'created_at'
        ]

    def get_participant_count(self, obj):
        return obj.participants.count()


class EventUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id', 'slug', 'title', 'description',
            'date_start', 'date_end', 'time_start', 'time_end',
            'timezone', 'deadline_at', 'updated_at'
        ]
        read_only_fields = ['id', 'slug', 'updated_at']

    def validate(self, attrs):
        # 현재 인스턴스의 값을 가져와서 검증
        instance = self.instance

        # 날짜 유효성 검사
        date_start = attrs.get('date_start', instance.date_start if instance else None)
        date_end = attrs.get('date_end', instance.date_end if instance else None)

        if date_end and date_start:
            if date_end < date_start:
                raise serializers.ValidationError("종료일이 시작일보다 먼저입니다")

        # 시간 유효성 검사
        time_start = attrs.get('time_start', instance.time_start if instance else None)
        time_end = attrs.get('time_end', instance.time_end if instance else None)

        if time_end and time_start:
            if time_end <= time_start:
                raise serializers.ValidationError("종료 시간이 시작 시간보다 먼저이거나 같습니다")

        return attrs

class SlotSummaryWithAllAvailableSerializer(serializers.Serializer):
    slot_id = serializers.IntegerField(source='id')
    date = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    available_count = serializers.SerializerMethodField()
    is_all_available = serializers.SerializerMethodField()

    def get_date(self, obj):
        tz = pytz.timezone(obj.event.timezone)
        local_dt = obj.start_datetime.astimezone(tz)
        return local_dt.strftime('%Y-%m-%d')

    def get_start_time(self, obj):
        tz = pytz.timezone(obj.event.timezone)
        local_dt = obj.start_datetime.astimezone(tz)
        return local_dt.strftime('%H:%M')

    def get_end_time(self, obj):
        tz = pytz.timezone(obj.event.timezone)
        local_dt = obj.end_datetime.astimezone(tz)
        return local_dt.strftime('%H:%M')

    def get_available_count(self, obj):
        return obj.availabilities.filter(is_available=True).count()

    def get_is_all_available(self, obj):
        total_participants = self.context.get('total_participants', 0)
        available_count = self.get_available_count(obj)
        return available_count == total_participants and total_participants > 0


class EventSummarySerializer(serializers.Serializer):
    event_id = serializers.IntegerField(source='id')
    total_participants = serializers.SerializerMethodField()
    slots = serializers.SerializerMethodField()
    best_slots = serializers.SerializerMethodField()

    def get_total_participants(self, obj):
        return obj.participants.count()

    def get_slots(self, obj):
        total_participants = self.get_total_participants(obj)
        time_slots = obj.time_slots.all().prefetch_related('availabilities')

        # 필터링
        min_participants = self.context.get('min_participants', 1)
        only_all_available = self.context.get('only_all_available', False)

        filtered_slots = []
        for slot in time_slots:
            available_count = slot.availabilities.filter(is_available=True).count()

            if available_count < min_participants:
                continue

            if only_all_available and available_count != total_participants:
                continue

            filtered_slots.append(slot)

        return SlotSummaryWithAllAvailableSerializer(
            filtered_slots,
            many=True,
            context={'total_participants': total_participants}
        ).data

    def get_best_slots(self, obj):
        total_participants = self.get_total_participants(obj)
        time_slots = obj.time_slots.all().prefetch_related('availabilities')

        # 필터링
        min_participants = self.context.get('min_participants', 1)
        only_all_available = self.context.get('only_all_available', False)

        filtered_slots = []
        for slot in time_slots:
            available_count = slot.availabilities.filter(is_available=True).count()

            if available_count < min_participants:
                continue

            if only_all_available and available_count != total_participants:
                continue

            filtered_slots.append(slot)

        # available_count로 정렬 (내림차순)
        sorted_slots = sorted(
            filtered_slots,
            key=lambda s: s.availabilities.filter(is_available=True).count(),
            reverse=True
        )

        return SlotSummaryWithAllAvailableSerializer(
            sorted_slots,
            many=True,
            context={'total_participants': total_participants}
        ).data


class FinalChoiceSerializer(serializers.Serializer):
    slot_id = serializers.IntegerField(write_only=True)
    event_id = serializers.IntegerField(source='event.id', read_only=True)
    date = serializers.SerializerMethodField()
    start_time = serializers.SerializerMethodField()
    end_time = serializers.SerializerMethodField()
    chosen_by = serializers.IntegerField(source='chosen_by.id', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    def get_date(self, obj):
        tz = pytz.timezone(obj.event.timezone)
        local_dt = obj.slot.start_datetime.astimezone(tz)
        return local_dt.strftime('%Y-%m-%d')

    def get_start_time(self, obj):
        tz = pytz.timezone(obj.event.timezone)
        local_dt = obj.slot.start_datetime.astimezone(tz)
        return local_dt.strftime('%H:%M')

    def get_end_time(self, obj):
        tz = pytz.timezone(obj.event.timezone)
        local_dt = obj.slot.end_datetime.astimezone(tz)
        return local_dt.strftime('%H:%M')

    def validate_slot_id(self, value):
        """슬롯 ID 유효성 검사"""
        if not TimeSlot.objects.filter(id=value).exists():
            raise serializers.ValidationError("유효하지 않은 슬롯 ID입니다")
        return value

    def validate(self, attrs):
        """전체 유효성 검사"""
        request = self.context.get('request')
        event = self.context.get('event')

        # 슬롯이 해당 이벤트에 속하는지 확인
        slot_id = attrs.get('slot_id')
        try:
            slot = TimeSlot.objects.get(id=slot_id)
            if slot.event != event:
                raise serializers.ValidationError("해당 슬롯은 이 이벤트에 속하지 않습니다")
            attrs['slot'] = slot
        except TimeSlot.DoesNotExist:
            raise serializers.ValidationError("유효하지 않은 슬롯 ID입니다")

        return attrs

    def create(self, validated_data):
        """최종 시간 확정 생성"""
        request = self.context.get('request')
        event = self.context.get('event')
        slot = validated_data['slot']

        # FinalChoice 생성
        final_choice = FinalChoice.objects.create(
            event=event,
            slot=slot,
            chosen_by=request.user
        )

        return final_choice


class RecommendedTimeSlotSerializer(serializers.Serializer):
    """최적 시간 추천 결과 Serializer"""
    slot_id = serializers.IntegerField()
    start_datetime = serializers.DateTimeField()
    end_datetime = serializers.DateTimeField()
    start_datetime_local = serializers.CharField()
    end_datetime_local = serializers.CharField()
    available_count = serializers.IntegerField()
    total_participants = serializers.IntegerField()
    available_percentage = serializers.FloatField()
    available_participants = serializers.ListField(child=serializers.CharField())


class TimeRecommendationSerializer(serializers.Serializer):
    """시간 추천 API 응답 Serializer"""
    event_id = serializers.IntegerField()
    event_title = serializers.CharField()
    total_participants = serializers.IntegerField()
    total_time_slots = serializers.IntegerField()
    recommended_slots = RecommendedTimeSlotSerializer(many=True)
    message = serializers.CharField()


class EventShareSerializer(serializers.Serializer):
    """이벤트 공유 정보 Serializer"""
    event_id = serializers.IntegerField()
    event_title = serializers.CharField()
    event_slug = serializers.CharField()
    share_url = serializers.CharField()
    qr_code_url = serializers.CharField()

    # 카카오톡 공유용 메타데이터
    kakao_title = serializers.CharField()
    kakao_description = serializers.CharField()
    kakao_image_url = serializers.CharField(required=False, allow_null=True)

    # 카카오톡 SDK용 템플릿 객체
    kakao_template = serializers.DictField(required=False)

    # 이메일 공유용 정보
    email_subject = serializers.CharField()
    email_body = serializers.CharField()


class InviteEmailSerializer(serializers.Serializer):
    """이메일 초대 요청 Serializer"""
    emails = serializers.ListField(
        child=serializers.EmailField(),
        min_length=1,
        max_length=50,
        help_text="초대할 이메일 주소 목록 (최대 50개)"
    )
    message = serializers.CharField(
        required=False,
        allow_blank=True,
        max_length=500,
        help_text="개인 메시지 (선택, 최대 500자)"
    )


class ParticipantStatusSerializer(serializers.Serializer):
    """참가자 상태 Serializer"""
    participant_id = serializers.IntegerField()
    nickname = serializers.CharField()
    email = serializers.EmailField(allow_null=True)
    is_registered = serializers.BooleanField()  # 회원 가입 여부
    has_submitted = serializers.BooleanField()  # 시간 제출 여부
    submitted_slots_count = serializers.IntegerField()  # 제출한 시간대 개수
    joined_at = serializers.DateTimeField()


class HeatmapSlotSerializer(serializers.Serializer):
    """히트맵용 타임슬롯 Serializer"""
    slot_id = serializers.IntegerField()
    start_datetime = serializers.DateTimeField()
    end_datetime = serializers.DateTimeField()
    start_datetime_local = serializers.CharField()
    end_datetime_local = serializers.CharField()
    available_count = serializers.IntegerField()
    available_participants = serializers.ListField(
        child=serializers.DictField()
    )
    availability_rate = serializers.FloatField()  # 가능 비율 (%)


class DashboardStatsSerializer(serializers.Serializer):
    """대시보드 통계 Serializer"""
    total_participants = serializers.IntegerField()
    submitted_participants = serializers.IntegerField()
    pending_participants = serializers.IntegerField()
    submission_rate = serializers.FloatField()
    total_time_slots = serializers.IntegerField()
    most_popular_slot = serializers.DictField(allow_null=True)


class EventDashboardSerializer(serializers.Serializer):
    """이벤트 대시보드 전체 응답 Serializer"""
    event_id = serializers.IntegerField()
    event_title = serializers.CharField()
    stats = DashboardStatsSerializer()
    participants = ParticipantStatusSerializer(many=True)
    heatmap = HeatmapSlotSerializer(many=True)


class CalendarExportSerializer(serializers.Serializer):
    """캘린더 내보내기 정보 Serializer"""
    event_id = serializers.IntegerField()
    event_title = serializers.CharField()
    has_final_choice = serializers.BooleanField()

    # 확정된 시간 정보
    final_start_datetime = serializers.DateTimeField(allow_null=True)
    final_end_datetime = serializers.DateTimeField(allow_null=True)
    final_start_datetime_local = serializers.CharField(allow_null=True)
    final_end_datetime_local = serializers.CharField(allow_null=True)

    # Google Calendar 링크
    google_calendar_url = serializers.CharField(allow_null=True)

    # .ics 파일 다운로드 URL
    ics_download_url = serializers.CharField()

    message = serializers.CharField()
