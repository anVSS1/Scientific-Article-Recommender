"""
SciBERT Embedding Generator for Scientific Articles

This script generates semantic embeddings for scientific articles and concepts
using the SciBERT model (Scientific BERT), specifically designed for scientific text.

SciBERT Features:
- Pre-trained on scientific literature corpus
- 768-dimensional embeddings optimized for scientific terminology
- Better performance on scientific text compared to general BERT models

Process:
1. Load processed articles and concepts from JSON files
2. Generate embeddings for article abstracts and titles
3. Generate embeddings for concept names
4. Save embeddings as CSV files for use in recommendation engine

Output:
- embeddings_articles.csv: Article embeddings with metadata
- embeddings_concepts.csv: Concept embeddings with metadata

Requirements:
- transformers library with SciBERT model
- torch for GPU acceleration (optional)
- pandas for data manipulation
"""

import pandas as pd
import numpy as np
from transformers import AutoTokenizer, AutoModel
import torch
from tqdm import tqdm

import re
import os
import json
import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..")) # Goes up to VER 2/
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from backend_api.config import Config

class EmbeddingGenerator:
    """
    SciBERT-based embedding generator for scientific text.
    
    This class handles the generation of semantic embeddings using the SciBERT model,
    which is specifically trained on scientific literature and performs better than
    general BERT models on scientific text.
    
    Attributes:
        tokenizer: SciBERT tokenizer for text preprocessing
        model: SciBERT model for embedding generation
        device: Computing device (CUDA GPU if available, else CPU)
    """
    
    def __init__(self):
        """Initialize the SciBERT model and tokenizer."""
        print("🔧 Initializing SciBERT model...")
        self.tokenizer = AutoTokenizer.from_pretrained("allenai/scibert_scivocab_uncased")
        self.model = AutoModel.from_pretrained("allenai/scibert_scivocab_uncased")
        
        # Use GPU if available for faster processing
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)
        print(f"✅ Model loaded on device: {self.device}")

    def get_embedding(self, text, max_length=512):
        """
        Generate SciBERT embedding for given text.
        
        Args:
            text (str): Input text to embed
            max_length (int): Maximum token length for truncation
            
        Returns:
            numpy.ndarray: 768-dimensional embedding vector
        """
        if not text or not isinstance(text, str) or pd.isna(text):
            return np.zeros(768)
        inputs = self.tokenizer(text, return_tensors="pt", max_length=max_length, truncation=True, padding=True)
        inputs = {k: v.to(self.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze().cpu().numpy()

    def generate_and_save_embeddings(self, articles_file, concepts_file, output_dir=r"C:\Users\VSS\Desktop\WebAPP\VER 2\data\embeddings"):
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            # Articles
            articles = pd.read_json(articles_file)
            article_embeddings = []
            for _, row in tqdm(articles.iterrows(), total=len(articles), desc="Generating Article Embeddings"):
                w_id = re.sub(r'\W+', '_', str(row["id"]))
                text = str(row["abstract"]) if row["abstract"] and isinstance(row["abstract"], str) else str(row["title"])
                abstract_emb = self.get_embedding(text).tolist()
                article_embeddings.append({
                    "uri": f"http://www.semanticweb.org/vss/ontology/scientific_recommender#{w_id}",
                    "hasAbstractEmbedding": abstract_emb
                })
            article_df = pd.DataFrame(article_embeddings)
            article_df.to_csv(f"{output_dir}/embeddings_articles.csv", index=False)
            print(f"Saved {len(article_embeddings)} article embeddings to {output_dir}/embeddings_articles.csv")

            # Concepts
            concepts = pd.read_json(concepts_file)
            concept_embeddings = []
            for _, row in tqdm(concepts.iterrows(), total=len(concepts), desc="Generating Concept Embeddings"):
                c_id = re.sub(r'\W+', '_', str(row["id"]))
                name = str(row["name"]) if row["name"] and isinstance(row["name"], str) else ""
                concept_emb = self.get_embedding(name).tolist()
                concept_embeddings.append({
                    "uri": f"http://www.semanticweb.org/vss/ontology/scientific_recommender#{c_id}",
                    "hasNameEmbedding": concept_emb
                })
            concept_df = pd.DataFrame(concept_embeddings)
            concept_df.to_csv(f"{output_dir}/embeddings_concepts.csv", index=False)
            print(f"Saved {len(concept_embeddings)} concept embeddings to {output_dir}/embeddings_concepts.csv")
        except Exception as e:
            print(f"Error generating embeddings: {e}")

if __name__ == "__main__":
    articles_file = r"C:\Users\VSS\Desktop\WebAPP\VER 2\data\processed_articles.json"
    concepts_file = r"C:\Users\VSS\Desktop\WebAPP\VER 2\data\processed_concepts.json"
    generator = EmbeddingGenerator()
    generator.generate_and_save_embeddings(articles_file, concepts_file)