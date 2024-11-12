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


    //const token = localStorage.getItem('jwt_token');

    // Проверка валидности токена
    if (!localStorage.getItem('jwt_token')) {
        window.location.href = '/';
    } else {
        $.ajax({
            url: '/protected',  // Защищённый маршрут для проверки токена
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
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

    let fileIndex = 0; // Индекс для добавляемых файлов

    // Функция для добавления нового поля файла
    function addFileInput() {
        fileIndex++;

        const fileInputGroup = `
            <div class="file-input-group" data-index="${fileIndex}">
                <label for="fileInput${fileIndex}">Выберите файл:</label>
                <input type="file" id="fileInput${fileIndex}" name="fileInput${fileIndex}" class="form-control">
                <label for="fileNameInput${fileIndex}">Имя файла:</label>
                <input type="text" id="fileNameInput${fileIndex}" class="form-control" placeholder="Введите имя файла">
                <button type="button" class="btn btn-danger remove-file-btn" data-index="${fileIndex}">Удалить файл</button>
            </div>
        `;

        $('#fileInputsContainer').append(fileInputGroup);
    }

    // Обработчик кнопки "Добавить файл"
    $('#addFileButton').on('click', function() {
        addFileInput();
    });

    // Обработчик кнопки "Удалить файл"
    $(document).on('click', '.remove-file-btn', function() {
        const index = $(this).data('index');
        $(`.file-input-group[data-index="${index}"]`).remove();
    });

    // Обработчик отправки формы
    $('#uploadForm').on('submit', function(event) {
        event.preventDefault();
        
        const formData = new FormData();
        let filesSelected = false;

        $('.file-input-group').each(function() {
            const index = $(this).data('index');
            const fileInput = $(`#fileInput${index}`)[0];
            const customFileName = $(`#fileNameInput${index}`).val() || fileInput.files[0].name;

            if (fileInput.files.length > 0) {
                filesSelected = true;
                formData.append('files', fileInput.files[0]);
                formData.append('fileNames', customFileName);
            }
        });

        if (!filesSelected) {
            alert('Выберите хотя бы один файл для загрузки.');
            return;
        }

        $.ajax({
            url: '/audio/upload',
            type: 'POST',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
            },
            data: formData,
            processData: false,
            contentType: false,
            success: function(response) {
                alert('Файлы успешно загружены!');
                $('#uploadForm')[0].reset();
                $('#fileInputsContainer').empty();
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
                'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
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
                            <td>
                                ${file.transcribed ? 'Yes' : 'No'}
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
        /*const token = localStorage.getItem('jwt_token');
        if (!token) {
            alert('Необходимо войти в систему, чтобы удалять файлы.');
            return;
        }
*/
        $.ajax({
            url: `/audio/${audioId}/delete`,  // Динамически подставляем audioId в URL
            type: 'DELETE',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
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
        /*const token = localStorage.getItem('jwt_token');
        if (!token) {
            alert('Необходимо войти в систему, чтобы загружать файлы.');
            return;
        }
            */
    
        $.ajax({
            url: `/audio/${audioId}/download_url`,  // Подставляем audioId в URL
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + localStorage.getItem('jwt_token')
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
