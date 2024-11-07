$(document).ready(function() {
    const token = localStorage.getItem('jwt_token');

    // Если токен отсутствует, перенаправляем на страницу home
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

                // Запрос имени пользователя
                $.ajax({
                    url: '/get_username',  // Маршрут для получения имени пользователя
                    type: 'GET',
                    headers: {
                        'Authorization': 'Bearer ' + token
                    },
                    success: function(username) {
                        // Вставляем имя пользователя в HTML
                        $('#username').text(username);
                    },
                    error: function(xhr, status, error) {
                        console.error('Ошибка получения имени пользователя:', error);
                    }
                });
            },
            error: function(xhr, status, error) {
                console.error('Ошибка проверки токена:', error);
                window.location.href = '/';
            }
        });
    }

    // Event listener for creating an API key
    $('#createApiKey').click(function() {
        const comment = $('#comment').val();
        
        $.ajax({
            url: '/set_api_token',
            type: 'POST',
            contentType: 'application/json',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            data: JSON.stringify({ comment: comment }),
            success: function(response) {
                $('#apiKeySection').show();  // Показываем секцию с ключом
                $('#apiKeyInput').val(response.api_key);  // Заполняем поле с API ключом
                alert('Ключ успешно создан! Скопируйте его, так как он больше не будет отображаться.');
            },
            error: function(xhr) {
                alert('Ошибка создания API ключа');
            }
        });
    });

    // Event listener for refreshing the API key
    $('#refreshApiKey').click(function() {
        const comment = $('#comment').val();

        $.ajax({
            url: '/refresh_api_token',
            type: 'PATCH',
            contentType: 'application/json',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            data: JSON.stringify({ comment: comment }),
            success: function(response) {
                $('#apiKeySection').show();  // Показываем секцию с ключом
                $('#apiKeyInput').val(response.api_key);  // Заполняем поле с API ключом
                alert('Ключ успешно обновлен! Скопируйте его, так как он больше не будет отображаться.');
            },
            error: function(xhr) {
                alert('Ошибка обновления API ключа');
            }
        });
    });

    // Event listener for copying the API key
    $('#copyApiKey').click(function() {
        const apiKey = $('#apiKeyInput');
        apiKey.select();
        apiKey.setSelectionRange(0, 99999);  // Для мобильных устройств
        document.execCommand('copy');
        alert('API ключ скопирован в буфер обмена!');
    });
});
