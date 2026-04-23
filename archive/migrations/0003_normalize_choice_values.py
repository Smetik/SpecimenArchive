from django.db import migrations


SPECIMEN_STATUS_MAP = {
    'Холодное хранилище': 'Контур содержания II',
    'Сектор наблюдения': 'Наблюдение',
    'св': 'Контур содержания II',
}

THREAT_LEVEL_MAP = {
    'свив': 'Средний',
}

INCIDENT_SEVERITY_MAP = {
    'свсвв': 'Средний',
}

INCIDENT_PROTOCOL_MAP = {
    'Изоляция': 'Изолировать',
    'свс': 'Наблюдение',
}


def normalize_choice_values(apps, schema_editor):
    Specimen = apps.get_model('archive', 'Specimen')
    Incident = apps.get_model('archive', 'Incident')

    for specimen in Specimen.objects.all():
        updated_fields = []
        if specimen.status in SPECIMEN_STATUS_MAP:
            specimen.status = SPECIMEN_STATUS_MAP[specimen.status]
            updated_fields.append('status')
        if specimen.threat_level in THREAT_LEVEL_MAP:
            specimen.threat_level = THREAT_LEVEL_MAP[specimen.threat_level]
            updated_fields.append('threat_level')
        if updated_fields:
            specimen.save(update_fields=updated_fields)

    for incident in Incident.objects.all():
        updated_fields = []
        if incident.severity in INCIDENT_SEVERITY_MAP:
            incident.severity = INCIDENT_SEVERITY_MAP[incident.severity]
            updated_fields.append('severity')
        if incident.response_protocol in INCIDENT_PROTOCOL_MAP:
            incident.response_protocol = INCIDENT_PROTOCOL_MAP[incident.response_protocol]
            updated_fields.append('response_protocol')
        if updated_fields:
            incident.save(update_fields=updated_fields)


def reverse_normalize_choice_values(apps, schema_editor):
    return None


class Migration(migrations.Migration):

    dependencies = [
        ('archive', '0002_alter_incident_response_protocol_and_more'),
    ]

    operations = [
        migrations.RunPython(normalize_choice_values, reverse_normalize_choice_values),
    ]
