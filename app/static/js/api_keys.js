$(document).ready(function() {
    const token = localStorage.getItem('access_token');

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
                loadApiKeys();
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
            url: '/api-key/create',
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
                loadApiKeys();
            },
            error: function(xhr) {
                alert('Ошибка создания API ключа');
            }
        });
    });

    // Event listener для удаления API ключа
    function deleteApiKey(keyId) {
        $.ajax({
            url: '/api-key/delete',  // Удаление API ключа
            type: 'DELETE',
            contentType: 'application/json',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            data: JSON.stringify({ key_id: keyId }),
            success: function(response) {
                alert('API ключ удален');
                loadApiKeys();  // Обновляем список ключей
            },
            error: function(xhr) {
                alert('Ошибка удаления API ключа');
            }
        });
    }

    // Загружаем все API ключи при старте страницы
    function loadApiKeys() {
        $.ajax({
            url: '/api-key/all',  // Получение всех API ключей
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                const apiKeys = response;
                $('#apiKeysList').empty();  // Очищаем список перед добавлением новых ключей
                apiKeys.forEach(function(apiKey) {
                    const apiKeyItem = $('<div>').addClass('api-key-item').text(`Comment: ${apiKey.comment}`);
                    const deleteButton = $('<button>').addClass('btn btn-danger ml-2').text('Delete').click(function() {
                        deleteApiKey(apiKey.key_id);
                    });
                    apiKeyItem.append(deleteButton);
                    $('#apiKeysList').append(apiKeyItem);
                });
            },
            error: function(xhr) {
                alert('Ошибка получения API ключей');
            }
        });
    }


    // Event listener for copying the API key
    $('#copyApiKey').click(function() {
        const apiKey = $('#apiKeyInput');
        apiKey.select();
        apiKey.setSelectionRange(0, 99999);  // Для мобильных устройств
        document.execCommand('copy');
        alert('API ключ скопирован в буфер обмена!');
    });
});
