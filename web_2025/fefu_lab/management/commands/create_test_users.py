from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from fefu_lab.models import Student, Instructor, Course, Enrollment
from datetime import date

class Command(BaseCommand):
    help = 'Создает тестовых пользователей с разными ролями'

    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых пользователей...')

        # Создаем пользователей
        users_data = [
            {
                'username': 'admin',
                'email': 'admin@fefu.ru',
                'password': 'admin123',
                'first_name': 'Андрей',
                'last_name': 'Администраторов',
                'role': 'ADMIN'
            },
            {
                'username': 'teacher1',
                'email': 'teacher1@fefu.ru', 
                'password': 'teacher123',
                'first_name': 'Иван',
                'last_name': 'Петров',
                'role': 'TEACHER'
            },
            {
                'username': 'teacher2',
                'email': 'teacher2@fefu.ru',
                'password': 'teacher123', 
                'first_name': 'Мария',
                'last_name': 'Сидорова',
                'role': 'TEACHER'
            },
            {
                'username': 'student1',
                'email': 'student1@fefu.ru',
                'password': 'student123',
                'first_name': 'Анна',
                'last_name': 'Иванова',
                'role': 'STUDENT'
            },
            {
                'username': 'student2', 
                'email': 'student2@fefu.ru',
                'password': 'student123',
                'first_name': 'Дмитрий',
                'last_name': 'Смирнов',
                'role': 'STUDENT'
            }
        ]

        for user_data in users_data:
            # Создаем пользователя Django
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name']
                }
            )
            
            if created:
                user.set_password(user_data['password'])
                user.save()
                self.stdout.write(f"Создан пользователь: {user.username}")
            
            # Создаем профиль студента
            student_profile, created = Student.objects.get_or_create(
                user=user,
                defaults={
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'], 
                    'email': user_data['email'],
                    'role': user_data['role'],
                    'faculty': 'CS'
                }
            )
            
            if created:
                self.stdout.write(f"Создан профиль: {student_profile.full_name} ({student_profile.role})")

        # Делаем админа staff для доступа к админке Django
        admin_user = User.objects.get(username='admin')
        admin_user.is_staff = True
        admin_user.is_superuser = True
        admin_user.save()
        
        self.stdout.write(
            self.style.SUCCESS('Тестовые пользователи успешно созданы!')
        )
        self.stdout.write('Логины и пароли:')
        self.stdout.write('- admin / admin123 (администратор)')
        self.stdout.write('- teacher1 / teacher123 (преподаватель)') 
        self.stdout.write('- student1 / student123 (студент)')
