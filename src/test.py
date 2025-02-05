import json
import faiss
import numpy as np
import sys
import asyncio
from sentence_transformers import SentenceTransformer

# Define file paths
content_path = r"D:\Rag-Vector-DB\DB_Storage\content.json"
index_path = r"D:\Rag-Vector-DB\DB_Storage\vectors_faiss.index"

def load_content():
    """Load the JSON content file."""
    try:
        with open(content_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        print("✅ Content JSON loaded successfully.")
        return content
    except Exception as e:
        print(f"❌ Error loading content JSON: {e}")
        return None

def load_faiss_index():
    """Load the FAISS index file."""
    try:
        index = faiss.read_index(index_path)
        print("✅ FAISS index loaded successfully.")
        return index
    except Exception as e:
        print(f"❌ Error loading FAISS index: {e}")
        return None

def test_faiss_search(index, content):
    """Perform a test FAISS search and validate content retrieval."""
    if index is None:
        print("❌ FAISS index not loaded. Skipping test.")
        return

    # Get FAISS index dimension
    faiss_dimension = index.d
    print(f"📏 FAISS index dimension: {faiss_dimension}")

    # Check how many vectors are stored in FAISS
    num_vectors = index.ntotal
    print(f"📊 FAISS index contains {num_vectors} stored vectors.")

    if num_vectors == 0:
        print("⚠️ Warning: FAISS index is empty! No stored embeddings found.")
        return

    # Generate a test vector with correct shape (comparing a random vector)
    test_vector = np.random.rand(1, faiss_dimension).astype('float32')
    print(f"🧪 Generated test vector shape: {test_vector.shape}")

    try:
        # Run FAISS search
        D, I = index.search(test_vector, k=3)  # Retrieve top 3 results
        print(f"🔍 FAISS Raw Search Output: D={D}, I={I}")

        if len(I[0]) == 0 or I[0][0] == -1:
            print("❌ FAISS search returned no valid results. No nearest neighbors found.")
            return

        # Retrieve content for each index
        for retrieved_index in I[0]:
            if retrieved_index == -1:
                print(f"⚠️ FAISS returned an invalid index: {retrieved_index}")
                continue

            retrieved_key = str(retrieved_index)
            if retrieved_key in content:
                print(f"✅ Retrieved content for index {retrieved_index}: {content[retrieved_key]}")
            else:
                print(f"❌ Error: Retrieved index {retrieved_index} not found in content JSON.")
    except Exception as e:
        print(f"❌ Error searching FAISS index: {e}")

def rebuild_faiss_index():
    """Rebuild and save the FAISS index if it is empty."""
    print("⚙️ Rebuilding FAISS index...")

    # Load content
    content = load_content()
    if not content:
        print("❌ Cannot rebuild FAISS: Content JSON not loaded.")
        return

    # Load sentence transformer model
    sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')

    # Extract text for embeddings
    texts = [content[key]['disease'] + " " + content[key]['treatment'] for key in content]

    # Generate embeddings
    embeddings = np.array(sentence_model.encode(texts), dtype='float32')

    # Create FAISS index
    d = embeddings.shape[1]  # Get embedding dimension
    index = faiss.IndexFlatL2(d)  
    index.add(embeddings)  # Add embeddings

    # Save FAISS index
    faiss.write_index(index, index_path)
    print("✅ FAISS index rebuilt and saved.")

async def main():
    """Main function to test FAISS index and JSON content."""
    content = load_content()
    index = load_faiss_index()

    if content and index:
        test_faiss_search(index, content)
        
        # Check if FAISS is empty, then rebuild
        if index.ntotal == 0:
            rebuild_faiss_index()
    else:
        print("❌ Failed to load FAISS index or JSON content. Check file paths.")

if __name__ == "__main__":
    asyncio.run(main())
