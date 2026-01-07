from django.contrib import admin
from .models import Participant, ParticipantAvailability


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['id', 'event', 'nickname', 'user', 'email', 'created_at']
    list_filter = ['event', 'created_at']
    search_fields = ['nickname', 'email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ParticipantAvailability)
class ParticipantAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['id', 'participant', 'time_slot', 'is_available', 'created_at']
    list_filter = ['is_available', 'participant__event', 'created_at']
    search_fields = ['participant__nickname']
    readonly_fields = ['created_at']
