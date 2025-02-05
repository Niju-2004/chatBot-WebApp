import faiss
print("FAISS version:", faiss.__version__)


index_path = r"D:\Rag-Vector-DB\DB_Storage\vectors_faiss.index"
index = faiss.read_index(index_path)

print(f"🔍 FAISS index contains {index.ntotal} entries.")
