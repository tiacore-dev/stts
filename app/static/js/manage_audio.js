$(document).ready(function() {

    // Подключение к серверу WebSocket
    const socket = io.connect('http://147.45.145.212:5000');  // Замените на ваш URL

    // Обработчик события подключения
    socket.on('connect', function() {
        console.log('Connected to the server');
    });

    // Обработчик для получения сообщений о загрузке
    // Удалить это
    socket.on('upload_progress', function(data) {
        console.log('Upload progress:', data.message);

        // Пример отображения уведомлений на странице
        const notification = document.createElement('div');
        notification.classList.add('alert');
        
        if (data.status === 'started') {
            notification.classList.add('alert-info');
            notification.textContent = data.message;  // "Загрузка началась"
        } else if (data.status === 'completed') {
            notification.classList.add('alert-success');
            notification.textContent = data.message;  // "Обработка завершена"
        }

        document.body.appendChild(notification);  // Добавляем уведомление в DOM
    });


    const token = localStorage.getItem('jwt_token');

    // Проверка валидности токена
    if (!token) {
        window.location.href = '/';
    } else {
        $.ajax({
            url: '/protected',  // Защищённый маршрут для проверки токена
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                loadFiles();  // Загрузка списка файлов
            },
            error: function(xhr, status, error) {
                console.error('Ошибка проверки токена:', error);
                window.location.href = '/';
            }
        });
    }

    // Функция загрузки файлов
    $('#uploadForm').on('submit', function(event) {
        event.preventDefault();
    
        let formData = new FormData(this);
        const fileInput = $('#fileInput')[0];
    
        // Проверяем, что выбрано хотя бы одно вложение
        if (fileInput.files.length === 0) {
            alert('Пожалуйста, выберите один или несколько файлов для загрузки.');
            return;
        }
    
        // Добавляем все выбранные файлы в formData
        for (let i = 0; i < fileInput.files.length; i++) {
            const file = fileInput.files[i];
            
            // Оригинальное имя и расширение файла
            const originalFileName = file.name;
            const fileExtension = originalFileName.split('.').pop();
    
            // Имя файла без расширения
            const fileNameWithoutExtension = originalFileName.split('.').slice(0, -1).join('.');
            
            // Устанавливаем поле 'fileName' в форме для каждого файла
            formData.append('files', file);
            formData.append('fileName', fileNameWithoutExtension); // Можно задать имя на стороне клиента
        }
    
        // Получаем токен из localStorage
        const token = localStorage.getItem('jwt_token');
        if (!token) {
            alert('Необходимо войти в систему, чтобы загружать файлы.');
            return;
        }
    
        // Отправка данных на сервер
        $.ajax({
            url: '/audio/upload',
            type: 'POST',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                alert('Файлы успешно загружены');
                loadFiles();  // Обновление списка файлов после загрузки
                $('#uploadForm')[0].reset(); // Сбрасываем форму
            },
            error: function(xhr, status, error) {
                console.error('Ошибка загрузки файлов:', error);
                alert('Ошибка при загрузке файлов. Пожалуйста, попробуйте еще раз.');
            }
        });
    });
    

    // Функция загрузки списка файлов
    function loadFiles(page = 1) {
        $.ajax({
            url: `/audio/all?page=${page}`,
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                let fileList = $('#fileList');
                fileList.empty();

                response.files.forEach(file => {
                    fileList.append(`
                        <tr>
                            <td>${file.name}</td>
                            <td>
                                <button class="btn btn-info" onclick="downloadFile('${file.audio_id}')">Download</button>
                                <button class="btn btn-danger" onclick="deleteFile('${file.audio_id}')">Delete</button>
                            </td>
                        </tr>
                    `);
                });

                // Пагинация
                let pagination = $('#pagination');
                pagination.empty();
                for (let i = 1; i <= response.total_pages; i++) {
                    pagination.append(`<li class="page-item"><a class="page-link" href="#" onclick="loadFiles(${i})">${i}</a></li>`);
                }
            },
            error: function(xhr, status, error) {
                console.error('Ошибка загрузки списка файлов:', error);
            }
        });
    }


    // Функция удаления файла
    window.deleteFile = function(audioId) {
        if (!confirm(`Вы уверены, что хотите удалить файл с ID '${audioId}'?`)) return;

        // Получаем токен из localStorage
        const token = localStorage.getItem('jwt_token');
        if (!token) {
            alert('Необходимо войти в систему, чтобы удалять файлы.');
            return;
        }

        $.ajax({
            url: `/audio/${audioId}/delete`,  // Динамически подставляем audioId в URL
            type: 'DELETE',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function() {
                alert(`Файл с ID '${audioId}' успешно удален`);
                loadFiles();  // Обновление списка файлов после удаления
            },
            error: function(xhr, status, error) {
                console.error(`Ошибка удаления файла с ID '${audioId}':`, error);
                alert('Ошибка при удалении файла. Пожалуйста, попробуйте еще раз.');
            }
        });
    };


    // Обработчик для кнопки "Назад"
    $('#backButton').on('click', function() {
        window.location.href = '/account';  // Перенаправляем на главную страницу аккаунта
    });

    window.downloadFile = function(audioId) {
        // Получаем токен из localStorage
        const token = localStorage.getItem('jwt_token');
        if (!token) {
            alert('Необходимо войти в систему, чтобы загружать файлы.');
            return;
        }
    
        $.ajax({
            url: `/audio/${audioId}/download_url`,  // Подставляем audioId в URL
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                if (response.url) {
                    // Перенаправление на временный URL для скачивания
                    window.location.href = response.url;
                } else {
                    alert('Ошибка при генерации URL для скачивания');
                }
            },
            error: function(xhr, status, error) {
                console.error(`Ошибка скачивания файла с ID '${audioId}':`, error);
            }
        });
    };
    
});
