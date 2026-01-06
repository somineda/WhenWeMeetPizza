from django.urls import path
from apps.participants.views import ParticipantCreateView, ParticipantListView

app_name = 'events'

urlpatterns = [
    path('<slug:slug>/participants/', ParticipantCreateView.as_view(), name='participant-create'),
    path('<int:event_id>/participants', ParticipantListView.as_view(), name='participant-list'),
]
