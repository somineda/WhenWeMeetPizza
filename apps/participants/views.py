from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from apps.events.models import Event
from .models import Participant
from .serializers import ParticipantSerializer, ParticipantListSerializer, SubmitAvailabilitySerializer, AvailabilityRetrieveSerializer
from .pagination import ParticipantPagination


class ParticipantCreateView(generics.CreateAPIView):
    serializer_class = ParticipantSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        event = get_object_or_404(Event, slug=slug)

        # nickname 필수 체크
        if 'nickname' not in request.data or not request.data['nickname'].strip():
            return Response({
                'detail': '닉네임을 입력해주세요'
            }, status=status.HTTP_400_BAD_REQUEST)

        nickname = request.data['nickname'].strip()
        email = request.data.get('email', '').strip() if request.data.get('email') else None

        # 익명 참가(비로그인) 시 이메일 필수
        if not request.user.is_authenticated and not email:
            return Response({
                'detail': '이메일을 입력해주세요'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 로그인한 사용자가 이메일과 함께 참가하는 경우
        # 같은 이벤트에서 같은 이메일을 가진 익명 참가자가 있으면 자동 연결
        existing_participant = None
        if request.user.is_authenticated and email:
            existing_participant = Participant.objects.filter(
                event=event,
                email=email,
                user__isnull=True
            ).first()

        # 닉네임 중복 체크 (기존 익명 참가자를 업데이트하는 경우 제외)
        nickname_query = Participant.objects.filter(event=event, nickname=nickname)
        if existing_participant:
            nickname_query = nickname_query.exclude(id=existing_participant.id)

        if nickname_query.exists():
            return Response({
                'detail': '이미 존재하는 닉네임입니다.'
            }, status=status.HTTP_400_BAD_REQUEST)

        # 기존 익명 참가자가 있으면 업데이트 (계정 연결)
        if existing_participant:
            existing_participant.user = request.user
            existing_participant.nickname = nickname
            existing_participant.save()

            serializer = self.get_serializer(existing_participant)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # 새로운 참가자 생성
        serializer = self.get_serializer(data=request.data, context={'request': request, 'event': event})
        serializer.is_valid(raise_exception=True)
        participant = serializer.save()

        return Response(serializer.data, status=status.HTTP_200_OK)


class ParticipantListView(generics.ListAPIView):
    serializer_class = ParticipantListSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ParticipantPagination

    def get_queryset(self):
        event_id = self.kwargs.get('event_id')
        return Participant.objects.filter(event_id=event_id).order_by('-created_at')


class ParticipantDeleteView(generics.DestroyAPIView):
    queryset = Participant.objects.all()
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def destroy(self, request, *args, **kwargs):
        participant = self.get_object()

        # 권한 체크: 본인만 삭제 가능
        if participant.user != request.user:
            raise PermissionDenied("이 참가자를 삭제할 권한이 없습니다.")

        participant.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AvailabilityView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return AvailabilityRetrieveSerializer
        return SubmitAvailabilitySerializer

    def get(self, request, *args, **kwargs):
        """가능 시간 조회"""
        participant_id = self.kwargs.get('participant_id')
        participant = get_object_or_404(Participant, id=participant_id)

        serializer = AvailabilityRetrieveSerializer(participant)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """가능 시간 저장"""
        participant_id = self.kwargs.get('participant_id')
        participant = get_object_or_404(Participant, id=participant_id)

        # 권한 체크: 로그인한 사용자는 본인의 참가자만, 익명은 누구나 가능
        if request.user.is_authenticated:
            # 로그인한 경우, 본인의 참가자인지 확인
            if participant.user and participant.user != request.user:
                raise PermissionDenied("이 참가자의 가능 시간을 제출할 권한이 없습니다.")

        serializer = SubmitAvailabilitySerializer(
            data=request.data,
            context={'participant': participant, 'request': request}
        )
        serializer.is_valid(raise_exception=True)
        result = serializer.save()

        return Response(result, status=status.HTTP_200_OK)
