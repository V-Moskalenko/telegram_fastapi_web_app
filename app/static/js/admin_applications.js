window.Telegram.WebApp.ready(); // Инициализация Web App
const user = window.Telegram.WebApp.initDataUnsafe.user;

function workOnApplication(application_data) {
    // Создаём форму
    const form = document.createElement('form');
    form.method = 'POST';
    form.action = '/enter_prices';  // Переходим на страницу ввода цен
    form.style.display = 'none';

    // Добавляем данные заявки как скрытые поля
    const input = document.createElement('input');
    input.type = 'hidden';
    input.name = 'application_data';
    input.value = JSON.stringify(application_data);
    form.appendChild(input);

    // Добавляем форму на страницу и отправляем её
    document.body.appendChild(form);
    form.submit();
}

function closeApp() {
    // Закрываем Telegram WebApp через 100 мс
    setTimeout(() => {
        window.Telegram.WebApp.close();
    }, 100);
}