from django.urls import path
from apps.participants.views import ParticipantCreateView, ParticipantListView
from .views import EventCreateView, EventDetailView, MyEventListView

app_name = 'events'

urlpatterns = [
    path('', EventCreateView.as_view(), name='event-create'),
    path('my/', MyEventListView.as_view(), name='my-events'),
    path('<slug:slug>/', EventDetailView.as_view(), name='event-detail'),
    path('<slug:slug>/participants/', ParticipantCreateView.as_view(), name='participant-create'),
    path('<int:event_id>/participants', ParticipantListView.as_view(), name='participant-list'),
]
