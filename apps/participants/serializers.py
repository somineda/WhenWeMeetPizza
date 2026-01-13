from rest_framework import serializers
from .models import Participant, ParticipantAvailability
from apps.events.models import TimeSlot


class ParticipantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['id', 'nickname', 'email', 'phone', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ParticipantSerializer(serializers.ModelSerializer):
    event_id = serializers.IntegerField(source='event.id', read_only=True)
    participant_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Participant
        fields = ['participant_id', 'event_id', 'nickname', 'email', 'phone', 'created_at']
        read_only_fields = ['participant_id', 'event_id', 'created_at']

    def validate_nickname(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError("닉네임은 필수입니다.")
        return value.strip()

    def create(self, validated_data):
        request = self.context.get('request')
        event = self.context.get('event')

        # 로그인한 유저인 경우 user_id 연결
        if request and request.user.is_authenticated:
            validated_data['user'] = request.user

        validated_data['event'] = event

        try:
            return super().create(validated_data)
        except Exception as e:
            # UNIQUE constraint 위반 시
            if 'unique_event_nickname' in str(e).lower() or 'duplicate' in str(e).lower():
                raise serializers.ValidationError({"detail": "이미 존재하는 닉네임입니다."})
            raise


class SubmitAvailabilitySerializer(serializers.Serializer):
    available_slot_ids = serializers.ListField(
        child=serializers.IntegerField(),
        allow_empty=True,
        help_text="참여 가능한 타임슬롯 ID 리스트"
    )

    def validate_available_slot_ids(self, value):
        participant = self.context.get('participant')
        if not participant:
            raise serializers.ValidationError("참가자 정보가 필요합니다.")

        # 해당 이벤트의 타임슬롯인지 확인
        event_slot_ids = set(participant.event.time_slots.values_list('id', flat=True))
        invalid_slots = set(value) - event_slot_ids

        if invalid_slots:
            raise serializers.ValidationError(
                f"유효하지 않은 타임슬롯 ID: {list(invalid_slots)}"
            )

        return value

    def save(self):
        participant = self.context.get('participant')
        available_slot_ids = self.validated_data['available_slot_ids']

        # 기존 availabilities 모두 삭제
        ParticipantAvailability.objects.filter(participant=participant).delete()

        # 새로운 availabilities 생성
        availabilities = [
            ParticipantAvailability(
                participant=participant,
                time_slot_id=slot_id,
                is_available=True
            )
            for slot_id in available_slot_ids
        ]

        ParticipantAvailability.objects.bulk_create(availabilities)

        return {
            'participant_id': participant.id,
            'event_id': participant.event.id,
            'submitted_count': len(available_slot_ids),
            'available_slot_ids': available_slot_ids
        }


class AvailabilityRetrieveSerializer(serializers.Serializer):
    participant_id = serializers.IntegerField()
    participant_nickname = serializers.CharField()
    event_id = serializers.IntegerField()
    available_slot_ids = serializers.ListField(child=serializers.IntegerField())
    total_available = serializers.IntegerField()

    def to_representation(self, participant):
        # 참가자의 가능한 타임슬롯 조회
        available_slots = ParticipantAvailability.objects.filter(
            participant=participant,
            is_available=True
        ).values_list('time_slot_id', flat=True)

        return {
            'participant_id': participant.id,
            'participant_nickname': participant.nickname,
            'event_id': participant.event.id,
            'available_slot_ids': list(available_slots),
            'total_available': len(available_slots)
        }
