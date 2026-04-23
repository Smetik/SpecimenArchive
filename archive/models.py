from django.db import models
from django.urls import reverse


class Specimen(models.Model):
    class Status(models.TextChoices):
        OBSERVATION = 'Наблюдение', 'Наблюдение'
        CONTAINMENT_II = 'Контур содержания II', 'Контур содержания II'
        CONTAINMENT_III = 'Контур содержания III', 'Контур содержания III'
        CONTAINMENT_IV = 'Контур содержания IV', 'Контур содержания IV'
        QUARANTINE = 'Карантинный контур', 'Карантинный контур'

    class ThreatLevel(models.TextChoices):
        LOW = 'Низкий', 'Низкий'
        MEDIUM = 'Средний', 'Средний'
        HIGH = 'Высокий', 'Высокий'
        CRITICAL = 'Критический', 'Критический'

    code = models.CharField('Код образца', max_length=32, unique=True)
    name = models.CharField('Наименование', max_length=255)
    status = models.CharField(
        'Статус содержания',
        max_length=64,
        choices=Status.choices,
        default=Status.CONTAINMENT_II,
    )
    short_description = models.TextField('Краткое описание')
    summary = models.TextField('Сводка')
    containment_protocol = models.TextField('Протокол содержания')
    threat_level = models.CharField(
        'Уровень угрозы',
        max_length=32,
        choices=ThreatLevel.choices,
        default=ThreatLevel.MEDIUM,
    )
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        ordering = ['code']
        verbose_name = 'образец'
        verbose_name_plural = 'образцы'

    def __str__(self):
        return f'{self.code} — {self.name}'

    def get_absolute_url(self):
        return reverse('specimen_detail', args=[self.pk])

    @property
    def active_incident(self):
        prefetched = getattr(self, 'prefetched_active_incident', None)
        if prefetched is not None:
            return prefetched
        return self.incidents.filter(is_resolved=False).order_by('-created_at').first()

    @property
    def latest_resolution(self):
        prefetched = getattr(self, 'prefetched_latest_resolution', None)
        if prefetched is not None:
            return prefetched
        return self.resolution_logs.order_by('-completed_at', '-created_at').first()

    @property
    def current_system_state(self):
        latest_resolution = self.latest_resolution
        if latest_resolution:
            return latest_resolution.final_status_text
        if self.active_incident:
            return 'Требуется решение'
        return 'Режим просмотра'

    @property
    def current_system_state_class(self):
        latest_resolution = self.latest_resolution
        if latest_resolution:
            return latest_resolution.ui_theme_state
        if self.active_incident:
            return 'alert'
        return 'review'


class Incident(models.Model):
    class ResponseProtocol(models.TextChoices):
        AUTO = 'Авто', 'Авто'
        OBSERVE = 'Наблюдение', 'Наблюдение'
        ISOLATE = 'Изолировать', 'Изолировать'
        QUARANTINE = 'Карантин', 'Карантин'

    class Severity(models.TextChoices):
        LOW = 'Низкий', 'Низкий'
        MEDIUM = 'Средний', 'Средний'
        HIGH = 'Высокий', 'Высокий'
        CRITICAL = 'Критический', 'Критический'

    specimen = models.ForeignKey(
        Specimen,
        on_delete=models.CASCADE,
        related_name='incidents',
        verbose_name='Образец',
    )
    title = models.CharField('Название инцидента', max_length=255)
    description = models.TextField('Описание инцидента')
    response_protocol = models.CharField(
        'Протокол реагирования',
        max_length=32,
        choices=ResponseProtocol.choices,
        default=ResponseProtocol.AUTO,
    )
    severity = models.CharField(
        'Уровень серьёзности',
        max_length=32,
        choices=Severity.choices,
        default=Severity.MEDIUM,
    )
    is_resolved = models.BooleanField('Устранён', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'инцидент'
        verbose_name_plural = 'инциденты'

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('incident_detail', args=[self.pk])

    @property
    def latest_resolution(self):
        prefetched = getattr(self, 'prefetched_latest_resolution', None)
        if prefetched is not None:
            return prefetched
        return self.resolution_logs.order_by('-completed_at', '-created_at').first()

    @property
    def current_system_state(self):
        latest_resolution = self.latest_resolution
        if latest_resolution:
            return latest_resolution.final_status_text
        if self.is_resolved:
            return 'Устранён'
        return 'Открыт'

    @property
    def current_system_state_class(self):
        latest_resolution = self.latest_resolution
        if latest_resolution:
            return latest_resolution.ui_theme_state
        return 'success' if self.is_resolved else 'alert'


class ResolutionLog(models.Model):
    class Role(models.TextChoices):
        RESEARCHER = 'Исследователь', 'Исследователь'
        OPERATOR = 'Оператор', 'Оператор'
        OBSERVER = 'Наблюдатель', 'Наблюдатель'

    class Outcome(models.TextChoices):
        SUCCESS = 'success', 'Стабилизирован'
        PARTIAL = 'partial', 'Под наблюдением'
        ESCALATION = 'escalation', 'Эскалация'
        REVIEW_ONLY = 'review_only', 'Режим просмотра'

    class ThemeState(models.TextChoices):
        SUCCESS = 'success', 'Стабилизация'
        PARTIAL = 'partial', 'Контроль'
        ESCALATION = 'escalation', 'Эскалация'
        REVIEW = 'review', 'Просмотр'

    specimen = models.ForeignKey(
        Specimen,
        on_delete=models.CASCADE,
        related_name='resolution_logs',
        verbose_name='Образец',
    )
    incident = models.ForeignKey(
        Incident,
        on_delete=models.SET_NULL,
        related_name='resolution_logs',
        verbose_name='Инцидент',
        null=True,
        blank=True,
    )
    selected_role = models.CharField('Выбранная роль', max_length=32, choices=Role.choices)
    selected_protocol = models.CharField(
        'Выбранный протокол',
        max_length=32,
        choices=Incident.ResponseProtocol.choices,
        blank=True,
    )
    recommended_protocol = models.CharField(
        'Рекомендованный протокол',
        max_length=32,
        choices=Incident.ResponseProtocol.choices,
        blank=True,
    )
    outcome = models.CharField('Исход', max_length=24, choices=Outcome.choices)
    result_title = models.CharField('Заголовок результата', max_length=255, blank=True)
    final_status_text = models.CharField('Итоговый статус', max_length=255)
    result_summary = models.TextField('Сводка результата')
    system_note = models.TextField('Системная заметка')
    was_incident_active = models.BooleanField('Был активный инцидент', default=False)
    previous_severity = models.CharField(
        'Предыдущая серьёзность',
        max_length=32,
        choices=Incident.Severity.choices,
        blank=True,
    )
    previous_resolved_state = models.BooleanField('Предыдущее состояние устранения', default=False)
    new_severity = models.CharField(
        'Новая серьёзность',
        max_length=32,
        choices=Incident.Severity.choices,
        blank=True,
    )
    new_resolved_state = models.BooleanField('Новое состояние устранения', default=False)
    ui_theme_state = models.CharField(
        'Тема интерфейса',
        max_length=24,
        choices=ThemeState.choices,
        default=ThemeState.REVIEW,
    )
    escalation_flag = models.BooleanField('Флаг эскалации', default=False)
    stabilization_flag = models.BooleanField('Флаг стабилизации', default=False)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    completed_at = models.DateTimeField('Дата завершения')

    class Meta:
        ordering = ['-completed_at', '-created_at']
        verbose_name = 'сессия доступа'
        verbose_name_plural = 'сессии доступа'

    def __str__(self):
        return f'{self.specimen.code} — {self.get_outcome_display()}'

    def get_absolute_url(self):
        return f'{self.specimen.get_absolute_url()}#access-history'
