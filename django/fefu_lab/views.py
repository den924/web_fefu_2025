from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db import IntegrityError
from .models import Student, Course, Enrollment, Instructor
from .forms import StudentForm, EnrollmentForm, UserRegisterForm, UserLoginForm, UserUpdateForm, StudentProfileForm

# Декораторы для проверки ролей
def is_student(user):
    return hasattr(user, 'student_profile') and user.student_profile.role == 'STUDENT'

def is_teacher(user):
    return hasattr(user, 'student_profile') and user.student_profile.role == 'TEACHER'

def is_admin(user):
    return hasattr(user, 'student_profile') and user.student_profile.role == 'ADMIN'

# Представления аутентификации
def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            try:
                user = form.save()
                
                # Создаем профиль студента
                student = Student.objects.create(
                    user=user,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    email=user.email,
                    role='STUDENT'
                )
                
                # Автоматический вход после регистрации
                login(request, user)
                messages.success(request, 'Регистрация прошла успешно!')
                return redirect('profile')
            except IntegrityError as e:
                messages.error(request, f'Ошибка при создании профиля: {e}')
    else:
        form = UserRegisterForm()
    
    return render(request, 'fefu_lab/registration/register.html', {
        'form': form,
        'title': 'Регистрация'
    })

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {user.first_name}!')
                next_url = request.GET.get('next', 'profile')
                return redirect(next_url)
            else:
                messages.error(request, 'Неверный email или пароль')
    else:
        form = UserLoginForm()
    
    return render(request, 'fefu_lab/registration/login.html', {
        'form': form,
        'title': 'Вход в систему'
    })

def logout_view(request):
    logout(request)
    messages.info(request, 'Вы успешно вышли из системы')
    return redirect('home')

@login_required
def profile_view(request):
    # Получаем или создаем профиль студента
    student_profile, created = Student.objects.get_or_create(
        user=request.user,
        defaults={
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'role': 'STUDENT'
        }
    )
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = StudentProfileForm(request.POST, request.FILES, instance=student_profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = StudentProfileForm(instance=student_profile)
    
    return render(request, 'fefu_lab/registration/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form,
        'title': 'Мой профиль'
    })

# Личные кабинеты
@login_required
def student_dashboard(request):
    if not is_student(request.user):
        messages.error(request, 'Доступ запрещен')
        return redirect('home')
    
    student_profile = request.user.student_profile
    enrollments = Enrollment.objects.filter(student=student_profile).select_related('course')
    
    return render(request, 'fefu_lab/dashboard/student_dashboard.html', {
        'student': student_profile,
        'enrollments': enrollments,
        'title': 'Личный кабинет студента'
    })

@login_required
@user_passes_test(is_teacher)
def teacher_dashboard(request):
    teacher_profile = request.user.student_profile
    courses = Course.objects.filter(instructor__email=request.user.email)
    
    return render(request, 'fefu_lab/dashboard/teacher_dashboard.html', {
        'teacher': teacher_profile,
        'courses': courses,
        'title': 'Личный кабинет преподавателя'
    })

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    return render(request, 'fefu_lab/dashboard/admin_dashboard.html', {
        'title': 'Панель администратора'
    })

# Обновляем существующие представления с проверкой доступа
@login_required
def enrollment_view(request):
    if not is_student(request.user):
        messages.error(request, 'Только студенты могут записываться на курсы')
        return redirect('home')
    
    if request.method == 'POST':
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            try:
                enrollment = form.save(commit=False)
                enrollment.student = request.user.student_profile
                enrollment.status = 'ACTIVE'
                enrollment.save()
                messages.success(request, 'Вы успешно записались на курс!')
                return redirect('student_dashboard')
            except IntegrityError:
                form.add_error(None, 'Вы уже записаны на этот курс')
    else:
        form = EnrollmentForm()
    
    return render(request, 'fefu_lab/enrollment.html', {
        'form': form,
        'title': 'Запись на курс'
    })

# Существующие представления остаются
def home_page(request):
    total_students = Student.objects.count()
    total_courses = Course.objects.filter(is_active=True).count()
    total_instructors = Instructor.objects.count()
    recent_courses = Course.objects.filter(is_active=True).order_by('-created_at')[:3]
    
    return render(request, 'fefu_lab/home.html', {
        'title': 'Главная страница',
        'total_students': total_students,
        'total_courses': total_courses,
        'total_instructors': total_instructors,
        'recent_courses': recent_courses
    })

def student_list(request):
    students = Student.objects.all().order_by('last_name', 'first_name')
    return render(request, 'fefu_lab/student_list.html', {
        'students': students,
        'title': 'Список студентов'
    })

def student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    enrollments = Enrollment.objects.filter(student=student).select_related('course')
    
    # Проверяем, может ли пользователь просматривать профиль
    can_edit = request.user.is_authenticated and (
        request.user == student.user or 
        (hasattr(request.user, 'student_profile') and 
         request.user.student_profile.role in ['TEACHER', 'ADMIN'])
    )
    
    return render(request, 'fefu_lab/student_detail.html', {
        'student': student,
        'enrollments': enrollments,
        'can_edit': can_edit,
        'title': f'Студент: {student.full_name}'
    })

def course_list(request):
    courses = Course.objects.filter(is_active=True).select_related('instructor')
    return render(request, 'fefu_lab/course_list.html', {
        'courses': courses,
        'title': 'Список курсов'
    })

def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, is_active=True)
    enrollments = Enrollment.objects.filter(course=course, status='ACTIVE').select_related('student')
    
    return render(request, 'fefu_lab/course_detail.html', {
        'course': course,
        'enrollments': enrollments,
        'title': f'Курс: {course.title}'
    })

def enrollment_success(request):
    return render(request, 'fefu_lab/enrollment_success.html', {
        'title': 'Запись успешно создана'
    })

def feedback_view(request):
    return render(request, 'fefu_lab/feedback.html', {
        'title': 'Обратная связь'
    })
