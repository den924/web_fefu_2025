# fefu_lab/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import Student, Course, Enrollment

class UserRegisterForm(UserCreationForm):
    """Форма регистрации пользователя"""
    email = forms.EmailField(
        label='Email',
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': 'example@fefu.ru', 'class': 'form-control'})
    )
    first_name = forms.CharField(
        label='Имя',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Введите имя', 'class': 'form-control'})
    )
    last_name = forms.CharField(
        label='Фамилия',
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={'placeholder': 'Введите фамилию', 'class': 'form-control'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'placeholder': 'Логин', 'class': 'form-control'}),
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Пользователь с таким email уже существует')
        return email

class StudentProfileForm(forms.ModelForm):
    """Форма профиля студента"""
    class Meta:
        model = Student
        fields = ['phone', 'bio', 'avatar', 'faculty', 'year', 'gpa']
        widgets = {
            'phone': forms.TextInput(attrs={'placeholder': '+7 (XXX) XXX-XX-XX', 'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'placeholder': 'Расскажите о себе...', 'rows': 4, 'class': 'form-control'}),
            'faculty': forms.Select(attrs={'class': 'form-select'}),
            'year': forms.NumberInput(attrs={'class': 'form-control'}),
            'gpa': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
        labels = {
            'phone': 'Телефон',
            'bio': 'О себе',
            'avatar': 'Аватар',
            'faculty': 'Факультет',
            'year': 'Курс',
            'gpa': 'Средний балл',
        }

class UserUpdateForm(forms.ModelForm):
    """Форма обновления данных пользователя"""
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
        }

class LoginForm(forms.Form):
    """Форма входа в систему"""
    username = forms.CharField(
        label='Email или логин',
        widget=forms.TextInput(attrs={'placeholder': 'Введите email или логин', 'class': 'form-control'})
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'placeholder': 'Введите пароль', 'class': 'form-control'})
    )

class StudentForm(forms.ModelForm):
    """Форма для создания/редактирования студента"""
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'email', 'birth_date', 'faculty', 'year', 'gpa']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'Введите имя'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Введите фамилию'}),
            'email': forms.EmailInput(attrs={'placeholder': 'example@fefu.ru'}),
        }
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
            'birth_date': 'Дата рождения',
            'faculty': 'Факультет',
            'year': 'Курс',
            'gpa': 'Средний балл',
        }

class CourseForm(forms.ModelForm):
    """Форма для создания/редактирования курса"""
    class Meta:
        model = Course
        fields = ['title', 'slug', 'description', 'duration', 'instructor', 'level', 'max_students', 'price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'title': forms.TextInput(attrs={'placeholder': 'Название курса'}),
            'slug': forms.TextInput(attrs={'placeholder': 'url-имя-курса'}),
        }
        labels = {
            'title': 'Название курса',
            'slug': 'URL-имя',
            'description': 'Описание',
            'duration': 'Продолжительность (часов)',
            'instructor': 'Преподаватель',
            'level': 'Уровень сложности',
            'max_students': 'Максимум студентов',
            'price': 'Стоимость',
        }

class EnrollmentForm(forms.ModelForm):
    """Форма для записи на курс"""
    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'status']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-select'}),
            'course': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'student': 'Студент',
            'course': 'Курс',
            'status': 'Статус записи',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        student = cleaned_data.get('student')
        course = cleaned_data.get('course')
        
        # Проверка, не записан ли уже студент на этот курс
        if student and course:
            existing = Enrollment.objects.filter(student=student, course=course).exists()
            if existing:
                raise ValidationError(f'Студент {student} уже записан на курс {course}')
            
            # Проверка доступных мест
            if course.enrolled_count() >= course.max_students:
                raise ValidationError(f'На курсе {course} нет свободных мест')
        
        return cleaned_data

class SearchStudentForm(forms.Form):
    """Форма поиска студента"""
    query = forms.CharField(
        max_length=100,
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Введите имя или фамилию студента',
            'class': 'search-input'
        })
    )
class FeedbackForm(forms.Form):
    """Форма обратной связи"""
    name = forms.CharField(
        max_length=100,
        label='Ваше имя',
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Введите ваше имя',
            'required': 'required'
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Введите ваш email',
            'required': 'required'
        })
    )
    message = forms.CharField(
        label='Сообщение',
        widget=forms.Textarea(attrs={
            'class': 'form-control', 
            'rows': 5, 
            'placeholder': 'Введите ваше сообщение',
            'required': 'required'
        })
    )
