$(document).ready(function() {
    const token = localStorage.getItem('access_token');
    const analysisId = window.location.pathname.split('/').pop();

    if (!token) {
        window.location.href = '/';
    }

    loadTranscriptionDetails(analysisId);

    function loadTranscriptionDetails(analysisId) {
        $('#loadingIndicator').show();
        $.ajax({
            url: `/api/analysis/${analysisId}`,
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                $('#analysisText').text(response.text);
                $('#analysisTokens').text(response.tokens);
                $('#audioFileName').text(response.audio_file_name);
                $('#promptName').text(response.prompt_name);
                $('#loadingIndicator').hide();
            },
            error: function(xhr, status, error) {
                console.error('Ошибка при загрузке анализа:', error);
                alert('Не удалось загрузить транскрипцию.');
                $('#loadingIndicator').hide();
            }
        });
    }

    $('#backButton').on('click', function() {
        window.location.href = '/analysis_result';
    });
});
