# Tutorial: Creación de una App de Búsqueda Semántica (RAG)

## 1. Introducción

Este documento detalla la creación de una aplicación web de Búsqueda Semántica, también conocida como RAG (Retrieval-Augmented Generation). El objetivo de la aplicación es permitir a un usuario cargar sus propios documentos (en formato PDF) y realizar preguntas en lenguaje natural para obtener respuestas basadas únicamente en el contenido de dichos documentos.

La aplicación cuenta con una interfaz sencilla y permite al usuario elegir en tiempo real entre un modelo de lenguaje grande (LLM) remoto de alto rendimiento (Google Gemini) y un LLM que se ejecuta localmente para máxima privacidad (vía Ollama).

## 2. Tecnologías Utilizadas

A continuación se detallan las tecnologías elegidas para cada parte del proyecto y el porqué de su elección.

### Backend

- **Python**: 
  - **Por qué**: Es el lenguaje estándar de facto para aplicaciones de Inteligencia Artificial y Machine Learning, con un ecosistema de librerías inigualable para estas tareas.

- **Flask**:
  - **Por qué**: Es un micro-framework web para Python. Se eligió por su simplicidad y ligereza, permitiendo crear una API RESTful de forma rápida y sin la complejidad de frameworks más robustos, lo cual es ideal para un prototipo funcional.

- **Sentence-Transformers**:
  - **Por qué**: Esta librería de Hugging Face es la herramienta estándar para crear *embeddings* de texto de alta calidad. Un *embedding* es una representación numérica (un vector) del significado de un texto. Usamos el modelo `all-MiniLM-L6-v2` porque es ligero, rápido y ofrece un excelente rendimiento para tareas de búsqueda semántica en múltiples idiomas.

- **ChromaDB**:
  - **Por qué**: Es una base de datos vectorial de código abierto diseñada específicamente para aplicaciones de IA. La elegimos porque es extremadamente fácil de poner en marcha (puede correr en memoria sin instalación) y se integra a la perfección con el resto de herramientas de IA, simplificando enormemente el almacenamiento y la consulta de vectores.

- **PyMuPDF (fitz)**:
  - **Por qué**: Para poder leer el contenido de los archivos PDF, necesitábamos una librería eficiente y rápida. PyMuPDF es una de las más performantes para la extracción de texto de PDFs en Python.

- **Google Gemini (API)**:
  - **Por qué**: Representa la opción de LLM remoto de alta calidad. Usar la API de Gemini nos da acceso a un modelo de generación de texto de última generación sin necesidad de tener hardware especializado, garantizando respuestas coherentes y bien redactadas.

- **Ollama (Local)**:
  - **Por qué**: Proporciona la alternativa de privacidad y control total. Al permitirnos ejecutar modelos de lenguaje como Llama 3 directamente en nuestra máquina, Ollama asegura que nuestros datos nunca salgan de nuestro entorno local. Es una opción fantástica para trabajar con documentos sensibles.

### Frontend

- **HTML, CSS y JavaScript (Vanilla)**:
  - **Por qué**: Para la interfaz de usuario, se optó por no usar frameworks complejos como React o Vue. Una estructura simple con HTML, estilos básicos con CSS y lógica de cliente con JavaScript "vanilla" es más que suficiente para la funcionalidad requerida (subir archivos y mostrar resultados), permitiéndonos centrarnos en la lógica del backend, que es el núcleo del proyecto.

## 3. Arquitectura y Funcionamiento

La aplicación se divide en dos flujos principales: el de carga de documentos y el de consulta.

### Flujo de Carga de Documentos

Cuando un usuario sube un archivo PDF, ocurren los siguientes pasos:

1.  **Recepción en Flask**: El frontend envía el archivo al endpoint `/api/upload` del backend.
2.  **Extracción de Texto**: Usando PyMuPDF, el backend abre el PDF y extrae todo el texto plano de sus páginas.
3.  **Fragmentación (Chunking)**: El texto completo se divide en fragmentos más pequeños o "chunks". En nuestro caso, usamos una estrategia simple de dividir por párrafos (dobles saltos de línea). Esto es crucial, ya que es más eficiente buscar sobre pequeños fragmentos relevantes que sobre un documento entero.
4.  **Creación de Embeddings**: Cada chunk de texto se pasa al modelo `Sentence-Transformer`, que lo convierte en un vector numérico. Este vector representa el significado semántico del chunk.
5.  **Almacenamiento en ChromaDB**: El backend almacena cada vector en la base de datos vectorial, junto con el texto original del chunk que representa. Ahora, el contenido del documento está "indexado" y listo para ser consultado.

### Flujo de Consulta (El Proceso RAG)

Cuando un usuario escribe una pregunta, se activa el flujo de RAG:

1.  **Envío de la Consulta**: El frontend envía la pregunta y la elección del LLM (Gemini u Ollama) al endpoint `/api/query`.
2.  **Embedding de la Consulta**: El backend toma la pregunta del usuario y, usando el mismo modelo `Sentence-Transformer`, la convierte también en un vector.
3.  **Búsqueda por Similitud (El Papel Clave de la BD Vectorial)**: El vector de la pregunta se usa para consultar ChromaDB. La base de datos no busca palabras clave, sino que busca los vectores de los chunks que están "más cerca" espacialmente del vector de la pregunta. Esta cercanía espacial equivale a similitud semántica. La base de datos devuelve los 3 chunks más relevantes.
4.  **Construcción del Contexto y Prompt**: El texto de los chunks recuperados se une para formar un "contexto". Este contexto, junto con la pregunta original del usuario, se inserta en una plantilla de prompt. El prompt instruye al LLM para que responda a la pregunta basándose *únicamente* en el contexto proporcionado.
5.  **Generación de Respuesta**: El prompt final se envía al LLM seleccionado (Gemini o Ollama).
6.  **Respuesta Final**: El LLM genera una respuesta sintetizando la información encontrada en el contexto y la devuelve al backend, que a su vez la envía al frontend para que el usuario la vea.

## 4. El Papel Clave de la Base de Datos Vectorial

El componente que hace "inteligente" a nuestra aplicación es la base de datos vectorial, y es fundamental entender por qué.

Una base de datos tradicional (como SQL) busca coincidencias exactas. Si buscas "coche", encontrará documentos con la palabra "coche", pero no aquellos que hablen de "automóvil" o "vehículo".

Una **base de datos vectorial** funciona de manera diferente. No almacena el texto directamente para buscarlo, sino que almacena su **representación matemática del significado** (el embedding o vector).

Imagina un espacio gigante en 3D. Cuando convertimos "coche", "automóvil" y "vehículo" en vectores, estos se sitúan como puntos muy cercanos entre sí en ese espacio. La palabra "planeta", sin embargo, se situaría en un punto muy lejano.

Cuando nuestra aplicación busca los "vecinos más cercanos" al vector de la pregunta del usuario, está encontrando los fragmentos de texto cuyo significado es más similar, sin importar si usan exactamente las mismas palabras. Esta capacidad de **buscar por concepto en lugar de por palabra clave** es la esencia de la búsqueda semántica y lo que permite que el sistema RAG encuentre el contexto correcto para responder a las preguntas del usuario de manera efectiva.

## 5. Cómo Usar la Aplicación

1.  **Requisitos**: Tener Python y Git instalados. Tener Ollama instalado si se desea usar el modelo local.
2.  **Clonar el Repositorio**: `git clone <URL_DEL_REPOSITORIO>`
3.  **Instalar Dependencias**: `pip install -r requirements.txt`
4.  **Crear Archivo de Entorno**: Crear un archivo `.env` en la raíz y añadir la clave de API de Gemini: `GOOGLE_API_KEY=TU_API_KEY`.
5.  **Ejecutar Ollama**: Si se usa el modelo local, asegurarse de que el servicio de Ollama esté corriendo y de haber descargado un modelo (ej: `ollama pull llama3`).
6.  **Iniciar la Aplicación**: Ejecutar el archivo `start.bat`.
7.  **Usar**: Abrir `http://127.0.0.1:5000` en el navegador.
