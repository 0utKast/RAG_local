# Aplicación de Búsqueda Semántica (RAG) con Flask y LLMs

Este proyecto implementa una aplicación web de Búsqueda Semántica (Retrieval-Augmented Generation - RAG) que permite a los usuarios cargar documentos PDF y realizar preguntas en lenguaje natural para obtener respuestas basadas en el contenido de esos documentos.

La aplicación ofrece la flexibilidad de usar un modelo de lenguaje grande (LLM) remoto de alto rendimiento (Google Gemini) o un LLM que se ejecuta localmente para máxima privacidad (vía Ollama).

## Características

- Carga y procesamiento de documentos PDF.
- Extracción de texto y fragmentación (chunking) automática.
- Generación de embeddings semánticos para los documentos.
- Almacenamiento y búsqueda eficiente de vectores en ChromaDB.
- Interfaz de usuario intuitiva para subir archivos y realizar consultas.
- Selección en tiempo real entre Google Gemini (remoto) y Ollama (local) para la generación de respuestas.

## Tecnologías Utilizadas

### Backend

- **Python**: Lenguaje principal para el desarrollo del backend y la lógica de IA.
- **Flask**: Micro-framework web para la creación de la API RESTful.
- **Sentence-Transformers**: Para la generación de embeddings de texto (`all-MiniLM-L6-v2`).
- **ChromaDB**: Base de datos vectorial para el almacenamiento y consulta de embeddings.
- **PyMuPDF (fitz)**: Para la extracción eficiente de texto de archivos PDF.
- **Google Gemini (API)**: Opción de LLM remoto de alta calidad.
- **Ollama**: Permite ejecutar modelos de lenguaje como Llama 3 localmente para privacidad y control.

### Frontend

- **HTML, CSS y JavaScript (Vanilla)**: Interfaz de usuario sencilla y funcional.

## Arquitectura y Funcionamiento

La aplicación sigue una arquitectura cliente-servidor con dos flujos principales:

### Flujo de Carga de Documentos

1.  **Recepción en Flask**: El PDF se envía al backend.
2.  **Extracción de Texto**: PyMuPDF extrae el texto del PDF.
3.  **Fragmentación (Chunking)**: El texto se divide en fragmentos más pequeños.
4.  **Creación de Embeddings**: Cada fragmento se convierte en un vector numérico usando Sentence-Transformers.
5.  **Almacenamiento en ChromaDB**: Los vectores y el texto original se almacenan en la base de datos vectorial.

### Flujo de Consulta (Proceso RAG)

1.  **Envío de la Consulta**: La pregunta del usuario y la elección del LLM se envían al backend.
2.  **Embedding de la Consulta**: La pregunta se convierte en un vector.
3.  **Búsqueda por Similitud**: ChromaDB encuentra los 3 fragmentos de documento más relevantes (semánticamente similares) a la pregunta.
4.  **Construcción del Contexto y Prompt**: Los fragmentos recuperados forman un contexto que, junto con la pregunta, se usa para construir un prompt para el LLM.
5.  **Generación de Respuesta**: El prompt se envía al LLM seleccionado (Gemini o Ollama), que genera la respuesta.
6.  **Respuesta Final**: La respuesta se envía al frontend.

## El Papel Clave de la Base de Datos Vectorial

Las bases de datos vectoriales son fundamentales para la búsqueda semántica. A diferencia de las bases de datos tradicionales que buscan coincidencias exactas de palabras clave, una base de datos vectorial almacena representaciones matemáticas del significado (embeddings). Esto permite buscar por **concepto** en lugar de por palabra clave, encontrando fragmentos de texto cuyo significado es similar, incluso si no usan las mismas palabras.

## Cómo Usar la Aplicación

1.  **Requisitos**: Asegúrate de tener Python y Git instalados. Si planeas usar el modelo local, instala Ollama.
2.  **Clonar el Repositorio**: 
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <nombre_del_repositorio>
    ```
3.  **Instalar Dependencias**: 
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configurar API Key de Gemini**: Crea un archivo `.env` en la raíz del proyecto y añade tu clave de API de Gemini:
    ```
    GOOGLE_API_KEY=TU_API_KEY
    ```
5.  **Configurar Ollama (Opcional)**: Si deseas usar el modelo local, asegúrate de que el servicio de Ollama esté corriendo y de haber descargado el modelo `llama3` (o el que desees usar, ajustando `app.py` si es diferente):
    ```bash
    ollama pull llama3
    ```
6.  **Iniciar la Aplicación**: Ejecuta el script de inicio:
    ```bash
    start.bat
    ```
7.  **Acceder a la Aplicación**: Abre tu navegador y ve a `http://127.0.0.1:5000`.

¡Disfruta de tu aplicación de búsqueda semántica!