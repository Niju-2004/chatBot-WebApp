import faiss
import json
import logging
import sys
from sentence_transformers import SentenceTransformer

# Set up logging
logging.basicConfig(level=logging.INFO, filename="chatbot_errors.log")

# Load embedding model
sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

def load_content():
    """Load content data from JSON."""
    try:
        with open(r"D:\Rag-Vector-DB\DB_Storage\content.json", 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Error loading content JSON: {e}")
        return {}

def load_faiss_index():
    """Load FAISS index file."""
    try:
        return faiss.read_index(r"D:\Rag-Vector-DB\DB_Storage\vectors_faiss.index")
    except Exception as e:
        logging.error(f"Error loading FAISS index: {e}")
        return None

def query_system(query, model, index, content, top_k=3):
    """Query the FAISS index and retrieve relevant content from content.json."""
    # Generate query embedding
    query_embedding = model.encode([query]).astype('float32')

    # Search FAISS index
    D, I = index.search(query_embedding, k=top_k)

    # 🔹 Debugging output
    print(f"\n🔍 FAISS Search Results:")
    print(f"   - Indices: {I}")
    print(f"   - Distances: {D}")

    relevant_contexts = []
    
    for idx, label in enumerate(I[0]):
        if label == -1:
            print(f"⚠️ No relevant match found for '{query}'.")
            continue  # Skip invalid indices
        
        content_key = str(label)  # Convert index to string to match JSON keys
        
        if content_key in content:
            retrieved_text = content[content_key]
            
            # Extract relevant parts (modify based on your dataset structure)
            sections = retrieved_text.split(". ")
            disease_name = sections[0] if len(sections) > 0 else "Unknown Disease"
            symptoms = sections[2] if len(sections) > 2 else "No symptoms provided"
            treatment = sections[-1] if len(sections) > 3 else "No treatment provided"

            # Print formatted response
            print("\n🌿 **Veterinary Recommendation:**")
            print(f"🐄 **Disease:** {disease_name}")
            print(f"⚠️ **Symptoms:** {symptoms}")
            print(f"💊 **Treatment:** {treatment}")

            relevant_contexts.append(retrieved_text)

    if not relevant_contexts:
        print("\n❌ No relevant data found. Try rephrasing your question.")

    return relevant_contexts



def main():
    """Main function to process user queries."""
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
        content = load_content()
        index = load_faiss_index()

        if index is None or not content:
            print("Error: FAISS index or content data is missing.")
            return
        
        relevant_contexts = query_system(query, sentence_model, index, content)
        
        if relevant_contexts:
            print("\nRelevant Contexts:")
            for context in relevant_contexts:
                print(context)  # Print the full text of the relevant row
        else:
            print("\n❌ No relevant data found for the query.")
    else:
        print("Please provide a query as a command-line argument.")

if __name__ == "__main__":
    main()