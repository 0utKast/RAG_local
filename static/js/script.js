document.addEventListener('DOMContentLoaded', () => {
    const uploadButton = document.getElementById('upload-button');
    const fileInput = document.getElementById('file-input');
    const uploadStatus = document.getElementById('upload-status');

    const queryButton = document.getElementById('query-button');
    const queryInput = document.getElementById('query-input');
    const queryResult = document.getElementById('query-result');

    // --- Manejador de Subida de Archivos ---
    uploadButton.addEventListener('click', async () => {
        if (fileInput.files.length === 0) {
            uploadStatus.textContent = 'Por favor, selecciona un archivo primero.';
            uploadStatus.style.color = 'red';
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append('file', file);

        uploadStatus.textContent = 'Subiendo y procesando archivo...';
        uploadStatus.style.color = 'blue';

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData,
            });

            const result = await response.json();

            if (response.ok) {
                uploadStatus.textContent = result.message;
                uploadStatus.style.color = 'green';
            } else {
                uploadStatus.textContent = `Error: ${result.error}`;
                uploadStatus.style.color = 'red';
            }
        } catch (error) {
            uploadStatus.textContent = `Error de red: ${error.message}`;
            uploadStatus.style.color = 'red';
        }
    });

    // --- Manejador de Preguntas ---
    queryButton.addEventListener('click', async () => {
        const query = queryInput.value;
        const llmChoice = document.getElementById('llm-selector').value;

        if (!query.trim()) {
            queryResult.innerHTML = '<p style="color: red;">Por favor, escribe una pregunta.</p>';
            return;
        }

        queryResult.innerHTML = '<p>Buscando respuesta...</p>';

        try {
            const response = await fetch('/api/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query, llm: llmChoice }),
            });

            const result = await response.json();

            if (response.ok) {
                // Reemplazar saltos de línea con <br> para una correcta visualización en HTML
                const formattedAnswer = result.answer.replace(/\n/g, '<br>');
                queryResult.innerHTML = `<p>${formattedAnswer}</p>`;
            } else {
                queryResult.innerHTML = `<p style="color: red;">Error: ${result.error}</p>`;
            }
        } catch (error) {
            queryResult.innerHTML = `<p style="color: red;">Error de red: ${error.message}</p>`;
        }
    });
});
