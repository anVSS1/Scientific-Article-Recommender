from neo4j import GraphDatabase
import pandas as pd
from tqdm import tqdm
import json

import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..")) # Goes up to VER 2/
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from backend_api.config import Config

class Neo4jEmbeddingLoader:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="anass2003"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def load_embeddings(self, articles_emb_file=r"C:\Users\VSS\Desktop\WebAPP\VER 2\data\embeddings\embeddings_articles.csv", concepts_emb_file=r"C:\Users\VSS\Desktop\WebAPP\VER 2\data\embeddings\embeddings_concepts.csv"):
        try:
            articles_emb = pd.read_csv(articles_emb_file)
            concepts_emb = pd.read_csv(concepts_emb_file)
        except Exception as e:
            print(f"Error loading CSV files: {e}")
            return

        def load_article_embeddings(tx):
            for _, row in tqdm(articles_emb.iterrows(), total=len(articles_emb), desc="Loading Article Embeddings"):
                try:
                    embedding = json.loads(row["hasAbstractEmbedding"]) if isinstance(row["hasAbstractEmbedding"], str) else row["hasAbstractEmbedding"]
                    if not isinstance(embedding, list) or len(embedding) != 768:
                        print(f"Invalid embedding for article {row['uri']}")
                        continue
                    tx.run(
                        """
                        MATCH (w:Work {uri: $uri})
                        SET w.hasAbstractEmbedding = $embedding
                        """,
                        uri=row["uri"], embedding=embedding
                    )
                except Exception as e:
                    print(f"Error loading article embedding for {row['uri']}: {e}")

        def load_concept_embeddings(tx):
            for _, row in tqdm(concepts_emb.iterrows(), total=len(concepts_emb), desc="Loading Concept Embeddings"):
                try:
                    embedding = json.loads(row["hasNameEmbedding"]) if isinstance(row["hasNameEmbedding"], str) else row["hasNameEmbedding"]
                    if not isinstance(embedding, list) or len(embedding) != 768:
                        print(f"Invalid embedding for concept {row['uri']}")
                        continue
                    tx.run(
                        """
                        MATCH (c:Concept {uri: $uri})
                        SET c.hasNameEmbedding = $embedding
                        """,
                        uri=row["uri"], embedding=embedding
                    )
                except Exception as e:
                    print(f"Error loading concept embedding for {row['uri']}: {e}")

        with self.driver.session() as session:
            session.execute_write(load_article_embeddings)
            session.execute_write(load_concept_embeddings)
        print("Embeddings loaded into Neo4j!")

if __name__ == "__main__":
    loader = Neo4jEmbeddingLoader(password="anass2003")
    try:
        loader.load_embeddings()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        loader.close()