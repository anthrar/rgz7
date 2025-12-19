"""
Сервис для логирования действий пользователей (аудит).
"""
from flask import request
from app.models import db, AuditLog


def log_audit_event(user_id, action, entity_type, entity_id, request_obj=None):
    """
    Логировать действие пользователя в систему аудита.
    
    Args:
        user_id: ID пользователя (может быть None для анонимных действий)
        action: Тип действия ('create', 'update', 'delete')
        entity_type: Тип сущности ('subscription')
        entity_id: ID измененной сущности
        request_obj: Объект Flask request для извлечения IP и User-Agent
    """
    ip_address = None
    user_agent = None
    
    if request_obj:
        ip_address = request_obj.remote_addr
        user_agent = request_obj.headers.get('User-Agent', '')[:255]  # Ограничение длины
    
    audit_log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    
    try:
        db.session.add(audit_log)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        # В production лучше использовать логирование
        print(f"Ошибка при записи в аудит: {e}")

