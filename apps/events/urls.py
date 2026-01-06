from django.urls import path
from apps.participants.views import ParticipantCreateView

app_name = 'events'

urlpatterns = [
    path('<slug:slug>/participants/', ParticipantCreateView.as_view(), name='participant-create'),
]
