from django.urls import path
from apps.participants.views import ParticipantCreateView, ParticipantListView
from .views import EventCreateView, EventDetailView, MyEventListView, EventUpdateView, EventSummaryView, FinalChoiceCreateView

app_name = 'events'

urlpatterns = [
    path('', EventCreateView.as_view(), name='event-create'),
    path('my/', MyEventListView.as_view(), name='my-events'),
    path('<int:pk>/', EventUpdateView.as_view(), name='event-update'),
    path('<int:pk>/summary/', EventSummaryView.as_view(), name='event-summary'),
    path('<int:pk>/final-choice', FinalChoiceCreateView.as_view(), name='final-choice-create'),
    path('<slug:slug>/', EventDetailView.as_view(), name='event-detail'),
    path('<slug:slug>/participants/', ParticipantCreateView.as_view(), name='participant-create'),
    path('<int:event_id>/participants', ParticipantListView.as_view(), name='participant-list'),
]
