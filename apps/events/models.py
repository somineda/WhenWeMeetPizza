from django.db import models
from django.conf import settings
from django.utils.text import slugify
import uuid


class Event(models.Model):
    slug = models.SlugField(unique=True, max_length=255, db_index=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_events', null=True, blank=True)

    # Date/Time range fields
    date_start = models.DateField(null=True, blank=True)
    date_end = models.DateField(null=True, blank=True)
    time_start = models.TimeField(null=True, blank=True)
    time_end = models.TimeField(null=True, blank=True)
    timezone = models.CharField(max_length=50, default='Asia/Seoul')
    deadline_at = models.DateTimeField(null=True, blank=True)

    is_deleted = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{uuid.uuid4().hex[:8]}")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'events'
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['-created_at']


class TimeSlot(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='time_slots')
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()

    def __str__(self):
        return f"{self.event.title}: {self.start_datetime} - {self.end_datetime}"

    class Meta:
        db_table = 'time_slots'
        verbose_name = 'Time Slot'
        verbose_name_plural = 'Time Slots'
        ordering = ['start_datetime']
        unique_together = ['event', 'start_datetime']


class FinalChoice(models.Model):
    event = models.OneToOneField(Event, on_delete=models.CASCADE, related_name='final_choice')
    slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='final_choices')
    chosen_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chosen_slots')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.event.title} - Final Choice: {self.slot}"

    class Meta:
        db_table = 'final_choices'
        verbose_name = 'Final Choice'
        verbose_name_plural = 'Final Choices'
        ordering = ['-created_at']
