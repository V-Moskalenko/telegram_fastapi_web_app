window.Telegram.WebApp.ready(); // Инициализация Web App
    const user = window.Telegram.WebApp.initDataUnsafe.user;

    // Автозаполнение полей формы
    if (user) {
        document.getElementById('user_name').value = user.first_name; // Получаем имя пользователя
        document.getElementById('user_id').value = user.id; // Получаем ID пользователя
    }
    document.addEventListener('DOMContentLoaded', function () {
        const servicesContainer = document.getElementById('services-container');
        const addServiceBtn = document.getElementById('add-service');
        // Загрузка видов обучения при загрузке страницы
        fetch("/get_training_types")
            .then(response => response.json())
            .then(data => {
                // Сохраняем данные видов обучения для повторного использования
                window.trainingTypes = data.types;
                loadTrainingTypes();
            });

        // Функция загрузки видов обучения для первого блока
        function loadTrainingTypes() {
            const selects = document.querySelectorAll(".training-type");
            selects.forEach(select => {
                window.trainingTypes.forEach(type => {
                    const option = document.createElement("option");
                    option.value = type.id;
                    option.textContent = type.name;
                    select.appendChild(option);
                });
            });
        }

        // Функция добавления нового блока услуги
        function addServiceBlock() {
            const serviceBlock = document.createElement('div');
            serviceBlock.classList.add('service-block');

            const newId = 'service-' + Date.now(); // Уникальный ID для каждого нового блока

            serviceBlock.innerHTML = `
            <div class="input-group">
                <label for="${newId}-training_type">Выберите вид обучения:</label>
                <select id="${newId}-training_type" class="training-type" onchange="loadProgramsForType(this)">
                    <option value="">-- Выберите вид обучения --</option>
                </select>
            </div>
            <div class="input-group">
                <label for="${newId}-training_program">Выберите программу обучения:</label>
                <select id="${newId}-training_program" class="training-program" disabled>
                    <option value="">-- Сначала выберите вид обучения --</option>
                </select>
            </div>
            <div class="input-group">
                <label for="training_rank">Разряд (опционально)</label>
                <input type="text" name="training_rank">
            </div>
            <div class="input-group">
                <label for="people_count">Количество человек</label>
                <input type="number" name="people_count" min="1" required>
            </div>
        `;
            servicesContainer.appendChild(serviceBlock);

            loadTrainingTypes(); // Загружаем виды обучения для нового блока
        }

        // Добавляем новый блок при нажатии на кнопку
        addServiceBtn.addEventListener('click', addServiceBlock);
    });

    // Функция для загрузки программ обучения при выборе вида обучения
    function loadProgramsForType(select) {
        const serviceBlock = select.closest('.service-block');
        const programSelect = serviceBlock.querySelector(".training-program");
        const typeId = select.value;

        if (!typeId) {
            programSelect.innerHTML = '<option value="">-- Сначала выберите вид обучения --</option>';
            programSelect.disabled = true;
            return;
        }

        fetch(`/get_programs?type_id=${typeId}`)
            .then(response => response.json())
            .then(data => {
                programSelect.innerHTML = '';
                data.programs.forEach(function (program) {
                    const option = document.createElement('option');
                    option.value = program.id;
                    option.textContent = program.name;
                    programSelect.appendChild(option);
                });
                programSelect.disabled = false;
            });
    }

    document.getElementById('application-form').addEventListener('submit', function (e) {
        e.preventDefault(); // Предотвращаем стандартное действие формы (перезагрузку страницы)

        // Собираем данные формы
        const formData = new FormData(document.getElementById('application-form'));
        const services = [];

        // Собираем данные всех услуг
        document.querySelectorAll('.service-block').forEach((block) => {
            const trainingType = block.querySelector('.training-type').value;
            const trainingProgram = block.querySelector('.training-program').value;
            const trainingRank = block.querySelector('[name="training_rank"]').value;
            const peopleCount = block.querySelector('[name="people_count"]').value;

            services.push({
                training_type_id: trainingType,
                training_program_id: trainingProgram,
                training_rank: trainingRank,
                people_count: peopleCount
            });
        });

        // Собираем все данные формы
        const data = {
            user_id: document.getElementById('user_id').value,
            user_name: formData.get('user_name'),
            company_name: formData.get('company_name'),
            phone_number: formData.get('phone_number'),
            email: formData.get('email'),
            services: services
        };

        // Отправляем данные на сервер
        fetch('/submit_application', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
            .then(response => response.json())
            .then(data => {
                // Проверяем, что сервер вернул статус 'success'
                if (data.status === 'success') {
                    // Отображаем popup с сообщением
                    document.getElementById('popupMessage').textContent = data.message;
                    document.getElementById('popup').style.display = 'flex'; // Показываем popup
                    // Логи для отладки
                    console.log('Popup display value:', getComputedStyle(document.getElementById('popup')).display);
                    console.log('Popup z-index value:', getComputedStyle(document.getElementById('popup')).zIndex);
                    console.log('Popup is shown');
                } else {
                    // Обрабатываем ошибки, если статус не 'success'
                    alert('Ошибка: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Ошибка:', error);
            });
    });

    // Закрытие popup при нажатии на кнопку "Закрыть"
    document.getElementById('closePopup').addEventListener('click', function () {
        document.getElementById('popup').style.display = 'none'; // Закрываем popup
        // Закрываем Telegram WebApp через 100 мс
        setTimeout(() => {
            window.Telegram.WebApp.close();
        }, 100);
    });

    // Анимация появления элементов при загрузке страницы
    function animateElements() {
        const elements = document.querySelectorAll('h3, .input-group, .add-service-btn, .submit-btn');
        elements.forEach((el, index) => {
            setTimeout(() => {
                el.style.opacity = '1';
                el.style.transform = 'translateY(0)';
            }, 100 * index);
        });
    }

    // Стили для анимации
    var styleSheet = document.styleSheets[0];
    styleSheet.insertRule(`
    h3, .input-group, .add-service-btn, .submit-btn {
        opacity: 0;
        transform: translateY(20px);
        transition: opacity 0.5s ease, transform 0.5s ease;
    }
`, styleSheet.cssRules.length);

    // Плавное появление страницы при загрузке
    window.addEventListener('load', function () {
        document.body.style.opacity = '1';
        animateElements();
    });

    styleSheet.insertRule(`
    body {
        opacity: 0;
        transition: opacity 0.5s ease;
`, styleSheet.cssRules.length);