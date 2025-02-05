import os
import pandas as pd
import numpy as np
import json
import hnswlib  # ✅ Use HNSW instead of FAISS
import logging
from sentence_transformers import SentenceTransformer

logging.basicConfig(level=logging.INFO)

def clean_dataset(df):
    """Clean the dataset by removing unwanted characters and handling missing values."""
    if 'Cause' in df.columns:
        df['Cause'] = df['Cause'].replace(r'=CONCATENATE\(.*\)', '', regex=True)
    df = df.fillna('')  # Fill missing values with empty strings
    return df

def read_excel(file_path):
    """Read and preprocess the Excel file."""
    df = pd.read_excel(file_path)
    df = clean_dataset(df)

    text_data = []
    for _, row in df.iterrows():
        row_text = (
            f"Disease: {row.get('Disease Name', '')}. "
            f"Animal: {row.get('Type of Animal', '')}. "
            f"Symptoms: {row.get('Symptoms', '')}. "
            f"Cause: {row.get('Cause', '')}. "
            f"Ingredients: {row.get('Incredients', '')}. "
            f"Treatment: {row.get('Treatment', '')}."
        )
        text_data.append(row_text)
    return text_data

def text_to_vector(text_data, model, batch_size=32):
    """Convert text data to embeddings in batches."""
    embeddings = []
    for i in range(0, len(text_data), batch_size):
        batch = text_data[i:i + batch_size]
        batch_embeddings = model.encode(batch, convert_to_tensor=False)
        embeddings.extend(batch_embeddings)
    return np.array(embeddings).astype('float32'), text_data

def store_in_hnsw(vectors, text_chunks, output_index, content_path):
    """Store embeddings in an HNSW index."""
    num_elements, dimension = vectors.shape
    index = hnswlib.Index(space='cosine', dim=dimension)  # ✅ Use Cosine Similarity

    index.init_index(max_elements=num_elements, ef_construction=200, M=16)
    index.add_items(vectors, np.arange(num_elements))  # ✅ Add vectors with unique IDs

    # Save the HNSW index
    index.save_index(output_index)
    logging.info(f"HNSW index saved to {output_index}")

    # Save text chunks for reference
    content_data = {str(i): text_chunks[i] for i in range(len(text_chunks))}
    with open(content_path, 'w', encoding='utf-8') as f:
        json.dump(content_data, f, indent=4)
    logging.info(f"Content data saved to {content_path}")

if __name__ == "__main__":
    excel_file = r"D:\Rag-Vector-DB\assets\RPP_Dataset - Copy.xlsx"
    output_index = r"D:\Rag-Vector-DB\DB_Storage\DbHNSW\vectors_hnswlib.bin"
    content_path = r"D:\Rag-Vector-DB\DB_Storage\DbHNSW\contentHNSW.json"

    model = SentenceTransformer('all-MiniLM-L6-v2')
    excel_text_data = read_excel(excel_file)
    vectors, text_chunks = text_to_vector(excel_text_data, model)
    store_in_hnsw(vectors, text_chunks, output_index, content_path)
    logging.info("Process completed successfully!")
