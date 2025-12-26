# Настройка Vercel для деплоя Django проекта с Neon PostgreSQL

## Шаг 1: Добавьте переменные окружения в Vercel

Перейдите в настройки проекта на Vercel → **Environment Variables** и добавьте:

### Обязательные переменные:

1. **POSTGRES_URL** (или DATABASE_URL)
   ```
   postgresql://neondb_owner:npg_slT4D2umNjdk@ep-flat-hill-adobb3z8-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
   ```

2. **DEBUG**
   ```
   False
   ```

3. **SECRET_KEY** (сгенерируйте новый!)
   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
   Пример результата:
   ```
   django-insecure-ваш-новый-секретный-ключ-здесь
   ```

### Важно:
- Для каждой переменной выберите: **Production**, **Preview**, **Development**
- После добавления всех переменных - нажмите **Save**

## Шаг 2: Выполните миграции базы данных

После первого успешного деплоя нужно применить миграции к Neon базе данных:

### Вариант 1: Локально с подключением к Neon (рекомендуется)

1. Создайте файл `.env` в корне проекта:
   ```bash
   DATABASE_URL=postgresql://neondb_owner:npg_slT4D2umNjdk@ep-flat-hill-adobb3z8-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require
   SECRET_KEY=ваш-секретный-ключ
   DEBUG=False
   ```

2. Установите python-dotenv:
   ```bash
   pip install python-dotenv
   ```

3. Обновите `manage.py` для загрузки .env (первые строки):
   ```python
   import os
   from dotenv import load_dotenv
   load_dotenv()
   ```

4. Выполните миграции:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

### Вариант 2: Через переменные окружения

```bash
export DATABASE_URL="postgresql://neondb_owner:npg_slT4D2umNjdk@ep-flat-hill-adobb3z8-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require"
python manage.py migrate
python manage.py createsuperuser
```

## Шаг 3: Деплой на Vercel

```bash
# Если еще не установлен Vercel CLI
npm i -g vercel

# Деплой
vercel --prod
```

## Шаг 4: Загрузка данных (опционально)

После миграций можно загрузить тестовые данные:

```bash
# С подключением к Neon
DATABASE_URL="postgresql://..." python manage.py loaddata your_fixture.json

# Или используйте ваш скрипт
DATABASE_URL="postgresql://..." python load_sample_data.py
```

## Проверка работы

1. После деплоя откройте ваш сайт на Vercel
2. Перейдите в `/admin` - должна открыться страница входа
3. Войдите с учетными данными суперпользователя

## Решение проблем

### Ошибка подключения к базе данных
- Проверьте, что переменная `POSTGRES_URL` или `DATABASE_URL` установлена в Vercel
- Убедитесь, что в конце URL есть `?sslmode=require`

### Статические файлы не загружаются
- Выполните `python manage.py collectstatic` локально
- Убедитесь, что папка `staticfiles` не в `.gitignore` (временно)
- Или настройте CDN для статики

### WhiteNoise ошибки
- Если возникают проблемы с WhiteNoise, можно временно отключить его
- Закомментируйте `whitenoise.middleware.WhiteNoiseMiddleware` в `MIDDLEWARE`
- Закомментируйте `STATICFILES_STORAGE` в settings.py

## Локальная разработка

Для локальной разработки просто не устанавливайте DATABASE_URL:
- Проект автоматически будет использовать SQLite
- DEBUG=True по умолчанию

```bash
# Запуск локально
python manage.py runserver
```
