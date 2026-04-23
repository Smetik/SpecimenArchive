# SpecimenArchive

Django-проект с интерактивной системой доступа к досье биообразцов и журналом биоинцидентов.

## Запуск проекта

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver