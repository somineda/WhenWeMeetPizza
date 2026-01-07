from django.urls import path
from .views import ParticipantDeleteView, SubmitAvailabilityView

app_name = 'participants'

urlpatterns = [
    path('<int:pk>', ParticipantDeleteView.as_view(), name='participant-delete'),
    path('<int:participant_id>/availabilities/', SubmitAvailabilityView.as_view(), name='submit-availability'),
]
