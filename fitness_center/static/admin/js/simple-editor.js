document.addEventListener('DOMContentLoaded', function() {
    const textarea = document.querySelector('#id_description');
    if (!textarea) return;

    // Создаем панель инструментов
    const toolbar = document.createElement('div');
    toolbar.className = 'simple-editor-toolbar';
    textarea.parentNode.insertBefore(toolbar, textarea);

    // Функция для обертывания выделенного текста тегами
    function wrapText(textarea, openTag, closeTag) {
        const start = textarea.selectionStart;
        const end = textarea.selectionEnd;
        const selectedText = textarea.value.substring(start, end);
        const beforeText = textarea.value.substring(0, start);
        const afterText = textarea.value.substring(end);

        textarea.value = beforeText + openTag + selectedText + closeTag + afterText;
        textarea.focus();
        textarea.setSelectionRange(start + openTag.length, end + openTag.length);
    }
}); 