"""
Основные роуты приложения.
"""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """Главная страница."""
    if current_user.is_authenticated:
        return redirect(url_for('main.subscriptions'))
    return render_template('index.html')


@main_bp.route('/subscriptions')
@login_required
def subscriptions():
    """Страница управления подписками."""
    return render_template('subscriptions.html')

