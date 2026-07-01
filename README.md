# Sport Complex — Django

Веб-платформа фитнес-центра **POWER GYM**: расписание, абонементы, тренеры, личный кабинет и чат с администратором.

![Python](https://img.shields.io/badge/Python-3.12+-blue)
![Django](https://img.shields.io/badge/Django-5.0-green)

## Возможности

- Главная с видео-hero, направлениями и абонементами
- Регистрация и личный кабинет пользователя
- Расписание тренировок с записью
- Заявки на абонементы
- Чат пользователь ↔ администратор
- Кастомная админ-панель Django

## Стек

- Python 3.12+, Django 5
- SQLite
- Bootstrap 5, Tailwind (theme app)
- Pillow

## Быстрый старт

```bash
git clone https://github.com/mxdshvch/Sport-Compex-Django_V1.git
cd Sport-Compex-Django_V1

python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cd fitness_center
cp ../.env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Сайт: http://127.0.0.1:8000/

## Переменные окружения

Скопируй `.env.example` → `fitness_center/.env`:

```env
SECRET_KEY=your-secret-key
DEBUG=True
```

## Основные URL

| Раздел | URL |
|--------|-----|
| Главная | `/` |
| Вход | `/users/login/` |
| Абонементы | `/memberships/` |
| Тренеры | `/trainers/` |
| Личный кабинет | `/account/` |
| Админка | `/admin/` |

## Структура

```
diplom-sport/
├── fitness_center/     # Django-проект
│   ├── users/          # auth, профиль, чат
│   ├── workouts/       # направления, расписание
│   ├── trainers/       # тренеры
│   ├── memberships/    # абонементы
│   ├── templates/
│   ├── static/
│   └── media/
├── requirements.txt
└── README.md
```

## Автор

[mxdshvch](https://github.com/mxdshvch)
