from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied, ValidationError
from django.shortcuts import get_object_or_404
from .models import Event, FinalChoice
from .serializers import EventSerializer, EventDetailSerializer, MyEventListSerializer, EventUpdateSerializer, EventSummarySerializer, FinalChoiceSerializer
from .pagination import EventPagination
from .tasks import send_final_choice_email


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

        # 자동으로 확정 이메일 발송 (비동기)
        try:
            send_final_choice_email.delay(event_id)
        except Exception:
            # Celery 연결 실패 시 무시
            pass

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

        # Celery task로 이메일 발송 (비동기)
        try:
            send_final_choice_email.delay(event_id)
        except Exception as e:
            # Celery 연결 실패 시 동기적으로 이메일 발송
            # 또는 나중에 재시도할 수 있도록 큐에 저장
            pass

        return Response(
            {"detail": "이메일 전송이 완료되었습니다"},
            status=status.HTTP_200_OK
        )
