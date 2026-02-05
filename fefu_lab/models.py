# fefu_lab/models.py
from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

# Сначала определяем Instructor, так как Course ссылается на него
class Instructor(models.Model):
    """Модель Преподавателя"""
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='instructor_profile',
        null=True,
        blank=True,
        verbose_name='Пользователь'
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
        verbose_name='Email'
    )
    specialization = models.CharField(
        max_length=200,
        verbose_name='Специализация'
    )
    degree = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='Ученая степень'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    
    class Meta:
        verbose_name = 'Преподаватель'
        verbose_name_plural = 'Преподаватели'
        ordering = ['last_name', 'first_name']
        db_table = 'instructors'
    
    def __str__(self):
        if self.user:
            return f"{self.user.get_full_name()}"
        return f"{self.last_name} {self.first_name}"
    
    @property
    def full_name(self):
        if self.user:
            return self.user.get_full_name()
        return f"{self.first_name} {self.last_name}"

# Теперь определяем Course, который ссылается на Instructor
class Course(models.Model):
    """Модель Курса"""
    LEVEL_CHOICES = [
        ('BEGINNER', 'Начальный'),
        ('INTERMEDIATE', 'Средний'),
        ('ADVANCED', 'Продвинутый'),
    ]
    
    title = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='URL-имя'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    duration = models.IntegerField(
        validators=[MinValueValidator(1)],
        verbose_name='Продолжительность (часов)'
    )
    instructor = models.ForeignKey(
        Instructor,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='courses',
        verbose_name='Преподаватель'
    )
    level = models.CharField(
        max_length=12,
        choices=LEVEL_CHOICES,
        default='BEGINNER',
        verbose_name='Уровень сложности'
    )
    max_students = models.IntegerField(
        default=20,
        validators=[MinValueValidator(1)],
        verbose_name='Максимум студентов'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        verbose_name='Стоимость'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['title']
        db_table = 'courses'
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'course_slug': self.slug})
    
    def enrolled_count(self):
        """Количество записанных студентов"""
        return self.enrollments.filter(status='ACTIVE').count()
    
    def available_spots(self):
        """Доступные места"""
        return self.max_students - self.enrolled_count()

# Затем определяем Student
class Student(models.Model):
    """Модель Студента"""
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
    
    # Связь с встроенной моделью User
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='student_profile',
        null=True,
        blank=True,
        verbose_name='Пользователь'
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
        verbose_name='Email'
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
    year = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(6)],
        verbose_name='Курс'
    )
    gpa = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0.00), MaxValueValidator(5.00)],
        verbose_name='Средний балл'
    )
    
    # Новые поля для лабораторной №4
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='STUDENT',
        verbose_name='Роль'
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='Телефон'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='О себе'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name='Аватар'
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    
    class Meta:
        verbose_name = 'Студент'
        verbose_name_plural = 'Студенты'
        ordering = ['last_name', 'first_name']
        db_table = 'students'
    
    def __str__(self):
        if self.user:
            return f"{self.user.get_full_name()}"
        return f"{self.last_name} {self.first_name}"
    
    def get_absolute_url(self):
        return reverse('student_profile', kwargs={'student_id': self.pk})
    
    @property
    def full_name(self):
        if self.user:
            return self.user.get_full_name()
        return f"{self.first_name} {self.last_name}"
    
    def get_faculty_display_name(self):
        return dict(self.FACULTY_CHOICES).get(self.faculty, 'Неизвестно')
    
    def get_role_display_name(self):
        return dict(self.ROLE_CHOICES).get(self.role, 'Неизвестно')
    
    def is_teacher(self):
        return self.role == 'TEACHER'
    
    def is_admin(self):
        return self.role == 'ADMIN'
    
    def is_student(self):
        return self.role == 'STUDENT'
    
    def get_skills(self):
        """Получить навыки студента"""
        return self.skill_set.all()
    
    def get_courses(self):
        """Получить курсы, на которые записан студент"""
        return self.courses.all()

# Определяем Enrollment, который ссылается на Student и Course
class Enrollment(models.Model):
    """Модель Записи на курс"""
    STATUS_CHOICES = [
        ('ACTIVE', 'Активна'),
        ('COMPLETED', 'Завершена'),
        ('CANCELLED', 'Отменена'),
    ]
    
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='enrollments',
        verbose_name='Студент'
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='enrollments',
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
    grade = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0.00), MaxValueValidator(5.00)],
        verbose_name='Оценка'
    )
    
    class Meta:
        verbose_name = 'Запись на курс'
        verbose_name_plural = 'Записи на курсы'
        unique_together = ['student', 'course']
        ordering = ['-enrolled_at']
        db_table = 'enrollments'
    
    def __str__(self):
        return f"{self.student} - {self.course}"

class Skill(models.Model):
    """Модель Навыка студента"""
    name = models.CharField(
        max_length=100,
        verbose_name='Название навыка'
    )
    student = models.ForeignKey(
        Student,
        on_delete=models.CASCADE,
        related_name='skill_set'
    )
    level = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        verbose_name='Уровень (1-10)'
    )
    
    class Meta:
        verbose_name = 'Навык'
        verbose_name_plural = 'Навыки'
        db_table = 'skills'
    
    def __str__(self):
        return f"{self.name} ({self.student})"

# Сигнал для автоматического обновления данных User при сохранении Student
@receiver(post_save, sender=Student)
def update_user_profile(sender, instance, created, **kwargs):
    if instance.user:
        # Синхронизируем основные данные
        if not instance.user.first_name and instance.first_name:
            instance.user.first_name = instance.first_name
        if not instance.user.last_name and instance.last_name:
            instance.user.last_name = instance.last_name
        if not instance.user.email and instance.email:
            instance.user.email = instance.email
        instance.user.save()
