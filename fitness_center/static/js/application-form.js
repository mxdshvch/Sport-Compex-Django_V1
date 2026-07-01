// Define color scheme
const primaryColor = '#ff3b4e';
const primaryDark = '#e0323f';
const secondaryColor = '#222222';
const lightColor = '#ffffff';

document.addEventListener('DOMContentLoaded', function() {
    // Apply styling to success message icon 
    const successIcons = document.querySelectorAll('.success-message .icon');
    successIcons.forEach(icon => {
        icon.style.backgroundColor = primaryColor;
        icon.style.color = lightColor;
    });
    
    // Style the pulse buttons
    const pulseButtons = document.querySelectorAll('.pulse-button');
    pulseButtons.forEach(button => {
        button.style.boxShadow = `0 0 0 0 rgba(255, 59, 78, 0.7)`;
    });
    
    // Получаем элементы модального окна
    const modal = document.getElementById('applicationModal');
    const modalInstance = new bootstrap.Modal(modal);
    const form = document.getElementById('applicationForm');
    const successMessage = document.getElementById('successMessage');
    
    // Находим все кнопки для открытия модального окна
    const applyButtons = document.querySelectorAll('.apply-button, .open-application-modal');
    
    // Добавляем обработчики для кнопок открытия модального окна
    applyButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Если на кнопке указано имя тренера, заполняем поле
            const trainerName = this.getAttribute('data-trainer-name');
            if (trainerName) {
                document.getElementById('trainerName').value = trainerName;
                document.getElementById('trainerNameField').style.display = 'block';
            } else {
                document.getElementById('trainerNameField').style.display = 'none';
                document.getElementById('trainerName').value = '';
            }
            
            // Если кнопка находится в карточке тренера, получаем название услуги
            const service = this.getAttribute('data-service');
            if (service) {
                document.getElementById('service').value = service;
            } else {
                document.getElementById('service').value = "Персональная тренировка";
            }
            
            // Показываем модальное окно
            modalInstance.show();
        });
    });
    
    // Обработка отправки формы
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Получаем данные формы
        const formData = new FormData(form);
        
        // Отправляем данные на сервер (AJAX запрос)
        fetch('/submit-application/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Если успешно, показываем сообщение об успехе
                form.style.display = 'none';
                successMessage.style.display = 'block';
                
                // Через 3 секунды закрываем модальное окно и сбрасываем форму
                setTimeout(() => {
                    form.reset();
                    form.style.display = 'block';
                    successMessage.style.display = 'none';
                    modalInstance.hide();
                }, 3000);
            } else {
                // Если есть ошибки, показываем их
                if (data.errors) {
                    Object.keys(data.errors).forEach(key => {
                        const input = document.getElementById(key);
                        const errorElement = document.getElementById(`${key}-error`);
                        if (errorElement) {
                            errorElement.textContent = data.errors[key];
                            errorElement.style.display = 'block';
                        }
                        input?.classList.add('is-invalid');
                    });
                }
            }
        })
        .catch(error => {
            console.error('Ошибка при отправке формы:', error);
        });
    });
    
    // При закрытии модального окна - сбрасываем форму
    modal.addEventListener('hidden.bs.modal', function() {
        form.reset();
        form.style.display = 'block';
        successMessage.style.display = 'none';
        
        // Убираем сообщения об ошибках
        document.querySelectorAll('.error-feedback').forEach(el => {
            el.textContent = '';
            el.style.display = 'none';
        });
        
        // Убираем классы ошибок с полей
        document.querySelectorAll('.is-invalid').forEach(el => {
            el.classList.remove('is-invalid');
        });
    });
    
    // Функция для получения CSRF токена
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
}); 