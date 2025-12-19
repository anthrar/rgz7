"""
Роуты для аутентификации и авторизации.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User
from app.utils.validators import validate_email, validate_password
from app.services.audit import log_audit_event

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа."""
    if current_user.is_authenticated:
        return redirect(url_for('main.subscriptions'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            if request.is_json:
                return jsonify({'error': 'Имя пользователя и пароль обязательны'}), 400
            flash('Имя пользователя и пароль обязательны', 'error')
            return render_template('login.html')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user, remember=True)
            if request.is_json:
                return jsonify({'message': 'Успешный вход', 'user_id': user.id}), 200
            flash('Вы успешно вошли в систему', 'success')
            return redirect(url_for('main.subscriptions'))
        else:
            if request.is_json:
                return jsonify({'error': 'Неверное имя пользователя или пароль'}), 401
            flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации."""
    if current_user.is_authenticated:
        return redirect(url_for('main.subscriptions'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        
        # Валидация
        errors = []
        if not username:
            errors.append('Имя пользователя обязательно')
        elif len(username) < 3:
            errors.append('Имя пользователя должно содержать минимум 3 символа')
        elif User.query.filter_by(username=username).first():
            errors.append('Пользователь с таким именем уже существует')
        
        if not email:
            errors.append('Email обязателен')
        elif not validate_email(email):
            errors.append('Некорректный email адрес')
        elif User.query.filter_by(email=email).first():
            errors.append('Пользователь с таким email уже существует')
        
        is_valid, password_error = validate_password(password)
        if not is_valid:
            errors.append(password_error)
        
        if errors:
            if request.is_json:
                return jsonify({'errors': errors}), 400
            for error in errors:
                flash(error, 'error')
            return render_template('register.html')
        
        # Создание пользователя
        user = User(username=username, email=email)
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            
            # Логирование аудита
            log_audit_event(user.id, 'create', 'user', user.id, request)
            
            login_user(user, remember=True)
            
            if request.is_json:
                return jsonify({'message': 'Пользователь успешно создан', 'user_id': user.id}), 201
            flash('Регистрация прошла успешно!', 'success')
            return redirect(url_for('main.subscriptions'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': 'Ошибка при создании пользователя'}), 500
            flash('Ошибка при создании пользователя', 'error')
    
    return render_template('register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """Выход из системы."""
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('main.index'))

