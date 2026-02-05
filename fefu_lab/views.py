from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404, HttpResponse
from django.views.generic import TemplateView, ListView, DetailView
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from .models import Student, Course, Enrollment, Instructor, Skill
from .forms import (
    UserRegisterForm, StudentProfileForm, UserUpdateForm, 
    StudentForm, CourseForm, EnrollmentForm, SearchStudentForm,
    LoginForm, FeedbackForm
)

# Декораторы для проверки ролей
def student_required(function=None):
    """Декоратор для проверки, что пользователь - студент"""
    actual_decorator = user_passes_test(
        lambda u: hasattr(u, 'student_profile') and u.student_profile.is_student(),
        login_url='/login/',
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def teacher_required(function=None):
    """Декоратор для проверки, что пользователь - преподаватель"""
    actual_decorator = user_passes_test(
        lambda u: hasattr(u, 'student_profile') and u.student_profile.is_teacher(),
        login_url='/login/',
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def admin_required(function=None):
    """Декоратор для проверки, что пользователь - администратор"""
    actual_decorator = user_passes_test(
        lambda u: u.is_staff or (hasattr(u, 'student_profile') and u.student_profile.is_admin()),
        login_url='/login/',
        redirect_field_name=None
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

# Аутентификация и регистрация
def register_view(request):
    """Регистрация нового пользователя"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Создаем профиль студента
            student = Student.objects.create(
                user=user,
                first_name=user.first_name,
                last_name=user.last_name,
                email=user.email,
                role='STUDENT'  # По умолчанию студент
            )
            
            # Автоматически логиним пользователя
            login(request, user)
            messages.success(request, f'Аккаунт создан для {user.username}!')
            return redirect('profile')
    else:
        form = UserRegisterForm()
    
    return render(request, 'fefu_lab/registration/register.html', {
        'title': 'Регистрация',
        'form': form
    })

def login_view(request):
    """Вход в систему"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.get_full_name() or user.username}!')
                
                # Редирект на следующую страницу или профиль
                next_page = request.GET.get('next', 'profile')
                return redirect(next_page)
            else:
                messages.error(request, 'Неверный email или пароль')
    else:
        form = LoginForm()
    
    return render(request, 'fefu_lab/registration/login.html', {
        'title': 'Вход в систему',
        'form': form
    })

def logout_view(request):
    """Выход из системы"""
    logout(request)
    messages.success(request, 'Вы успешно вышли из системы')
    return redirect('home')

@login_required
def profile_view(request):
    """Личный кабинет пользователя"""
    student_profile = None
    instructor_profile = None
    
    try:
        student_profile = request.user.student_profile
    except Student.DoesNotExist:
        pass
    
    try:
        instructor_profile = request.user.instructor_profile
    except Instructor.DoesNotExist:
        pass
    
    # Определяем тип пользователя
    is_student = student_profile is not None
    is_teacher = instructor_profile is not None or (student_profile and student_profile.is_teacher())
    is_admin = request.user.is_staff or (student_profile and student_profile.is_admin())
    
    return render(request, 'fefu_lab/registration/profile.html', {
        'title': 'Личный кабинет',
        'user': request.user,
        'student_profile': student_profile,
        'instructor_profile': instructor_profile,
        'is_student': is_student,
        'is_teacher': is_teacher,
        'is_admin': is_admin,
    })

@login_required
def profile_edit_view(request):
    """Редактирование профиля"""
    student_profile = None
    
    try:
        student_profile = request.user.student_profile
    except Student.DoesNotExist:
        pass
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        student_form = StudentProfileForm(request.POST, request.FILES, instance=student_profile)
        
        if user_form.is_valid() and (student_profile is None or student_form.is_valid()):
            user_form.save()
            if student_profile:
                student_form.save()
                # Обновляем данные в модели Student
                student_profile.first_name = request.user.first_name
                student_profile.last_name = request.user.last_name
                student_profile.email = request.user.email
                student_profile.save()
            
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        student_form = StudentProfileForm(instance=student_profile)
    
    return render(request, 'fefu_lab/registration/profile_edit.html', {
        'title': 'Редактирование профиля',
        'user_form': user_form,
        'student_form': student_form,
        'student_profile': student_profile,
    })

# Личные кабинеты
@login_required
@student_required
def student_dashboard(request):
    """Личный кабинет студента"""
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        messages.error(request, 'Профиль студента не найден')
        return redirect('home')
    
    # Получаем активные записи на курсы
    enrollments = Enrollment.objects.filter(
        student=student,
        status='ACTIVE'
    ).select_related('course')
    
    # Получаем завершенные курсы
    completed_enrollments = Enrollment.objects.filter(
        student=student,
        status='COMPLETED'
    ).select_related('course')
    
    return render(request, 'fefu_lab/dashboard/student_dashboard.html', {
        'title': 'Личный кабинет студента',
        'student': student,
        'enrollments': enrollments,
        'completed_enrollments': completed_enrollments,
    })

@login_required
@teacher_required
def teacher_dashboard(request):
    """Личный кабинет преподавателя"""
    # Ищем курсы, где пользователь является преподавателем
    courses = Course.objects.filter(
        instructor__user=request.user
    ).prefetch_related('enrollments')
    
    # Получаем общую статистику
    total_students = Enrollment.objects.filter(
        course__instructor__user=request.user,
        status='ACTIVE'
    ).count()
    
    return render(request, 'fefu_lab/dashboard/teacher_dashboard.html', {
        'title': 'Личный кабинет преподавателя',
        'courses': courses,
        'total_students': total_students,
    })

@login_required
@admin_required
def admin_dashboard(request):
    """Панель администратора"""
    # Статистика для админа
    stats = {
        'total_students': Student.objects.filter(is_active=True).count(),
        'total_courses': Course.objects.filter(is_active=True).count(),
        'total_instructors': Instructor.objects.filter(is_active=True).count(),
        'total_enrollments': Enrollment.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
    }
    
    return render(request, 'fefu_lab/dashboard/admin_dashboard.html', {
        'title': 'Панель администратора',
        'stats': stats,
    })

# Обновляем существующие функции для работы с аутентификацией
def home_page(request):
    """Главная страница с поиском студентов"""
    total_students = Student.objects.filter(is_active=True).count()
    total_courses = Course.objects.filter(is_active=True).count()
    total_instructors = Instructor.objects.filter(is_active=True).count()
    recent_courses = Course.objects.filter(is_active=True).order_by('-created_at')[:3]
    
    # Поиск студентов
    search_results = None
    search_query = ''
    
    if 'query' in request.GET:
        form = SearchStudentForm(request.GET)
        if form.is_valid():
            search_query = form.cleaned_data['query']
            search_results = search_student_by_name(search_query)
    else:
        form = SearchStudentForm()
    
    context = {
        'total_students': total_students,
        'total_courses': total_courses,
        'total_instructors': total_instructors,
        'recent_courses': recent_courses,
        'all_students': Student.objects.filter(is_active=True).order_by('last_name')[:10],
        'search_form': form,
        'search_query': search_query,
        'search_results': search_results,
    }
    
    return render(request, 'fefu_lab/home.html', context)

def search_student_by_name(query):
    """Поиск студента по имени"""
    query_lower = query.lower().strip()
    
    try:
        # Ищем точное совпадение по полному имени
        student = Student.objects.get(
            Q(full_name__iexact=query_lower) |
            Q(first_name__iexact=query_lower) |
            Q(last_name__iexact=query_lower)
        )
        return {
            'success': True,
            'student': student,
            'message': f'Найден студент: {student.full_name}'
        }
    except Student.DoesNotExist:
        # Ищем частичное совпадение
        students = Student.objects.filter(
            Q(first_name__icontains=query_lower) |
            Q(last_name__icontains=query_lower) |
            Q(email__icontains=query_lower)
        )
        
        if students.exists():
            return {
                'success': True,
                'student': students.first(),
                'message': f'Найдено {students.count()} студентов'
            }
        else:
            return {
                'success': False,
                'student': None,
                'message': f'Студент "{query}" не найден'
            }

def about_page(request):
    """Страница 'О нас'"""
    return render(request, 'fefu_lab/about.html')

def student_profile(request, student_id):
    """Профиль студента из БД"""
    student = get_object_or_404(Student, pk=student_id, is_active=True)
    
    # Получаем курсы студента
    enrollments = Enrollment.objects.filter(student=student, status='ACTIVE')
    
    # Получаем навыки студента
    skills = Skill.objects.filter(student=student)
    
    context = {
        'student': student,
        'enrollments': enrollments,
        'skills': skills,
        'other_students': Student.objects.filter(is_active=True).exclude(pk=student_id).order_by('?')[:3],
    }
    return render(request, 'fefu_lab/student_profile.html', context)

def student_list(request):
    """Список всех студентов"""
    students = Student.objects.filter(is_active=True).order_by('last_name', 'first_name')
    
    # Фильтрация по факультету
    faculty = request.GET.get('faculty')
    if faculty:
        students = students.filter(faculty=faculty)
    
    context = {
        'students': students,
        'faculty_filter': faculty,
        'total_students': students.count(),
    }
    return render(request, 'fefu_lab/student_list.html', context)

def course_list(request):
    """Список всех курсов"""
    courses = Course.objects.filter(is_active=True).order_by('title')
    
    # Фильтрация по уровню
    level = request.GET.get('level')
    if level:
        courses = courses.filter(level=level)
    
    context = {
        'courses': courses,
        'level_filter': level,
        'total_courses': courses.count(),
    }
    return render(request, 'fefu_lab/course_list.html', context)

def enrollment_create(request):
    """Запись студента на курс"""
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save()
            messages.success(request, f'Студент {enrollment.student} успешно записан на курс {enrollment.course}!')
            return redirect('student_profile', student_id=enrollment.student.pk)
    else:
        form = EnrollmentForm()
    
    context = {
        'form': form,
        'students': Student.objects.filter(is_active=True),
        'courses': Course.objects.filter(is_active=True),
    }
    return render(request, 'fefu_lab/enrollment.html', context)

# Class-Based Views
class CourseDetailView(DetailView):
    """Детальная страница курса"""
    model = Course
    template_name = 'fefu_lab/course_detail.html'
    context_object_name = 'course'
    slug_field = 'slug'
    slug_url_kwarg = 'course_slug'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course = self.get_object()
        
        # Получаем студентов, записанных на курс
        enrollments = Enrollment.objects.filter(course=course, status='ACTIVE')
        
        context['enrollments'] = enrollments
        context['available_spots'] = course.available_spots()
        context['other_courses'] = Course.objects.filter(is_active=True).exclude(pk=course.pk).order_by('?')[:3]
        
        return context
def feedback_page(request):
    """Страница обратной связи"""
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # Здесь можно сохранить в БД или отправить email
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            message = form.cleaned_data['message']
            
            # Просто показываем сообщение об успехе
            messages.success(request, f'Спасибо, {name}! Ваше сообщение отправлено.')
            return redirect('success')
    else:
        form = FeedbackForm()
    
    return render(request, 'fefu_lab/feedback.html', {
        'title': 'Обратная связь',
        'form': form
    })


def login_page(request):
    """Страница входа в систему"""
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            # Простая имитация авторизации
            # В реальном приложении здесь была бы проверка пароля
            try:
                student = Student.objects.get(email=email)
                messages.success(request, f'Добро пожаловать, {student.full_name}!')
                return redirect('student_profile', student_id=student.id)
            except Student.DoesNotExist:
                messages.error(request, 'Пользователь с таким email не найден')
    else:
        form = LoginForm()
    
    return render(request, 'fefu_lab/login.html', {
        'title': 'Вход в систему',
        'form': form
    })

def success_page(request):
    """Страница успешного выполнения операции"""
    return render(request, 'fefu_lab/success.html', {
        'title': 'Успешно'
    })

# Обработчик 404 ошибки
def custom_404(request, exception):
    """Кастомная страница 404"""
    return render(request, 'fefu_lab/404.html', status=404)
