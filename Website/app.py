"""
Scientific Article Recommender - Flask Web Application

This is the main Flask application that provides a web interface for the 
Scientific Article Recommendation System. It integrates with Neo4j graph database
and provides both topic-based search and personalized recommendations.

Features:
- Topic-based article search using semantic similarity
- Personalized recommendations based on user profiles
- Ontology exploration for scientific concepts
- Real-time article details and metadata

Author: Scientific Article Recommender Team
Dependencies: Flask, Neo4j, recommendation engine
"""

from flask import Flask, render_template, request, jsonify
from neo4j import GraphDatabase
import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)
from backend.reco import RecommendationEngine

# Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "your_password_here")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5050))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "True").lower() == "true"

app = Flask(__name__)
engine = RecommendationEngine(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)
neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

@app.route('/')
def index():
    """Render the index page."""
    return render_template('index.html')

@app.route('/ontology')
def ontology():
    """Render the ontology exploration page."""
    return render_template('ontology.html')

@app.route('/users', methods=['GET'])
def get_users():
    """Retrieve the list of users from the database."""
    try:
        with neo4j_driver.session() as session:
            result = session.run("MATCH (u:User) RETURN u.has_id AS user_id")
            users = [record["user_id"] for record in result]
        return jsonify(users)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['POST'])
def search():
    """Handle the search request for topic-based article search."""
    try:
        data = request.get_json()
        topic = data.get('topic', 'Neural Networks')
        embeddings_file = "data/embeddings/embeddings_articles.csv"
        concepts_embeddings_file = "data/embeddings/embeddings_concepts.csv"
        
        # ADD DEBUG LOGGING:
        print(f"Search request for topic: {topic}")
        recommendations = engine.get_search_recommendations(topic, embeddings_file, concepts_embeddings_file)
        print(f"Found {len(recommendations)} recommendations")
        
        return jsonify(recommendations)
    except Exception as e:
        print(f"Search error: {str(e)}")  # ADD THIS
        return jsonify({"error": str(e)}), 500

@app.route('/recommend', methods=['POST'])
def recommend():
    """Handle the recommend request for personalized article recommendations."""
    try:
        data = request.get_json()
        user_id = data.get('user_id', 'User_0')
        topic = data.get('topic', 'Neural Networks')
        search_query = data.get('search_query', '')
        recommendations = engine.get_recommendations(user_id, topic, search_query)
        return jsonify(recommendations)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/article/<path:uri>', methods=['GET'])
def get_article(uri):
    """Retrieve the detailed information of a specific article."""
    try:
        # Decode the URI to handle any encoding
        decoded_uri = uri.replace('%2F', '/').replace('%23', '#')
        with neo4j_driver.session() as session:
            result = session.run(
                """
                MATCH (w:Work {uri: $uri})
                OPTIONAL MATCH (w)-[:hasAuthor]->(a:Author)
                OPTIONAL MATCH (w)-[:hasTopic|hasConcept]->(c:Concept)
                RETURN w.hasTitle AS title, w.hasAbstract AS abstract, w.hasOpenAlexId AS openalex_id,
                       w.domain AS domain, w.citedByCount AS cited_by_count,
                       collect(a.foaf__name) AS authors, collect(c.skos__prefLabel) AS topics
                """,
                uri=decoded_uri
            )
            record = result.single()
            if record:
                return jsonify({
                    "title": record["title"] or "Untitled",
                    "abstract": record["abstract"] or "No abstract available",
                    "openalex_id": record["openalex_id"] or "N/A",
                    "domain": record["domain"] or "Unknown",
                    "cited_by_count": record["cited_by_count"] or 0,
                    "authors": record["authors"] or [],
                    "topics": record["topics"] or []
                })
            return jsonify({"error": "Article not found", "uri": decoded_uri}), 404
    except Exception as e:
        return jsonify({"error": str(e), "uri": uri}), 500

@app.route('/concept_search', methods=['POST'])
def concept_search():
    """Search for concepts and related works based on a given concept label."""
    try:
        data = request.get_json()
        concept = data.get('concept', '')
        if not concept:
            return jsonify({"error": "No concept provided"}), 400
        with neo4j_driver.session() as session:
            result = session.run(
                """
                MATCH (c:Concept)
                WHERE toLower(c.skos__prefLabel) CONTAINS toLower($concept)
                OPTIONAL MATCH (c)-[:isSubclassOf]->(super:Concept)
                OPTIONAL MATCH (sub:Concept)-[:isSubclassOf]->(c)
                OPTIONAL MATCH (w:Work)-[:hasTopic|hasConcept]->(c)
                RETURN c.skos__prefLabel AS label, c.uri AS uri,
                       collect(DISTINCT super.skos__prefLabel) AS superclasses,
                       collect(DISTINCT sub.skos__prefLabel) AS subclasses,
                       collect(DISTINCT w.hasTitle) AS related_works
                LIMIT 1
                """,
                concept=concept
            )
            record = result.single()
            if record:
                return jsonify({
                    "label": record["label"],
                    "uri": record["uri"],
                    "superclasses": record["superclasses"],
                    "subclasses": record["subclasses"],
                    "related_works": record["related_works"]
                })
            return jsonify({"error": "Concept not found"}), 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    try:
        app.run(debug=FLASK_DEBUG, port=FLASK_PORT)
    finally:
        engine.close()
        neo4j_driver.close()