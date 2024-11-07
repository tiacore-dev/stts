/*
$(document).ready(function() {
    // Проверка наличия токена в localStorage
    const token = localStorage.getItem('jwt_token');

    // Если токен отсутствует, перенаправляем на страницу входа
    if (!token) {
        window.location.href = '/';
    } else {
        // Проверка валидности токена с сервером
        $.ajax({
            url: '/protected',  // Защищенный маршрут для проверки токена
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                console.log('Токен валидный, пользователь: ', response.logged_in_as);
                loadPrompts(); // Загружаем промпты после проверки токена
            },
            error: function(xhr, status, error) {
                console.error('Ошибка проверки токена:', error);
                window.location.href = '/';
            }
        });
    }

    

    $('#audioForm').on('submit', function(event) {
        console.log("Событие отправки формы поймано");  // Лог для отладки
        event.preventDefault();
        
        const formData = new FormData();
        formData.append('audio', $('#audioFile')[0].files[0]);  // Загрузка аудиофайла
        formData.append('prompt', $('#prompt').val());  // Промпт пользователя
    
        const audioFile = $('#audioFile')[0].files[0];
        const promptText = $('#prompt').val();
    
        if (!audioFile) {
            alert('Пожалуйста, выберите аудиофайл.');
            return;
        }
    
        if (!promptText) {
            alert('Пожалуйста, выберите промпт.');
            return;
        }
    
        // Показываем спиннер и дизейблим кнопку
        $('#loadingIcon').show();  // Показываем иконку загрузки
        $('#submitButton').prop('disabled', true).text('Отправка...');  // Блокируем кнопку
    
        $.ajax({
            url: '/process_audio',  // Маршрут обработки аудио
            type: 'POST',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                console.log('Аудиофайл успешно отправлен');
    
                // Скрываем спиннер и восстанавливаем кнопку
                $('#loadingIcon').hide();  
                $('#submitButton').prop('disabled', false).text('Отправить');
    
                // Получаем транскрипцию и анализ из ответа
                const transcription = encodeURIComponent(response.transcription);
                const analysis = encodeURIComponent(response.analysis);
            
                // Перенаправляем на страницу с параметрами
                window.location.href = /transcription_result?transcription=${transcription}&analysis=${analysis};
            },
            error: function(xhr) {
                // Скрываем иконку загрузки и восстанавливаем кнопку при ошибке
                $('#loadingIcon').hide();
                $('#submitButton').prop('disabled', false).text('Отправить');
                
                let errorMsg = 'Произошла ошибка при обработке аудио.';
                if (xhr.responseJSON && xhr.responseJSON.msg) {
                    errorMsg = xhr.responseJSON.msg;
                }
                alert(errorMsg);
            }
        });
    });


    // Обработчик для кнопки "Назад"
    $('#backButton').on('click', function() {
        window.location.href = '/account';  // Перенаправляем на главную страницу аккаунта
    });

});


// Загрузка всех промптов
function loadPrompts() {
    const token = localStorage.getItem('jwt_token');
    $.ajax({
        url: '/user_prompts',
        type: 'GET',
        headers: {
            'Authorization': 'Bearer ' + token
        },
        success: function(response) {
            const promptSelect = $('#prompt'); // Используем выпадающий список
            promptSelect.empty(); // Очищаем перед обновлением списка
            promptSelect.append('<option value="">-- Выберите промпт --</option>'); // Добавляем опцию по умолчанию

            // Добавляем каждый промпт в выпадающий список, отображая только prompt_name
            response.prompt_data.forEach(prompt => {
                promptSelect.append(<option value="${prompt.prompt_name}">${prompt.prompt_name}</option>); // Используем prompt_name в качестве текста
            });
        },
        error: function(xhr, status, error) {
            console.error('Ошибка загрузки промптов:', status, error);
        }
    });
}

*/