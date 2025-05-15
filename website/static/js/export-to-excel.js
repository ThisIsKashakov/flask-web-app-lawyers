// Функция для экспорта данных таблицы в Excel файл
function exportTableToExcel() {
    try {
        // Получаем таблицу
        const table = document.querySelector('.table');
        
        // Создаем массив для хранения данных
        const data = [];
        
        // Получаем заголовки (первые 9 колонок, исключая колонку Edit)
        const headers = Array.from(table.querySelectorAll('thead th'))
            .slice(0, 9)
            .map(th => th.textContent.trim());
        
        data.push(headers);
        
        // Получаем строки данных
        const rows = table.querySelectorAll('tbody tr');
        
        rows.forEach(row => {
            const rowData = Array.from(row.querySelectorAll('td'))
                .slice(0, 9) // Берем только первые 9 колонок, исключая колонку с кнопкой Edit
                .map(td => td.textContent.trim());
            
            data.push(rowData);
        });
        
        // Создаем рабочую книгу
        const workbook = XLSX.utils.book_new();
        const worksheet = XLSX.utils.aoa_to_sheet(data);
        
        // Добавляем лист в книгу
        XLSX.utils.book_append_sheet(workbook, worksheet, 'Court Schedules');
        
        // Генерируем файл и запускаем скачивание
        const excelBuffer = XLSX.write(workbook, { bookType: 'xlsx', type: 'array' });
        
        // Добавляем дату и время к имени файла
        const now = new Date();
        const dateTime = now.getFullYear() + '-' +
                      String(now.getMonth() + 1).padStart(2, '0') + '-' +
                      String(now.getDate()).padStart(2, '0') + '_' +
                      String(now.getHours()).padStart(2, '0') + '-' +
                      String(now.getMinutes()).padStart(2, '0') + '-' +
                      String(now.getSeconds()).padStart(2, '0');
        
        const fileName = `court_schedules_${dateTime}.xlsx`;
        saveExcelFile(excelBuffer, fileName);
        
        console.log('Export completed successfully');
    } catch (error) {
        console.error('Error exporting to Excel:', error);
        alert('An error occurred while exporting to Excel. Please try again.');
    }
}

// Функция для сохранения файла Excel
function saveExcelFile(buffer, fileName) {
    const blob = new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    
    // Создаем элемент ссылки для скачивания
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = fileName;
    
    // Добавляем ссылку в документ, кликаем по ней и удаляем
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    // Находим кнопку экспорта и добавляем обработчик события
    const exportButton = document.getElementById('exportToExcel');
    if (exportButton) {
        exportButton.addEventListener('click', exportTableToExcel);
        console.log('Export to Excel button initialized');
    } else {
        console.error('Export to Excel button not found');
    }
});