import os
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
import google.generativeai as genai
import sentence_transformers
import chromadb
import fitz  # PyMuPDF

# Cargar variables de entorno
load_dotenv()

# Configurar la API de Gemini
# Asegúrate de tener la variable de entorno GOOGLE_API_KEY en tu archivo .env
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Inicializar modelos y clientes
# Usaremos un modelo de embedding más pequeño y eficiente para la tarea de recuperación
embedding_model = sentence_transformers.SentenceTransformer('all-MiniLM-L6-v2')
# Modelo generativo para responder preguntas
generation_model = genai.GenerativeModel('gemini-1.5-flash')

# Inicializar ChromaDB
# Usaremos un cliente en memoria para simplicidad. No persistirá entre reinicios.
chroma_client = chromadb.Client()
# Crear una colección (o tabla) para nuestros documentos.
# Si la colección ya existe, la obtendrá en lugar de crear una nueva.
collection = chroma_client.get_or_create_collection(name="documentos")


# Inicializar la aplicación Flask
app = Flask(__name__)

@app.route('/')
def index():
    """
    Renderiza la página principal de la aplicación.
    """
    return render_template('index.html')

@app.route('/api/upload', methods=['POST'])
def api_upload():
    """
    API endpoint para subir un archivo, procesarlo y almacenarlo en la base de datos vectorial.
    """
    if 'file' not in request.files:
        return jsonify({"error": "No se encontró el archivo"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No se seleccionó ningún archivo"}), 400

    if file and file.filename.endswith('.pdf'):
        try:
            # Limpiar la colección antes de añadir un nuevo documento para mantenerlo simple
            print(f"Limpiando entradas antiguas para '{file.filename}' en la colección.")
            # Esto es una simplificación. En una app real, manejarías esto de forma más granular.
            ids_to_delete = collection.get(where={"source_file": file.filename})['ids']
            if ids_to_delete:
                collection.delete(ids=ids_to_delete)

            # Guardar temporalmente el archivo para procesarlo
            temp_dir = "temp"
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, file.filename)
            file.save(temp_path)

            # 1. Extraer texto del PDF
            doc = fitz.open(temp_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            os.remove(temp_path) # Limpiar el archivo temporal
            print(f"[DEBUG] Texto extraído: {len(text)} caracteres.")

            if not text.strip():
                print("[DEBUG] El PDF está vacío o no contiene texto.")
                return jsonify({"message": "El PDF está vacío o no contiene texto."} ), 400

            # 2. Dividir el texto en fragmentos (chunks)
            chunks = text.split('\n\n')
            chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
            print(f"[DEBUG] Número de chunks creados: {len(chunks)}")
            if chunks:
                print(f"[DEBUG] Ejemplo de chunk: '{chunks[0][:100]}...'")

            if not chunks:
                print("[DEBUG] No se generaron chunks, no hay nada que añadir a la BD.")
                return jsonify({"error": "No se pudo extraer contenido procesable del PDF."} ), 400

            # 3. Generar embeddings y metadatos para cada chunk
            doc_ids = [f"{file.filename}_{i}" for i in range(len(chunks))]
            metadatas = [{"source_file": file.filename} for _ in chunks]
            
            collection.add(
                embeddings=embedding_model.encode(chunks).tolist(),
                documents=chunks,
                metadatas=metadatas,
                ids=doc_ids
            )
            print(f"[DEBUG] Chunks añadidos a la colección. Total de items ahora: {collection.count()}\n")

            return jsonify({"message": f"Archivo '{file.filename}' procesado y añadido a la base de datos."} ), 200

        except Exception as e:
            print(f"[ERROR] {str(e)}")
            return jsonify({"error": f"Error procesando el archivo: {str(e)}"}), 500

    return jsonify({"error": "Formato de archivo no soportado. Por favor, sube un PDF."} ), 400


@app.route('/api/query', methods=['POST'])
def api_query():
    """
    API endpoint para recibir una pregunta, buscar en la base de datos vectorial
    y generar una respuesta usando Gemini.
    """
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"error": "Pregunta no proporcionada"}), 400

    query = data['query']
    print(f"\n[DEBUG] Recibida nueva pregunta: '{query}'")

    try:
        # 1. Buscar los chunks más relevantes en ChromaDB
        query_embedding = embedding_model.encode([query]).tolist()
        results = collection.query(
            query_embeddings=query_embedding,
            n_results=3
        )

        print(f"[DEBUG] Resultados de la búsqueda vectorial: {results['documents']}")

        if not results['documents'] or not results['documents'][0]:
            print("[DEBUG] La búsqueda no devolvió documentos.")
            return jsonify({"answer": "No encontré información relevante en los documentos para responder a tu pregunta."} )

        context = "\n\n".join(results['documents'][0])
        print(f"[DEBUG] Contexto enviado a Gemini: '{context[:200]}...'")

        # 2. Construir el prompt para Gemini
        prompt = f"""
        Basándote únicamente en el siguiente contexto extraído de un documento, responde a la pregunta.
        Si la respuesta no se encuentra en el contexto, di "No encontré información relevante en los documentos para responder a tu pregunta.".

        Contexto:
        ---
        {context}
        ---

        Pregunta: {query}

        Respuesta:
        """

        # 3. Generar la respuesta con Gemini
        response = generation_model.generate_content(prompt)
        print(f"[DEBUG] Respuesta de Gemini: '{response.text}'\n")

        return jsonify({"answer": response.text})

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return jsonify({"error": f"Error al generar la respuesta: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)