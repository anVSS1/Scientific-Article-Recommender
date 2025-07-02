# Configuration file for the Scientific Article Recommender
# Copy this file to config.py and update with your actual values

# Neo4j Database Configuration
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "your_password_here"

# Flask Configuration
FLASK_DEBUG = True
FLASK_PORT = 5050

# SciBERT Model Configuration
SCIBERT_MODEL = "allenai/scibert_scivocab_uncased"

# Data Paths
DATA_DIR = "data"
EMBEDDINGS_DIR = "data/embeddings"
CLEANED_DATA_DIR = "data/cleaned data"
FETCHED_DATA_DIR = "data/fetched data"

# Recommendation Engine Settings
EMBEDDING_DIMENSION = 768
DEFAULT_RECOMMENDATIONS = 10
CONTENT_WEIGHT = 0.6
ONTOLOGY_WEIGHT = 0.4
