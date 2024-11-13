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
                loadAnalysis();
            },
            error: function(xhr, status, error) {
                console.error('Ошибка проверки токена:', error);
                window.location.href = '/';
            }
        });
    }

    function loadAnalysis() {
        $.ajax({
            url: `/analysis/all?offset=${offset}&limit=${limit}`,
            type: 'GET',
            headers: {
                'Authorization': 'Bearer ' + token
            },
            success: function(response) {
                $('#loadingIndicator').hide();
                $('#analysissTable tbody').empty();
    
                if (response.length === 0) {
                    $('#analysissTable tbody').append('<tr><td colspan="4">Нет анализов.</td></tr>');
                }
    
                response.forEach(function(analysis, index) {
                    const rowNumber = offset + index + 1;  // Нумерация строк
                    
                    // Обрезка текста анализа, если он слишком длинный
                    const trimmedText = analysis.text.length > 100 ? analysis.text.substring(0, 100) + '...' : analysis.text;
    
                    const row = `<tr class="clickable-row" data-analysis-id="${analysis.analysis_id}">
                                    <td>${rowNumber}</td>
                                    <td>${trimmedText}</td>
                                    <td>${analysis.audio_file_name}</td>
                                    <td>${analysis.prompt_name}</td>
                                </tr>`;
                    $('#analysissTable tbody').append(row);
                });
    
                $('.clickable-row').on('click', function() {
                    const analysisId = $(this).data('analysis-id');
                    window.location.href = `/analysis/${analysisId}/view`;
                });
            },
            error: function(xhr, status, error) {
                $('#loadingIndicator').hide();
                console.error('Ошибка при загрузке анализа:', error);
            }
        });
    }
    
    

});
