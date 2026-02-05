from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator
import os
from django.contrib.auth.models import User

def user_avatar_path(instance, filename):

    return f'avatars/user_{instance.user.id}/{filename}'

class Student(models.Model):
    ROLE_CHOICES = [
        ('STUDENT', 'Студент'),
        ('TEACHER', 'Преподаватель'),
        ('ADMIN', 'Администратор'),
    ]
    
    FACULTY_CHOICES = [
        ('CS', 'Кибербезопасность'),
        ('SE', 'Программная инженерия'),
        ('IT', 'Информационные технологии'),
        ('DS', 'Наука о данных'),
        ('WEB', 'Веб-технологии'),
    ]
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        verbose_name='Пользователь',
        null=True,
        blank=True
    )
    first_name = models.CharField(
        max_length=100,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=100,
        verbose_name='Фамилия'
    )
    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта'
    )
    birth_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Дата рождения'
    )
    faculty = models.CharField(
        max_length=3,
        choices=FACULTY_CHOICES,
        default='CS',
        verbose_name='Факультет'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Телефон'
    )
    avatar = models.ImageField(
        upload_to=user_avatar_path,
        blank=True,
        null=True,
        verbose_name='Аватар'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='О себе'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='STUDENT',
        verbose_name='Роль'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    class Meta:
        verbose_name = 'Профиль студента'
        verbose_name_plural = 'Профили студентов'
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"
    
    def save(self, *args, **kwargs):

        if self.user:
            self.first_name = self.user.first_name
            self.last_name = self.user.last_name
            self.email = self.user.email
        super().save(*args, **kwargs)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class Instructor(models.Model):
    first_name = models.CharField(max_length=100, verbose_name='Имя')
    last_name = models.CharField(max_length=100, verbose_name='Фамилия')
    email = models.EmailField(unique=True, verbose_name='Электронная почта')
    specialization = models.CharField(max_length=200, verbose_name='Специализация')
    degree = models.CharField(max_length=100, blank=True, verbose_name='Ученая степень')
    
    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'
    
    def __str__(self):
        return f"{self.last_name} {self.first_name}"

class Course(models.Model):
    LEVEL_CHOICES = [
        ('BEGINNER', 'Начальный'),
        ('INTERMEDIATE', 'Средний'),
        ('ADVANCED', 'Продвинутый'),
    ]
    
    title = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название курса'
    )
    slug = models.SlugField(unique=True, verbose_name='URL-адрес')
    description = models.TextField(verbose_name='Описание')
    duration = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Продолжительность (часов)'
    )
    instructor = models.ForeignKey(
        'Instructor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Преподаватель'
    )
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    level = models.CharField(
        max_length=12,
        choices=LEVEL_CHOICES,
        default='BEGINNER',
        verbose_name='Уровень сложности'
    )
    max_students = models.PositiveIntegerField(default=30, verbose_name='Максимум студентов')
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Стоимость'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['title']
    
    def __str__(self):
        return self.title

class Enrollment(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Активен'),
        ('COMPLETED', 'Завершен'),
    ]
    
    student = models.ForeignKey(
        'Student',
        on_delete=models.CASCADE,
        verbose_name='Студент'
    )
    course = models.ForeignKey(
        'Course',
        on_delete=models.CASCADE,
        verbose_name='Курс'
    )
    enrolled_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата записи'
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='ACTIVE',
        verbose_name='Статус'
    )
    
    class Meta:
        verbose_name = 'Запись на курс'
        verbose_name_plural = 'Записи на курсы'
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']
    
    def __str__(self):
        return f"{self.student} - {self.course}"
