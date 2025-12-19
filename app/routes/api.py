"""
RESTful API эндпоинты для управления подписками.
"""
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime
from app.models import db, Subscription
from app.utils.validators import validate_subscription_interval, validate_date
from app.services.audit import log_audit_event

api_bp = Blueprint('api', __name__)


@api_bp.route('/subscriptions', methods=['GET'])
@login_required
def get_subscriptions():
    """Получить список всех активных подписок текущего пользователя."""
    subscriptions = Subscription.query.filter_by(
        user_id=current_user.id,
        is_active=True
    ).all()
    
    return jsonify({
        'subscriptions': [sub.to_dict() for sub in subscriptions]
    }), 200


@api_bp.route('/subscriptions/<int:subscription_id>', methods=['GET'])
@login_required
def get_subscription(subscription_id):
    """Получить детали одной подписки."""
    subscription = Subscription.query.get_or_404(subscription_id)
    
    # Проверка прав доступа
    if subscription.user_id != current_user.id:
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    return jsonify(subscription.to_dict()), 200


@api_bp.route('/subscriptions', methods=['POST'])
@login_required
def create_subscription():
    """Создать новую подписку."""
    data = request.get_json()
    
    if not data:
        return jsonify({'error': 'Данные не предоставлены'}), 400
    
    # Валидация данных
    name = data.get('name', '').strip()
    amount = data.get('amount')
    interval = data.get('interval', '').strip().lower()
    next_billing_date_str = data.get('next_billing_date', '').strip()
    
    errors = []
    
    if not name:
        errors.append('Название подписки обязательно')
    elif len(name) > 200:
        errors.append('Название подписки слишком длинное (максимум 200 символов)')
    
    if amount is None:
        errors.append('Сумма обязательна')
    else:
        try:
            amount = float(amount)
            if amount <= 0:
                errors.append('Сумма должна быть положительным числом')
        except (ValueError, TypeError):
            errors.append('Некорректная сумма')
    
    if not validate_subscription_interval(interval):
        errors.append("Интервал должен быть 'monthly' или 'yearly'")
    
    is_valid_date, next_billing_date = validate_date(next_billing_date_str)
    if not is_valid_date:
        errors.append('Некорректная дата следующего списания (формат: YYYY-MM-DD)')
    
    if errors:
        return jsonify({'errors': errors}), 400
    
    # Создание подписки
    subscription = Subscription(
        user_id=current_user.id,
        name=name,
        amount=amount,
        interval=interval,
        next_billing_date=next_billing_date,
        is_active=True
    )
    
    try:
        db.session.add(subscription)
        db.session.commit()
        
        # Логирование аудита
        log_audit_event(current_user.id, 'create', 'subscription', subscription.id, request)
        
        return jsonify(subscription.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при создании подписки'}), 500


@api_bp.route('/subscriptions/<int:subscription_id>', methods=['PUT'])
@login_required
def update_subscription(subscription_id):
    """Обновить существующую подписку."""
    subscription = Subscription.query.get_or_404(subscription_id)
    
    # Проверка прав доступа
    if subscription.user_id != current_user.id:
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Данные не предоставлены'}), 400
    
    errors = []
    
    # Обновление полей (только если они предоставлены)
    if 'name' in data:
        name = data['name'].strip()
        if not name:
            errors.append('Название подписки не может быть пустым')
        elif len(name) > 200:
            errors.append('Название подписки слишком длинное')
        else:
            subscription.name = name
    
    if 'amount' in data:
        try:
            amount = float(data['amount'])
            if amount <= 0:
                errors.append('Сумма должна быть положительным числом')
            else:
                subscription.amount = amount
        except (ValueError, TypeError):
            errors.append('Некорректная сумма')
    
    if 'interval' in data:
        interval = data['interval'].strip().lower()
        if not validate_subscription_interval(interval):
            errors.append("Интервал должен быть 'monthly' или 'yearly'")
        else:
            subscription.interval = interval
    
    if 'next_billing_date' in data:
        is_valid_date, next_billing_date = validate_date(data['next_billing_date'])
        if not is_valid_date:
            errors.append('Некорректная дата следующего списания (формат: YYYY-MM-DD)')
        else:
            subscription.next_billing_date = next_billing_date
    
    if errors:
        return jsonify({'errors': errors}), 400
    
    try:
        db.session.commit()
        
        # Логирование аудита
        log_audit_event(current_user.id, 'update', 'subscription', subscription.id, request)
        
        return jsonify(subscription.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при обновлении подписки'}), 500


@api_bp.route('/subscriptions/<int:subscription_id>', methods=['DELETE'])
@login_required
def delete_subscription(subscription_id):
    """Удалить подписку."""
    subscription = Subscription.query.get_or_404(subscription_id)
    
    # Проверка прав доступа
    if subscription.user_id != current_user.id:
        return jsonify({'error': 'Доступ запрещен'}), 403
    
    try:
        # Физическое удаление
        db.session.delete(subscription)
        db.session.commit()
        
        # Логирование аудита
        log_audit_event(current_user.id, 'delete', 'subscription', subscription_id, request)
        
        return jsonify({'message': 'Подписка удалена'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Ошибка при удалении подписки'}), 500


@api_bp.route('/audit_logs', methods=['GET'])
@login_required
def get_audit_logs():
    """Получить логи аудита текущего пользователя."""
    from app.models import AuditLog
    
    logs = AuditLog.query.filter_by(user_id=current_user.id)\
        .order_by(AuditLog.timestamp.desc())\
        .limit(100)\
        .all()
    
    return jsonify({
        'audit_logs': [log.to_dict() for log in logs]
    }), 200


# Обработчики ошибок
@api_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Ресурс не найден'}), 404


@api_bp.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({'error': 'Внутренняя ошибка сервера'}), 500

