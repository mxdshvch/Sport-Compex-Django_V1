document.addEventListener('DOMContentLoaded', function() {
    initTrainersRow();
});

function initTrainersRow() {
    // Находим нужные элементы
    const rowContainer = document.querySelector('.trainers-row-container');
    if (!rowContainer) return;
    
    const trainersRow = rowContainer.querySelector('.trainers-row');
    const prevButton = rowContainer.querySelector('.trainers-row-prev');
    const nextButton = rowContainer.querySelector('.trainers-row-next');
    const trainerCards = trainersRow.querySelectorAll('.trainer-simple-card');
    
    if (!trainersRow || !trainerCards.length) return;
    
    // Первоначально скрываем кнопку "предыдущий", так как начинаем с первого тренера
    if (prevButton) {
        prevButton.style.opacity = '0.5';
        prevButton.style.pointerEvents = 'none';
    }
    
    // Обработчик для кнопки следующего тренера
    if (nextButton) {
        nextButton.addEventListener('click', function() {
            // Прокручиваем карточку тренера
            const cardWidth = trainerCards[0].offsetWidth + 20; // Ширина карточки + gap
            trainersRow.scrollBy({ left: cardWidth, behavior: 'smooth' });
            
            // После прокрутки проверяем, нужно ли активировать/деактивировать кнопки
            setTimeout(updateButtonStates, 300);
        });
    }
    
    // Обработчик для кнопки предыдущего тренера
    if (prevButton) {
        prevButton.addEventListener('click', function() {
            // Прокручиваем карточку тренера назад
            const cardWidth = trainerCards[0].offsetWidth + 20; // Ширина карточки + gap
            trainersRow.scrollBy({ left: -cardWidth, behavior: 'smooth' });
            
            // После прокрутки проверяем, нужно ли активировать/деактивировать кнопки
            setTimeout(updateButtonStates, 300);
        });
    }
    
    // Обновление состояния кнопок в зависимости от прокрутки
    function updateButtonStates() {
        // Если прокрутка в начале, деактивируем кнопку "предыдущий"
        if (prevButton) {
            if (trainersRow.scrollLeft <= 10) {
                prevButton.style.opacity = '0.5';
                prevButton.style.pointerEvents = 'none';
            } else {
                prevButton.style.opacity = '1';
                prevButton.style.pointerEvents = 'auto';
            }
        }
        
        // Если прокрутка в конце, деактивируем кнопку "следующий"
        if (nextButton) {
            const maxScrollLeft = trainersRow.scrollWidth - trainersRow.clientWidth - 10;
            if (trainersRow.scrollLeft >= maxScrollLeft) {
                nextButton.style.opacity = '0.5';
                nextButton.style.pointerEvents = 'none';
            } else {
                nextButton.style.opacity = '1';
                nextButton.style.pointerEvents = 'auto';
            }
        }
    }
    
    // Обработчик скролла для обновления состояния кнопок
    trainersRow.addEventListener('scroll', updateButtonStates);
    
    // Обработчик изменения размера окна
    window.addEventListener('resize', updateButtonStates);
    
    // Инициализация состояния кнопок
    updateButtonStates();
    
    // Добавляем анимацию при наведении на карточки
    trainerCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
        
        // Обработчик для кнопки "Записаться"
        const button = card.querySelector('.trainer-simple-button');
        if (button) {
            button.addEventListener('click', function() {
                const trainerName = this.getAttribute('data-trainer-name');
                if (trainerName) {
                    document.getElementById('trainerName').value = trainerName;
                    document.getElementById('trainerNameField').style.display = 'block';
                }
            });
        }
    });
} 