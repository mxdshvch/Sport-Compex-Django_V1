document.addEventListener('DOMContentLoaded', function() {
    tinymce.init({
        selector: 'textarea[name$="description"]',
        menubar: false,
        plugins: [],
        toolbar: 'bold italic | fontselect',
        font_formats: 'Arial=arial,helvetica,sans-serif;Times New Roman=times new roman,times;Helvetica=helvetica;Georgia=georgia;Verdana=verdana;Roboto=roboto;',
        branding: false,
        height: 250,
        content_style: "body { font-size:15px; }"
    });
}); 