"""
Валидаторы для проверки данных.
"""
import re
from datetime import datetime


def validate_email(email):
    """
    Валидация email адреса.
    
    Args:
        email: Email адрес для проверки
    
    Returns:
        bool: True если email валиден
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_password(password):
    """
    Валидация пароля.
    
    Args:
        password: Пароль для проверки
    
    Returns:
        tuple: (bool, str) - (валиден ли пароль, сообщение об ошибке)
    """
    if len(password) < 6:
        return False, "Пароль должен содержать минимум 6 символов"
    return True, ""


def validate_subscription_interval(interval):
    """
    Валидация интервала подписки.
    
    Args:
        interval: Интервал подписки
    
    Returns:
        bool: True если интервал валиден ('monthly' или 'yearly')
    """
    return interval in ['monthly', 'yearly']


def validate_date(date_string):
    """
    Валидация даты в формате YYYY-MM-DD.
    
    Args:
        date_string: Строка с датой
    
    Returns:
        tuple: (bool, datetime.date или None) - (валидна ли дата, объект даты)
    """
    try:
        date_obj = datetime.strptime(date_string, '%Y-%m-%d').date()
        return True, date_obj
    except (ValueError, TypeError):
        return False, None

