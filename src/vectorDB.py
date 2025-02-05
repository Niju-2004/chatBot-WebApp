import os
import pandas as pd
import numpy as np
import json
import faiss
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
    """Read and preprocess the Excel file into structured data."""
    df = pd.read_excel(file_path)
    df = clean_dataset(df)
    
    structured_data = []
    for _, row in df.iterrows():
        entry = {
            "disease": row.get('Disease Name', 'Unknown'),
            "animal": row.get('Type of Animal', 'Unknown'),
            "symptoms": row.get('Symptoms', 'No symptoms provided'),
            "treatment": row.get('Treatment', 'No treatment available'),
            "ingredients": row.get('Incredients', 'No ingredients listed')
        }
        structured_data.append(entry)
    return structured_data

def text_to_vector(text_data, model, batch_size=32):
    """Convert text data to embeddings in batches."""
    text_strings = [
        f"Disease: {entry['disease']}. Animal: {entry['animal']}. "
        f"Symptoms: {entry['symptoms']}. Treatment: {entry['treatment']}. "
        f"Ingredients: {entry['ingredients']}."
        for entry in text_data
    ]
    
    embeddings = []
    for i in range(0, len(text_strings), batch_size):
        batch = text_strings[i:i + batch_size]
        batch_embeddings = model.encode(batch, convert_to_tensor=False)
        embeddings.extend(batch_embeddings)
    
    return np.array(embeddings).astype('float32'), text_data

def store_in_faiss(vectors, structured_data, output_index, content_path):
    """Store embeddings in a FAISS index and save structured content."""
    dimension = vectors.shape[1]
    index = faiss.IndexFlatL2(dimension)  # FlatL2 index
    index.add(vectors)  # No training needed

    faiss.write_index(index, output_index)
    logging.info(f"FAISS index saved to {output_index}")

    # Save structured content with index keys
    content_data = {str(i): structured_data[i] for i in range(len(structured_data))}
    with open(content_path, 'w', encoding='utf-8') as f:
        json.dump(content_data, f, indent=4)
    logging.info(f"Content data saved to {content_path}")

if __name__ == "__main__":
    excel_file = r"D:\chatBot-WebApp\assets\RPP_Dataset - Copy.xlsx"
    output_index = r"D:\chatBot-WebApp\DB_Storage\vectors_faiss.index"
    content_path = r"D:\chatBot-WebApp\DB_Storage\content.json"

    model = SentenceTransformer('all-MiniLM-L6-v2')
    structured_data = read_excel(excel_file)
    vectors, text_chunks = text_to_vector(structured_data, model)
    store_in_faiss(vectors, structured_data, output_index, content_path)
    logging.info("Process completed successfully!")