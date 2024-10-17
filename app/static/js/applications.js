window.Telegram.WebApp.ready(); // Инициализация Web App
const user = window.Telegram.WebApp.initDataUnsafe.user;


function closeApp() {
    // Закрываем Telegram WebApp через 100 мс
    setTimeout(() => {
        window.Telegram.WebApp.close();
    }, 100);
}

