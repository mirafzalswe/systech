from django.urls import path
from . import views

urlpatterns = [
    # Основные страницы пользователя
    path('', views.register, name='register'),
    path('tests/', views.test_list, name='test_list'),
    path('test/<int:test_id>/take/', views.take_test, name='take_test'),
    path('test/<int:test_id>/save-answer/', views.save_answer, name='save_answer'),
    path('result/<int:result_id>/', views.test_result, name='test_result'),
    path('logout/', views.logout_user, name='logout'),
    
    # API endpoints
    path('api/test/<int:test_id>/timer/', views.get_test_timer, name='get_test_timer'),
    
    # Админские страницы
    path('admin-builder/', views.admin_test_builder, name='admin_test_builder'),
    path('admin-builder/create/', views.admin_create_test, name='admin_create_test'),
    path('admin-builder/<int:test_id>/edit/', views.admin_edit_test, name='admin_edit_test'),
    path('admin-builder/<int:test_id>/delete/', views.admin_delete_test, name='admin_delete_test'),
    path('admin-builder/<int:test_id>/duplicate/', views.admin_duplicate_test, name='admin_duplicate_test'),
]
