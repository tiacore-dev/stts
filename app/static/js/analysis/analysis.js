$(document).ready(function() {
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

                // Загружаем промпты и аудиофайлы последовательно
                loadPrompts().then(() => {
                    checkAutomaticPrompt();  // Проверяем автоматический промпт только после загрузки промптов
                });
                loadTranscriptions(); // Загружаем аудиофайлы
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

        const selectedPrompt = $('#prompt_name').val();       // Получаем выбранный промпт
        const selectedTranscriptions = $('#audio_file_name').val();  // Получаем выбранные ID транскрипций

        if (!selectedPrompt) {
            alert('Пожалуйста, выберите промпт.');
            return;
        }

        if (!selectedTranscriptions || selectedTranscriptions.length === 0) {
            alert('Пожалуйста, выберите хотя бы одну транскрипцию.');
            return;
        }

        // Передаем промпт и список транскрипций на сервер для анализа
        processAnalysis(selectedPrompt, selectedTranscriptions);
    });

    // Основная функция для обработки анализа
    function processAnalysis(prompt, transcriptionIds) {
        $('#loadingIcon').show();
        $('#submitButton').prop('disabled', true).text('Отправка...');

        $.ajax({
            url: '/analysis/create',
            type: 'POST',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            data: JSON.stringify({ prompt_id: prompt_id, transcription_ids: transcriptionIds }),
            contentType: 'application/json',
            success: function(response) {
                console.log('Аудиофайлы успешно отправлены');
                $('#loadingIcon').hide();
                $('#submitButton').prop('disabled', false).text('Отправить');
                window.location.href = `/analysis_result`;
            },
            error: function(xhr) {
                $('#loadingIcon').hide();
                $('#submitButton').prop('disabled', false).text('Отправить');
                alert('Ошибка при обработке аудио.');
            }
        });
    }

    // Функции для загрузки промптов и транскрипций
    function loadPrompts() {
        return $.ajax({  // Добавлено return для возврата Promise
            url: '/user_prompts',
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                const promptSelect = $('#prompt_name');
                promptSelect.empty().append('<option value="">-- Выберите промпт --</option>');
                response.prompt_data.forEach(prompt => {
                    promptSelect.append(`<option value="${prompt.prompt_id}">${prompt.prompt_name}</option>`);
                });
            },
            error: function(xhr, status, error) {
                console.error('Ошибка загрузки промптов:', status, error);
            }
        });
    }
    

    function loadTranscriptions() {
        return $.ajax({
            url: '/user_transcriptions',
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                console.log('Ответ сервера для транскрипций:', response); // Логирование полного ответа
                
                const transcriptionSelect = $('#audio_file_name');
                transcriptionSelect.empty().append('<option value="">-- Выберите транскрипции --</option>');
                
                if (response.transcription && response.transcription.length) {
                    response.transcription.forEach(transcription => {
                        transcriptionSelect.append(`<option value="${transcription.transcription_id}">${transcription.audio_name}</option>`);
                    });
                } else {
                    console.error('Транскрипции не найдены в ответе сервера.');
                }
            },
            error: function(xhr, status, error) {
                console.error('Ошибка загрузки транскрипций:', status, error);
            }
        });
    }
    

    function checkAutomaticPrompt() {
        return $.ajax({
            url: '/get_automatic_prompt',
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                if (response.prompt_name) {
                    $('#prompt_name').val(response.prompt_name);  // Автоматически выбираем промпт
                }
            },
            error: function(xhr, status, error) {
                console.log('Ошибка получения автоматического промпта:', error);
            }
        });
    }
});
