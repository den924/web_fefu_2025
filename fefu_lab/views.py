from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.views.generic import TemplateView

# База данных студентов
STUDENTS_DATA = {
    1: {
        'id': 1,
        'name': 'Иван Иванов',
        'faculty': 'ФИТ (Фундаментальная информатика)',
        'year': 3,
        'group': 'Б9121-01.03.02',
        'gpa': 4.7,
        'is_active': True,
        'enrollment_year': 2022,
        'skills': ['Python', 'Django', 'JavaScript', 'SQL', 'Git'],
        'bio': 'Активный студент 3 курса ФИТ. Увлекается веб-разработкой и машинным обучением. Участник олимпиад по программированию.',
        'courses': [
            {'name': 'Python Basics', 'slug': 'python-basics'},
            {'name': 'Django Advanced', 'slug': 'django-advanced'}
        ],
        'achievements': [
            'Призер олимпиады по программированию 2023',
            'Стипендия за академические успехи',
            'Участник хакатона Digital Breakthrough'
        ]
    },
    2: {
        'id': 2,
        'name': 'Мария Петрова',
        'faculty': 'ФЭМ (Физическая электроника)',
        'year': 2,
        'group': 'Б9122-01.03.01',
        'gpa': 4.9,
        'is_active': True,
        'enrollment_year': 2023,
        'skills': ['C++', 'Arduino', 'Python', 'Matlab'],
        'bio': 'Студентка 2 курса ФЭМ. Интересуется микроэлектроникой и робототехникой. Вела исследовательский проект по созданию микроконтроллерных систем.',
        'courses': [
            {'name': 'Python Basics', 'slug': 'python-basics'}
        ],
        'achievements': [
            'Победитель конкурса инновационных проектов',
            'Автор научной публикации'
        ]
    },
    3: {
        'id': 3,
        'name': 'Алексей Сидоров',
        'faculty': 'ФЕН (Физика и нанотехнологии)',
        'year': 4,
        'group': 'Б9120-01.03.03',
        'gpa': 4.5,
        'is_active': True,
        'enrollment_year': 2021,
        'skills': ['Physics', 'Matlab', 'Python', 'Data Analysis'],
        'bio': 'Студент 4 курса ФЕН. Специализируется в области нанотехнологий и материаловедения. Работает над дипломным проектом по созданию новых материалов.',
        'courses': [],
        'achievements': [
            'Стажировка в исследовательском центре',
            'Публикация в научном журнале',
            'Доклад на международной конференции'
        ]
    }
}

# Function-Based Views
def home_page(request):
    """Главная страница с поиском студентов"""
    context = {
        'all_students': list(STUDENTS_DATA.values()),
        'search_query': '',
        'search_results': None
    }
    
    # Проверяем, был ли поисковый запрос
    query = request.GET.get('query', '').strip()
    if query:
        context['search_query'] = query
        context['search_results'] = search_student_by_name(query)
    
    return render(request, 'fefu_lab/home.html', context)

def search_student_by_name(query):
    """Поиск студента по имени"""
    query_lower = query.lower().strip()
    
    # Ищем точное совпадение
    for student_id, student_data in STUDENTS_DATA.items():
        if student_data['name'].lower() == query_lower:
            return {
                'success': True,
                'student': student_data,
                'message': f'Найден студент: {student_data["name"]}'
            }
    
    # Ищем частичное совпадение
    for student_id, student_data in STUDENTS_DATA.items():
        if query_lower in student_data['name'].lower():
            return {
                'success': True,
                'student': student_data,
                'message': f'Найден студент: {student_data["name"]}'
            }
    
    # Студент не найден
    return {
        'success': False,
        'student': None,
        'message': f'Студент "{query}" не найден'
    }

def about_page(request):
    """Страница 'О нас'"""
    return render(request, 'fefu_lab/about.html')

def student_profile(request, student_id):
    """Профиль студента"""
    if student_id in STUDENTS_DATA:
        context = {
            'student': STUDENTS_DATA[student_id],
            'student_id': student_id,
            'other_students': [id for id in STUDENTS_DATA.keys() if id != student_id]
        }
        return render(request, 'fefu_lab/student_profile.html', context)
    else:
        raise Http404("Студент не найден")

# Class-Based View
class CourseDetailView(TemplateView):
    """Детальная страница курса"""
    template_name = 'fefu_lab/course_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        course_slug = self.kwargs['course_slug']
        
        courses = {
            'python-basics': {
                'title': 'Python Basics',
                'description': 'Курс охватывает фундаментальные концепции программирования на Python.',
                'duration': '36 часов',
                'credits': '3',
                'level': 'Начальный',
                'instructor': 'Доцент Сергеев А.В.',
                'topics': [
                    'Введение в Python',
                    'Структуры данных',
                    'Функции и модули',
                    'Объектно-ориентированное программирование',
                ],
                'requirements': [
                    'Базовые знания информатики',
                    'Установленный Python 3.8+'
                ],
                'enrolled_students': 45,
                'rating': 4.8
            },
            'django-advanced': {
                'title': 'Django Advanced',
                'description': 'Продвинутый курс по веб-фреймворку Django.',
                'duration': '48 часов',
                'credits': '4',
                'level': 'Продвинутый',
                'instructor': 'Профессор Иванова М.С.',
                'topics': [
                    'Оптимизация ORM-запросов',
                    'REST API с Django REST Framework',
                    'JWT аутентификация',
                    'Кэширование и Celery',
                ],
                'requirements': [
                    'Знание Python',
                    'Базовый опыт работы с Django'
                ],
                'enrolled_students': 28,
                'rating': 4.9
            }
        }
        
        if course_slug in courses:
            context.update(courses[course_slug])
            context['other_courses'] = [slug for slug in courses.keys() if slug != course_slug]
        else:
            raise Http404("Курс не найден")
        
        return context

# Обработчик 404 ошибки
def custom_404(request, exception):
    """Кастомная страница 404"""
    return render(request, 'fefu_lab/404.html', status=404)

# Отдельное view для поиска (если нужно отдельным маршрутом)
def search_student(request):
    """Отдельная страница поиска студента"""
    query = request.GET.get('query', '').strip()
    
    if query:
        result = search_student_by_name(query)
        if result['success']:
            # Перенаправляем на страницу найденного студента
            return redirect('student_profile', student_id=result['student']['id'])
        else:
            # Показываем сообщение об ошибке
            context = {
                'all_students': list(STUDENTS_DATA.values()),
                'search_query': query,
                'search_results': result
            }
            return render(request, 'fefu_lab/home.html', context)
    
    # Если запрос пустой, возвращаем на главную
    return redirect('home')
