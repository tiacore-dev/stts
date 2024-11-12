$(document).ready(function() {
    const token = localStorage.getItem('jwt_token');
    let offset = 0;
    const limit = 10;

    if (!token) {
        window.location.href = '/';
    } else {
        $.ajax({
            url: '/protected',
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                loadTranscriptions();
            },
            error: function(xhr, status, error) {
                console.error('Ошибка проверки токена:', error);
                window.location.href = '/';
            }
        });
    }

    function loadTranscriptions() {
        $.ajax({
            url: `/transcription/all?offset=${offset}&limit=${limit}`,
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                $('#loadingIndicator').hide();
                $('#transcriptionsTable tbody').empty();
    
                if (response.length === 0) {
                    $('#transcriptionsTable tbody').append('<tr><td colspan="2">Нет транскрипций.</td></tr>');
                }
    
                response.forEach(function(transcription, index) {
                    const rowNumber = offset + index + 1;  // Нумерация строк
                    
                    // Обрезка текста транскрипции, если он слишком длинный
                    const trimmedText = transcription.text.length > 100 ? transcription.text.substring(0, 100) + '...' : transcription.text;
    
                    const row = `<tr class="clickable-row" data-transcription-id="${transcription.transcription_id}">
                                    <td>${rowNumber}</td>
                                    <td>${trimmedText}</td>
                                    <td>${transcription.audio_file_name}</td>
                                </tr>`;
                    $('#transcriptionsTable tbody').append(row);
                });
    
                $('.clickable-row').on('click', function() {
                    const transcriptionId = $(this).data('transcription-id');
                    window.location.href = `/transcription/${transcriptionId}/view`;
                });
            },
            error: function(xhr, status, error) {
                $('#loadingIndicator').hide();
                console.error('Ошибка при загрузке транскрипций:', error);
            }
        });
    }
    
    

});
