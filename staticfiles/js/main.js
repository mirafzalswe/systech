// ====================================
// ОСНОВНОЙ JAVASCRIPT КОД
// ====================================

// Утилита для показа сообщений
function showMessage(text, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = text;
    
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alert, container.firstChild);
        
        setTimeout(() => {
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 300);
        }, 3000);
    }
}

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    console.log('Приложение загружено');
});
