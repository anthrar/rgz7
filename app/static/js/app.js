// API базовый URL
const API_BASE = '/api';

// Загрузка подписок при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('subscriptionsTableBody')) {
        loadSubscriptions();
    }
});

// Загрузка списка подписок
async function loadSubscriptions() {
    const tbody = document.getElementById('subscriptionsTableBody');
    if (!tbody) return;

    try {
        const response = await fetch(`${API_BASE}/subscriptions`);
        
        if (!response.ok) {
            if (response.status === 401) {
                window.location.href = '/login';
                return;
            }
            throw new Error('Ошибка загрузки подписок');
        }

        const data = await response.json();
        displaySubscriptions(data.subscriptions);
    } catch (error) {
        console.error('Ошибка:', error);
        tbody.innerHTML = '<tr><td colspan="5" class="loading">Ошибка загрузки данных</td></tr>';
        showError('Не удалось загрузить подписки');
    }
}

// Отображение подписок в таблице
function displaySubscriptions(subscriptions) {
    const tbody = document.getElementById('subscriptionsTableBody');
    
    if (subscriptions.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="loading">Нет активных подписок</td></tr>';
        return;
    }

    tbody.innerHTML = subscriptions.map(sub => `
        <tr>
            <td>${escapeHtml(sub.name)}</td>
            <td>${formatAmount(sub.amount)}</td>
            <td>${formatInterval(sub.interval)}</td>
            <td>${formatDate(sub.next_billing_date)}</td>
            <td class="actions">
                <button class="btn btn-primary btn-small" onclick="editSubscription(${sub.id})">Редактировать</button>
                <button class="btn btn-danger btn-small" onclick="deleteSubscription(${sub.id})">Удалить</button>
            </td>
        </tr>
    `).join('');
}

// Форматирование суммы
function formatAmount(amount) {
    return new Intl.NumberFormat('ru-RU', {
        style: 'currency',
        currency: 'RUB'
    }).format(amount);
}

// Форматирование интервала
function formatInterval(interval) {
    const intervals = {
        'monthly': 'Ежемесячно',
        'yearly': 'Ежегодно'
    };
    return intervals[interval] || interval;
}

// Форматирование даты
function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString);
    return date.toLocaleDateString('ru-RU');
}

// Экранирование HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Показать модальное окно для добавления
function showAddModal() {
    document.getElementById('modalTitle').textContent = 'Добавить подписку';
    document.getElementById('subscriptionForm').reset();
    document.getElementById('subscriptionId').value = '';
    document.getElementById('subscriptionModal').style.display = 'block';
}

// Показать модальное окно для редактирования
async function editSubscription(id) {
    try {
        const response = await fetch(`${API_BASE}/subscriptions/${id}`);
        
        if (!response.ok) {
            throw new Error('Ошибка загрузки подписки');
        }

        const subscription = await response.json();
        
        document.getElementById('modalTitle').textContent = 'Редактировать подписку';
        document.getElementById('subscriptionId').value = subscription.id;
        document.getElementById('name').value = subscription.name;
        document.getElementById('amount').value = subscription.amount;
        document.getElementById('interval').value = subscription.interval;
        document.getElementById('next_billing_date').value = subscription.next_billing_date;
        
        document.getElementById('subscriptionModal').style.display = 'block';
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Не удалось загрузить данные подписки');
    }
}

// Скрыть модальное окно
function hideModal() {
    document.getElementById('subscriptionModal').style.display = 'none';
}

// Закрытие модального окна при клике вне его
window.onclick = function(event) {
    const modal = document.getElementById('subscriptionModal');
    if (event.target === modal) {
        hideModal();
    }
}

// Обработка формы подписки
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('subscriptionForm');
    if (form) {
        form.addEventListener('submit', handleSubscriptionSubmit);
    }
});

// Отправка формы подписки
async function handleSubscriptionSubmit(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('name').value.trim(),
        amount: parseFloat(document.getElementById('amount').value),
        interval: document.getElementById('interval').value,
        next_billing_date: document.getElementById('next_billing_date').value
    };

    const subscriptionId = document.getElementById('subscriptionId').value;
    const isEdit = subscriptionId !== '';

    try {
        const url = isEdit ? `${API_BASE}/subscriptions/${subscriptionId}` : `${API_BASE}/subscriptions`;
        const method = isEdit ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (!response.ok) {
            if (data.errors) {
                showError(data.errors.join(', '));
            } else {
                showError(data.error || 'Ошибка при сохранении подписки');
            }
            return;
        }

        hideModal();
        loadSubscriptions();
        showSuccess(isEdit ? 'Подписка обновлена' : 'Подписка добавлена');
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Ошибка при сохранении подписки');
    }
}

// Удаление подписки
async function deleteSubscription(id) {
    if (!confirm('Вы уверены, что хотите удалить эту подписку?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/subscriptions/${id}`, {
            method: 'DELETE'
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.error || 'Ошибка при удалении подписки');
        }

        loadSubscriptions();
        showSuccess('Подписка удалена');
    } catch (error) {
        console.error('Ошибка:', error);
        showError('Не удалось удалить подписку');
    }
}

// Показать сообщение об ошибке
function showError(message) {
    const errorDiv = document.getElementById('errorMessage');
    if (errorDiv) {
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
        setTimeout(() => {
            errorDiv.style.display = 'none';
        }, 5000);
    } else {
        alert(message);
    }
}

// Показать сообщение об успехе
function showSuccess(message) {
    // Создаем временное сообщение
    const messagesDiv = document.querySelector('.messages') || document.querySelector('.container');
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message message-success';
    messageDiv.textContent = message;
    messagesDiv.insertBefore(messageDiv, messagesDiv.firstChild);
    
    setTimeout(() => {
        messageDiv.remove();
    }, 5000);
}

