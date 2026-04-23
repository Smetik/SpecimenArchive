from django.contrib import admin

from .models import Incident, ResolutionLog, Specimen


@admin.register(Specimen)
class SpecimenAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'name',
        'status',
        'threat_level',
        'is_active',
        'created_at',
    )
    search_fields = ('code', 'name')
    list_filter = ('status', 'threat_level', 'is_active')


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'specimen',
        'response_protocol',
        'severity',
        'is_resolved',
        'created_at',
    )
    search_fields = ('title', 'specimen__code', 'specimen__name')
    list_filter = ('severity', 'is_resolved', 'specimen__status', 'specimen__threat_level')


@admin.register(ResolutionLog)
class ResolutionLogAdmin(admin.ModelAdmin):
    list_display = (
        'specimen',
        'incident',
        'selected_role',
        'selected_protocol',
        'recommended_protocol',
        'outcome',
        'final_status_text',
        'completed_at',
    )
    search_fields = ('specimen__code', 'specimen__name', 'incident__title', 'result_summary', 'system_note')
    list_filter = ('outcome', 'selected_role', 'selected_protocol', 'recommended_protocol', 'ui_theme_state')
