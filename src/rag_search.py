import psycopg2
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# 1. Connect to your local PostgreSQL data warehouse
def fetch_warehouse_data():
    try:
        conn = psycopg2.connect(
            dbname="medical_warehouse",   
            user="postgres",           
            password="MyRealPassword123", 
            host="localhost",
            port="5432"
        )
        cursor = conn.cursor()
        
        query = """
            SELECT c.channel_name, f.detected_objects 
            FROM main.fct_image_detections f
            JOIN main.dim_channels c ON f.channel_key = c.channel_key;
        """
        cursor.execute(query)
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"\n[ERROR] Database connection failed: {e}")
        return []

# 2. Extract database logs and build the FAISS vector index
def build_rag_system():
    print("Fetching warehouse data from PostgreSQL...")
    data = fetch_warehouse_data()
    
    if not data:
        print("No records retrieved from the database. System cannot start.")
        return None, None, None
    
    documents = []
    for row in data:
        channel, objects = row
        object_list = objects if objects and objects.strip() != "" else "none"
        text_representation = f"Channel: {channel} | Detected objects: {object_list}."
        documents.append(text_representation)
        
    print(f"Loaded {len(documents)} context strings. Initializing sentence-transformer model...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    print("Generating vector embeddings...")
    embeddings = model.encode(documents, show_progress_bar=False)
    
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(np.array(embeddings).astype('float32'))
    
    print("FAISS vector index built and loaded successfully!")
    return model, index, documents

# 3. Query the semantic index and generate an LLM context prompt
def chat_with_warehouse(query_text, model, index, documents, k=3):
    if not model or not index:
        return
        
    query_vector = model.encode([query_text]).astype('float32')
    distances, indices = index.search(query_vector, k)
    
    # Package retrieved facts into an LLM context block
    context_facts = []
    for idx in indices[0]:
        if idx < len(documents):
            context_facts.append(documents[idx])
            
    context_str = "\n".join([f"- {fact}" for fact in context_facts])
    
    # This constructs the prompt context that would be sent straight to an API (OpenAI/Ollama/HuggingFace)
    print("\n" + "="*50)
    print(f"❓ USER QUESTION: {query_text}")
    print("="*50)
    print("🤖 GENERATED CONTEXT PROMPT FOR LLM:")
    print("You are an expert AI assistant answering questions about Ethiopian medical data telemetry.")
    print("Based strictly on the following database records retrieved via semantic vector search:")
    print(context_str)
    print(f"\nAnswer the user's question: '{query_text}' directly and accurately.")
    print("="*50 + "\n")

if __name__ == "__main__":
    model, index, documents = build_rag_system()
    
    if model and index:
        print("\n🚀 RAG Chat System Ready! Type your question below (or type 'exit' to quit).")
        while True:
            user_input = input("\nAsk something about the warehouse data: ")
            if user_input.lower() in ['exit', 'quit']:
                print("Exiting RAG system. Goodbye!")
                break
            if user_input.strip() == "":
                continue
            chat_with_warehouse(user_input, model, index, documents)