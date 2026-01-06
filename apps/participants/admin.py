from django.contrib import admin
from .models import Participant


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['id', 'event', 'nickname', 'user', 'email', 'created_at']
    list_filter = ['event', 'created_at']
    search_fields = ['nickname', 'email']
    readonly_fields = ['created_at']
