from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Основные маршруты
    path('', views.home_page, name='home'),
    path('students/', views.student_list, name='student_list'),
    path('students/<int:pk>/', views.student_detail, name='student_detail'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/', views.course_list, name='courses'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    
    # Аутентификация
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
    
    # Личные кабинеты
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    
    # Функциональность
    path('enrollment/', views.enrollment_view, name='enrollment'),
    path('enrollment/success/', views.enrollment_success, name='enrollment_success'),
    path('feedback/', views.feedback_view, name='feedback'),
]
# Добавляем обработку медиа файлов в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
