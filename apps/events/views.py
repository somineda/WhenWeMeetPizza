from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Event
from .serializers import EventSerializer, EventDetailSerializer, MyEventListSerializer, EventUpdateSerializer, EventSummarySerializer
from .pagination import EventPagination


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
