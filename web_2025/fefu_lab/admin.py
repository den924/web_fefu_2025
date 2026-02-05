from django.contrib import admin
from .models import Student, Instructor, Course, Enrollment

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'email', 'faculty', 'created_at']
    list_filter = ['faculty', 'created_at']
    search_fields = ['first_name', 'last_name', 'email']
    readonly_fields = ['created_at']
    fieldsets = [
        ('Основная информация', {
            'fields': ['first_name', 'last_name', 'email']
        }),
        ('Дополнительная информация', {
            'fields': ['birth_date', 'faculty', 'created_at'],
            'classes': ['collapse']
        }),
    ]

@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'email', 'specialization']
    search_fields = ['first_name', 'last_name', 'email', 'specialization']
    list_filter = ['specialization']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'duration', 'level', 'is_active', 'created_at']
    list_filter = ['is_active', 'level', 'created_at']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at']
    prepopulated_fields = {'slug': ['title']}
    fieldsets = [
        ('Основная информация', {
            'fields': ['title', 'slug', 'description', 'is_active']
        }),
        ('Детали курса', {
            'fields': ['duration', 'level', 'instructor', 'max_students', 'price']
        }),
    ]

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrolled_at', 'status']
    list_filter = ['status', 'enrolled_at', 'course']
    search_fields = ['student__first_name', 'student__last_name', 'course__title']
    readonly_fields = ['enrolled_at']
