from rest_framework import serializers
from django.conf import settings
from datetime import datetime, timedelta
from django.utils import timezone
import pytz
from .models import Event, TimeSlot


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

    class Meta:
        model = Event
        fields = [
            'id', 'slug', 'title', 'description',
            'date_start', 'date_end', 'time_start', 'time_end',
            'timezone', 'deadline_at', 'organizer_id',
            'created_at', 'url', 'time_slots_count'
        ]
        read_only_fields = ['id', 'slug', 'created_at', 'organizer_id', 'url', 'time_slots_count']

    def get_time_slots_count(self, obj):
        """생성된 타임슬롯 개수"""
        return obj.time_slots.count()

    def get_url(self, obj):
        frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
        return f"{frontend_url}/e/{obj.slug}"

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
