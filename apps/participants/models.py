from django.db import models
from django.conf import settings
from apps.events.models import Event, TimeSlot


class Participant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='participations')
    nickname = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.nickname} @ {self.event.title}"

    class Meta:
        db_table = 'participants'
        verbose_name = 'Participant'
        verbose_name_plural = 'Participants'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['event', 'nickname'], name='unique_event_nickname')
        ]


class ParticipantAvailability(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='availabilities')
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='availabilities')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.participant.nickname} - {self.time_slot} ({'O' if self.is_available else 'X'})"

    class Meta:
        db_table = 'participant_availabilities'
        verbose_name = 'Participant Availability'
        verbose_name_plural = 'Participant Availabilities'
        ordering = ['time_slot__start_datetime']
        unique_together = ['participant', 'time_slot']
