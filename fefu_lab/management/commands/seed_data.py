from django.core.management.base import BaseCommand
from django.utils import timezone
from fefu_lab.models import Student, Instructor, Course, Enrollment, Skill
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Заполняет базу данных тестовыми данными'
    
    def handle(self, *args, **options):
        self.stdout.write('Создание тестовых данных...')
        
        # Очистка существующих данных
        Enrollment.objects.all().delete()
        Course.objects.all().delete()
        Student.objects.all().delete()
        Instructor.objects.all().delete()
        Skill.objects.all().delete()
        
        # Создание преподавателей
        instructors = [
            Instructor(
                first_name='Иван',
                last_name='Петров',
                email='i.petrov@fefu.ru',
                specialization='Кибербезопасность',
                degree='Кандидат технических наук',
                bio='Эксперт в области кибербезопасности с 10-летним опытом.'
            ),
            Instructor(
                first_name='Мария',
                last_name='Сидорова',
                email='m.sidorova@fefu.ru',
                specialization='Веб-разработка',
                degree='Доктор технических наук',
                bio='Специалист по современным веб-технологиям и фреймворкам.'
            ),
            Instructor(
                first_name='Алексей',
                last_name='Козлов',
                email='a.kozlov@fefu.ru',
                specialization='Сетевые технологии',
                bio='Инженер сетевой безопасности с практическим опытом.'
            ),
        ]
        
        for instructor in instructors:
            instructor.save()
        
        self.stdout.write(f'Создано {len(instructors)} преподавателей')
        
        # Создание студентов
        students = [
            Student(
                first_name='Анна',
                last_name='Иванова',
                email='anna.ivanova@fefu.ru',
                birth_date=date(2000, 5, 15),
                faculty='CS',
                year=3,
                gpa=4.7
            ),
            Student(
                first_name='Дмитрий',
                last_name='Смирнов',
                email='dmitry.smirnov@fefu.ru',
                birth_date=date(1999, 8, 22),
                faculty='SE',
                year=4,
                gpa=4.2
            ),
            Student(
                first_name='Екатерина',
                last_name='Попова',
                email='ekaterina.popova@fefu.ru',
                birth_date=date(2001, 3, 10),
                faculty='IT',
                year=2,
                gpa=4.9
            ),
            Student(
                first_name='Михаил',
                last_name='Васильев',
                email='mikhail.vasilyev@fefu.ru',
                birth_date=date(2000, 11, 5),
                faculty='DS',
                year=3,
                gpa=4.0
            ),
            Student(
                first_name='Ольга',
                last_name='Новикова',
                email='olga.novikova@fefu.ru',
                birth_date=date(1999, 12, 30),
                faculty='WEB',
                year=5,
                gpa=4.5
            ),
        ]
        
        for student in students:
            student.save()
        
        self.stdout.write(f'Создано {len(students)} студентов')
        
        # Создание навыков для студентов
        skills_data = [
            ('Python', 8),
            ('Django', 7),
            ('JavaScript', 6),
            ('HTML/CSS', 9),
            ('SQL', 7),
            ('Git', 8),
            ('Docker', 5),
            ('React', 6),
            ('Алгоритмы', 8),
            ('Машинное обучение', 4),
        ]
        
        for i, student in enumerate(students):
            for skill_name, level in skills_data[i % len(skills_data):(i+3) % len(skills_data)]:
                Skill.objects.create(
                    name=skill_name,
                    student=student,
                    level=level
                )
        
        self.stdout.write(f'Создано {Skill.objects.count()} навыков')
        
        # Создание курсов
        courses = [
            Course(
                title='Основы Python',
                slug='python-basics',
                description='Базовый курс по программированию на языке Python. Изучение синтаксиса, структур данных и основ ООП.',
                duration=36,
                instructor=instructors[0],
                level='BEGINNER',
                max_students=25,
                price=0
            ),
            Course(
                title='Веб-безопасность',
                slug='web-security',
                description='Продвинутый курс по защите веб-приложений. SQL-инъекции, XSS, CSRF и другие уязвимости.',
                duration=48,
                instructor=instructors[0],
                level='ADVANCED',
                max_students=20,
                price=15000
            ),
            Course(
                title='Современный JavaScript',
                slug='modern-javascript',
                description='Изучение современных возможностей JavaScript: ES6+, асинхронное программирование, фреймворки.',
                duration=42,
                instructor=instructors[1],
                level='INTERMEDIATE',
                max_students=30,
                price=12000
            ),
            Course(
                title='Защита сетей',
                slug='network-defense',
                description='Курс по защите компьютерных сетей. Firewalls, IDS/IPS, VPN и методы атак на сети.',
                duration=40,
                instructor=instructors[2],
                level='ADVANCED',
                max_students=15,
                price=18000
            ),
            Course(
                title='Веб-разработка на Django',
                slug='django-web-dev',
                description='Полный курс по созданию веб-приложений на Django с нуля до deployment.',
                duration=60,
                instructor=instructors[1],
                level='INTERMEDIATE',
                max_students=20,
                price=20000
            ),
        ]
        
        for course in courses:
            course.save()
        
        self.stdout.write(f'Создано {len(courses)} курсов')
        
        # Создание записей на курсы
        enrollments = [
            Enrollment(student=students[0], course=courses[0], status='ACTIVE'),
            Enrollment(student=students[0], course=courses[1], status='ACTIVE'),
            Enrollment(student=students[1], course=courses[0], status='ACTIVE'),
            Enrollment(student=students[1], course=courses[2], status='ACTIVE'),
            Enrollment(student=students[2], course=courses[0], status='ACTIVE'),
            Enrollment(student=students[2], course=courses[4], status='COMPLETED', grade=5.0),
            Enrollment(student=students[3], course=courses[3], status='ACTIVE'),
            Enrollment(student=students[4], course=courses[2], status='ACTIVE'),
            Enrollment(student=students[4], course=courses[4], status='ACTIVE'),
        ]
        
        for enrollment in enrollments:
            enrollment.save()
        
        self.stdout.write(f'Создано {len(enrollments)} записей на курсы')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Успешно создано тестовых данных!\n'
                f'• {len(instructors)} преподавателей\n'
                f'• {len(students)} студентов\n'
                f'• {Skill.objects.count()} навыков\n'
                f'• {len(courses)} курсов\n'
                f'• {len(enrollments)} записей на курсы\n\n'
                f'Для входа в админ-панель используйте:\n'
                f'Логин: admin\n'
                f'Пароль: admin123\n'
                f'URL: http://127.0.0.1:8000/admin/\n'
            )
        )
