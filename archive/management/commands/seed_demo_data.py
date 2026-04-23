from datetime import timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from archive.models import Incident, ResolutionLog, Specimen


SPECIMEN_DATA = [
    {
        'code': 'SA-21',
        'name': 'Лигатурный мицелий «Офелий»',
        'status': Specimen.Status.CONTAINMENT_III,
        'short_description': 'Волокнистый биоматериал с циклической споровой реакцией и склонностью к вторичному разрастанию.',
        'summary': 'Стабилизирован после частичной изоляции. Сохраняет всплески импульсной активности при нарушении температурного режима.',
        'containment_protocol': 'Двухконтурный контейнер, температурный коридор 3–5°C, ручная сверка журналов доступа.',
        'threat_level': Specimen.ThreatLevel.MEDIUM,
        'is_active': True,
        'created_offset_days': 42,
    },
    {
        'code': 'SA-22',
        'name': 'Пелагическая тканевая масса',
        'status': Specimen.Status.CONTAINMENT_IV,
        'short_description': 'Тканевая масса глубоководного происхождения с реакцией на механический перенос.',
        'summary': 'Активный контур повышенной угрозы. Наблюдается нестабильность при транспортировке между секциями.',
        'containment_protocol': 'Герметичная транспортная капсула, дублированная среда содержания, операторский контур допуска.',
        'threat_level': Specimen.ThreatLevel.HIGH,
        'is_active': True,
        'created_offset_days': 37,
    },
    {
        'code': 'SA-23',
        'name': 'Культура «Чёрная вена»',
        'status': Specimen.Status.CONTAINMENT_IV,
        'short_description': 'Сосудистая культура с выраженной реакцией на колебания давления и биохимического состава среды.',
        'summary': 'Объект остаётся одним из ключевых источников биоинцидентов в архиве. Требует жёсткого контура содержания.',
        'containment_protocol': 'Герметичный биоконтейнер, изоляционный шлюз, непрерывный контроль давления.',
        'threat_level': Specimen.ThreatLevel.HIGH,
        'is_active': True,
        'created_offset_days': 31,
    },
    {
        'code': 'SA-24',
        'name': 'Споровый конгломерат «Абиссаль-II»',
        'status': Specimen.Status.CONTAINMENT_IV,
        'short_description': 'Композитная споровая масса лабораторного происхождения, склонная к резкому выбросу при вскрытии контура.',
        'summary': 'Частично стабилизирован после серии карантинных мер. Возможна повторная эскалация при нарушении герметичности.',
        'containment_protocol': 'Карантинный отсек, отрицательное давление, изолирующие маски фильтрации класса IV.',
        'threat_level': Specimen.ThreatLevel.HIGH,
        'is_active': True,
        'created_offset_days': 29,
    },
    {
        'code': 'SA-25',
        'name': 'Криогенная плазма «Левиафан»',
        'status': Specimen.Status.OBSERVATION,
        'short_description': 'Плазменный раствор, сохраняющий стабильность только при глубокой криоконсервации.',
        'summary': 'Активных инцидентов нет. Последняя сессия завершилась успешной стабилизацией и переводом в режим наблюдения.',
        'containment_protocol': 'Криомодуль с двойным резервированием, закрытый доступ по заявке, пассивный мониторинг.',
        'threat_level': Specimen.ThreatLevel.LOW,
        'is_active': True,
        'created_offset_days': 25,
    },
    {
        'code': 'SA-26',
        'name': 'Вазальный субстрат «Секция Е»',
        'status': Specimen.Status.CONTAINMENT_II,
        'short_description': 'Материал для восстановления сосудистых структур, реагирующий на смену спектра освещения.',
        'summary': 'Режим просмотра. Открытых инцидентов нет, доступ требуется в основном для истории вмешательств.',
        'containment_protocol': 'Закрытая кассета хранения, ограничение по времени экспозиции, журнал вскрытий.',
        'threat_level': Specimen.ThreatLevel.LOW,
        'is_active': True,
        'created_offset_days': 20,
    },
    {
        'code': 'SA-27',
        'name': 'Морфогенная сеть «Таласса»',
        'status': Specimen.Status.CONTAINMENT_III,
        'short_description': 'Органоидная сеть, формирующая вторичные узлы при контакте с морской солью.',
        'summary': 'Под наблюдением после неполной стабилизации. Инцидент удержан, но объект остаётся активным.',
        'containment_protocol': 'Контур сухого хранения, датчики влажности, допуск исследовательского контура.',
        'threat_level': Specimen.ThreatLevel.MEDIUM,
        'is_active': True,
        'created_offset_days': 18,
    },
    {
        'code': 'SA-28',
        'name': 'Ферментативный узел «Гидра»',
        'status': Specimen.Status.QUARANTINE,
        'short_description': 'Ферментативный комплекс с агрессивной реакцией на белковые среды и ростом при контакте с воздухом.',
        'summary': 'После неудачного вмешательства объект переведён в карантинный контур. Идёт расследование эскалации.',
        'containment_protocol': 'Карантинный бокс, дистанционное обслуживание, полный запрет на физический перенос.',
        'threat_level': Specimen.ThreatLevel.CRITICAL,
        'is_active': True,
        'created_offset_days': 15,
    },
    {
        'code': 'SA-29',
        'name': 'Инкапсулированный сгусток «Нереида»',
        'status': Specimen.Status.CONTAINMENT_II,
        'short_description': 'Гелевая биомасса с низкой активностью, проявляющая реакцию только при вскрытии внешней оболочки.',
        'summary': 'Пассивное хранение без активных инцидентов. Используется как контрольный объект архива.',
        'containment_protocol': 'Стационарная капсула, недельная сверка оболочки, просмотр без оперативного допуска.',
        'threat_level': Specimen.ThreatLevel.LOW,
        'is_active': True,
        'created_offset_days': 12,
    },
    {
        'code': 'SA-30',
        'name': 'Дермальный матрикс «Оникс»',
        'status': Specimen.Status.CONTAINMENT_III,
        'short_description': 'Плотный матрикс регенеративного класса с устойчивой реакцией на акустические импульсы.',
        'summary': 'Последний инцидент закрыт. Образец переведён в устойчивый режим внутреннего допуска.',
        'containment_protocol': 'Изолированный стенд хранения, акустическая защита, журнал технических запусков.',
        'threat_level': Specimen.ThreatLevel.MEDIUM,
        'is_active': True,
        'created_offset_days': 9,
    },
    {
        'code': 'SA-31',
        'name': 'Гемолатентная колония «Сумрак»',
        'status': Specimen.Status.CONTAINMENT_IV,
        'short_description': 'Латентная колония с задержанным гемореактивным откликом и ускорением при нарушении биофильтра.',
        'summary': 'Активный инцидент высокой серьёзности. Система рекомендует жёсткий протокол, доступ ограничен операторским контуром.',
        'containment_protocol': 'Герметичный шлюз, биофильтр двойной ступени, ручное подтверждение каждого доступа.',
        'threat_level': Specimen.ThreatLevel.HIGH,
        'is_active': True,
        'created_offset_days': 5,
    },
    {
        'code': 'SA-32',
        'name': 'Синовиальная плёнка «Ламбда-Риф»',
        'status': Specimen.Status.CONTAINMENT_II,
        'short_description': 'Полупрозрачная плёнка биосинтетического класса, реагирующая на солевой сдвиг среды.',
        'summary': 'Используется как образец низкой угрозы с редкими техническими отклонениями по обслуживанию.',
        'containment_protocol': 'Закрытая кассета хранения, ежесуточная замена буферной среды, журнал инспекций.',
        'threat_level': Specimen.ThreatLevel.LOW,
        'is_active': True,
        'created_offset_days': 16,
    },
    {
        'code': 'SA-33',
        'name': 'Фибриллярная капсула «Гелиос»',
        'status': Specimen.Status.CONTAINMENT_III,
        'short_description': 'Фибриллярная культура с реакцией на световой импульс и задержанным морфогенезом.',
        'summary': 'Сохраняет средний уровень угрозы. После частичной стабилизации переведена в режим расширенного наблюдения.',
        'containment_protocol': 'Светонепроницаемый модуль, циклическая сверка спектра, ограничение на лабораторный перенос.',
        'threat_level': Specimen.ThreatLevel.MEDIUM,
        'is_active': True,
        'created_offset_days': 14,
    },
    {
        'code': 'SA-34',
        'name': 'Капиллярный органоид «Нокс»',
        'status': Specimen.Status.CONTAINMENT_IV,
        'short_description': 'Органоид сосудистого типа, ускоряющий рост при контакте с нестерильной биосредой.',
        'summary': 'По образцу открыт активный инцидент высокой серьёзности. Требуется постоянный операторский контроль.',
        'containment_protocol': 'Герметичный шлюзовый модуль, двойная фильтрация среды, ручное подтверждение вскрытия.',
        'threat_level': Specimen.ThreatLevel.HIGH,
        'is_active': True,
        'created_offset_days': 8,
    },
    {
        'code': 'SA-35',
        'name': 'Спектральный матрикс «Кассиопея»',
        'status': Specimen.Status.QUARANTINE,
        'short_description': 'Матричный биокомплекс с резким фазовым откликом на электромагнитные помехи.',
        'summary': 'Карантинный образец критического класса. История вмешательств включает успешные и эскалационные сессии.',
        'containment_protocol': 'Экранированный карантинный блок, дистанционный доступ, запрет на прямой контакт с контуром.',
        'threat_level': Specimen.ThreatLevel.CRITICAL,
        'is_active': True,
        'created_offset_days': 6,
    },
]

INCIDENT_DATA = [
    ('SA-21', 'Рост импульсной активности мицелия', 'Во время контрольной сверки зафиксирован краткий всплеск роста по внешнему контуру.', Incident.ResponseProtocol.AUTO, Incident.Severity.HIGH, False, 40),
    ('SA-21', 'Стабилизация температурного контура', 'После перенастройки хладагента отклонение было устранено без повторного выброса.', Incident.ResponseProtocol.OBSERVE, Incident.Severity.LOW, True, 35),
    ('SA-22', 'Нестабильность ткани при переносе', 'При перемещении между секциями масса показала краткий всплеск структурной подвижности.', Incident.ResponseProtocol.AUTO, Incident.Severity.HIGH, False, 22),
    ('SA-22', 'Сбой транспортного крепления', 'Наружный фиксатор капсулы дал кратковременную просадку давления.', Incident.ResponseProtocol.QUARANTINE, Incident.Severity.MEDIUM, True, 26),
    ('SA-23', 'Подозрение на нестабильность сосудистой культуры', 'Зафиксировано атипичное изменение структуры культуры и отклонение от стандартных показателей.', Incident.ResponseProtocol.QUARANTINE, Incident.Severity.CRITICAL, False, 19),
    ('SA-24', 'Нарушение герметичности внешнего контейнера', 'При плановой проверке обнаружено частичное повреждение защитного слоя контейнера.', Incident.ResponseProtocol.QUARANTINE, Incident.Severity.HIGH, True, 17),
    ('SA-24', 'Повторное спорообразование во внутреннем контуре', 'Часть массы перешла в активный режим после краткой просадки температуры.', Incident.ResponseProtocol.QUARANTINE, Incident.Severity.HIGH, False, 12),
    ('SA-25', 'Кратковременный перегрев криомодуля', 'Резервный контур автоматически компенсировал потерю охлаждения.', Incident.ResponseProtocol.OBSERVE, Incident.Severity.MEDIUM, True, 21),
    ('SA-26', 'Отклонение спектра освещения', 'Источник внутренней подсветки вышел за допустимый диапазон, инцидент устранён обслуживанием.', Incident.ResponseProtocol.OBSERVE, Incident.Severity.LOW, True, 15),
    ('SA-27', 'Рост вторичных узлов после анализа', 'После отбора проб структура начала формировать новые ответвления за пределами контрольной схемы.', Incident.ResponseProtocol.OBSERVE, Incident.Severity.HIGH, False, 11),
    ('SA-27', 'Задержка отклика датчиков влажности', 'Показания одного из модулей временно перестали соответствовать контрольному диапазону.', Incident.ResponseProtocol.OBSERVE, Incident.Severity.MEDIUM, True, 13),
    ('SA-28', 'Ферментативная эскалация при вскрытии', 'Контур вскрытия вызвал резкий рост агрессивной ферментативной активности.', Incident.ResponseProtocol.QUARANTINE, Incident.Severity.CRITICAL, False, 8),
    ('SA-29', 'Плановая ревизия оболочки', 'Нарушений не выявлено, запись оставлена как техническая история проверки.', Incident.ResponseProtocol.OBSERVE, Incident.Severity.LOW, True, 7),
    ('SA-30', 'Акустический резонанс в стенде', 'После теста амортизирующего контура возник краткий вторичный отклик.', Incident.ResponseProtocol.ISOLATE, Incident.Severity.MEDIUM, True, 10),
    ('SA-31', 'Рост латентной колонии в биофильтре', 'Во внутреннем биофильтре обнаружен переход колонии в высокоактивную фазу.', Incident.ResponseProtocol.QUARANTINE, Incident.Severity.HIGH, False, 4),
    ('SA-32', 'Плавающее солевое отклонение в кассете', 'Буферная среда сместилась от эталонной солевой карты, но была быстро скорректирована.', Incident.ResponseProtocol.OBSERVE, Incident.Severity.LOW, True, 14),
    ('SA-32', 'Плановая ревизия внутренней оболочки', 'Во время технической проверки подтверждена полная герметичность кассеты.', Incident.ResponseProtocol.OBSERVE, Incident.Severity.LOW, True, 9),
    ('SA-32', 'Микроразрыв внутренней мембраны', 'На внутренней мембране кассеты обнаружен локальный дефект без выхода материала за внешний контур.', Incident.ResponseProtocol.AUTO, Incident.Severity.MEDIUM, False, 3),
    ('SA-33', 'Медленный всплеск морфогенеза', 'После серии световых импульсов структура сформировала дополнительный фибриллярный узел.', Incident.ResponseProtocol.QUARANTINE, Incident.Severity.MEDIUM, False, 10),
    ('SA-33', 'Срыв светового коридора', 'Один из экранов модуля дал кратковременный выброс яркости выше допустимого диапазона.', Incident.ResponseProtocol.OBSERVE, Incident.Severity.MEDIUM, True, 12),
    ('SA-33', 'Кратковременная потеря спектральной маскировки', 'Внешний кожух модуля не удержал полную световую маскировку в фазе технического прогрева.', Incident.ResponseProtocol.OBSERVE, Incident.Severity.LOW, True, 4),
    ('SA-34', 'Рост капиллярной сетки в рабочем шлюзе', 'В служебном шлюзе обнаружено ускоренное формирование сосудистых нитей.', Incident.ResponseProtocol.ISOLATE, Incident.Severity.HIGH, False, 7),
    ('SA-34', 'Перекос фильтрационной линии', 'Дополнительный фильтр среды не выдержал расчётного потока при ночном цикле.', Incident.ResponseProtocol.QUARANTINE, Incident.Severity.MEDIUM, True, 11),
    ('SA-34', 'Отклонение сосудистой вязкости среды', 'При ночной сверке обнаружено устойчивое изменение вязкости рабочей среды внутри капсулы.', Incident.ResponseProtocol.ISOLATE, Incident.Severity.MEDIUM, True, 6),
    ('SA-35', 'Фазовый выброс в экранированном блоке', 'Контур зафиксировал краткий электромагнитный импульс с ростом внутренней активности.', Incident.ResponseProtocol.QUARANTINE, Incident.Severity.CRITICAL, False, 5),
    ('SA-35', 'Сбой экранирующей решётки', 'В экранирующем модуле обнаружена просадка изоляции с временным ростом фона.', Incident.ResponseProtocol.QUARANTINE, Incident.Severity.HIGH, True, 13),
    ('SA-35', 'Нестабильность экранированной камеры при запуске резерва', 'Во время перехода на резервное питание матрикс дал краткий скачок фазового шума.', Incident.ResponseProtocol.QUARANTINE, Incident.Severity.HIGH, True, 3),
]

LOG_DATA = [
    ('SA-21', 'Рост импульсной активности мицелия', ResolutionLog.Role.OPERATOR, Incident.ResponseProtocol.ISOLATE, Incident.ResponseProtocol.ISOLATE, ResolutionLog.Outcome.SUCCESS, 'Контур стабилизирован', 'Стабилизирован', 'Протокол изоляции удержал всплеск активности без повторного роста.', 'Система снизила угрозу и закрыла текущую фазу отклонения.', Incident.Severity.HIGH, False, Incident.Severity.MEDIUM, True, ResolutionLog.ThemeState.SUCCESS, False, True, 34),
    ('SA-22', 'Нестабильность ткани при переносе', ResolutionLog.Role.RESEARCHER, Incident.ResponseProtocol.QUARANTINE, Incident.ResponseProtocol.ISOLATE, ResolutionLog.Outcome.PARTIAL, 'Ситуация удержана под контролем', 'Под наблюдением', 'Выбран карантинный режим. Контур удержан, но транспортные ограничения оставлены активными.', 'Инцидент остаётся открытым до повторной транспортной сверки.', Incident.Severity.HIGH, False, Incident.Severity.MEDIUM, False, ResolutionLog.ThemeState.PARTIAL, False, False, 10),
    ('SA-23', 'Подозрение на нестабильность сосудистой культуры', ResolutionLog.Role.OPERATOR, Incident.ResponseProtocol.QUARANTINE, Incident.ResponseProtocol.QUARANTINE, ResolutionLog.Outcome.SUCCESS, 'Критическая фаза локализована', 'Стабилизирован', 'Система подтвердила корректность выбранного карантинного протокола и закрыла активную фазу.', 'Сосудистая культура переведена в устойчивый режим под повторным наблюдением.', Incident.Severity.CRITICAL, False, Incident.Severity.HIGH, True, ResolutionLog.ThemeState.SUCCESS, False, True, 18),
    ('SA-24', 'Повторное спорообразование во внутреннем контуре', ResolutionLog.Role.RESEARCHER, Incident.ResponseProtocol.QUARANTINE, Incident.ResponseProtocol.QUARANTINE, ResolutionLog.Outcome.SUCCESS, 'Споровый выброс купирован', 'Стабилизирован', 'Карантинный протокол совпал с рекомендацией системы и погасил выброс.', 'Контур содержания удержан без повторной утечки.', Incident.Severity.HIGH, False, Incident.Severity.MEDIUM, True, ResolutionLog.ThemeState.SUCCESS, False, True, 11),
    ('SA-25', 'Кратковременный перегрев криомодуля', ResolutionLog.Role.OBSERVER, '', '', ResolutionLog.Outcome.REVIEW_ONLY, 'Открыт режим просмотра', 'Режим просмотра', 'Активных инцидентов не найдено. Система зафиксировала просмотр досье.', 'Криомодуль остаётся в пассивном мониторинге.', Incident.Severity.MEDIUM, True, Incident.Severity.MEDIUM, True, ResolutionLog.ThemeState.REVIEW, False, False, 6),
    ('SA-26', None, ResolutionLog.Role.OBSERVER, '', '', ResolutionLog.Outcome.REVIEW_ONLY, 'Открыт режим просмотра', 'Режим просмотра', 'Для образца отсутствуют активные инциденты. Сохранён только факт доступа.', 'Просмотр выполнен без изменения параметров.', '', False, '', False, ResolutionLog.ThemeState.REVIEW, False, False, 5),
    ('SA-27', 'Рост вторичных узлов после анализа', ResolutionLog.Role.RESEARCHER, Incident.ResponseProtocol.QUARANTINE, Incident.ResponseProtocol.ISOLATE, ResolutionLog.Outcome.PARTIAL, 'Контур удержан частично', 'Под наблюдением', 'Система признала протокол достаточным по силе, но несоответствующим базовой рекомендации.', 'Узел оставлен под расширенным наблюдением.', Incident.Severity.HIGH, False, Incident.Severity.MEDIUM, False, ResolutionLog.ThemeState.PARTIAL, False, False, 9),
    ('SA-28', 'Ферментативная эскалация при вскрытии', ResolutionLog.Role.OPERATOR, Incident.ResponseProtocol.ISOLATE, Incident.ResponseProtocol.QUARANTINE, ResolutionLog.Outcome.ESCALATION, 'Система фиксирует эскалацию', 'Эскалация', 'Выбранный протокол оказался слабее требуемого уровня. Контур переведён в аварийный режим.', 'Объект удерживается только в карантинном контуре.', Incident.Severity.HIGH, False, Incident.Severity.CRITICAL, False, ResolutionLog.ThemeState.ESCALATION, True, False, 7),
    ('SA-30', 'Акустический резонанс в стенде', ResolutionLog.Role.OPERATOR, Incident.ResponseProtocol.ISOLATE, Incident.ResponseProtocol.ISOLATE, ResolutionLog.Outcome.SUCCESS, 'Резонанс локализован', 'Стабилизирован', 'Операторский протокол совпал с рекомендацией и быстро вернул стенд в устойчивый режим.', 'Образец переведён в штатный режим внутреннего допуска.', Incident.Severity.MEDIUM, False, Incident.Severity.LOW, True, ResolutionLog.ThemeState.SUCCESS, False, True, 3),
    ('SA-31', 'Рост латентной колонии в биофильтре', ResolutionLog.Role.OPERATOR, Incident.ResponseProtocol.ISOLATE, Incident.ResponseProtocol.QUARANTINE, ResolutionLog.Outcome.ESCALATION, 'Наблюдается повторная эскалация', 'Эскалация', 'Система зафиксировала недостаточную силу вмешательства и рост активности колонии.', 'Рекомендуется немедленный карантинный протокол и повторный доступ только оператору.', Incident.Severity.HIGH, False, Incident.Severity.CRITICAL, False, ResolutionLog.ThemeState.ESCALATION, True, False, 2),
    ('SA-33', 'Медленный всплеск морфогенеза', ResolutionLog.Role.RESEARCHER, Incident.ResponseProtocol.QUARANTINE, Incident.ResponseProtocol.ISOLATE, ResolutionLog.Outcome.PARTIAL, 'Морфогенез удержан частично', 'Под наблюдением', 'Карантинный режим оказался достаточным по силе, но базовая рекомендация системы оставалась мягче и точнее для текущего контура.', 'Образец оставлен под расширенным исследовательским наблюдением.', Incident.Severity.MEDIUM, False, Incident.Severity.LOW, False, ResolutionLog.ThemeState.PARTIAL, False, False, 8),
    ('SA-35', 'Фазовый выброс в экранированном блоке', ResolutionLog.Role.OPERATOR, Incident.ResponseProtocol.QUARANTINE, Incident.ResponseProtocol.QUARANTINE, ResolutionLog.Outcome.SUCCESS, 'Фазовый контур стабилизирован', 'Стабилизирован', 'Система подтвердила, что жёсткий карантинный протокол полностью совпал с рекомендацией и локализовал выброс.', 'Экранированный блок возвращён в контролируемую фазу без повторной утечки.', Incident.Severity.CRITICAL, False, Incident.Severity.HIGH, True, ResolutionLog.ThemeState.SUCCESS, False, True, 4),
]


class Command(BaseCommand):
    help = 'Наполняет проект Specimen Archive демонстрационными данными.'

    @transaction.atomic
    def handle(self, *args, **options):
        now = timezone.now()
        created_specimens = 0
        created_incidents = 0
        created_logs = 0

        specimens = {}
        for item in SPECIMEN_DATA:
            defaults = {key: value for key, value in item.items() if key not in {'code', 'created_offset_days'}}
            specimen, created = Specimen.objects.update_or_create(code=item['code'], defaults=defaults)
            Specimen.objects.filter(pk=specimen.pk).update(created_at=now - timedelta(days=item['created_offset_days']))
            specimen.refresh_from_db()
            specimens[item['code']] = specimen
            created_specimens += int(created)

        incidents = {}
        for specimen_code, title, description, protocol, severity, is_resolved, days_offset in INCIDENT_DATA:
            specimen = specimens[specimen_code]
            incident, created = Incident.objects.update_or_create(
                specimen=specimen,
                title=title,
                defaults={
                    'description': description,
                    'response_protocol': protocol,
                    'severity': severity,
                    'is_resolved': is_resolved,
                },
            )
            Incident.objects.filter(pk=incident.pk).update(created_at=now - timedelta(days=days_offset))
            incident.refresh_from_db()
            incidents[(specimen_code, title)] = incident
            created_incidents += int(created)

        for (
            specimen_code,
            incident_title,
            role,
            selected_protocol,
            recommended_protocol,
            outcome,
            result_title,
            final_status_text,
            result_summary,
            system_note,
            previous_severity,
            previous_resolved_state,
            new_severity,
            new_resolved_state,
            ui_theme_state,
            escalation_flag,
            stabilization_flag,
            days_offset,
        ) in LOG_DATA:
            specimen = specimens[specimen_code]
            incident = incidents.get((specimen_code, incident_title)) if incident_title else None
            completed_at = now - timedelta(days=days_offset, hours=2)

            log, created = ResolutionLog.objects.get_or_create(
                specimen=specimen,
                incident=incident,
                selected_role=role,
                outcome=outcome,
                completed_at=completed_at,
                defaults={
                    'selected_protocol': selected_protocol,
                    'recommended_protocol': recommended_protocol,
                    'result_title': result_title,
                    'final_status_text': final_status_text,
                    'result_summary': result_summary,
                    'system_note': system_note,
                    'was_incident_active': bool(incident),
                    'previous_severity': previous_severity,
                    'previous_resolved_state': previous_resolved_state,
                    'new_severity': new_severity,
                    'new_resolved_state': new_resolved_state,
                    'ui_theme_state': ui_theme_state,
                    'escalation_flag': escalation_flag,
                    'stabilization_flag': stabilization_flag,
                },
            )
            if created:
                ResolutionLog.objects.filter(pk=log.pk).update(created_at=completed_at - timedelta(minutes=6))
                created_logs += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Демо-данные готовы: образцов {len(SPECIMEN_DATA)}, инцидентов {len(INCIDENT_DATA)}, '
                f'сессий доступа {len(LOG_DATA)}. Создано новых: specimens={created_specimens}, '
                f'incidents={created_incidents}, resolution_logs={created_logs}.'
            )
        )
