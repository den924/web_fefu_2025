# fefu_lab/backends.py
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User
from django.db.models import Q

class EmailBackend(ModelBackend):
    """Кастомный бэкенд для аутентификации по email"""
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Ищем пользователя по email или username
            user = User.objects.get(
                Q(email=username) | Q(username=username)
            )
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None
        except User.MultipleObjectsReturned:
            # Если найдено несколько пользователей с одинаковым email
            user = User.objects.filter(email=username).order_by('id').first()
            if user.check_password(password):
                return user
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
