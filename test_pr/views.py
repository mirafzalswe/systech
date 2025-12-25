from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.admin.views.decorators import staff_member_required
from django.utils import timezone
from django.http import JsonResponse
from django.db import transaction
from datetime import timedelta
import json

from .models import Test, Question, Answer, Participant, TestResult, UserAnswer
from .forms import TestForm, QuestionForm, AnswerForm


# ============================================================================
# ПОЛЬЗОВАТЕЛЬСКИЕ VIEWS
# ============================================================================

@require_http_methods(["GET", "POST"])
def register(request):
    """
    Регистрация участника перед началом теста.
    GET: Показывает форму регистрации
    POST: Создаёт участника и перенаправляет на выбор теста
    """
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        
        if not first_name or not last_name:
            return render(request, 'test_pr/register.html', {
                'error': 'Пожалуйста, введите имя и фамилию'
            })
        
        # Создаём или получаем существующего участника
        participant, created = Participant.objects.get_or_create(
            first_name=first_name,
            last_name=last_name
        )
        
        # Сохраняем ID участника в сессии
        request.session['participant_id'] = participant.id
        
        return redirect('test_list')
    
    # Если участник уже зарегистрирован, перенаправляем на список тестов
    if 'participant_id' in request.session:
        return redirect('test_list')
    
    return render(request, 'test_pr/register.html')


@require_http_methods(["GET"])
def test_list(request):
    """
    Отображение списка активных тестов.
    Пользователь должен быть зарегистрирован.
    """
    # Проверяем, зарегистрирован ли пользователь
    participant_id = request.session.get('participant_id')
    if not participant_id:
        return redirect('register')
    
    try:
        participant = Participant.objects.get(id=participant_id)
    except Participant.DoesNotExist:
        request.session.flush()
        return redirect('register')
    
    # Получаем активные тесты
    tests = Test.objects.filter(status='active')
    
    # Получаем информацию о пройденных тестах
    completed_tests = TestResult.objects.filter(
        participant=participant
    ).values_list('test_id', flat=True)
    
    context = {
        'participant': participant,
        'tests': tests,
        'completed_tests': completed_tests,
    }
    
    return render(request, 'test_pr/test_list.html', context)


@require_http_methods(["GET", "POST"])
def take_test(request, test_id):
    """
    Прохождение теста.
    GET: Показывает все вопросы теста с возможностью навигации
    POST: Сохраняет ответы и завершает тест
    """
    participant_id = request.session.get('participant_id')
    if not participant_id:
        return redirect('register')
    
    try:
        participant = Participant.objects.get(id=participant_id)
        test = Test.objects.get(id=test_id, status='active')
    except (Participant.DoesNotExist, Test.DoesNotExist):
        return redirect('test_list')
    
    # Проверяем, не прошёл ли уже этот тест
    existing_result = TestResult.objects.filter(
        test=test,
        participant=participant
    ).first()
    
    if existing_result:
        return redirect('test_result', result_id=existing_result.id)
    
    questions = test.questions.all().order_by('order')
    
    if request.method == 'POST':
        # Завершение теста и сохранение результатов
        total_questions = questions.count()
        
        # Создаём результат теста
        result = TestResult.objects.create(
            test=test,
            participant=participant,
            total_questions=total_questions,
            correct_answers=0,
            percentage=0,
            started_at=timezone.now(),
            is_completed=True
        )
        
        correct_count = 0
        
        # Обрабатываем ответы
        for question in questions:
            answer_id = request.POST.get(f'answer_{question.id}')
            
            user_answer = UserAnswer.objects.create(
                test_result=result,
                question=question,
                is_correct=False
            )
            
            if answer_id:
                try:
                    selected_answer = Answer.objects.get(
                        id=answer_id,
                        question=question
                    )
                    user_answer.selected_answer = selected_answer
                    user_answer.is_correct = selected_answer.is_correct
                    
                    if selected_answer.is_correct:
                        correct_count += 1
                except Answer.DoesNotExist:
                    pass
            
            user_answer.save()
        
        # Обновляем результат
        result.correct_answers = correct_count
        result.percentage = (correct_count / total_questions * 100) if total_questions > 0 else 0
        result.save()
        
        return redirect('test_result', result_id=result.id)
    
    # GET: Показываем форму с вопросами
    # Инициализируем таймер, если установлен
    timer_seconds = None
    if test.timer_minutes:
        timer_seconds = test.timer_minutes * 60
    
    context = {
        'test': test,
        'questions': questions,
        'participant': participant,
        'timer_seconds': timer_seconds,
    }
    
    return render(request, 'test_pr/take_test.html', context)


@require_http_methods(["POST"])
def save_answer(request, test_id):
    """
    AJAX endpoint для сохранения ответа пользователя.
    """
    try:
        data = json.loads(request.body)
        question_id = data.get('question_id')
        answer_id = data.get('answer_id')
        
        question = Question.objects.get(id=question_id)
        
        # Валидируем, что ответ принадлежит этому вопросу
        if answer_id:
            Answer.objects.get(id=answer_id, question=question)
        
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["GET"])
def test_result(request, result_id):
    """
    Отображение результатов прохождения теста.
    """
    participant_id = request.session.get('participant_id')
    if not participant_id:
        return redirect('register')
    
    try:
        participant = Participant.objects.get(id=participant_id)
        result = TestResult.objects.get(id=result_id, participant=participant)
    except (Participant.DoesNotExist, TestResult.DoesNotExist):
        return redirect('test_list')
    
    user_answers = result.user_answers.select_related(
        'question',
        'selected_answer'
    ).order_by('question__order')
    
    context = {
        'result': result,
        'user_answers': user_answers,
        'test': result.test,
        'participant': participant,
    }
    
    return render(request, 'test_pr/test_result.html', context)


@require_http_methods(["GET"])
def logout_user(request):
    """
    Выход пользователя (очистка сессии).
    """
    request.session.flush()
    return redirect('register')


# ============================================================================
# API ENDPOINTS
# ============================================================================

@require_http_methods(["GET"])
def get_test_timer(request, test_id):
    """
    API: Получить информацию о таймере теста.
    """
    try:
        test = Test.objects.get(id=test_id, status='active')
        return JsonResponse({
            'success': True,
            'timer_minutes': test.timer_minutes,
            'timer_seconds': (test.timer_minutes * 60) if test.timer_minutes else None,
        })
    except Test.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Тест не найден'})


# ============================================================================
# АДМИНСКИЕ VIEWS
# ============================================================================

@staff_member_required
@require_http_methods(["GET"])
def admin_test_builder(request):
    """
    Админская страница: Список всех тестов с возможностью создания/редактирования
    """
    tests = Test.objects.all().order_by('-created_at')
    return render(request, 'test_pr/admin/test_builder.html', {
        'tests': tests
    })


@staff_member_required
@require_http_methods(["GET", "POST"])
def admin_create_test(request):
    """
    Админская страница: Создание нового теста с вопросами и ответами
    """
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Создаём тест
                test_form = TestForm(request.POST)
                if not test_form.is_valid():
                    return JsonResponse({
                        'success': False,
                        'errors': test_form.errors
                    })
                
                test = test_form.save()
                
                # Обрабатываем вопросы из JSON
                questions_data = json.loads(request.POST.get('questions_data', '[]'))
                
                if not questions_data:
                    return JsonResponse({
                        'success': False,
                        'error': 'Добавьте хотя бы один вопрос'
                    })
                
                for q_index, q_data in enumerate(questions_data):
                    question_text = q_data.get('text', '').strip()
                    
                    if not question_text:
                        return JsonResponse({
                            'success': False,
                            'error': f'Текст вопроса #{q_index + 1} пуст'
                        })
                    
                    question = Question.objects.create(
                        test=test,
                        text=question_text,
                        order=q_data.get('order', q_index)
                    )
                    
                    # Создаём ответы для вопроса
                    answers = q_data.get('answers', [])
                    
                    if len(answers) < 2:
                        return JsonResponse({
                            'success': False,
                            'error': f'Вопрос #{q_index + 1} должен иметь минимум 2 варианта ответа'
                        })
                    
                    has_correct = False
                    for a_index, a_data in enumerate(answers):
                        answer_text = a_data.get('text', '').strip()
                        
                        if not answer_text:
                            return JsonResponse({
                                'success': False,
                                'error': f'Текст ответа в вопросе #{q_index + 1} пуст'
                            })
                        
                        is_correct = a_data.get('is_correct', False)
                        if is_correct:
                            has_correct = True
                        
                        Answer.objects.create(
                            question=question,
                            text=answer_text,
                            is_correct=is_correct,
                            order=a_data.get('order', a_index)
                        )
                    
                    if not has_correct:
                        return JsonResponse({
                            'success': False,
                            'error': f'Вопрос #{q_index + 1} должен иметь хотя бы один правильный ответ'
                        })
                
                return JsonResponse({
                    'success': True,
                    'test_id': test.id,
                    'redirect_url': f'/admin-builder/{test.id}/edit/'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    # GET запрос - показываем форму
    form = TestForm()
    return render(request, 'test_pr/admin/create_test.html', {
        'form': form
    })


@staff_member_required
@require_http_methods(["GET", "POST"])
def admin_edit_test(request, test_id):
    """
    Админская страница: Редактирование существующего теста
    """
    test = get_object_or_404(Test, id=test_id)
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Обновляем тест
                test_form = TestForm(request.POST, instance=test)
                if not test_form.is_valid():
                    return JsonResponse({
                        'success': False,
                        'errors': test_form.errors
                    })
                
                test = test_form.save()
                
                # Удаляем старые вопросы
                test.questions.all().delete()
                
                # Создаём новые вопросы из JSON
                questions_data = json.loads(request.POST.get('questions_data', '[]'))
                
                if not questions_data:
                    return JsonResponse({
                        'success': False,
                        'error': 'Добавьте хотя бы один вопрос'
                    })
                
                for q_index, q_data in enumerate(questions_data):
                    question_text = q_data.get('text', '').strip()
                    
                    if not question_text:
                        return JsonResponse({
                            'success': False,
                            'error': f'Текст вопроса #{q_index + 1} пуст'
                        })
                    
                    question = Question.objects.create(
                        test=test,
                        text=question_text,
                        order=q_data.get('order', q_index)
                    )
                    
                    # Создаём ответы для вопроса
                    answers = q_data.get('answers', [])
                    
                    if len(answers) < 2:
                        return JsonResponse({
                            'success': False,
                            'error': f'Вопрос #{q_index + 1} должен иметь минимум 2 варианта ответа'
                        })
                    
                    has_correct = False
                    for a_index, a_data in enumerate(answers):
                        answer_text = a_data.get('text', '').strip()
                        
                        if not answer_text:
                            return JsonResponse({
                                'success': False,
                                'error': f'Текст ответа в вопросе #{q_index + 1} пуст'
                            })
                        
                        is_correct = a_data.get('is_correct', False)
                        if is_correct:
                            has_correct = True
                        
                        Answer.objects.create(
                            question=question,
                            text=answer_text,
                            is_correct=is_correct,
                            order=a_data.get('order', a_index)
                        )
                    
                    if not has_correct:
                        return JsonResponse({
                            'success': False,
                            'error': f'Вопрос #{q_index + 1} должен иметь хотя бы один правильный ответ'
                        })
                
                return JsonResponse({
                    'success': True,
                    'message': 'Тест успешно обновлён'
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            })
    
    # GET запрос - показываем форму с данными
    form = TestForm(instance=test)
    questions = test.questions.prefetch_related('answers').order_by('order')
    
    # Подготавливаем данные вопросов для JavaScript
    questions_data = []
    for question in questions:
        questions_data.append({
            'text': question.text,
            'order': question.order,
            'answers': [
                {
                    'text': answer.text,
                    'is_correct': answer.is_correct,
                    'order': answer.order
                }
                for answer in question.answers.all()
            ]
        })
    
    return render(request, 'test_pr/admin/edit_test.html', {
        'form': form,
        'test': test,
        'questions': json.dumps(questions_data)
    })


@staff_member_required
@require_http_methods(["POST"])
def admin_delete_test(request, test_id):
    """
    API: Удаление теста
    """
    try:
        test = get_object_or_404(Test, id=test_id)
        test_title = test.title
        test.delete()
        
        return JsonResponse({
            'success': True,
            'message': f'Тест "{test_title}" успешно удалён'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })


@staff_member_required
@require_http_methods(["POST"])
def admin_duplicate_test(request, test_id):
    """
    API: Дублирование теста
    """
    try:
        with transaction.atomic():
            test = get_object_or_404(Test, id=test_id)
            questions = test.questions.all()
            
            # Дублируем тест
            test.pk = None
            test.title = f"{test.title} (копия)"
            test.status = 'draft'
            test.save()
            
            # Дублируем вопросы и ответы
            for question in questions:
                answers = question.answers.all()
                question.pk = None
                question.test = test
                question.save()
                
                for answer in answers:
                    answer.pk = None
                    answer.question = question
                    answer.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Тест успешно дублирован',
            'new_test_id': test.id
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })

