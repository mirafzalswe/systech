"""
Скрипт для заполнения БД примерами данных.

Используйте команду:
python manage.py shell < load_sample_data.py
"""

from test_pr.models import Test, Question, Answer

# Очищаем существующие данные
print("Очистка существующих данных...")
Test.objects.all().delete()

# Создаём первый тест: Математика
print("✓ Создание теста 'Основы математики'...")
math_test = Test.objects.create(
    title="Основы математики",
    description="Базовые вопросы по математике для начинающих",
    status="active",
    show_answers="after_each",
    show_result=True,
    timer_minutes=15
)

# Вопрос 1: Сложение
q1 = Question.objects.create(
    test=math_test,
    text="Сколько будет 2 + 2?",
    order=1
)
Answer.objects.create(question=q1, text="3", is_correct=False, order=1)
Answer.objects.create(question=q1, text="4", is_correct=True, order=2)
Answer.objects.create(question=q1, text="5", is_correct=False, order=3)

# Вопрос 2: Умножение
q2 = Question.objects.create(
    test=math_test,
    text="Чему равно 5 × 3?",
    order=2
)
Answer.objects.create(question=q2, text="15", is_correct=True, order=1)
Answer.objects.create(question=q2, text="8", is_correct=False, order=2)
Answer.objects.create(question=q2, text="25", is_correct=False, order=3)

# Вопрос 3: Деление
q3 = Question.objects.create(
    test=math_test,
    text="Результат 10 ÷ 2?",
    order=3
)
Answer.objects.create(question=q3, text="5", is_correct=True, order=1)
Answer.objects.create(question=q3, text="8", is_correct=False, order=2)
Answer.objects.create(question=q3, text="20", is_correct=False, order=3)

# Вопрос 4: Вычитание
q4 = Question.objects.create(
    test=math_test,
    text="15 - 7 = ?",
    order=4
)
Answer.objects.create(question=q4, text="8", is_correct=True, order=1)
Answer.objects.create(question=q4, text="22", is_correct=False, order=2)
Answer.objects.create(question=q4, text="7", is_correct=False, order=3)

# Вопрос 5: Степень
q5 = Question.objects.create(
    test=math_test,
    text="2 в степени 3 (2³) = ?",
    order=5
)
Answer.objects.create(question=q5, text="6", is_correct=False, order=1)
Answer.objects.create(question=q5, text="8", is_correct=True, order=2)
Answer.objects.create(question=q5, text="9", is_correct=False, order=3)

print("✓ Создан тест 'Основы математики' с 5 вопросами")

# Создаём второй тест: История
print("\n✓ Создание теста 'История России'...")
history_test = Test.objects.create(
    title="История России",
    description="Вопросы об истории Российской Федерации",
    status="active",
    show_answers="at_end",
    show_result=True,
    timer_minutes=20
)

# Вопрос 1: Основатель Москвы
q6 = Question.objects.create(
    test=history_test,
    text="Кто основал Москву?",
    order=1
)
Answer.objects.create(question=q6, text="Юрий Долгорукий", is_correct=True, order=1)
Answer.objects.create(question=q6, text="Иван Грозный", is_correct=False, order=2)
Answer.objects.create(question=q6, text="Петр I", is_correct=False, order=3)

# Вопрос 2: Год основания
q7 = Question.objects.create(
    test=history_test,
    text="В каком году основана Москва?",
    order=2
)
Answer.objects.create(question=q7, text="1147", is_correct=True, order=1)
Answer.objects.create(question=q7, text="1243", is_correct=False, order=2)
Answer.objects.create(question=q7, text="1380", is_correct=False, order=3)

# Вопрос 3: Ледовое побоище
q8 = Question.objects.create(
    test=history_test,
    text="В каком году произошло Ледовое побоище?",
    order=3
)
Answer.objects.create(question=q8, text="1240", is_correct=True, order=1)
Answer.objects.create(question=q8, text="1242", is_correct=False, order=2)
Answer.objects.create(question=q8, text="1380", is_correct=False, order=3)

print("✓ Создан тест 'История России' с 3 вопросами")

# Создаём третий тест: География
print("\n✓ Создание теста 'География'...")
geo_test = Test.objects.create(
    title="География",
    description="Вопросы по географии России",
    status="active",
    show_answers="never",
    show_result=True,
    timer_minutes=None  # Без таймера
)

# Вопрос 1: Столица
q9 = Question.objects.create(
    test=geo_test,
    text="Столица России?",
    order=1
)
Answer.objects.create(question=q9, text="Москва", is_correct=True, order=1)
Answer.objects.create(question=q9, text="Санкт-Петербург", is_correct=False, order=2)
Answer.objects.create(question=q9, text="Новосибирск", is_correct=False, order=3)

# Вопрос 2: Самая длинная река
q10 = Question.objects.create(
    test=geo_test,
    text="Самая длинная река России?",
    order=2
)
Answer.objects.create(question=q10, text="Волга", is_correct=True, order=1)
Answer.objects.create(question=q10, text="Обь", is_correct=False, order=2)
Answer.objects.create(question=q10, text="Амур", is_correct=False, order=3)

print("✓ Создан тест 'География' с 2 вопросами")

print("\n" + "="*50)
print("✅ База данных успешно заполнена!")
print("="*50)
print("\nТесты готовы к использованию:")
print("1. Основы математики (5 вопросов) - 15 минут")
print("2. История России (3 вопроса) - 20 минут")
print("3. География (2 вопроса) - без ограничения по времени")
print("\nОткройте http://localhost:8000 для начала тестирования")
