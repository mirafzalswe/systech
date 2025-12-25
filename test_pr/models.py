from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


class Test(models.Model):
    """Модель теста"""
    STATUS_CHOICES = [
        ('active', 'Активен'),
        ('inactive', 'Неактивен'),
    ]
    
    ANSWER_DISPLAY_CHOICES = [
        ('after_each', 'После каждого вопроса'),
        ('at_end', 'В конце теста'),
        ('never', 'Не показывать'),
    ]
    
    title = models.CharField(
        max_length=255,
        verbose_name='Название теста',
        help_text='Введите понятное название теста (например, "История России 10 класс")'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание',
        help_text='Краткое описание теста для участников'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='active',
        verbose_name='Статус',
        help_text='Активен - тест доступен участникам, Неактивен - скрыт'
    )
    show_answers = models.CharField(
        max_length=20,
        choices=ANSWER_DISPLAY_CHOICES,
        default='after_each',
        verbose_name='Показывать правильные ответы'
    )
    show_result = models.BooleanField(
        default=True,
        verbose_name='Показывать результат в конце'
    )
    timer_minutes = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1)],
        verbose_name='Таймер (в минутах)',
        help_text='Оставьте пусто для отсутствия ограничения по времени'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлён')
    
    class Meta:
        verbose_name = 'Тест'
        verbose_name_plural = 'Тесты'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def get_active_questions(self):
        """Получить все вопросы теста"""
        return self.questions.all()


class Question(models.Model):
    """Модель вопроса"""
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Тест'
    )
    text = models.TextField(
        verbose_name='Текст вопроса',
        help_text='Сформулируйте вопрос четко и понятно'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='Порядок',
        help_text='Порядок отображения вопроса (0 - первый)'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    
    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['test', 'order']
        unique_together = ('test', 'order')
    
    def __str__(self):
        return f"{self.test.title} - {self.text[:50]}"
    
    def clean(self):
        """Валидация вопроса"""
        super().clean()
        if not self.text or not self.text.strip():
            raise ValidationError({'text': 'Текст вопроса не может быть пустым'})
    
    def get_answers(self):
        """Получить все варианты ответов для этого вопроса"""
        return self.answers.all()
    
    def get_correct_answer(self):
        """Получить правильный ответ"""
        return self.answers.filter(is_correct=True).first()


class Answer(models.Model):
    """Модель варианта ответа"""
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Вопрос'
    )
    text = models.CharField(
        max_length=500,
        verbose_name='Текст ответа',
        help_text='Введите вариант ответа'
    )
    is_correct = models.BooleanField(
        default=False,
        verbose_name='Правильный ответ',
        help_text='Отметьте галочкой, если это правильный ответ'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='Порядок',
        help_text='Порядок отображения варианта (0 - первый)'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    
    class Meta:
        verbose_name = 'Ответ'
    
    def clean(self):
        """Валидация ответа"""
        super().clean()
        if not self.text or not self.text.strip():
            raise ValidationError({'text': 'Текст ответа не может быть пустым'})
        verbose_name_plural = 'Ответы'
        ordering = ['question', 'order']
        unique_together = ('question', 'order')
    
    def __str__(self):
        return f"{self.question.text[:30]} - {self.text[:40]}"


class Participant(models.Model):
    """Модель участника тестирования"""
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    
    class Meta:
        verbose_name = 'Участник'
        verbose_name_plural = 'Участники'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class TestResult(models.Model):
    """Модель результата прохождения теста"""
    test = models.ForeignKey(
        Test,
        on_delete=models.CASCADE,
        related_name='results',
        verbose_name='Тест'
    )
    participant = models.ForeignKey(
        Participant,
        on_delete=models.CASCADE,
        related_name='test_results',
        verbose_name='Участник'
    )
    total_questions = models.IntegerField(verbose_name='Всего вопросов')
    correct_answers = models.IntegerField(verbose_name='Правильные ответы')
    percentage = models.FloatField(verbose_name='Процент правильных ответов')
    started_at = models.DateTimeField(verbose_name='Начало')
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name='Завершение')
    is_completed = models.BooleanField(default=True, verbose_name='Завершён')
    
    class Meta:
        verbose_name = 'Результат теста'
        verbose_name_plural = 'Результаты тестов'
        ordering = ['-completed_at']
        unique_together = ('test', 'participant')
    
    def __str__(self):
        return f"{self.participant} - {self.test.title} ({self.percentage}%)"


class UserAnswer(models.Model):
    """Модель ответа пользователя на вопрос"""
    test_result = models.ForeignKey(
        TestResult,
        on_delete=models.CASCADE,
        related_name='user_answers',
        verbose_name='Результат теста'
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name='Вопрос'
    )
    selected_answer = models.ForeignKey(
        Answer,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Выбранный ответ'
    )
    is_correct = models.BooleanField(default=False, verbose_name='Верно')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлён')
    
    class Meta:
        verbose_name = 'Ответ пользователя'
        verbose_name_plural = 'Ответы пользователей'
        ordering = ['test_result', 'question__order']
        unique_together = ('test_result', 'question')
    
    def __str__(self):
        answer_text = self.selected_answer.text if self.selected_answer else "Не ответил"
        return f"{self.test_result.participant} - {answer_text}"
