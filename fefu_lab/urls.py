# fefu_lab/urls.py
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Основные маршруты
    path('', views.home_page, name='home'),
    path('about/', views.about_page, name='about'),
    path('students/', views.student_list, name='student_list'),
    path('courses/', views.course_list, name='course_list'),
    path('enrollment/', views.enrollment_create, name='enrollment_create'),
    path('student/<int:student_id>/', views.student_profile, name='student_profile'),
    path('course/<slug:course_slug>/', views.CourseDetailView.as_view(), name='course_detail'),
    
    # Формы (лабораторные работы №1-3)
    path('feedback/', views.feedback_page, name='feedback'),
    
    # Аутентификация (лабораторная №4)
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    
    # Личные кабинеты (лабораторная №4)
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # API и поиск
    path('search/', views.home_page, name='search_student'),
]

# Добавляем маршруты для медиа-файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
