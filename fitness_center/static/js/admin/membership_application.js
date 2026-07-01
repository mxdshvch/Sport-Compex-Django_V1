/**
 * Скрипт для управления заявками на абонементы
 */
document.addEventListener('DOMContentLoaded', function() {
    // Инициализация интерфейса
    initApplicationsUI();
    
    // Обработчик изменения статуса заявки
    setupStatusChangeHandlers();
    
    // Обработчик для фильтров
    setupFilterHandlers();
});

/**
 * Инициализация интерфейса заявок
 */
function initApplicationsUI() {
    // Проверяем наличие таблицы с заявками
    const applicationsTable = document.querySelector('#result_list');
    if (!applicationsTable) return;
    
    // Добавляем иконки для действий
    const actionCells = document.querySelectorAll('.field-actions');
    actionCells.forEach(cell => {
        // Получаем текущие ссылки
        const links = cell.querySelectorAll('a');
        
        // Добавляем иконки к ссылкам
        links.forEach(link => {
            const text = link.textContent.trim().toLowerCase();
            let iconClass = '';
            
            if (text.includes('изменить')) {
                iconClass = 'fas fa-edit';
            } else if (text.includes('удалить')) {
                iconClass = 'fas fa-trash-alt';
            } else if (text.includes('просмотр')) {
                iconClass = 'fas fa-eye';
            }
            
            if (iconClass) {
                // Создаем иконку
                const icon = document.createElement('i');
                icon.className = iconClass;
                
                // Очищаем текст ссылки и добавляем иконку
                link.innerHTML = '';
                link.appendChild(icon);
                link.classList.add('action-icon');
                
                // Добавляем подсказку
                link.setAttribute('title', text);
            }
        });
    });
    
    // Добавляем иконки для статусов
    const statusCells = document.querySelectorAll('.field-status_display');
    statusCells.forEach(cell => {
        const statusText = cell.textContent.trim().toLowerCase();
        let statusIcon = '';
        
        if (statusText.includes('одобрено')) {
            statusIcon = 'fas fa-check-circle';
        } else if (statusText.includes('отклонено')) {
            statusIcon = 'fas fa-times-circle';
        } else if (statusText.includes('обработке')) {
            statusIcon = 'fas fa-clock';
        }
        
        if (statusIcon) {
            // Получаем или создаем span для иконки
            let span = cell.querySelector('span');
            if (!span) {
                span = document.createElement('span');
                cell.innerHTML = '';
                cell.appendChild(span);
            }
            
            // Добавляем иконку перед текстом
            const icon = document.createElement('i');
            icon.className = statusIcon + ' icon';
            span.prepend(icon);
        }
    });
}

/**
 * Настройка обработчиков изменения статуса
 */
function setupStatusChangeHandlers() {
    const statusSelects = document.querySelectorAll('.status-select');
    
    statusSelects.forEach(select => {
        select.addEventListener('change', function() {
            const applicationId = this.dataset.applicationId;
            const newStatus = this.value;
            
            updateApplicationStatus(applicationId, newStatus);
        });
    });
}

/**
 * Обновление статуса заявки через AJAX
 */
function updateApplicationStatus(applicationId, newStatus) {
    // Формируем данные для запроса
    const formData = new FormData();
    formData.append('status', newStatus);
    
    // Получаем CSRF токен
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
    
    // Отправляем запрос
    fetch(`/memberships/admin/applications/${applicationId}/update-status/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken,
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Обновляем отображение статуса в интерфейсе
            const statusCell = document.querySelector(`#application-${applicationId} .status-display`);
            if (statusCell) {
                statusCell.className = `status-display status-${newStatus}`;
                statusCell.textContent = data.status_text;
            }
            
            // Показываем уведомление об успешном обновлении
            showNotification('Статус заявки успешно обновлен', 'success');
        } else {
            showNotification('Ошибка при обновлении статуса: ' + (data.error || 'Неизвестная ошибка'), 'error');
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
        showNotification('Произошла ошибка при обработке запроса', 'error');
    });
}

/**
 * Настройка обработчиков фильтров
 */
function setupFilterHandlers() {
    const filterButtons = document.querySelectorAll('.filter-button');
    
    filterButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            // Предотвращаем стандартное поведение ссылки
            e.preventDefault();
            
            // Убираем активный класс у всех кнопок
            filterButtons.forEach(btn => btn.classList.remove('active'));
            
            // Добавляем активный класс к текущей кнопке
            this.classList.add('active');
            
            // Обновляем URL без перезагрузки страницы
            const url = this.getAttribute('href');
            window.history.pushState({}, '', url);
            
            // Загружаем данные с новым фильтром
            loadFilteredApplications(url);
        });
    });
}

/**
 * Загрузка отфильтрованных заявок через AJAX
 */
function loadFilteredApplications(url) {
    fetch(url, {
        headers: {
            'X-Requested-With': 'XMLHttpRequest'
        }
    })
    .then(response => response.text())
    .then(html => {
        // Обновляем только таблицу с заявками, не всю страницу
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newTable = doc.querySelector('#result_list');
        
        if (newTable) {
            const currentTable = document.querySelector('#result_list');
            if (currentTable) {
                currentTable.innerHTML = newTable.innerHTML;
                
                // Переинициализируем интерфейс
                initApplicationsUI();
                setupStatusChangeHandlers();
            }
        }
    })
    .catch(error => {
        console.error('Ошибка при загрузке данных:', error);
        showNotification('Ошибка при загрузке данных', 'error');
    });
}

/**
 * Показ уведомления
 */
function showNotification(message, type = 'info') {
    // Создаем элемент уведомления
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Добавляем на страницу
    document.body.appendChild(notification);
    
    // Автоматически скрываем через 3 секунды
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
            notification.remove();
        }, 500);
    }, 3000);
} 