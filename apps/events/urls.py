from django.urls import path
from apps.participants.views import ParticipantCreateView, ParticipantListView
from .views import (
    EventCreateView, EventDetailView, MyEventListView, EventUpdateView,
    EventSummaryView, FinalChoiceView, SendFinalChoiceEmailView, TimeRecommendationView,
    EventQRCodeView, EventShareInfoView, EventInviteEmailView, EventDashboardView
)

app_name = 'events'

urlpatterns = [
    path('', EventCreateView.as_view(), name='event-create'),
    path('my/', MyEventListView.as_view(), name='my-events'),
    path('<int:pk>/', EventUpdateView.as_view(), name='event-update'),
    path('<int:pk>/summary/', EventSummaryView.as_view(), name='event-summary'),
    path('<int:pk>/final-choice', FinalChoiceView.as_view(), name='final-choice'),
    path('<int:pk>/final-choice/send-email', SendFinalChoiceEmailView.as_view(), name='send-final-choice-email'),
    path('<int:event_id>/recommend-time', TimeRecommendationView.as_view(), name='recommend-time'),
    path('<int:event_id>/qr-code', EventQRCodeView.as_view(), name='qr-code'),
    path('<int:event_id>/share-info', EventShareInfoView.as_view(), name='share-info'),
    path('<int:event_id>/invite', EventInviteEmailView.as_view(), name='invite'),
    path('<int:event_id>/dashboard', EventDashboardView.as_view(), name='dashboard'),
    path('<slug:slug>/', EventDetailView.as_view(), name='event-detail'),
    path('<slug:slug>/participants/', ParticipantCreateView.as_view(), name='participant-create'),
    path('<int:event_id>/participants', ParticipantListView.as_view(), name='participant-list'),
]
