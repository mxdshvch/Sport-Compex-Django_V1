/**
 * Admin Font Override - Forced application
 * This script applies Roboto font and correct font sizes 
 * to all admin elements after DOM is fully loaded
 */

document.addEventListener('DOMContentLoaded', function() {
    // Загружаем шрифт Roboto, если он еще не загружен
    if (!document.getElementById('roboto-font')) {
        const fontLink = document.createElement('link');
        fontLink.id = 'roboto-font';
        fontLink.rel = 'stylesheet';
        fontLink.href = 'https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap';
        document.head.appendChild(fontLink);
    }
    
    // Применяем шрифт ко всем элементам
    const style = document.createElement('style');
    style.textContent = `
        * {
            font-family: 'Roboto', -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif !important;
        }
    `;
    document.head.appendChild(style);
    
    // Добавляем Font Awesome, если он еще не загружен
    if (!document.querySelector('link[href*="font-awesome"]')) {
        const faLink = document.createElement('link');
        faLink.rel = 'stylesheet';
        faLink.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
        document.head.appendChild(faLink);
    }
    
    // Функция для применения стилей к элементам
    function applyFontStyles() {
        // Основной размер шрифта (16px вместо 14px) для всех элементов
        var allElements = document.querySelectorAll('*');
        allElements.forEach(function(el) {
            el.style.fontFamily = "'Roboto', -apple-system, BlinkMacSystemFont, sans-serif";
            el.style.fontSize = '16px';
        });
        
        // Заголовки главных разделов (28px)
        var mainHeadings = document.querySelectorAll('#content > h1, .content > h1, .dashboard .module caption, h1, .app-list > div > h1, .model-membershipapplication > div > h1, #header #branding h1, #branding h1, .dashboard #content h1, .app-dashboard #content h1');
        mainHeadings.forEach(function(el) {
            el.style.fontSize = '28px';
            el.style.fontWeight = '500';
            el.style.lineHeight = '1.2';
            el.style.marginBottom = '20px';
        });
        
        // Подзаголовки (20px)
        var subHeadings = document.querySelectorAll('.module h2, .module caption, .inline-group h2, h2');
        subHeadings.forEach(function(el) {
            el.style.fontSize = '20px';
            el.style.fontWeight = '500';
        });
        
        // Средний текст (18px) - меню, навигация
        var mediumText = document.querySelectorAll('.sidebar-menu a, .sidebar-menu span, .nav-sidebar .nav-label, .breadcrumbs a, .breadcrumbs, .object-tools a');
        mediumText.forEach(function(el) {
            el.style.fontSize = '18px';
        });
        
        // Кнопки и элементы управления (16px)
        var buttons = document.querySelectorAll('.button, input[type=submit], input[type=button], .submit-row input, a.button');
        buttons.forEach(function(el) {
            el.style.fontSize = '16px';
            el.style.fontWeight = '500';
        });
        
        // Поля ввода и формы (16px)
        var inputs = document.querySelectorAll('input, textarea, select, .form-row label, .aligned label');
        inputs.forEach(function(el) {
            el.style.fontSize = '16px';
        });
        
        // Таблицы (16px)
        var tables = document.querySelectorAll('table, tr, th, td, #changelist table thead th, #changelist table tbody td');
        tables.forEach(function(el) {
            el.style.fontSize = '16px';
        });
        
        // Вспомогательный текст (14px)
        var smallText = document.querySelectorAll('.help, p.help, small, .small, .quiet, .form-text, .form-help, .description, .price');
        smallText.forEach(function(el) {
            el.style.fontSize = '14px';
        });
        
        // Особые правила для страницы заявок
        var applicationItems = document.querySelectorAll('.app-name, .phone-number, .membership-name, .date-cell, .status-dropdown, .app-table th, .app-table td');
        applicationItems.forEach(function(el) {
            el.style.fontSize = '16px';
        });
        
        // Специальная обработка карточек на главной странице
        var dashboardItems = document.querySelectorAll('.card-title, .card-text, .card-body p, .card-body a, .card-header, .stat-value, .stat-label');
        dashboardItems.forEach(function(el) {
            el.style.fontSize = '18px';
        });
        
        // Числа в статистических карточках
        var statNumbers = document.querySelectorAll('.stat-value, .card-title');
        statNumbers.forEach(function(el) {
            el.style.fontSize = '36px';
            el.style.fontWeight = '500';
        });
        
        // Стили для меню слева
        var sideMenu = document.querySelectorAll('#sidebar a, #sidebar span, .nav-sidebar a, .nav-sidebar span');
        sideMenu.forEach(function(el) {
            el.style.fontSize = '18px';
        });
    }
    
    // Применяем стили сразу
    applyFontStyles();
    
    // И повторно через небольшую задержку для динамически добавленных элементов
    setTimeout(applyFontStyles, 500);
    
    // Добавляем повторное применение стилей при загрузке изображений и других ресурсов
    window.addEventListener('load', function() {
        applyFontStyles();
        // Еще раз с задержкой, чтобы перекрыть возможные стили, загруженные позже
        setTimeout(applyFontStyles, 1000);
    });
    
    // MutationObserver для отслеживания изменений в DOM
    var observer = new MutationObserver(function(mutations) {
        applyFontStyles();
    });
    
    // Настройка наблюдателя
    observer.observe(document.body, { 
        childList: true, 
        subtree: true,
        attributes: true,
        characterData: true
    });
}); 