from django import forms
from .models import Test, Question, Answer


class TestForm(forms.ModelForm):
    """Форма для создания/редактирования теста"""
    class Meta:
        model = Test
        fields = ['title', 'description', 'status', 'timer_minutes', 'show_answers', 'show_result']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Введите название теста'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Описание теста (необязательно)'
            }),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'timer_minutes': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'Оставьте пусто для неограниченного времени'
            }),
            'show_answers': forms.Select(attrs={'class': 'form-control'}),
            'show_result': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class QuestionForm(forms.ModelForm):
    """Форма для создания/редактирования вопроса"""
    class Meta:
        model = Question
        fields = ['text', 'order']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-control question-text',
                'rows': 2,
                'placeholder': 'Введите текст вопроса'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 0
            }),
        }


class AnswerForm(forms.ModelForm):
    """Форма для создания/редактирования ответа"""
    class Meta:
        model = Answer
        fields = ['text', 'is_correct', 'order']
        widgets = {
            'text': forms.TextInput(attrs={
                'class': 'form-control answer-text',
                'placeholder': 'Вариант ответа'
            }),
            'is_correct': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'order': forms.NumberInput(attrs={
                'class': 'form-control',
                'value': 0
            }),
        }
