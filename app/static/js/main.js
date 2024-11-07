$(document).ready(function() {
    // Проверка, есть ли боковое меню и JWT токен
    const hasSidebar = $('#sidebar').length > 0;

    if (localStorage.getItem('jwt_token')) {
         $('#logoutButton').show();
        if (hasSidebar) {
            $('#sidebar').show();  // Показываем боковое меню
        } else {
            $('#sidebar').hide();  // Если бокового меню нет, скрываем
            $('#content-wrapper').addClass('sidebar-hidden');  // Добавляем класс для центрирования контента
        }
    } else {
        $('#logoutButton').hide();  // Скрываем кнопку выхода, если нет токена
        $('#sidebar').hide();  // Скрываем боковое меню
        $('#content-wrapper').addClass('sidebar-hidden');  // Центрируем контент
    }

    function adjustSidebar() {
        const navbarHeight = $('.navbar').outerHeight();
        $('.sidebar').css('top', navbarHeight + 'px'); // Устанавливаем верхнее положение сайдбара
        $('#main-content').css('padding-top', navbarHeight + 'px'); // Увеличиваем верхний отступ для основного контента
    }

    adjustSidebar(); // Настраиваем сайдбар при загрузке страницы

    $(window).resize(function() {
        adjustSidebar(); // Перенастраиваем сайдбар при изменении размера окна
    });

    // Функция для обновления токена
    function refreshAccessToken() {
        const refreshToken = localStorage.getItem('refresh_token');
        if (!refreshToken) {
            console.error('Refresh token отсутствует.');
            return;
        }
        
        return $.ajax({
            url: '/refresh',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ refresh_token: refreshToken }),
            success: function(response) {
                saveTokens(response.access_token, refreshToken);
            },
            error: function() {
                console.error('Ошибка при обновлении токена.');
                // Если обновление не удалось, можно перенаправить пользователя на страницу входа
                window.location.href = '/';
            }
        });
    }

    // Функция для выполнения запроса с проверкой access token
    function withAuthRequest(settings) {
        const token = localStorage.getItem('jwt_token');
        if (!token) {
            window.location.href = '/';
            return;
        }

        settings.headers = { ...settings.headers, 'Authorization': `Bearer ${token}` };
        
        return $.ajax(settings).fail(async function(xhr) {
            if (xhr.status === 401) { // Если access token истек
                await refreshAccessToken();
                // Повторный запрос после обновления токена
                settings.headers['Authorization'] = `Bearer ${localStorage.getItem('jwt_token')}`;
                return $.ajax(settings);
            } else {
                console.error('Ошибка при выполнении запроса:', xhr);
            }
        });
    }

    // Функция для сохранения токенов в localStorage
    function saveTokens(accessToken, refreshToken) {
        localStorage.setItem('jwt_token', accessToken);
        localStorage.setItem('refresh_token', refreshToken);
    }


    // Форма входа
    $('#loginForm').on('submit', function(event) {
        event.preventDefault();

        let login = $('#login').val();
        let password = $('#password').val();

        $.ajax({
            url: '/auth',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ login: login, password: password }),
            success: function(response) {
                saveTokens(response.access_token, response.refresh_token);
                $('#loginAlert').html('<div class="alert alert-success">Login successful!</div>');
                window.location.href = '/account';
            },
            error: function(xhr) {
                let errorMsg = 'An error occurred.';
                if (xhr.responseJSON && xhr.responseJSON.msg) {
                    errorMsg = xhr.responseJSON.msg;
                }
                $('#loginAlert').html(`<div class="alert alert-danger">${errorMsg}</div>`);
            }
        });
    });

    // Кнопка выхода
    $('#logoutButton').on('click', function() {
        localStorage.removeItem('jwt_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/';
    });

    // Обработчик для кнопки "Register"
    $('#registerButton').on('click', function() {
        // Редиректим пользователя на страницу регистрации
        window.location.href = '/register';
    });

    // Обработчик для формы регистрации
    $('#registerForm').on('submit', function(event) {
        event.preventDefault();

        let username = $('#username').val();
        let login = $('#login').val();
        let password = $('#password').val();

        $.ajax({
            url: '/register',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ username: username, login: login, password: password }),
            success: function(response) {
                $('#registerAlert').html('<div class="alert alert-success">Registration successful! Redirecting...</div>');
                saveTokens(response.access_token, response.refresh_token);
                window.location.href = '/account'; 
            },
            error: function() {
                $('#registerAlert').html('<div class="alert alert-danger">Error during registration.</div>');
            }
        });
    });

    // Таймер для регулярного обновления токена
    function startTokenRefreshInterval() {
        setInterval(refreshAccessToken, 15 * 60 * 1000); // Обновление каждые 15 минут
    }

    if (localStorage.getItem('refresh_token')) {
        startTokenRefreshInterval();
    }

    // Флаг активности пользователя
    let userActive = true;

    // Сброс флага активности при любом действии пользователя
    $(document).on('mousemove click keypress', function() {
        userActive = true;
    });

    // Функция для обновления токена при активности пользователя
    function checkAndRefreshToken() {
        if (userActive) {
            refreshAccessToken();
            userActive = false; // Сбрасываем флаг после обновления токена
        }
    }

    // Таймер для проверки активности пользователя и обновления токена
    setInterval(checkAndRefreshToken, 10 * 60 * 1000); // Проверка активности каждые 10 минут
});
