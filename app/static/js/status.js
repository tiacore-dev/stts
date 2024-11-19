// static/js/status.js

$(document).ready(function() {
    const token = localStorage.getItem('access_token');

    // Если токен отсутствует, перенаправляем на страницу home
    if (!token) {
        window.location.href = '/';
    } else {
        // Проверка валидности токена
        $.ajax({
            url: '/protected',  // Защищенный маршрут для проверки токена
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                console.log('Токен валидный, пользователь: ', response.logged_in_as);
                
                // Запуск обновления статусов задач
                fetchTaskStatuses(token);
                setInterval(() => fetchTaskStatuses(token), 10000);  // Обновление каждые 10 секунд
            },
            error: function(xhr, status, error) {
                console.error('Ошибка проверки токена:', error);
                window.location.href = '/';
            }
        });
    }

    // Функция для получения статусов задач
    function fetchTaskStatuses(token) {
        $.ajax({
            url: '/api/tasks/statuses',  // Эндпоинт для получения статусов всех задач
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                displayTaskStatuses(response.tasks);  // Вывод статусов задач
            },
            error: function(xhr, status, error) {
                console.error('Ошибка получения статусов задач:', error);
            }
        });
    }

    // Функция для отображения статусов задач
    function displayTaskStatuses(tasks) {
        const statusContainer = $('#statusContainer');
        statusContainer.empty();  // Очищаем контейнер перед обновлением

        tasks.forEach(task => {
            const taskDiv = $('<div>').addClass('task-status');
            taskDiv.html(`
                <h3>Задача ID: ${task.task_id}</h3>
                <p>Статус: ${task.status}</p>
                <p>Transcription ID: ${task.transcription_id || "В процессе..."}</p>
                <p>Результат: ${task.result || "Ожидание..."}</p>
            `);
            statusContainer.append(taskDiv);
        });
    }
});
