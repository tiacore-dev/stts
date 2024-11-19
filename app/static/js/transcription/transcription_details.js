$(document).ready(function() {
    const token = localStorage.getItem('access_token');
    const transcriptionId = window.location.pathname.split('/').pop();

    if (!token) {
        window.location.href = '/';
    }

    loadTranscriptionDetails(transcriptionId);

    function loadTranscriptionDetails(transcriptionId) {
        $('#loadingIndicator').show();
        $.ajax({
            url: `/api/transcription/${transcriptionId}`,
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                $('#transcriptionText').text(response.text);
                $('#transcriptionTokens').text(response.tokens);
                $('#audioFileName').text(response.audio_file_name);
                $('#loadingIndicator').hide();
            },
            error: function(xhr, status, error) {
                console.error('Ошибка при загрузке транскрипции:', error);
                alert('Не удалось загрузить транскрипцию.');
                $('#loadingIndicator').hide();
            }
        });
    }

    $('#backButton').on('click', function() {
        window.location.href = '/transcription_result';
    });
});
