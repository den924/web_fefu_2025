from django.contrib import admin

# Register your models here.
from django.contrib import admin
from django.utils.html import format_html
from .models import Student, Instructor, Course, Enrollment, Skill

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'email', 'faculty', 'year', 'gpa', 'is_active', 'created_at']
    list_filter = ['is_active', 'faculty', 'year', 'created_at']
    search_fields = ['first_name', 'last_name', 'email']
    list_per_page = 20
    ordering = ['last_name', 'first_name']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('first_name', 'last_name', 'email', 'birth_date')
        }),
        ('Академическая информация', {
            'fields': ('faculty', 'year', 'gpa')
        }),
        ('Статус', {
            'fields': ('is_active',)
        }),
    )
    
    def get_faculty_display(self, obj):
        return obj.get_faculty_display_name()
    get_faculty_display.short_description = 'Факультет'

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'email', 'specialization', 'is_active']
    list_filter = ['is_active', 'specialization']
    search_fields = ['first_name', 'last_name', 'email', 'specialization']
    list_per_page = 20

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'duration', 'level', 'price', 'enrolled_count', 'is_active']
    list_filter = ['is_active', 'level', 'instructor']
    search_fields = ['title', 'description', 'instructor__last_name']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page = 20
    
    def enrolled_count(self, obj):
        return obj.enrolled_count()
    enrolled_count.short_description = 'Записано студентов'

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'status', 'grade']
    list_filter = ['status', 'enrolled_at', 'course']
    search_fields = ['student__last_name', 'student__first_name', 'course__title']
    list_per_page = 20
    date_hierarchy = 'enrolled_at'

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'student', 'level']
    list_filter = ['level']
    search_fields = ['name', 'student__last_name']
    list_per_page = 20
