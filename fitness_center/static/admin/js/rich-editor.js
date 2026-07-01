// (Удалён весь код редактора, чтобы не было кастомного редактора, только стандартное поле textarea) 

document.addEventListener('DOMContentLoaded', function() {
    const textareas = document.querySelectorAll('textarea[name$="description"]');
    if (!textareas.length) return;

    const fonts = [
        'Arial', 'Times New Roman', 'Helvetica', 'Georgia', 'Verdana', 'Roboto'
    ];

    textareas.forEach(textarea => {
        // Скрываем textarea
        textarea.style.display = 'none';

        // Создаем тулбар
        const toolbar = document.createElement('div');
        toolbar.className = 'rich-editor-toolbar';
        toolbar.style.marginBottom = '6px';
        toolbar.style.display = 'flex';
        toolbar.style.gap = '6px';

        // Bold
        const boldBtn = document.createElement('button');
        boldBtn.type = 'button';
        boldBtn.innerHTML = '<b>B</b>';
        boldBtn.title = 'Жирный';
        boldBtn.onclick = function() {
            document.execCommand('bold');
            editor.focus();
        };
        toolbar.appendChild(boldBtn);

        // Italic
        const italicBtn = document.createElement('button');
        italicBtn.type = 'button';
        italicBtn.innerHTML = '<i>I</i>';
        italicBtn.title = 'Курсив';
        italicBtn.onclick = function() {
            document.execCommand('italic');
            editor.focus();
        };
        toolbar.appendChild(italicBtn);

        // Font-family
        const fontSelect = document.createElement('select');
        fontSelect.title = 'Шрифт';
        fonts.forEach(font => {
            const option = document.createElement('option');
            option.value = font;
            option.textContent = font;
            option.style.fontFamily = font;
            fontSelect.appendChild(option);
        });
        fontSelect.onchange = function() {
            document.execCommand('fontName', false, fontSelect.value);
            editor.focus();
        };
        toolbar.appendChild(fontSelect);

        // Создаем contenteditable div
        const editor = document.createElement('div');
        editor.className = 'rich-editor-content';
        editor.contentEditable = true;
        editor.style.minHeight = '180px';
        editor.style.border = '1px solid #ccc';
        editor.style.borderRadius = '4px';
        editor.style.padding = '8px';
        editor.style.fontSize = '15px';
        editor.style.background = '#fff';
        editor.innerHTML = textarea.value;

        // При изменении содержимого — копируем HTML в textarea
        editor.addEventListener('input', function() {
            textarea.value = editor.innerHTML;
        });

        // Вставляем тулбар и редактор перед textarea
        textarea.parentNode.insertBefore(toolbar, textarea);
        textarea.parentNode.insertBefore(editor, textarea);
    });
}); 