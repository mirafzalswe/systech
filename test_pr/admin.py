from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Count
from .models import Test, Question, Answer, Participant, TestResult, UserAnswer


class AnswerInline(admin.TabularInline):
    """Inline-редактор для вариантов ответов"""
    model = Answer
    extra = 4
    fields = ('text', 'is_correct', 'order')
    verbose_name = "Вариант ответа"
    verbose_name_plural = "Варианты ответов"
    classes = ['collapse']
    
    def get_extra(self, request, obj=None, **kwargs):
        """Больше пустых форм при создании, меньше при редактировании"""
        if obj:
            return 1
        return 4


class QuestionInline(admin.StackedInline):
    """Inline-редактор для вопросов"""
    model = Question
    extra = 3
    fields = ('text', 'order')
    verbose_name = "Вопрос"
    verbose_name_plural = "Вопросы"
    classes = ['collapse']
    show_change_link = True
    
    def get_extra(self, request, obj=None, **kwargs):
        """Больше пустых форм при создании"""
        if obj:
            return 1
        return 3


@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    """Админ для управления тестами"""
    list_display = (
        'title',
        'status_badge',
        'get_questions_count',
        'timer_minutes',
        'show_answers',
        'created_at'
    )
    list_filter = ('status', 'created_at', 'show_answers')
    search_fields = ('title', 'description')
    date_hierarchy = 'created_at'
    save_on_top = True
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'description', 'status'),
            'description': 'Введите название и описание теста'
        }),
        ('Настройки времени и отображения', {
            'fields': ('timer_minutes', 'show_answers', 'show_result'),
            'description': 'Настройте таймер и параметры отображения результатов'
        }),
        ('Служебная информация', {
            'fields': ('created_at', 'updated_at', 'preview_link'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at', 'updated_at', 'preview_link')
    inlines = [QuestionInline]
    
    actions = ['make_active', 'make_inactive', 'duplicate_test']
    
    # Для автозаполнения в других моделях
    search_fields = ['title']
    
    @admin.display(description='Статус')
    def status_badge(self, obj):
        """Красивый значок статуса"""
        colors = {
            'active': '#10b981',
            'inactive': '#6b7280',
            'draft': '#f59e0b'
        }
        labels = {
            'active': 'Активен',
            'inactive': 'Неактивен',
            'draft': 'Черновик'
        }
        color = colors.get(obj.status, '#6b7280')
        label = labels.get(obj.status, obj.status)
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 12px; '
            'border-radius: 12px; font-weight: 600; font-size: 11px;">{}</span>',
            color, label
        )
    
    @admin.display(description='Вопросов')
    def get_questions_count(self, obj):
        """Количество вопросов с цветом"""
        count = obj.questions.count()
        color = '#10b981' if count >= 5 else '#f59e0b' if count >= 1 else '#ef4444'
        return format_html(
            '<span style="color: {}; font-weight: 600;">{} вопр.</span>',
            color, count
        )
    
    def make_active(self, request, queryset):
        """Активировать выбранные тесты"""
        updated = queryset.update(status='active')
        self.message_user(request, f'Активировано тестов: {updated}')
    make_active.short_description = "✓ Активировать выбранные тесты"
    
    def make_inactive(self, request, queryset):
        """Деактивировать выбранные тесты"""
        updated = queryset.update(status='inactive')
        self.message_user(request, f'Деактивировано тестов: {updated}')
    make_inactive.short_description = "✗ Деактивировать выбранные тесты"
    
    def duplicate_test(self, request, queryset):
        """Дублировать тест"""
        for test in queryset:
            questions = test.questions.all()
            test.pk = None
            test.title = f"{test.title} (копия)"
            test.status = 'draft'
            test.save()
            
            for question in questions:
                answers = question.answers.all()
                question.pk = None
                question.test = test
                question.save()
                
                for answer in answers:
                    answer.pk = None
                    answer.question = question
                    answer.save()
        
        self.message_user(request, f'Дублировано тестов: {queryset.count()}')
    duplicate_test.short_description = "📋 Дублировать выбранные тесты"
    
    @admin.display(description='Предпросмотр')
    def preview_link(self, obj):
        """Ссылка на предпросмотр теста"""
        if obj.pk:
            from django.urls import reverse
            url = reverse('take_test', args=[obj.pk])
            return format_html(
                '<a href="{}" target="_blank" style="'
                'background: #2563eb; color: white; padding: 8px 16px; '
                'border-radius: 6px; text-decoration: none; font-weight: 600; '
                'display: inline-block;">🔍 Открыть тест</a>',
                url
            )
        return "Сохраните тест для предпросмотра"


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    """Админ для управления вопросами"""
    list_display = (
        'get_test_title',
        'text_preview',
        'order',
        'get_answers_count',
        'has_correct_answer'
    )
    list_filter = ('test', 'test__status', 'created_at')
    search_fields = ('text', 'test__title')
    list_select_related = ('test',)
    save_on_top = True
    
    fieldsets = (
        ('Вопрос', {
            'fields': ('test', 'text', 'order'),
            'description': 'Введите текст вопроса и порядок отображения'
        }),
        ('Служебная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)
    inlines = [AnswerInline]
    
    autocomplete_fields = ['test']
    
    # Для автозаполнения в других моделях
    search_fields = ['text']
    
    actions = ['move_to_top', 'add_default_answers']
    
    @admin.display(description='Тест')
    def get_test_title(self, obj):
        """Название теста с цветным статусом"""
        status_colors = {
            'active': '#10b981',
            'inactive': '#6b7280',
            'draft': '#f59e0b'
        }
        color = status_colors.get(obj.test.status, '#6b7280')
        return format_html(
            '<span style="color: {}; font-weight: 600;">{}</span>',
            color, obj.test.title
        )
    
    @admin.display(description='Текст вопроса')
    def text_preview(self, obj):
        """Превью текста вопроса"""
        text = obj.text[:70] + '...' if len(obj.text) > 70 else obj.text
        return format_html('<span style="font-size: 13px;">{}</span>', text)
    
    @admin.display(description='Ответов')
    def get_answers_count(self, obj):
        """Количество ответов"""
        count = obj.answers.count()
        color = '#10b981' if count >= 2 else '#ef4444'
        return format_html(
            '<span style="color: {}; font-weight: 600;">{}</span>',
            color, count
        )
    
    @admin.display(description='Правильный ответ')
    def has_correct_answer(self, obj):
        """Есть ли правильный ответ"""
        has_correct = obj.answers.filter(is_correct=True).exists()
        if has_correct:
            return mark_safe('<span style="color: #10b981; font-size: 16px;">✓</span>')
        return mark_safe('<span style="color: #ef4444; font-size: 16px;">✗</span>')
    
    def move_to_top(self, request, queryset):
        """Переместить вопросы в начало"""
        for question in queryset:
            question.order = 0
            question.save()
        self.message_user(request, f'Перемещено вопросов: {queryset.count()}')
    move_to_top.short_description = "↑ Переместить в начало"
    
    def add_default_answers(self, request, queryset):
        """Добавить стандартные варианты ответов"""
        for question in queryset:
            if question.answers.count() == 0:
                Answer.objects.create(
                    question=question,
                    text="Вариант А",
                    order=1,
                    is_correct=True
                )
                Answer.objects.create(
                    question=question,
                    text="Вариант Б",
                    order=2,
                    is_correct=False
                )
                Answer.objects.create(
                    question=question,
                    text="Вариант В",
                    order=3,
                    is_correct=False
                )
        self.message_user(request, f'Добавлены ответы для {queryset.count()} вопросов')
    add_default_answers.short_description = "➕ Добавить варианты ответов"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    """Админ для управления ответами"""
    list_display = (
        'get_question_preview',
        'text_preview',
        'is_correct_badge',
        'order',
        'get_test_name'
    )
    list_filter = ('is_correct', 'question__test', 'created_at')
    search_fields = ('text', 'question__text', 'question__test__title')
    list_select_related = ('question', 'question__test')
    save_on_top = True
    
    fieldsets = (
        ('Ответ', {
            'fields': ('question', 'text', 'order', 'is_correct'),
            'description': 'Введите текст ответа и отметьте правильный'
        }),
        ('Служебная информация', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('created_at',)
    
    autocomplete_fields = ['question']
    
    actions = ['mark_as_correct', 'mark_as_incorrect']
    
    @admin.display(description='Вопрос')
    def get_question_preview(self, obj):
        """Превью вопроса"""
        text = obj.question.text[:50] + '...' if len(obj.question.text) > 50 else obj.question.text
        return format_html('<span style="font-size: 12px; color: #64748b;">{}</span>', text)
    
    @admin.display(description='Текст ответа')
    def text_preview(self, obj):
        """Превью текста ответа"""
        return format_html('<span style="font-weight: 500;">{}</span>', obj.text)
    
    @admin.display(description='Правильность')
    def is_correct_badge(self, obj):
        """Значок правильности"""
        if obj.is_correct:
            return mark_safe(
                '<span style="background-color: #10b981; color: white; padding: 4px 10px; '
                'border-radius: 10px; font-size: 11px; font-weight: 600;">ВЕРНО</span>'
            )
        return mark_safe(
            '<span style="background-color: #6b7280; color: white; padding: 4px 10px; '
            'border-radius: 10px; font-size: 11px; font-weight: 600;">НЕВЕРНО</span>'
        )
    
    @admin.display(description='Тест')
    def get_test_name(self, obj):
        """Название теста"""
        return obj.question.test.title
    
    def mark_as_correct(self, request, queryset):
        """Пометить как правильные"""
        updated = queryset.update(is_correct=True)
        self.message_user(request, f'Помечено правильными: {updated}')
    mark_as_correct.short_description = "✓ Пометить как правильные"
    
    def mark_as_incorrect(self, request, queryset):
        """Пометить как неправильные"""
        updated = queryset.update(is_correct=False)
        self.message_user(request, f'Помечено неправильными: {updated}')
    mark_as_incorrect.short_description = "✗ Пометить как неправильные"


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    """Админ для просмотра участников"""
    list_display = ('get_full_name', 'get_test_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('first_name', 'last_name')
    fieldsets = (
        ('Личные данные', {
            'fields': ('first_name', 'last_name')
        }),
    )
    readonly_fields = ('created_at',)
    
    @admin.display(description='Имя')
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    @admin.display(description='Пройдено тестов')
    def get_test_count(self, obj):
        return obj.test_results.count()


@admin.register(TestResult)
class TestResultAdmin(admin.ModelAdmin):
    """Админ для просмотра результатов тестов"""
    list_display = (
        'get_participant_name',
        'test',
        'correct_answers',
        'total_questions',
        'get_percentage',
        'completed_at'
    )
    list_filter = ('test', 'completed_at', 'is_completed')
    search_fields = (
        'participant__first_name',
        'participant__last_name',
        'test__title'
    )
    readonly_fields = (
        'test',
        'participant',
        'total_questions',
        'correct_answers',
        'percentage',
        'started_at',
        'completed_at',
        'is_completed',
        'get_user_answers_display'
    )
    fieldsets = (
        ('Информация об участнике', {
            'fields': ('participant', 'test')
        }),
        ('Результаты', {
            'fields': ('correct_answers', 'total_questions', 'percentage')
        }),
        ('Время прохождения', {
            'fields': ('started_at', 'completed_at', 'is_completed')
        }),
        ('Подробные ответы', {
            'fields': ('get_user_answers_display',),
            'classes': ('collapse',)
        }),
    )
    
    @admin.display(description='Участник')
    def get_participant_name(self, obj):
        return f"{obj.participant.first_name} {obj.participant.last_name}"
    
    @admin.display(description='Результат')
    def get_percentage(self, obj):
        return f"{obj.percentage:.1f}%"
    
    @admin.display(description='Ответы пользователя')
    def get_user_answers_display(self, obj):
        """Отображение всех ответов пользователя"""
        answers = obj.user_answers.select_related('question', 'selected_answer')
        html = '<table style="width:100%; border-collapse:collapse;"><tr><th>Вопрос</th><th>Ответ</th><th>Результат</th></tr>'
        for ua in answers:
            status = '✓ Верно' if ua.is_correct else '✗ Неверно'
            answer_text = ua.selected_answer.text if ua.selected_answer else 'Не ответил'
            html += f'<tr><td style="border:1px solid #ddd; padding:8px;">{ua.question.text}</td>'
            html += f'<td style="border:1px solid #ddd; padding:8px;">{answer_text}</td>'
            html += f'<td style="border:1px solid #ddd; padding:8px; color:{"green" if ua.is_correct else "red"};">{status}</td></tr>'
        html += '</table>'
        return mark_safe(html)
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(UserAnswer)
class UserAnswerAdmin(admin.ModelAdmin):
    """Админ для просмотра ответов пользователя"""
    list_display = (
        'get_participant_name',
        'get_question_text',
        'get_selected_answer',
        'is_correct'
    )
    list_filter = ('is_correct', 'created_at', 'test_result__test')
    search_fields = (
        'test_result__participant__first_name',
        'test_result__participant__last_name',
        'question__text'
    )
    readonly_fields = (
        'test_result',
        'question',
        'selected_answer',
        'is_correct',
        'created_at',
        'updated_at'
    )
    
    @admin.display(description='Участник')
    def get_participant_name(self, obj):
        return f"{obj.test_result.participant.first_name} {obj.test_result.participant.last_name}"
    
    @admin.display(description='Вопрос')
    def get_question_text(self, obj):
        text = obj.question.text
        return text[:40] + '...' if len(text) > 40 else text
    
    @admin.display(description='Выбранный ответ')
    def get_selected_answer(self, obj):
        return obj.selected_answer.text if obj.selected_answer else 'Не ответил'
    
    def has_add_permission(self, request):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
