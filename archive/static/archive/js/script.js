document.documentElement.classList.add('js-enabled');

const modal = document.querySelector('#access-modal');
const modalPanel = document.querySelector('.modal-panel');
const closeButtons = document.querySelectorAll('.js-close-modal');
const stages = [...document.querySelectorAll('.protocol-stage')];
const progressSteps = [...document.querySelectorAll('.progress-step')];

const designationElement = document.querySelector('#modal-designation');
const dossierCodeElement = document.querySelector('#dossier-code');
const dossierStatusElement = document.querySelector('#dossier-status');
const dossierThreatElement = document.querySelector('#dossier-threat');
const dossierRoleElement = document.querySelector('#dossier-role');
const dossierTitleElement = document.querySelector('#dossier-title');
const dossierSummaryElement = document.querySelector('#dossier-summary');
const dossierContainmentElement = document.querySelector('#dossier-containment');
const roleBriefElement = document.querySelector('#role-brief');
const roleNoteElement = document.querySelector('#role-note');
const processingCopyElement = document.querySelector('#processing-copy');
const processingLog = document.querySelector('#processing-log');

const incidentModeBanner = document.querySelector('#incident-mode-banner');
const incidentModePill = document.querySelector('#incident-mode-pill');
const incidentModeTitle = document.querySelector('#incident-mode-title');
const incidentModeCopy = document.querySelector('#incident-mode-copy');
const incidentConsoleLabel = document.querySelector('#incident-console-label');
const incidentConsole = document.querySelector('#incident-console');
const incidentTitleElement = document.querySelector('#incident-title');
const incidentDescriptionElement = document.querySelector('#incident-description');
const incidentProtocolLabelElement = document.querySelector('#incident-protocol-label');
const incidentProtocolElement = document.querySelector('#incident-protocol');
const incidentRoleContextElement = document.querySelector('#incident-role-context');
const incidentBriefElement = document.querySelector('#incident-brief');
const incidentSeverityPill = document.querySelector('#incident-severity-pill');
const incidentStatePill = document.querySelector('#incident-state-pill');
const incidentAdvanceButton = document.querySelector('#incident-advance-button');

const responseCopyElement = document.querySelector('#response-copy');
const responseGrid = document.querySelector('#response-grid');
const responseHintElement = document.querySelector('#response-hint');
const responseErrorElement = document.querySelector('#response-error');
const reviewOnlyNote = document.querySelector('#review-only-note');
const reviewOnlyActions = document.querySelector('#review-only-actions');

const executionCopyElement = document.querySelector('#execution-copy');
const executionSteps = [...document.querySelectorAll('.execution-step')];

const protocolResultElement = document.querySelector('#protocol-result');
const outcomeBanner = document.querySelector('#outcome-banner');
const outcomePillElement = document.querySelector('#outcome-pill');
const outcomeTitleElement = document.querySelector('#outcome-title');
const resultSelectedProtocolElement = document.querySelector('#result-selected-protocol');
const resultRecommendedProtocolElement = document.querySelector('#result-recommended-protocol');
const resultRoleSummaryElement = document.querySelector('#result-role-summary');
const resultSystemNoteElement = document.querySelector('#result-system-note');
const resultOutcomeReasonElement = document.querySelector('#result-outcome-reason');
const resultIncidentChangeElement = document.querySelector('#result-incident-change');
const resultSpecimenChangeElement = document.querySelector('#result-specimen-change');

const journalRoleElement = document.querySelector('#journal-role');
const journalActionElement = document.querySelector('#journal-action');
const journalTimeElement = document.querySelector('#journal-time');
const journalStatusElement = document.querySelector('#journal-status');
const journalSummaryElement = document.querySelector('#journal-summary');
const journalNoteElement = document.querySelector('#journal-note');
const finalSessionLink = document.querySelector('#final-session-link');
const finalIncidentLink = document.querySelector('#final-incident-link');
const finalHistoryLink = document.querySelector('#final-history-link');

const filterForms = [...document.querySelectorAll('[data-filter-form]')];

const roleProfiles = {
    'Исследователь': {
        note: 'Исследовательский доступ акцентирует биологическую интерпретацию и влияние мер на сохранность материала.',
        brief: 'Система показывает аналитический срез по образцу, отклонения структуры и возможные последствия вмешательства.',
        incidentContext: 'Приоритет смещён к анализу образца, стабильности среды и риску потери материала.',
        processing: 'Сверка исследовательского допуска, досье образца, журнала содержания и активных инцидентов.',
        journalNote: 'Исследовательская сессия зафиксировала влияние решения на аналитическую доступность материала.',
    },
    'Оператор': {
        note: 'Операторский доступ акцентирует текущий контур содержания, силу протокола и влияние решения на удержание среды.',
        brief: 'Система показывает оперативный срез по образцу, границы контура и риск вторичного отклонения.',
        incidentContext: 'Приоритет смещён к удержанию контура, ограничению переноса и применению мер содержания.',
        processing: 'Сверка операторского допуска, контура содержания, журнала реагирования и актуального режима ограничения.',
        journalNote: 'Операторская сессия сопоставила выбранное вмешательство с допустимой силой протокола.',
    },
    'Наблюдатель': {
        note: 'Наблюдательный доступ акцентирует мониторинг, ограничения доступа и подтверждение итогового статуса.',
        brief: 'Система показывает событийный срез, последовательность отклонений и последствия без расширения полномочий.',
        incidentContext: 'Приоритет смещён к мониторингу, подтверждению статуса и фиксации действий в журнале.',
        processing: 'Сверка наблюдательного допуска, истории отклонений, ограничений контура и статуса реагирования.',
        journalNote: 'Наблюдательная сессия зафиксировала реакцию и итоговое состояние без изменения уровня доступа.',
    },
};

const roleProtocolMatrix = {
    'Наблюдатель': ['Наблюдение'],
    'Исследователь': ['Наблюдение', 'Карантин'],
    'Оператор': ['Изолировать', 'Карантин'],
};

const outcomeProfiles = {
    success: {
        pill: 'Стабилизирован',
        title: 'Контур удержан и возвращён в допустимое состояние',
        bannerClass: 'is-stabilized',
        theme: 'success',
    },
    partial: {
        pill: 'Под наблюдением',
        title: 'Ситуация удержана, но остаётся активной',
        bannerClass: 'is-contained',
        theme: 'partial',
    },
    escalation: {
        pill: 'Эскалация',
        title: 'Система фиксирует ухудшение контура',
        bannerClass: 'is-escalation',
        theme: 'escalation',
    },
    review_only: {
        pill: 'Режим просмотра',
        title: 'Активный инцидент не обнаружен',
        bannerClass: 'is-review',
        theme: 'review',
    },
};

const protocolState = {
    specimen: null,
    incident: null,
    role: '',
    action: '',
    recommendationProfile: null,
    outcome: '',
    savedSession: null,
    timers: [],
    hasActiveIncident: false,
    isSubmitting: false,
};

function getCookie(name) {
    const cookie = document.cookie
        .split(';')
        .map((item) => item.trim())
        .find((item) => item.startsWith(`${name}=`));
    return cookie ? decodeURIComponent(cookie.split('=').slice(1).join('=')) : '';
}

function clearProtocolTimers() {
    protocolState.timers.forEach((timer) => window.clearTimeout(timer));
    protocolState.timers = [];
}

function scheduleProtocolTask(callback, delay) {
    const timer = window.setTimeout(callback, delay);
    protocolState.timers.push(timer);
}

function delay(ms) {
    return new Promise((resolve) => {
        scheduleProtocolTask(resolve, ms);
    });
}

function updateProgress(step) {
    progressSteps.forEach((item, index) => {
        item.classList.toggle('is-active', index === step - 1);
        item.classList.toggle('is-complete', index < step - 1);
    });
}

function showStage(step) {
    stages.forEach((stage) => {
        stage.classList.toggle('is-active', Number(stage.dataset.step) === step);
    });

    if (modalPanel) {
        modalPanel.dataset.step = String(step);
        modalPanel.classList.toggle('is-processing', step === 3 || step === 7);
        modalPanel.classList.toggle('is-final', step >= 8);
    }

    updateProgress(step);
    if (modalPanel) {
        modalPanel.scrollTop = 0;
    }
}

function normalizeValue(value) {
    return (value || '').toLowerCase().replace('ё', 'е');
}

function getThreatClass(value) {
    const normalized = normalizeValue(value);
    if (normalized.includes('крит')) {
        return 'critical';
    }
    if (normalized.includes('высок')) {
        return 'high';
    }
    if (normalized.includes('сред')) {
        return 'medium';
    }
    return 'low';
}

function applyOutcomeTheme(theme) {
    if (!modalPanel) {
        return;
    }
    modalPanel.dataset.outcome = theme || '';
    modalPanel.classList.remove('is-escalation-pulse');
    if (theme === 'escalation') {
        modalPanel.classList.add('is-escalation-pulse');
        scheduleProtocolTask(() => modalPanel.classList.remove('is-escalation-pulse'), 780);
    }
}

function getProtocolStrength(protocol) {
    const normalized = normalizeValue(protocol);
    if (normalized.includes('карантин')) {
        return 3;
    }
    if (normalized.includes('изол')) {
        return 2;
    }
    if (normalized.includes('наблюд')) {
        return 1;
    }
    return 0;
}

function protocolFromStrength(strength) {
    if (strength >= 3) {
        return 'Карантин';
    }
    if (strength === 2) {
        return 'Изолировать';
    }
    return 'Наблюдение';
}

function deriveRecommendationProfile(specimen, incident) {
    if (!incident || !incident.hasActiveIncident) {
        return {
            manualProtocol: '',
            formulaProtocol: '',
            effectiveProtocol: '',
            formulaStrength: 0,
            manualIsAuto: false,
            manualDiffers: false,
        };
    }

    const severity = normalizeValue(incident.severity);
    const threat = normalizeValue(specimen.threat);
    let formulaProtocol = 'Наблюдение';
    if (severity.includes('крит') || threat.includes('крит')) {
        formulaProtocol = 'Карантин';
    } else if (severity.includes('высок') || threat.includes('высок')) {
        formulaProtocol = 'Изолировать';
    }

    const responseProtocol = incident.responseProtocol || '';
    const normalizedManual = normalizeValue(responseProtocol);
    const manualConcreteProtocol = getProtocolStrength(responseProtocol) ? responseProtocol : '';
    const manualIsAuto = normalizedManual.includes('авто') || !manualConcreteProtocol;
    const effectiveProtocol = manualIsAuto
        ? formulaProtocol
        : protocolFromStrength(Math.max(getProtocolStrength(manualConcreteProtocol), getProtocolStrength(formulaProtocol)));

    return {
        manualProtocol: responseProtocol || 'Авто',
        manualConcreteProtocol,
        formulaProtocol,
        effectiveProtocol,
        formulaStrength: getProtocolStrength(formulaProtocol),
        manualIsAuto,
        manualDiffers: Boolean(manualConcreteProtocol && manualConcreteProtocol !== formulaProtocol),
    };
}

function setRolePresentation() {
    const roleProfile = roleProfiles[protocolState.role] || roleProfiles['Наблюдатель'];
    roleNoteElement.textContent = roleProfile.note;
    roleBriefElement.textContent = roleProfile.brief;
    processingCopyElement.textContent = roleProfile.processing;
    incidentRoleContextElement.textContent = roleProfile.incidentContext;
}

function populateDossier() {
    if (!protocolState.specimen) {
        return;
    }
    designationElement.textContent = `${protocolState.specimen.designation} · ${protocolState.role || 'ожидание допуска'}`;
    dossierCodeElement.textContent = protocolState.specimen.designation;
    dossierStatusElement.textContent = protocolState.specimen.status;
    dossierThreatElement.textContent = protocolState.specimen.threat;
    dossierRoleElement.textContent = protocolState.role || 'Не определена';
    dossierTitleElement.textContent = protocolState.specimen.title;
    dossierSummaryElement.textContent = protocolState.specimen.summary;
    dossierContainmentElement.textContent = protocolState.specimen.containment;
}

function applyIncidentSeverityStyle(severity, isResolved) {
    incidentSeverityPill.className = 'incident-pill';
    incidentConsole.classList.remove('is-critical', 'is-high', 'is-medium', 'is-low', 'is-review');
    const normalized = normalizeValue(severity);

    if (!protocolState.hasActiveIncident) {
        incidentConsole.classList.add('is-review');
        incidentSeverityPill.classList.add('incident-pill-resolved');
        return;
    }

    if (isResolved || normalized.includes('низ')) {
        incidentConsole.classList.add('is-low');
        incidentSeverityPill.classList.add('incident-pill-resolved');
        return;
    }
    if (normalized.includes('крит')) {
        incidentConsole.classList.add('is-critical');
        incidentSeverityPill.classList.add('incident-pill-open');
        return;
    }
    if (normalized.includes('высок')) {
        incidentConsole.classList.add('is-high');
        incidentSeverityPill.classList.add('incident-pill-high');
        return;
    }
    if (normalized.includes('сред')) {
        incidentConsole.classList.add('is-medium');
        incidentSeverityPill.classList.add('incident-pill-medium');
        return;
    }
    incidentConsole.classList.add('is-low');
    incidentSeverityPill.classList.add('incident-pill-resolved');
}

function configureDecisionStage() {
    const reviewOnly = !protocolState.hasActiveIncident;
    responseGrid.hidden = reviewOnly;
    responseHintElement.hidden = reviewOnly;
    reviewOnlyNote.hidden = !reviewOnly;
    reviewOnlyActions.hidden = !reviewOnly;
    responseErrorElement.hidden = true;
    responseErrorElement.textContent = '';
    responseCopyElement.textContent = reviewOnly
        ? 'Активный инцидент не найден. Система допускает только просмотр досье и фиксацию сессии.'
        : 'Система ожидает подтверждённого решения. Выбранный протокол определит исход текущего инцидента.';

    const allowedProtocols = roleProtocolMatrix[protocolState.role] || roleProtocolMatrix['Наблюдатель'];
    document.querySelectorAll('[data-action]').forEach((button) => {
        const isReviewButton = button.closest('#review-only-actions');
        if (reviewOnly) {
            button.disabled = false;
            button.hidden = Boolean(!isReviewButton && button.dataset.action);
            return;
        }

        if (!button.dataset.action) {
            return;
        }
        const allowed = allowedProtocols.includes(button.dataset.action);
        button.hidden = !allowed;
        button.disabled = !allowed;
        button.classList.toggle('is-disabled', !allowed);
    });

    if (!reviewOnly) {
        responseHintElement.textContent = `Для роли «${protocolState.role}» доступны: ${allowedProtocols.join(', ')}.`;
    }
}

function populateIncidentConsole() {
    if (!protocolState.specimen || !protocolState.incident) {
        return;
    }

    if (!protocolState.hasActiveIncident) {
        incidentModeBanner.className = 'incident-mode-banner is-review';
        incidentModePill.className = 'system-state-pill system-state-pill-review';
        incidentModePill.textContent = 'Режим просмотра';
        incidentModeTitle.textContent = 'Активных инцидентов нет';
        incidentModeCopy.textContent = 'Система не нашла неустранённых инцидентов по этому образцу. Доступ открыт только для просмотра.';
        incidentConsoleLabel.textContent = 'Контур просмотра';
        incidentTitleElement.textContent = 'Режим просмотра досье';
        incidentDescriptionElement.textContent = protocolState.incident.description;
        incidentProtocolLabelElement.textContent = 'Рекомендация системы';
        incidentProtocolElement.textContent = 'Протокол не требуется';
        incidentBriefElement.textContent = 'Вмешательство не требуется. После фиксации будет создана запись о просмотре.';
        incidentSeverityPill.textContent = protocolState.specimen.threat;
        incidentStatePill.textContent = 'Нет активного инцидента';
        incidentStatePill.className = 'incident-pill incident-pill-resolved';
        incidentAdvanceButton.textContent = 'Перейти к фиксации просмотра';
        applyIncidentSeverityStyle(protocolState.specimen.threat, true);
        configureDecisionStage();
        return;
    }

    incidentModeBanner.className = 'incident-mode-banner is-alert';
    incidentModePill.className = 'system-state-pill system-state-pill-alert';
    incidentModePill.textContent = 'Требуется реакция';
    incidentModeTitle.textContent = 'Активный инцидент открыт';
    incidentModeCopy.textContent = 'Система ожидает подтверждённого решения. Окно реакции остаётся активным до применения протокола.';
    incidentConsoleLabel.textContent = 'Окно реакции открыто';
    incidentTitleElement.textContent = protocolState.incident.title;
    incidentDescriptionElement.textContent = protocolState.incident.description;
    if (protocolState.recommendationProfile.manualIsAuto) {
        incidentProtocolLabelElement.textContent = 'Рекомендация системы';
        incidentProtocolElement.textContent = protocolState.recommendationProfile.effectiveProtocol;
        incidentBriefElement.textContent = `Рекомендуемая мера: ${protocolState.recommendationProfile.effectiveProtocol}. Система ожидает подтверждённого решения по текущей фазе инцидента.`;
    } else {
        incidentProtocolLabelElement.textContent = 'Рекомендация по инциденту';
        incidentProtocolElement.textContent = protocolState.recommendationProfile.manualProtocol;
        incidentBriefElement.textContent = `В журнале инцидента зафиксирована мера «${protocolState.recommendationProfile.manualProtocol}». Система ожидает подтверждённого решения по текущей фазе инцидента.`;
    }
    incidentSeverityPill.textContent = protocolState.incident.severity;
    incidentStatePill.textContent = 'Требуется решение';
    incidentStatePill.className = 'incident-pill incident-pill-open';
    incidentAdvanceButton.textContent = 'Перейти к решению';
    applyIncidentSeverityStyle(protocolState.incident.severity, protocolState.incident.isResolved);
    configureDecisionStage();
}

function resetProcessingIndicators() {
    [...processingLog.children].forEach((item) => item.classList.remove('is-complete'));
    executionSteps.forEach((item) => item.classList.remove('is-complete', 'is-active'));
}

function fillExecutionTimeline() {
    const actionLabel = protocolState.action || 'Режим просмотра';
    const reviewOnly = protocolState.outcome === 'review_only';
    const messages = reviewOnly
        ? [
            'Сессия просмотра принята системой',
            'Фиксация доступа без вмешательства',
            'Сверка журналов завершена',
            'Запись подготовлена к сохранению',
        ]
        : [
            `Протокол «${actionLabel}» принят системой`,
            'Применение мер к контуру содержания',
            'Сверка обновлённых параметров',
            'Формирование итогового статуса',
        ];

    executionSteps.forEach((item, index) => {
        const title = item.querySelector('strong');
        if (title) {
            title.textContent = messages[index];
        }
    });
}

function populateFinalOutcome() {
    if (!protocolState.savedSession) {
        return;
    }
    const session = protocolState.savedSession;
    const outcomeProfile = outcomeProfiles[session.outcome] || outcomeProfiles.review_only;

    outcomeBanner.className = `outcome-banner ${outcomeProfile.bannerClass}`;
    outcomePillElement.textContent = session.final_status_text;
    outcomeTitleElement.textContent = session.result_title;
    protocolResultElement.textContent = session.result_summary;
    resultSelectedProtocolElement.textContent = session.selected_protocol || 'не применялся';
    resultRecommendedProtocolElement.textContent = session.effective_recommended_protocol || session.recommended_protocol || 'не требовался';
    resultRoleSummaryElement.textContent = session.role_summary;
    resultSystemNoteElement.textContent = session.system_note;
    resultOutcomeReasonElement.textContent = session.outcome_reason;
    resultIncidentChangeElement.textContent = session.incident_change;
    resultSpecimenChangeElement.textContent = session.specimen_change;

    journalRoleElement.textContent = session.selected_role;
    journalActionElement.textContent = session.selected_protocol || 'не применялся';
    journalTimeElement.textContent = session.completed_at;
    journalStatusElement.textContent = session.final_status_text;
    journalSummaryElement.textContent = session.result_summary;
    journalNoteElement.textContent = session.system_note;

    finalSessionLink.href = session.url;
    finalHistoryLink.href = session.history_url;
    finalIncidentLink.hidden = !session.incident_url;
    if (session.incident_url) {
        finalIncidentLink.href = session.incident_url;
    }

    applyOutcomeTheme(outcomeProfile.theme);
}

function resetProtocol() {
    clearProtocolTimers();
    protocolState.role = '';
    protocolState.action = '';
    protocolState.outcome = '';
    protocolState.savedSession = null;
    protocolState.isSubmitting = false;

    document.querySelectorAll('[data-role], [data-action]').forEach((button) => {
        button.classList.remove('is-selected');
    });

    designationElement.textContent = `${protocolState.specimen.designation} · ожидание подтверждения`;
    protocolResultElement.textContent = 'Системное сообщение будет сформировано после подтверждения результата.';
    outcomeBanner.className = 'outcome-banner';
    outcomePillElement.textContent = '-';
    outcomeTitleElement.textContent = 'Результат будет сформирован после выбора протокола.';
    resultSelectedProtocolElement.textContent = '-';
    resultRecommendedProtocolElement.textContent = '-';
    resultRoleSummaryElement.textContent = '-';
    resultSystemNoteElement.textContent = '-';
    resultOutcomeReasonElement.textContent = '-';
    resultIncidentChangeElement.textContent = '-';
    resultSpecimenChangeElement.textContent = '-';
    journalRoleElement.textContent = '-';
    journalActionElement.textContent = '-';
    journalTimeElement.textContent = '-';
    journalStatusElement.textContent = '-';
    journalSummaryElement.textContent = '-';
    journalNoteElement.textContent = '-';
    finalSessionLink.href = '#';
    finalHistoryLink.href = '#';
    finalIncidentLink.hidden = true;
    incidentStatePill.textContent = 'Требуется решение';
    responseHintElement.textContent = 'После выбора система применит меры, выполнит сверку параметров и зафиксирует новый статус.';

    resetProcessingIndicators();
    setRolePresentation();
    populateDossier();
    populateIncidentConsole();
    applyOutcomeTheme('');
    showStage(1);
}

function openModal(button) {
    if (!modal) {
        return;
    }

    protocolState.specimen = {
        id: button.dataset.specimenId,
        designation: button.dataset.designation,
        title: button.dataset.title,
        status: button.dataset.status,
        threat: button.dataset.threat,
        summary: button.dataset.summary,
        containment: button.dataset.containment,
        currentState: button.dataset.currentState,
    };

    protocolState.hasActiveIncident = button.dataset.hasActiveIncident === 'true';
    protocolState.incident = {
        id: button.dataset.incidentId,
        title: button.dataset.incidentTitle,
        description: button.dataset.incidentDescription,
        severity: button.dataset.incidentSeverity,
        responseProtocol: button.dataset.incidentProtocol,
        isResolved: button.dataset.incidentResolved === 'true',
        createdAt: button.dataset.incidentCreated,
        hasActiveIncident: protocolState.hasActiveIncident,
    };

    protocolState.recommendationProfile = deriveRecommendationProfile(protocolState.specimen, protocolState.incident);

    resetProtocol();
    modal.classList.add('is-visible');
    modal.setAttribute('aria-hidden', 'false');
    document.body.classList.add('modal-open');
}

function closeModal() {
    if (!modal) {
        return;
    }
    clearProtocolTimers();
    modal.classList.remove('is-visible');
    modal.setAttribute('aria-hidden', 'true');
    document.body.classList.remove('modal-open');
}

function runProcessingSequence() {
    showStage(3);
    [...processingLog.children].forEach((item, index) => {
        scheduleProtocolTask(() => {
            item.classList.add('is-complete');
        }, 220 + index * 220);
    });

    scheduleProtocolTask(() => {
        populateDossier();
        populateIncidentConsole();
        showStage(4);
    }, 1560);
}

async function submitProtocolSession() {
    const requestBody = new URLSearchParams();
    requestBody.append('specimen_id', protocolState.specimen.id);
    requestBody.append('selected_role', protocolState.role);
    requestBody.append('selected_protocol', protocolState.action);

    const response = await fetch(modal.dataset.executeUrl, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded;charset=UTF-8',
            'X-CSRFToken': getCookie('csrftoken'),
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: requestBody.toString(),
    });

    const payload = await response.json();
    if (!response.ok) {
        const error = new Error(payload.error || 'Не удалось сохранить результат сессии.');
        error.payload = payload;
        throw error;
    }

    return payload;
}

function updateSpecimenStateInDom(specimenId, state) {
    document.querySelectorAll(`[data-specimen-state-pill][data-specimen-id="${specimenId}"]`).forEach((pill) => {
        pill.className = `system-state-pill system-state-pill-${state.system_state_class}`;
        pill.textContent = state.system_state;
    });

    document.querySelectorAll(`[data-specimen-status-plain][data-specimen-id="${specimenId}"], [data-specimen-status-pill][data-specimen-id="${specimenId}"]`).forEach((item) => {
        item.textContent = state.status;
    });

    document.querySelectorAll(`[data-specimen-threat-pill][data-specimen-id="${specimenId}"]`).forEach((item) => {
        item.className = `threat-pill threat-pill-${getThreatClass(state.threat_level)}`;
        item.setAttribute('data-specimen-threat-pill', '');
        item.setAttribute('data-specimen-id', specimenId);
        item.textContent = state.threat_level;
    });

    document.querySelectorAll(`.js-open-dossier[data-specimen-id="${specimenId}"]`).forEach((button) => {
        button.dataset.status = state.status;
        button.dataset.threat = state.threat_level;
        button.dataset.currentState = state.system_state;

        if (!state.active_incident_id || !state.active_incident) {
            button.dataset.hasActiveIncident = 'false';
            button.dataset.incidentId = '';
            button.dataset.incidentTitle = 'Активных инцидентов нет';
            button.dataset.incidentDescription = 'По текущему образцу не найдено неустранённых инцидентов. Система откроет досье в режиме просмотра и зафиксирует факт доступа.';
            button.dataset.incidentSeverity = state.threat_level;
            button.dataset.incidentProtocol = '';
            button.dataset.incidentResolved = 'false';
            button.dataset.incidentCreated = 'Текущая сессия';
        } else {
            button.dataset.hasActiveIncident = 'true';
            button.dataset.incidentId = String(state.active_incident.id);
            button.dataset.incidentTitle = state.active_incident.title;
            button.dataset.incidentDescription = state.active_incident.description;
            button.dataset.incidentSeverity = state.active_incident.severity;
            button.dataset.incidentProtocol = state.active_incident.response_protocol;
            button.dataset.incidentResolved = state.active_incident.is_resolved ? 'true' : 'false';
            button.dataset.incidentCreated = state.active_incident.created_at;
        }
    });
}

function updateIncidentStateInDom(incidentState) {
    if (!incidentState.id) {
        return;
    }
    document.querySelectorAll(`[data-incident-state-pill][data-incident-id="${incidentState.id}"]`).forEach((pill) => {
        pill.className = `system-state-pill system-state-pill-${incidentState.system_state_class}`;
        pill.textContent = incidentState.system_state;
    });
    document.querySelectorAll(`[data-incident-open-pill][data-incident-id="${incidentState.id}"]`).forEach((pill) => {
        pill.className = `incident-pill incident-pill-${incidentState.is_resolved ? 'resolved' : 'open'}`;
        pill.textContent = incidentState.is_resolved ? 'Устранён' : 'Открыт';
    });
    document.querySelectorAll(`[data-incident-severity-text][data-incident-id="${incidentState.id}"]`).forEach((label) => {
        label.textContent = incidentState.severity;
    });
}

function applyServerFragments(payload) {
    updateSpecimenStateInDom(protocolState.specimen.id, payload.specimen_state);
    updateIncidentStateInDom(payload.incident_state);

    const activityFeed = document.querySelector('#activity-feed');
    if (activityFeed && payload.recent_activity_html) {
        activityFeed.innerHTML = payload.recent_activity_html;
    }

    const specimenHistoryPanel = document.querySelector('#specimen-history-panel');
    if (specimenHistoryPanel && payload.specimen_history_html) {
        specimenHistoryPanel.innerHTML = payload.specimen_history_html;
    }

    const incidentHistoryPanel = document.querySelector('#incident-history-panel');
    if (incidentHistoryPanel && payload.incident_history_html) {
        incidentHistoryPanel.innerHTML = payload.incident_history_html;
    }

    protocolState.specimen.status = payload.specimen_state.status;
    protocolState.specimen.threat = payload.specimen_state.threat_level;
    protocolState.hasActiveIncident = Boolean(payload.specimen_state.active_incident_id);
    protocolState.incident.hasActiveIncident = protocolState.hasActiveIncident;

    if (!protocolState.hasActiveIncident) {
        protocolState.incident.id = '';
        protocolState.incident.title = 'Активных инцидентов нет';
        protocolState.incident.description = 'По текущему образцу не найдено неустранённых инцидентов. Система откроет досье в режиме просмотра и зафиксирует факт доступа.';
        protocolState.incident.severity = payload.specimen_state.threat_level;
        protocolState.incident.responseProtocol = '';
        protocolState.incident.isResolved = false;
        protocolState.incident.createdAt = 'Текущая сессия';
    } else if (payload.specimen_state.active_incident) {
        protocolState.incident.id = String(payload.specimen_state.active_incident.id);
        protocolState.incident.title = payload.specimen_state.active_incident.title;
        protocolState.incident.description = payload.specimen_state.active_incident.description;
        protocolState.incident.severity = payload.specimen_state.active_incident.severity;
        protocolState.incident.responseProtocol = payload.specimen_state.active_incident.response_protocol;
        protocolState.incident.isResolved = payload.specimen_state.active_incident.is_resolved;
        protocolState.incident.createdAt = payload.specimen_state.active_incident.created_at;
    }

    protocolState.recommendationProfile = deriveRecommendationProfile(protocolState.specimen, protocolState.incident);
}

async function runExecutionSequence() {
    if (protocolState.isSubmitting) {
        return;
    }
    protocolState.isSubmitting = true;
    showStage(7);
    fillExecutionTimeline();

    executionSteps.forEach((item, index) => {
        scheduleProtocolTask(() => {
            item.classList.add('is-active');
            if (index > 0) {
                executionSteps[index - 1].classList.remove('is-active');
                executionSteps[index - 1].classList.add('is-complete');
            }
        }, 240 + index * 360);
    });

    try {
        const [payload] = await Promise.all([
            submitProtocolSession(),
            delay(1900),
        ]);
        const lastStep = executionSteps[executionSteps.length - 1];
        lastStep.classList.remove('is-active');
        lastStep.classList.add('is-complete');

        protocolState.savedSession = payload.session;
        protocolState.outcome = payload.session.outcome;
        applyServerFragments(payload);
        populateFinalOutcome();
        showStage(8);
    } catch (error) {
        if (error.payload && error.payload.allowed_protocols) {
            protocolState.isSubmitting = false;
            responseErrorElement.hidden = false;
            responseErrorElement.textContent = error.payload.error;
            responseHintElement.textContent = `Доступные протоколы для роли «${protocolState.role}»: ${error.payload.allowed_protocols.join(', ')}.`;
            showStage(6);
            return;
        }
        protocolResultElement.textContent = 'Не удалось зафиксировать сессию. Повторите попытку.';
        outcomeBanner.className = 'outcome-banner is-escalation';
        outcomePillElement.textContent = 'Ошибка';
        outcomeTitleElement.textContent = 'Система не сохранила результат';
        resultOutcomeReasonElement.textContent = error.message;
        showStage(8);
    } finally {
        protocolState.isSubmitting = false;
    }
}

function handleStepAdvance(nextStep, trigger) {
    const stepNumber = Number(nextStep);

    if (trigger.dataset.role) {
        protocolState.role = trigger.dataset.role;
        designationElement.textContent = `${protocolState.specimen.designation} · ${protocolState.role}`;
        document.querySelectorAll('[data-role]').forEach((button) => {
            button.classList.toggle('is-selected', button === trigger);
        });
        setRolePresentation();
        populateDossier();
        populateIncidentConsole();
    }

    if (Object.prototype.hasOwnProperty.call(trigger.dataset, 'action')) {
        if (trigger.disabled) {
            return;
        }
        protocolState.action = trigger.dataset.action || '';
        document.querySelectorAll('[data-action]').forEach((button) => {
            button.classList.toggle('is-selected', button === trigger && !!trigger.dataset.action);
        });
        responseErrorElement.hidden = true;
        responseErrorElement.textContent = '';
        responseHintElement.textContent = protocolState.action
            ? `Выбран протокол «${protocolState.action}». Система применяет меры и сверяет изменение статуса.`
            : 'Система фиксирует сессию просмотра без активного вмешательства.';
    }

    if (stepNumber === 3) {
        runProcessingSequence();
        return;
    }
    if (stepNumber === 7) {
        runExecutionSequence();
        return;
    }
    if (stepNumber === 9) {
        showStage(9);
        return;
    }
    showStage(stepNumber);
}

if (modal) {
    closeButtons.forEach((button) => {
        button.addEventListener('click', closeModal);
    });

    modal.addEventListener('click', (event) => {
        const trigger = event.target.closest('[data-next-step]');
        if (trigger) {
            handleStepAdvance(trigger.dataset.nextStep, trigger);
        }
    });

    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape' && modal.classList.contains('is-visible')) {
            closeModal();
        }
    });
}

document.addEventListener('click', (event) => {
    const dossierButton = event.target.closest('.js-open-dossier');
    if (dossierButton) {
        openModal(dossierButton);
    }
});

function setFilterLoading(context, isLoading) {
    if (!context.loading || !context.results) {
        return;
    }
    context.loading.hidden = !isLoading;
    context.results.classList.toggle('is-loading', isLoading);
    context.isLoading = isLoading;
}

async function requestFilterUpdate(context) {
    if (!context.form || !context.results) {
        return;
    }

    const requestId = context.requestId + 1;
    context.requestId = requestId;

    if (context.controller) {
        context.controller.abort();
    }

    context.controller = new AbortController();
    const params = new URLSearchParams(new FormData(context.form));
    const endpoint = context.results.dataset.endpoint;

    setFilterLoading(context, true);

    try {
        const response = await fetch(`${endpoint}?${params.toString()}`, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
            signal: context.controller.signal,
        });

        if (!response.ok) {
            throw new Error('Не удалось обновить список.');
        }

        const payload = await response.json();
        if (requestId !== context.requestId) {
            return;
        }

        context.results.innerHTML = payload.html;
        if (context.count) {
            context.count.textContent = payload.count_text;
        }
    } catch (error) {
        if (error.name !== 'AbortError') {
            if (requestId !== context.requestId) {
                return;
            }
            context.results.innerHTML = `
                <article class="empty-state">
                    <p class="eyebrow">Ошибка загрузки</p>
                    <h2>Не удалось обновить список</h2>
                    <p>Повторите попытку ещё раз. Текущий набор фильтров сохранён.</p>
                </article>
            `;
            if (context.count) {
                context.count.textContent = 'Ошибка обновления';
            }
        }
    } finally {
        if (requestId === context.requestId) {
            setFilterLoading(context, false);
            context.controller = null;
        }
    }
}

function debounceFilterRequest(context) {
    window.clearTimeout(context.debounceTimer);
    context.debounceTimer = window.setTimeout(() => {
        context.debounceTimer = null;
        requestFilterUpdate(context);
    }, 280);
}

filterForms.forEach((form) => {
    const context = {
        form,
        results: document.getElementById(form.dataset.resultsId),
        count: document.getElementById(form.dataset.countId),
        loading: document.getElementById(form.dataset.loadingId),
        resetButton: form.querySelector('[data-filter-reset]'),
        debounceTimer: null,
        controller: null,
        requestId: 0,
        isLoading: false,
    };

    if (!context.results) {
        return;
    }

    form.addEventListener('submit', (event) => {
        event.preventDefault();
        requestFilterUpdate(context);
    });

    form.addEventListener('input', (event) => {
        if (event.target.name === 'q') {
            debounceFilterRequest(context);
        }
    });

    form.addEventListener('change', () => {
        requestFilterUpdate(context);
    });

    if (context.resetButton) {
        context.resetButton.addEventListener('click', () => {
            form.reset();
            form.querySelectorAll('select').forEach((select) => {
                if (!select.name) {
                    return;
                }
                if (select.name === 'activity' || select.name === 'resolved') {
                    select.value = 'all';
                } else {
                    select.value = '';
                }
            });
            requestFilterUpdate(context);
        });
    }
});
