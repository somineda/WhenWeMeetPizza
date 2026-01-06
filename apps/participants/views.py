from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from apps.events.models import Event
from .models import Participant
from .serializers import ParticipantSerializer


class ParticipantCreateView(generics.CreateAPIView):
    serializer_class = ParticipantSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        event = get_object_or_404(Event, slug=slug)

        # nickname 필수 체크
        if 'nickname' not in request.data or not request.data['nickname'].strip():
            return Response({
                'detail': 'empty_fields'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 닉네임 중복 체크
        nickname = request.data['nickname'].strip()
        if Participant.objects.filter(event=event, nickname=nickname).exists():
            return Response({
                'detail': '이미 존재하는 닉네임입니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data, context={'request': request, 'event': event})
        serializer.is_valid(raise_exception=True)
        participant = serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)
