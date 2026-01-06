from django.urls import path
from .views import ParticipantDeleteView

app_name = 'participants'

urlpatterns = [
    path('<int:pk>', ParticipantDeleteView.as_view(), name='participant-delete'),
]
