from django.urls import path
from .views import ParticipantDeleteView, AvailabilityView

app_name = 'participants'

urlpatterns = [
    path('<int:pk>', ParticipantDeleteView.as_view(), name='participant-delete'),
    path('<int:participant_id>/availabilities/', AvailabilityView.as_view(), name='availability'),
]
