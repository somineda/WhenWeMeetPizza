from django.db import models
from django.conf import settings
from apps.events.models import Event


class Participant(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='participations')
    nickname = models.CharField(max_length=50)
    email = models.EmailField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

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
