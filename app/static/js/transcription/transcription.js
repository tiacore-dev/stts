$(document).ready(function() {
    // Проверка наличия токена в localStorage
    const token = localStorage.getItem('jwt_token');

    if (!token) {
        window.location.href = '/';
    } else {
        // Проверка валидности токена с сервером
        $.ajax({
            url: '/protected',
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                console.log('Токен валидный, пользователь: ', response.logged_in_as);

                // Загружаем аудиофайлы после проверки токена
                loadAudioFiles();
            },
            error: function(xhr, status, error) {
                console.error('Ошибка проверки токена:', error);
                window.location.href = '/';
            }
        });
    }

    // Обработка отправки формы
    $('#audioForm').on('submit', function(event) {
        event.preventDefault();

        // Собираем выбранные аудиофайлы (их ID)
        const selectedAudioFiles = $('#audioSelect').val();

        if (!selectedAudioFiles || selectedAudioFiles.length === 0) {
            alert('Пожалуйста, выберите хотя бы один аудиофайл.');
            return;
        }

        // Отправляем список выбранных ID файлов на сервер
        processAudio(selectedAudioFiles);
    });

    // Обработка отправки аудиофайлов на сервер
    function processAudio(audioIds) {
        const token = localStorage.getItem('jwt_token');
        $('#loadingIcon').show();
        $('#submitButton').prop('disabled', true).text('Отправка...');

        $.ajax({
            url: '/transcription/create',  // Убедитесь, что этот URL соответствует вашему серверному маршруту
            type: 'POST',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            data: JSON.stringify({ audio_ids: audioIds }),
            contentType: 'application/json',
            success: function(response) {
                console.log('Аудиофайлы успешно отправлены');
                $('#loadingIcon').hide();
                $('#submitButton').prop('disabled', false).text('Отправить');

                window.location.href = `/transcription_result`;
            },
            error: function(xhr) {
                $('#loadingIcon').hide();
                $('#submitButton').prop('disabled', false).text('Отправить');
                alert('Ошибка при обработке аудио.');
            }
        });
    }

    // Загрузка всех аудиофайлов с сервера
    function loadAudioFiles() {
        const token = localStorage.getItem('jwt_token');
        $.ajax({
            url: '/user_audio_files',  // Путь для получения списка аудиофайлов
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                const audioSelect = $('#audioSelect');
                audioSelect.empty();  // Очищаем выпадающий список перед добавлением новых данных
                audioSelect.append('<option value="">-- Выберите аудиофайл --</option>');  // Заголовок по умолчанию

                // Добавляем файлы в выпадающий список
                response.audio_files.forEach(audio => {
                    audioSelect.append(`<option value="${audio.audio_id}">${audio.file_name}</option>`);  // Используем id как значение
                });
            },
            error: function(xhr, status, error) {
                console.error('Ошибка загрузки аудиофайлов:', status, error);
            }
        });
    }

    

});
