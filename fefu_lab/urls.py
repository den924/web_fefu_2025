from django.urls import path
from . import views

urlpatterns = [
    # Статические маршруты
    path('', views.home_page, name='home'),
    path('about/', views.about_page, name='about'),
    path('search/', views.search_student, name='search_student'),
    
    # Динамические маршруты
    path('student/<int:student_id>/', views.student_profile, name='student_profile'),
    path('course/<slug:course_slug>/', views.CourseDetailView.as_view(), name='course_detail'),
]
