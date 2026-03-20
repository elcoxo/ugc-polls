# ugc-polls

Сервис для создания и прохождения UGC-опросов.

## Описание

Сервис обеспечивает следующие основные функции:

* Просмотр списка опросов и отдельного опроса (для всех пользователей);
* Создание, редактирование и удаление опросов (только для автора опроса);
* Начало прохождения линейного опроса и получение текущего вопроса (для авторизованных пользователей);
* Сохранение ответа на вопрос с автоматическим переходом к следующему;
* Статистика по опросу — количество прохождений, популярные ответы, среднее время (для автора);
* Административная панель для управления данными;
* Swagger UI для интерактивной документации API;
* Регистрация и аутентификация пользователей через сессии.

<img width="1840" height="1140" alt="1" src="https://github.com/user-attachments/assets/9d1161da-5730-4d77-8836-2542598e6ddc" />

## Технологии

- Django
- Django REST Framework
- PostgreSQL
- Docker / Docker Compose
- Swagger

## Быстрый старт

### Первый запуск

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/elcoxo/quick-quiz.git
   ```

2. Перейдите в директорию проекта:
   ```bash
   cd quick-quiz
   ```

3. Запустите скрипт первого запуска:
   ```bash
   chmod +x first_run.sh && ./first_run.sh
   ```

Скрипт автоматически:

- Запустит контейнеры;
- Выполнит миграции;
- Создаст тестовые данные и пользователя admin (логин и пароль — `admin`);
- Создаст несколько опросов с вопросами и вариантами ответов для демонстрации.

### Остальные запуски

Для последующих запусков используйте команду:

```bash
docker compose -f docker-compose.yml up -d
```

## Альтернативный старт

1. Запустите контейнеры:
   ```bash
   docker compose -f docker-compose.yml up -d
   ```

2. Выполните миграции:
   ```bash
   docker compose -f docker-compose.yml exec backend python manage.py migrate
   ```

3. Создайте суперюзера:
   ```bash
   docker compose -f docker-compose.yml exec backend python manage.py createsuperuser
   ```

<img width="2064" height="874" alt="5" src="https://github.com/user-attachments/assets/dd094721-67cd-40a0-8bcf-d6ee2b8415ff" />


### Доступ

| Сервис         | URL                              |
|----------------|----------------------------------|
| Список опросов | http://127.0.0.1:8000/           |
| API            | http://127.0.0.1:8000/api/       |
| Admin панель   | http://127.0.0.1:8000/admin/     |
| Swagger        | http://127.0.0.1:8000/api/docs/  |
| ReDoc          | http://127.0.0.1:8000/api/redoc/ |

## Структура проекта

- `core/` — основные настройки Django
- `polls/` — опросы, вопросы, сессии и ответы пользователей
- `users/` — управление пользователями и статистика
- `common/` — общие модели и миксины

## Модели

## BaseModel (Базовая модель)

- `created_at`, `updated_at` — даты создания и обновления

### Poll (Опрос)

- `title` — название опроса
- `slug` — уникальный идентификатор (генерируется автоматически)
- `user` — автор опроса (FK на User)

### Question (Вопрос)

- `poll` — опрос (FK на Poll)
- `text` — текст вопроса
- `ordering` — порядок вопроса в опросе

### AnswerOption (Вариант ответа)

- `question` — вопрос (FK на Question)
- `text` — текст варианта ответа
- `order` — порядок отображения

### PollSession (Сессия прохождения)

- `user` — пользователь (FK на User)
- `poll` — опрос (FK на Poll)
- `slug` — уникальный идентификатор сессии
- `finished_at` — дата завершения (null если не завершён)

### UserResponse (Ответ пользователя)

- `session` — сессия (FK на PollSession)
- `question` — вопрос (FK на Question)
- `option` — выбранный вариант (FK на AnswerOption)

## Эндпоинты

Полная интерактивная документация доступна в Swagger: http://127.0.0.1:8000/api/docs/

<img width="2064" height="1032" alt="CleanShot 2026-03-20 at 06 54 18@2x" src="https://github.com/user-attachments/assets/e8d93f41-3c0c-45a6-bdcd-bb37744ef9a6" />


### Аутентификация (через HTML формы)

- `GET /login/` — форма входа
- `POST /login/` — вход в систему
- `POST /logout/` — выход из системы
- `GET /register/` — форма регистрации
- `POST /register/` — регистрация нового пользователя

### Опросы

#### `GET /api/polls/` — список всех опросов

Доступен всем пользователям. Для авторизованных возвращает `is_finished`.

Ответ:

```json
[
  {
    "id": 1,
    "slug": "aB3kR9mNpQ2x",
    "title": "Овощи",
    "user": "admin",
    "is_finished": false,
    "created_at": "2026-03-20T10:00:00Z",
    "updated_at": "2026-03-20T10:00:00Z"
  }
]
```

#### `POST /api/polls/` — создать опрос

Требует аутентификации. Автор назначается автоматически.

Тело запроса:

```json
{
  "title": "Мой опрос"
}
```

#### `GET /api/polls/{slug}/` — детали опроса (доступен всем пользователям)

#### `PUT/PATCH /api/polls/{slug}/` — редактировать опрос (только автор опроса.)

#### `DELETE /api/polls/{slug}/` — удалить опрос (только автор опроса.)

#### `POST /api/polls/{slug}/start/` — начать прохождение опроса

Требует аутентификации. Создаёт сессию и возвращает первый вопрос.

Ответ:

```json
{
  "session_slug": "o65UkFiTQiKE",
  "question": {
    "id": 1,
    "text": "Ты любишь помидоры?",
    "ordering": 0,
    "options": [
      {
        "id": 1,
        "text": "Да",
        "order": 0
      },
      {
        "id": 2,
        "text": "Нет",
        "order": 1
      }
    ]
  }
}
```

### Прохождение опроса

<img width="1840" height="758" alt="4" src="https://github.com/user-attachments/assets/8a742951-3988-429a-8659-4e06375d8250" />


#### `GET /api/sessions/{slug}/question/` — текущий вопрос

Возвращает следующий вопрос или `{"completed": true}` если опрос пройден.

#### `POST /api/sessions/{slug}/answer/` — отправить ответ

Сохраняет ответ и возвращает следующий вопрос.

Тело запроса:

```json
{
  "question": 1,
  "option": 2
}
```

Ответ (следующий вопрос):

```json
{
  "id": 2,
  "text": "Ты любишь огурцы?",
  "ordering": 1,
  "options": [
    ...
  ]
}
```

Ответ (опрос завершён):

```json
{
  "completed": true
}
```

<img width="1840" height="550" alt="3" src="https://github.com/user-attachments/assets/77363bd2-8b74-4406-8c4f-8ae1f2d66a10" />


### Статистика

#### `GET /polls/{slug}/stats/` — страница статистики по опросу

Только автор опроса. Возвращает HTML-страницу с графиками:

- количество начатых и завершённых прохождений
- среднее время прохождения
- распределение ответов по каждому вопросу

<img width="1840" height="1204" alt="2" src="https://github.com/user-attachments/assets/90877278-97e2-4391-9dc8-73c4e8ec448a" />

## Линтеры

Для проверки кода используется flake8:

```bash
docker compose -f docker-compose.yml exec backend flake8
```
