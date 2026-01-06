from django.contrib import admin
from .models import Event, TimeSlot


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'slug', 'date_start', 'date_end', 'created_at']
    search_fields = ['title', 'slug']
    readonly_fields = ['created_at', 'updated_at']
    prepopulated_fields = {'slug': ('title',)}


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['id', 'event', 'start_datetime', 'end_datetime']
    list_filter = ['event']
    search_fields = ['event__title']
    readonly_fields = ['event', 'start_datetime', 'end_datetime']
