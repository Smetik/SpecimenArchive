from django.contrib import messages
from django.db import transaction
from django.db.models import Prefetch
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from .forms import IncidentForm, SpecimenForm
from .models import Incident, ResolutionLog, Specimen


PROTOCOL_STRENGTH = {
    Incident.ResponseProtocol.OBSERVE: 1,
    Incident.ResponseProtocol.ISOLATE: 2,
    Incident.ResponseProtocol.QUARANTINE: 3,
}

SEVERITY_STRENGTH = {
    Incident.Severity.LOW: 1,
    Incident.Severity.MEDIUM: 1,
    Incident.Severity.HIGH: 2,
    Incident.Severity.CRITICAL: 3,
}

THREAT_STRENGTH = {
    Specimen.ThreatLevel.LOW: 1,
    Specimen.ThreatLevel.MEDIUM: 1,
    Specimen.ThreatLevel.HIGH: 2,
    Specimen.ThreatLevel.CRITICAL: 3,
}

SEVERITY_SCALE = [
    Incident.Severity.LOW,
    Incident.Severity.MEDIUM,
    Incident.Severity.HIGH,
    Incident.Severity.CRITICAL,
]

THREAT_SCALE = [
    Specimen.ThreatLevel.LOW,
    Specimen.ThreatLevel.MEDIUM,
    Specimen.ThreatLevel.HIGH,
    Specimen.ThreatLevel.CRITICAL,
]

OUTCOME_PRESENTATION = {
    ResolutionLog.Outcome.SUCCESS: {
        'title': 'Контур стабилизирован',
        'status': 'Стабилизирован',
        'theme': ResolutionLog.ThemeState.SUCCESS,
        'summary': 'Протокол сработал штатно. Активный инцидент закрыт, параметры возвращены в допустимый диапазон.',
        'note': 'Система подтверждает переход образца в контролируемую фазу.',
    },
    ResolutionLog.Outcome.PARTIAL: {
        'title': 'Ситуация удержана под контролем',
        'status': 'Под наблюдением',
        'theme': ResolutionLog.ThemeState.PARTIAL,
        'summary': 'Контур удержан, но инцидент не закрыт полностью. Требуется дополнительная сверка и расширенное наблюдение.',
        'note': 'Система оставляет инцидент активным до повторной оценки параметров.',
    },
    ResolutionLog.Outcome.ESCALATION: {
        'title': 'Система фиксирует эскалацию',
        'status': 'Эскалация',
        'theme': ResolutionLog.ThemeState.ESCALATION,
        'summary': 'Выбранный протокол оказался недостаточным. Риск повышен, инцидент остаётся активным в более жёстком режиме.',
        'note': 'Требуется повторное вмешательство с усилением мер содержания.',
    },
    ResolutionLog.Outcome.REVIEW_ONLY: {
        'title': 'Открыт режим просмотра',
        'status': 'Режим просмотра',
        'theme': ResolutionLog.ThemeState.REVIEW,
        'summary': 'Активный инцидент не найден. Досье открыто только для просмотра без оперативного вмешательства.',
        'note': 'Система зафиксировала просмотр без изменения параметров содержания.',
    },
}

ROLE_PRESENTATION = {
    ResolutionLog.Role.RESEARCHER: {
        'summary': 'Исследовательский доступ усилил аналитическую интерпретацию результата и влияние мер на сохранность материала.',
        'note': 'Сеанс выполнен в аналитическом контуре с акцентом на свойства образца.',
    },
    ResolutionLog.Role.OPERATOR: {
        'summary': 'Операторский доступ зафиксировал влияние решения на режим содержания и оперативный контроль.',
        'note': 'Сеанс выполнен в оперативном контуре с приоритетом удержания среды.',
    },
    ResolutionLog.Role.OBSERVER: {
        'summary': 'Наблюдательный доступ сохранил акцент на мониторинге, ограничениях и повторной проверке.',
        'note': 'Сеанс выполнен в наблюдательном контуре без расширения полномочий.',
    },
}

ROLE_ALLOWED_PROTOCOLS = {
    ResolutionLog.Role.OBSERVER: [Incident.ResponseProtocol.OBSERVE],
    ResolutionLog.Role.RESEARCHER: [Incident.ResponseProtocol.OBSERVE, Incident.ResponseProtocol.QUARANTINE],
    ResolutionLog.Role.OPERATOR: [Incident.ResponseProtocol.ISOLATE, Incident.ResponseProtocol.QUARANTINE],
}


def normalize_search_text(value):
    if not value:
        return ''
    return ' '.join(str(value).casefold().replace('ё', 'е').split())


def contains_normalized_text(*values, query=''):
    normalized_query = normalize_search_text(query)
    if not normalized_query:
        return True
    haystack = ' '.join(normalize_search_text(value) for value in values if value)
    return normalized_query in haystack


def get_specimen_queryset():
    return Specimen.objects.prefetch_related(
        Prefetch('incidents', queryset=Incident.objects.order_by('-created_at'), to_attr='prefetched_incidents'),
        Prefetch(
            'resolution_logs',
            queryset=ResolutionLog.objects.select_related('incident').order_by('-completed_at', '-created_at'),
            to_attr='prefetched_resolution_logs',
        ),
    )


def get_incident_queryset():
    return Incident.objects.select_related('specimen').prefetch_related(
        Prefetch(
            'resolution_logs',
            queryset=ResolutionLog.objects.select_related('specimen').order_by('-completed_at', '-created_at'),
            to_attr='prefetched_resolution_logs',
        )
    )


def hydrate_specimen_state(specimens):
    hydrated = []
    for specimen in specimens:
        incidents = list(getattr(specimen, 'prefetched_incidents', []))
        logs = list(getattr(specimen, 'prefetched_resolution_logs', []))
        specimen.prefetched_active_incident = next(
            (incident for incident in incidents if not incident.is_resolved),
            None,
        )
        specimen.prefetched_latest_resolution = logs[0] if logs else None
        specimen.prefetched_history = logs
        hydrated.append(specimen)
    return hydrated


def hydrate_incident_state(incidents):
    hydrated = []
    for incident in incidents:
        logs = list(getattr(incident, 'prefetched_resolution_logs', []))
        incident.prefetched_latest_resolution = logs[0] if logs else None
        incident.prefetched_history = logs
        hydrated.append(incident)
    return hydrated


def severity_to_required_strength(severity):
    return SEVERITY_STRENGTH.get(severity, 1)


def threat_to_required_strength(threat_level):
    return THREAT_STRENGTH.get(threat_level, 1)


def protocol_from_strength(strength):
    if strength >= 3:
        return Incident.ResponseProtocol.QUARANTINE
    if strength == 2:
        return Incident.ResponseProtocol.ISOLATE
    return Incident.ResponseProtocol.OBSERVE


def get_formula_protocol(specimen, incident):
    if not incident:
        return ''
    required_strength = max(
        severity_to_required_strength(incident.severity),
        threat_to_required_strength(specimen.threat_level),
    )
    return protocol_from_strength(required_strength)


def get_manual_protocol(incident):
    if not incident:
        return ''
    if incident.response_protocol in PROTOCOL_STRENGTH:
        return incident.response_protocol
    return ''


def get_protocol_profile(specimen, incident):
    if not incident:
        return {
            'manual_protocol': '',
            'manual_concrete_protocol': '',
            'formula_protocol': '',
            'effective_recommended_protocol': '',
            'formula_strength': 0,
            'effective_strength': 0,
            'manual_is_auto': False,
            'manual_differs': False,
        }

    formula_protocol = get_formula_protocol(specimen, incident)
    formula_strength = PROTOCOL_STRENGTH.get(formula_protocol, 0)
    manual_protocol = incident.response_protocol or Incident.ResponseProtocol.AUTO
    manual_concrete_protocol = get_manual_protocol(incident)
    manual_is_auto = manual_protocol == Incident.ResponseProtocol.AUTO or not manual_concrete_protocol

    if manual_is_auto:
        effective_protocol = formula_protocol
    else:
        effective_protocol = protocol_from_strength(
            max(PROTOCOL_STRENGTH.get(manual_concrete_protocol, 0), formula_strength)
        )

    return {
        'manual_protocol': manual_protocol,
        'manual_concrete_protocol': manual_concrete_protocol,
        'formula_protocol': formula_protocol,
        'effective_recommended_protocol': effective_protocol,
        'formula_strength': formula_strength,
        'effective_strength': PROTOCOL_STRENGTH.get(effective_protocol, 0),
        'manual_is_auto': manual_is_auto,
        'manual_differs': bool(manual_concrete_protocol and manual_concrete_protocol != formula_protocol),
    }


def shift_level(value, scale, delta):
    try:
        index = scale.index(value)
    except ValueError:
        return value
    new_index = max(0, min(len(scale) - 1, index + delta))
    return scale[new_index]


def derive_specimen_status(threat_level, outcome):
    if outcome == ResolutionLog.Outcome.ESCALATION:
        if threat_level == Specimen.ThreatLevel.CRITICAL:
            return Specimen.Status.QUARANTINE
        if threat_level == Specimen.ThreatLevel.HIGH:
            return Specimen.Status.CONTAINMENT_IV
        if threat_level == Specimen.ThreatLevel.MEDIUM:
            return Specimen.Status.CONTAINMENT_III
        return Specimen.Status.CONTAINMENT_II

    if outcome == ResolutionLog.Outcome.PARTIAL:
        if threat_level in {Specimen.ThreatLevel.CRITICAL, Specimen.ThreatLevel.HIGH}:
            return Specimen.Status.CONTAINMENT_IV
        if threat_level == Specimen.ThreatLevel.MEDIUM:
            return Specimen.Status.CONTAINMENT_III
        return Specimen.Status.CONTAINMENT_II

    if threat_level == Specimen.ThreatLevel.LOW:
        return Specimen.Status.OBSERVATION
    if threat_level == Specimen.ThreatLevel.MEDIUM:
        return Specimen.Status.CONTAINMENT_II
    if threat_level == Specimen.ThreatLevel.HIGH:
        return Specimen.Status.CONTAINMENT_III
    return Specimen.Status.CONTAINMENT_IV


def build_outcome(selected_protocol, effective_recommended_protocol, formula_protocol, incident):
    if not incident:
        return ResolutionLog.Outcome.REVIEW_ONLY

    formula_strength = PROTOCOL_STRENGTH.get(formula_protocol, 0)
    selected_strength = PROTOCOL_STRENGTH.get(selected_protocol, 0)

    if selected_protocol == effective_recommended_protocol:
        return ResolutionLog.Outcome.SUCCESS
    if selected_strength >= formula_strength:
        return ResolutionLog.Outcome.PARTIAL
    return ResolutionLog.Outcome.ESCALATION


def build_result_texts(role, outcome, specimen, incident, selected_protocol, effective_recommended_protocol):
    role_data = ROLE_PRESENTATION.get(role, ROLE_PRESENTATION[ResolutionLog.Role.OBSERVER])
    outcome_data = OUTCOME_PRESENTATION[outcome]
    incident_title = incident.title if incident else f'Просмотр досье {specimen.code}'

    result_summary = (
        f'{incident_title}: выбран протокол «{selected_protocol or "не применялся"}». '
        f'{outcome_data["summary"]}'
    )
    system_note = (
        f'{role_data["note"]} Рекомендованный протокол: '
        f'«{effective_recommended_protocol or "не требуется"}». {outcome_data["note"]}'
    )
    return {
        'result_title': outcome_data['title'],
        'final_status_text': outcome_data['status'],
        'result_summary': result_summary,
        'system_note': system_note,
        'role_summary': role_data['summary'],
        'theme_state': outcome_data['theme'],
    }


def describe_outcome_reason(
    incident,
    effective_recommended_protocol,
    outcome,
):
    if not incident:
        return 'Активный инцидент не найден. Система открыла досье в режиме просмотра и зафиксировала факт доступа.'

    if outcome == ResolutionLog.Outcome.SUCCESS:
        return (
            'Выбранный протокол совпал с ожидаемым сценарием реагирования. '
            'Система зафиксировала стабилизацию.'
        )
    if outcome == ResolutionLog.Outcome.PARTIAL:
        return (
            'Выбранный протокол оказался допустимым, но не оптимальным для текущей фазы инцидента. '
            'Контур удержан, однако ситуация требует дополнительного контроля.'
        )
    return (
        'Выбранный протокол оказался недостаточным для текущей фазы инцидента. '
        'Система фиксирует эскалацию и переводит объект в более жёсткий режим.'
        if effective_recommended_protocol
        else 'Система зафиксировала эскалацию текущего инцидента.'
    )


def get_role_protocols(role):
    return ROLE_ALLOWED_PROTOCOLS.get(role, ROLE_ALLOWED_PROTOCOLS[ResolutionLog.Role.OBSERVER])


def get_specimen_filter_context(request):
    return {
        'status_options': [value for value, _ in Specimen.Status.choices],
        'threat_level_options': [value for value, _ in Specimen.ThreatLevel.choices],
        'filters': {
            'q': request.GET.get('q', '').strip(),
            'status': request.GET.get('status', '').strip(),
            'threat_level': request.GET.get('threat_level', '').strip(),
            'activity': request.GET.get('activity', 'all').strip() or 'all',
        },
    }


def get_incident_filter_context(request):
    return {
        'severity_options': [value for value, _ in Incident.Severity.choices],
        'specimen_options': Specimen.objects.order_by('code'),
        'incident_filters': {
            'q': request.GET.get('q', '').strip(),
            'severity': request.GET.get('severity', '').strip(),
            'resolved': request.GET.get('resolved', 'all').strip() or 'all',
            'specimen': request.GET.get('specimen', '').strip(),
        },
    }


def get_specimen_count_text(count):
    if count == 1:
        return 'Найдена 1 запись'
    if 2 <= count <= 4:
        return f'Найдено {count} записи'
    return f'Найдено {count} записей'


def get_incident_count_text(count):
    if count == 1:
        return 'Найден 1 инцидент'
    if 2 <= count <= 4:
        return f'Найдено {count} инцидента'
    return f'Найдено {count} инцидентов'


def get_filtered_specimens(request):
    queryset = get_specimen_queryset()
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    threat_level = request.GET.get('threat_level', '').strip()
    activity = request.GET.get('activity', 'all').strip() or 'all'

    if status:
        queryset = queryset.filter(status=status)
    if threat_level:
        queryset = queryset.filter(threat_level=threat_level)
    if activity == 'active':
        queryset = queryset.filter(is_active=True)
    elif activity == 'inactive':
        queryset = queryset.filter(is_active=False)

    specimens = hydrate_specimen_state(list(queryset.order_by('code')))
    if query:
        specimens = [
            specimen for specimen in specimens
            if contains_normalized_text(specimen.code, specimen.name, query=query)
        ]
    return specimens


def get_filtered_incidents(request):
    queryset = get_incident_queryset()
    query = request.GET.get('q', '').strip()
    severity = request.GET.get('severity', '').strip()
    resolved = request.GET.get('resolved', 'all').strip() or 'all'
    specimen = request.GET.get('specimen', '').strip()

    if severity:
        queryset = queryset.filter(severity=severity)
    if resolved == 'resolved':
        queryset = queryset.filter(is_resolved=True)
    elif resolved == 'open':
        queryset = queryset.filter(is_resolved=False)
    if specimen:
        queryset = queryset.filter(specimen_id=specimen)

    incidents = hydrate_incident_state(list(queryset.order_by('-created_at')))
    if query:
        incidents = [
            incident for incident in incidents
            if contains_normalized_text(incident.title, incident.description, query=query)
        ]
    return incidents


def get_home_priority():
    active_incidents = Incident.objects.filter(is_resolved=False)
    if active_incidents.filter(severity=Incident.Severity.CRITICAL).exists():
        return 'Локализация критических биоинцидентов'
    if active_incidents.filter(severity=Incident.Severity.HIGH).exists():
        return 'Контроль активных биоинцидентов'
    if active_incidents.exists():
        return 'Мониторинг нестабильных образцов'
    return 'Плановый мониторинг архива'


def home(request):
    specimens = hydrate_specimen_state(list(get_specimen_queryset().filter(is_active=True).order_by('code')))
    recent_logs = ResolutionLog.objects.select_related('specimen', 'incident')[:8]
    return render(
        request,
        'archive/home.html',
        {
            'specimens': specimens,
            'recent_logs': recent_logs,
            'current_priority': get_home_priority(),
        },
    )


class SuccessMessageMixin:
    success_message = ''

    def form_valid(self, form):
        response = super().form_valid(form)
        if self.success_message:
            messages.success(self.request, self.success_message)
        return response


class DeleteSuccessMessageMixin:
    success_message = ''

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        if self.success_message:
            messages.success(request, self.success_message)
        return response


class SpecimenListView(ListView):
    model = Specimen
    template_name = 'archive/specimen_list.html'
    context_object_name = 'specimens'

    def get_queryset(self):
        return get_filtered_specimens(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_specimen_filter_context(self.request))
        context['specimen_count'] = len(context['specimens'])
        context['specimen_count_text'] = get_specimen_count_text(context['specimen_count'])
        return context


class SpecimenDetailView(DetailView):
    model = Specimen
    template_name = 'archive/specimen_detail.html'
    context_object_name = 'specimen'

    def get_queryset(self):
        return get_specimen_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        specimen = hydrate_specimen_state([context['specimen']])[0]
        context['specimen'] = specimen
        context['latest_session'] = specimen.latest_resolution
        context['resolution_history'] = specimen.prefetched_history[:8]
        return context


class SpecimenCreateView(SuccessMessageMixin, CreateView):
    model = Specimen
    form_class = SpecimenForm
    template_name = 'archive/specimen_form.html'
    success_message = 'Запись успешно создана.'


class SpecimenUpdateView(SuccessMessageMixin, UpdateView):
    model = Specimen
    form_class = SpecimenForm
    template_name = 'archive/specimen_form.html'
    success_message = 'Запись успешно изменена.'


class SpecimenDeleteView(DeleteSuccessMessageMixin, DeleteView):
    model = Specimen
    template_name = 'archive/specimen_confirm_delete.html'
    success_url = reverse_lazy('specimen_list')
    success_message = 'Запись успешно удалена.'


class IncidentListView(ListView):
    model = Incident
    template_name = 'archive/incident_list.html'
    context_object_name = 'incidents'

    def get_queryset(self):
        return get_filtered_incidents(self.request)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(get_incident_filter_context(self.request))
        context['incident_count'] = len(context['incidents'])
        context['incident_count_text'] = get_incident_count_text(context['incident_count'])
        return context


class IncidentDetailView(DetailView):
    model = Incident
    template_name = 'archive/incident_detail.html'
    context_object_name = 'incident'

    def get_queryset(self):
        return get_incident_queryset()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        incident = hydrate_incident_state([context['incident']])[0]
        context['incident'] = incident
        context['resolution_history'] = incident.prefetched_history[:8]
        return context


class IncidentCreateView(SuccessMessageMixin, CreateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'archive/incident_form.html'
    success_message = 'Запись успешно создана.'


class IncidentUpdateView(SuccessMessageMixin, UpdateView):
    model = Incident
    form_class = IncidentForm
    template_name = 'archive/incident_form.html'
    success_message = 'Запись успешно изменена.'


class IncidentDeleteView(DeleteSuccessMessageMixin, DeleteView):
    model = Incident
    template_name = 'archive/incident_confirm_delete.html'
    success_url = reverse_lazy('incident_list')
    success_message = 'Запись успешно удалена.'


class ResolutionLogDetailView(DetailView):
    model = ResolutionLog
    template_name = 'archive/resolutionlog_detail.html'
    context_object_name = 'session'

    def get_queryset(self):
        return ResolutionLog.objects.select_related('specimen', 'incident')


def specimen_filter(request):
    specimens = get_filtered_specimens(request)
    html = render_to_string(
        'archive/includes/specimen_cards.html',
        {'specimens': specimens},
        request=request,
    )
    return JsonResponse(
        {
            'html': html,
            'count': len(specimens),
            'count_text': get_specimen_count_text(len(specimens)),
        }
    )


def incident_filter(request):
    incidents = get_filtered_incidents(request)
    html = render_to_string(
        'archive/includes/incident_cards.html',
        {'incidents': incidents},
        request=request,
    )
    return JsonResponse(
        {
            'html': html,
            'count': len(incidents),
            'count_text': get_incident_count_text(len(incidents)),
        }
    )


def render_post_session_fragments(request, specimen, incident):
    refreshed_specimen = hydrate_specimen_state([get_specimen_queryset().get(pk=specimen.pk)])[0]
    refreshed_incident = None
    if incident:
        refreshed_incident = hydrate_incident_state([get_incident_queryset().get(pk=incident.pk)])[0]
    active_incident = refreshed_specimen.active_incident

    return {
        'recent_activity_html': render_to_string(
            'archive/includes/activity_feed.html',
            {'recent_logs': ResolutionLog.objects.select_related('specimen', 'incident')[:8]},
            request=request,
        ),
        'specimen_history_html': render_to_string(
            'archive/includes/specimen_history.html',
            {
                'specimen': refreshed_specimen,
                'latest_session': refreshed_specimen.latest_resolution,
                'resolution_history': refreshed_specimen.prefetched_history[:8],
            },
            request=request,
        ),
        'incident_history_html': render_to_string(
            'archive/includes/incident_history.html',
            {
                'incident': refreshed_incident,
                'resolution_history': getattr(refreshed_incident, 'prefetched_history', [])[:8],
            },
            request=request,
        ) if refreshed_incident else '',
        'specimen_state': {
            'status': refreshed_specimen.status,
            'threat_level': refreshed_specimen.threat_level,
            'system_state': refreshed_specimen.current_system_state,
            'system_state_class': refreshed_specimen.current_system_state_class,
            'active_incident_id': active_incident.pk if active_incident else None,
            'active_incident': {
                'id': active_incident.pk,
                'title': active_incident.title,
                'description': active_incident.description,
                'severity': active_incident.severity,
                'response_protocol': active_incident.response_protocol,
                'is_resolved': active_incident.is_resolved,
                'created_at': timezone.localtime(active_incident.created_at).strftime('%d.%m.%Y %H:%M'),
            } if active_incident else None,
        },
        'incident_state': {
            'id': refreshed_incident.pk if refreshed_incident else None,
            'severity': refreshed_incident.severity if refreshed_incident else '',
            'is_resolved': refreshed_incident.is_resolved if refreshed_incident else False,
            'response_protocol': refreshed_incident.response_protocol if refreshed_incident else '',
            'system_state': refreshed_incident.current_system_state if refreshed_incident else 'Режим просмотра',
            'system_state_class': refreshed_incident.current_system_state_class if refreshed_incident else 'review',
        },
    }


def build_escalation_change_texts(
    previous_severity,
    new_severity,
    previous_threat_level,
    new_threat_level,
    previous_status,
    new_status,
):
    severity_text = (
        'Серьёзность инцидента остаётся на критическом уровне.'
        if previous_severity == Incident.Severity.CRITICAL and new_severity == Incident.Severity.CRITICAL
        else f'Серьёзность инцидента повышена: {previous_severity} → {new_severity}.'
    )
    threat_text = (
        'Уровень угрозы уже достиг максимума и не может быть повышен выше.'
        if previous_threat_level == Specimen.ThreatLevel.CRITICAL and new_threat_level == Specimen.ThreatLevel.CRITICAL
        else f'Уровень угрозы повышен: {previous_threat_level} → {new_threat_level}.'
    )
    status_text = (
        'Режим содержания сохраняется в аварийном контуре.'
        if previous_status == Specimen.Status.QUARANTINE and new_status == Specimen.Status.QUARANTINE
        else f'Статус образца усилен: {previous_status} → {new_status}.'
    )
    return {
        'incident_change': f'Инцидент остаётся активным. {severity_text}',
        'specimen_change': f'{threat_text} {status_text}',
        'limit_reached': all(
            [
                previous_severity == Incident.Severity.CRITICAL and new_severity == Incident.Severity.CRITICAL,
                previous_threat_level == Specimen.ThreatLevel.CRITICAL and new_threat_level == Specimen.ThreatLevel.CRITICAL,
                previous_status == Specimen.Status.QUARANTINE and new_status == Specimen.Status.QUARANTINE,
            ]
        ),
    }


@require_POST
def execute_protocol_session(request):
    specimen = get_object_or_404(get_specimen_queryset(), pk=request.POST.get('specimen_id'))
    specimen = hydrate_specimen_state([specimen])[0]
    role = request.POST.get('selected_role', ResolutionLog.Role.OBSERVER)
    selected_protocol = request.POST.get('selected_protocol', '').strip()
    active_incident = specimen.active_incident
    protocol_profile = get_protocol_profile(specimen, active_incident)
    manual_protocol = protocol_profile['manual_protocol']
    formula_protocol = protocol_profile['formula_protocol']
    effective_recommended_protocol = protocol_profile['effective_recommended_protocol']
    previous_severity = active_incident.severity if active_incident else ''
    previous_threat_level = specimen.threat_level
    previous_resolved_state = active_incident.is_resolved if active_incident else False
    previous_formula_protocol = formula_protocol if active_incident else ''
    previous_effective_recommended_protocol = effective_recommended_protocol if active_incident else ''
    previous_manual_protocol = manual_protocol if active_incident else ''
    previous_formula_strength = protocol_profile['formula_strength'] if active_incident else 0
    previous_selected_strength = PROTOCOL_STRENGTH.get(selected_protocol, 0)
    previous_manual_is_auto = protocol_profile['manual_is_auto'] if active_incident else False

    if role not in dict(ResolutionLog.Role.choices):
        return JsonResponse({'error': 'Недопустимая роль доступа.'}, status=400)

    allowed_protocols = get_role_protocols(role)
    if active_incident and selected_protocol not in allowed_protocols:
        return JsonResponse(
            {
                'error': 'Выбранный протокол недоступен для этой роли.',
                'allowed_protocols': allowed_protocols,
            },
            status=400,
        )

    if not active_incident:
        selected_protocol = ''

    outcome = build_outcome(
        selected_protocol,
        effective_recommended_protocol,
        formula_protocol,
        active_incident,
    )
    result_texts = build_result_texts(
        role=role,
        outcome=outcome,
        specimen=specimen,
        incident=active_incident,
        selected_protocol=selected_protocol,
        effective_recommended_protocol=effective_recommended_protocol,
    )

    with transaction.atomic():
        new_severity = previous_severity
        new_resolved_state = previous_resolved_state
        specimen_status_before = specimen.status
        specimen_threat_before = previous_threat_level
        escalation_change_texts = None

        if active_incident:
            if outcome == ResolutionLog.Outcome.SUCCESS:
                new_severity = shift_level(active_incident.severity, SEVERITY_SCALE, -1)
                new_resolved_state = True
                active_incident.severity = new_severity
                active_incident.is_resolved = True
                specimen.threat_level = shift_level(specimen.threat_level, THREAT_SCALE, -1)
                specimen.status = derive_specimen_status(specimen.threat_level, outcome)
            elif outcome == ResolutionLog.Outcome.PARTIAL:
                new_severity = shift_level(active_incident.severity, SEVERITY_SCALE, -1)
                new_resolved_state = False
                active_incident.severity = new_severity
                active_incident.is_resolved = False
                specimen.status = derive_specimen_status(specimen.threat_level, outcome)
            elif outcome == ResolutionLog.Outcome.ESCALATION:
                new_severity = shift_level(active_incident.severity, SEVERITY_SCALE, 1)
                new_resolved_state = False
                active_incident.severity = new_severity
                active_incident.is_resolved = False
                specimen.threat_level = shift_level(specimen.threat_level, THREAT_SCALE, 1)
                specimen.status = derive_specimen_status(specimen.threat_level, outcome)
                escalation_change_texts = build_escalation_change_texts(
                    previous_severity=previous_severity,
                    new_severity=new_severity,
                    previous_threat_level=specimen_threat_before,
                    new_threat_level=specimen.threat_level,
                    previous_status=specimen_status_before,
                    new_status=specimen.status,
                )

            active_incident.save(update_fields=['severity', 'is_resolved'])
            specimen.save(update_fields=['status', 'threat_level'])

        completed_at = timezone.now()
        escalation_at_limit = bool(escalation_change_texts and escalation_change_texts['limit_reached'])
        if escalation_at_limit:
            result_texts['result_title'] = 'Достигнут верхний предел эскалации'
            result_texts['final_status_text'] = 'Эскалация'
            result_texts['result_summary'] = (
                f'{active_incident.title}: дальнейшее ужесточение невозможно. '
                'Система удерживает объект на максимальном уровне тревоги.'
            )
            result_texts['system_note'] = (
                f'{ROLE_PRESENTATION.get(role, ROLE_PRESENTATION[ResolutionLog.Role.OBSERVER])["note"]} '
                'Контур остаётся в критической фазе. Дальнейшее ужесточение невозможно, '
                'система удерживает максимальный уровень тревоги.'
            )
        session = ResolutionLog.objects.create(
            specimen=specimen,
            incident=active_incident,
            selected_role=role,
            selected_protocol=selected_protocol if outcome != ResolutionLog.Outcome.REVIEW_ONLY else '',
            recommended_protocol=effective_recommended_protocol if active_incident else '',
            outcome=outcome,
            result_title=result_texts['result_title'],
            final_status_text=result_texts['final_status_text'],
            result_summary=result_texts['result_summary'],
            system_note=result_texts['system_note'],
            was_incident_active=bool(active_incident),
            previous_severity=previous_severity,
            previous_resolved_state=previous_resolved_state,
            new_severity=new_severity,
            new_resolved_state=new_resolved_state,
            ui_theme_state=result_texts['theme_state'],
            escalation_flag=outcome == ResolutionLog.Outcome.ESCALATION,
            stabilization_flag=outcome == ResolutionLog.Outcome.SUCCESS,
            completed_at=completed_at,
        )

    fragments = render_post_session_fragments(request, specimen, active_incident)
    return JsonResponse(
        {
            'session': {
                'id': session.pk,
                'url': reverse('resolution_log_detail', args=[session.pk]),
                'specimen_url': specimen.get_absolute_url(),
                'incident_url': active_incident.get_absolute_url() if active_incident else '',
                'history_url': f'{specimen.get_absolute_url()}#access-history',
                'selected_role': session.selected_role,
                'selected_protocol': session.selected_protocol,
                'recommended_protocol': session.recommended_protocol,
                'manual_protocol': previous_manual_protocol,
                'formula_protocol': previous_formula_protocol,
                'effective_recommended_protocol': previous_effective_recommended_protocol,
                'manual_is_auto': previous_manual_is_auto,
                'outcome': session.outcome,
                'outcome_display': session.get_outcome_display(),
                'result_title': session.result_title,
                'final_status_text': session.final_status_text,
                'result_summary': session.result_summary,
                'system_note': session.system_note,
                'completed_at': timezone.localtime(session.completed_at).strftime('%d.%m.%Y %H:%M'),
                'ui_theme_state': session.ui_theme_state,
                'role_summary': result_texts['role_summary'],
                'outcome_reason': describe_outcome_reason(
                    active_incident,
                    previous_effective_recommended_protocol,
                    outcome,
                ),
                'active_incident': bool(active_incident),
                'incident_change': (
                    escalation_change_texts['incident_change']
                    if escalation_change_texts else (
                        f'Инцидент {"закрыт" if new_resolved_state else "остаётся активным"}'
                        f'{f", серьёзность изменена на {new_severity}" if new_severity else ""}.'
                    )
                ) if active_incident else 'Инцидент не изменялся: активных записей не было.',
                'specimen_change': (
                    escalation_change_texts['specimen_change']
                    if escalation_change_texts else (
                        f'Статус образца: {specimen_status_before} → {specimen.status}. '
                        f'Уровень угрозы: {specimen_threat_before} → {specimen.threat_level}.'
                    )
                ) if active_incident else 'Параметры образца не изменялись: доступ был открыт только для просмотра.',
            },
            **fragments,
        }
    )
