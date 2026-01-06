from rest_framework import serializers
from .models import Participant


class ParticipantListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participant
        fields = ['id', 'nickname', 'email', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class ParticipantSerializer(serializers.ModelSerializer):
    event_id = serializers.IntegerField(source='event.id', read_only=True)
    participant_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Participant
        fields = ['participant_id', 'event_id', 'nickname', 'email', 'created_at']
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
