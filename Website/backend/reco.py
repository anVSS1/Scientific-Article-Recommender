"""
Recommendation Engine Backend for Scientific Article Recommender

This module implements a hybrid recommendation system that combines:
1. Content-based filtering using SciBERT embeddings
2. Ontology-based recommendations using Neo4j concept relationships
3. User preference matching based on interaction history

The engine provides both topic-based search and personalized recommendations
for scientific articles stored in a Neo4j graph database.

Key Features:
- Semantic similarity using SciBERT embeddings (768-dimensional vectors)
- Graph-based concept relationships and hierarchies
- User profile-based personalization
- Hybrid recommendation scoring

Dependencies:
- pandas, numpy: Data manipulation and numerical operations
- neo4j: Graph database connectivity
- scipy: Cosine similarity calculations
- sklearn: Vector normalization and preprocessing
"""

import pandas as pd
import numpy as np
import json
from neo4j import GraphDatabase
from scipy.spatial.distance import cosine
from sklearn.preprocessing import normalize

class RecommendationEngine:
    """
    Hybrid Recommendation Engine for Scientific Articles
    
    This class implements a multi-faceted recommendation system that combines:
    - Ontology-based recommendations using graph relationships
    - Content-based filtering with SciBERT embeddings
    - User preference analysis from interaction history
    
    Attributes:
        driver: Neo4j database driver instance
        embedding_dim (int): Dimension of SciBERT embeddings (768)
    """
    
    def __init__(self, uri, user, password):
        """
        Initialize the recommendation engine with Neo4j connection.
        
        Args:
            uri (str): Neo4j database URI (e.g., "bolt://localhost:7687")
            user (str): Neo4j username
            password (str): Neo4j password
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.embedding_dim = 768  # SciBERT embedding size

    def close(self):
        """Close the Neo4j database connection."""
        self.driver.close()

    def get_ontology_recommendations(self, topic, search_query):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (w:Work)-[:hasTopic|hasConcept]->(c:Concept)
                WHERE toLower(c.skos__prefLabel) CONTAINS toLower($topic)
                AND ($search_query = '' OR toLower(w.hasTitle) CONTAINS toLower($search_query) OR toLower(w.hasAbstract) CONTAINS toLower($search_query))
                RETURN w.uri, w.hasTitle, w.domain
                """,
                topic=topic, search_query=search_query
            )
            return [(record["w.uri"], record["w.hasTitle"], record["w.domain"], 'Ontology') for record in result]

    def get_user_recommendations(self, user_id):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {has_id: $user_id})-[:hasInterest]->(c:Concept)<-[:hasTopic|hasConcept]-(w:Work)
                RETURN w.uri, w.hasTitle, w.domain
                """,
                user_id=user_id
            )
            return [(record["w.uri"], record["w.hasTitle"], record["w.domain"], 'User') for record in result]

    def get_content_recommendations(self, user_id, embeddings_file, concepts_embeddings_file):
        embeddings_df = pd.read_csv(embeddings_file)
        valid_embeddings = embeddings_df.dropna(subset=['hasAbstractEmbedding']).copy()

        if valid_embeddings.empty:
            return []

        valid_embeddings['embedding'] = valid_embeddings['hasAbstractEmbedding'].apply(json.loads)
        embeddings_matrix = np.array(valid_embeddings['embedding'].tolist())
        embeddings_matrix = normalize(embeddings_matrix)

        # Get user concept embeddings from Neo4j
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {has_id: $user_id})-[:hasInterest]->(c:Concept)
                WHERE c.hasNameEmbedding IS NOT NULL
                RETURN c.uri, c.hasNameEmbedding
                """,
                user_id=user_id
            )
            user_embeddings = [(record["c.uri"], record["c.hasNameEmbedding"]) for record in result]

        if not user_embeddings:
            return []

        user_embedding = np.mean([emb for _, emb in user_embeddings], axis=0)
        user_embedding = normalize([user_embedding])[0]

        # Use lower threshold like the working version
        similarities = 1 - np.array([cosine(user_embedding, emb) for emb in embeddings_matrix])
        valid_indices = np.where(similarities > 0)[0]  # Keep all non-zero similarities

        recommendations = []
        for idx in valid_indices:
            article = valid_embeddings.iloc[idx]
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (w:Work {uri: $uri})
                    RETURN w.hasTitle, w.domain
                    """,
                    uri=article['uri']
                )
                record = result.single()
                if record:
                    recommendations.append((article['uri'], record["w.hasTitle"], record["w.domain"], 'Content'))
        return recommendations

    def get_collaborative_recommendations(self, user_id):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {has_id: $user_id})-[:hasInterest]->(c:Concept)<-[:hasInterest]-(other:User)-[:hasInterest]->(c2:Concept)<-[:hasTopic|hasConcept]-(w:Work)
                WHERE u <> other
                RETURN DISTINCT w.uri, w.hasTitle, w.domain
                """,
                user_id=user_id
            )
            recommendations = [(record["w.uri"], record["w.hasTitle"], record["w.domain"], 'Collaborative') for record in result]
            print(f"Collaborative recommendations found: {len(recommendations)}")
            return recommendations

    def get_search_recommendations(self, search_topic, embeddings_file, concepts_embeddings_file):
        # Ontology-based: Include related concepts via isSubclassOf
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:Concept)
                WHERE toLower(c.skos__prefLabel) CONTAINS toLower($topic)
                OPTIONAL MATCH (c)-[:isSubclassOf*0..2]->(related:Concept)
                WITH collect(c) + collect(related) AS concepts
                UNWIND concepts AS concept
                MATCH (w:Work)-[:hasTopic|hasConcept]->(concept)
                RETURN w.uri, w.hasTitle, w.domain
                """,
                topic=search_topic
            )
            ontology_recs = [(record["w.uri"], record["w.hasTitle"], record["w.domain"], 'Ontology') for record in result]

        # Content-based: Use embeddings for semantic similarity
        embeddings_df = pd.read_csv(embeddings_file)
        valid_embeddings = embeddings_df.dropna(subset=['hasAbstractEmbedding']).copy()

        if valid_embeddings.empty:
            return ontology_recs

        valid_embeddings['embedding'] = valid_embeddings['hasAbstractEmbedding'].apply(json.loads)
        embeddings_matrix = np.array(valid_embeddings['embedding'].tolist())
        embeddings_matrix = normalize(embeddings_matrix)

        # Get concept embedding from Neo4j
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (c:Concept)
                WHERE toLower(c.skos__prefLabel) CONTAINS toLower($topic)
                AND c.hasNameEmbedding IS NOT NULL
                RETURN c.hasNameEmbedding
                LIMIT 1
                """,
                topic=search_topic
            )
            record = result.single()
            if not record:
                print(f"No concept embedding found for '{search_topic}' - returning only ontology results")
                return [(row[0], row[1], row[2], row[3]) for row in ontology_recs]  # Return with URI
            
            topic_embedding = record["c.hasNameEmbedding"]
            topic_embedding = normalize([topic_embedding])[0]

        # Calculate similarities with lower threshold
        similarities = 1 - np.array([cosine(topic_embedding, emb) for emb in embeddings_matrix])
        valid_indices = np.where(similarities > 0)[0]  # Keep all non-zero similarities

        content_recs = []
        for idx in valid_indices:
            article = valid_embeddings.iloc[idx]
            with self.driver.session() as session:
                result = session.run(
                    """
                    MATCH (w:Work {uri: $uri})
                    RETURN w.hasTitle, w.domain
                    """,
                    uri=article['uri']
                )
                record = result.single()
                if record:
                    content_recs.append((article['uri'], record["w.hasTitle"], record["w.domain"], 'Content'))
        
        print(f"Found {len(ontology_recs)} ontology + {len(content_recs)} content recommendations")
        
        # Combine and group results
        all_recs = ontology_recs + content_recs
        recs_df = pd.DataFrame(all_recs, columns=["uri", "title", "domain", "approach"])
        if recs_df.empty:
            return []

        # Group by uri to combine approaches
        recs_grouped = recs_df.groupby(['uri', 'title', 'domain'])['approach'].apply(lambda x: ', '.join(sorted(set(x)))).reset_index()
        return [(row['uri'], row['title'], row['domain'], row['approach']) for _, row in recs_grouped.iterrows()]

    def get_recommendations(self, user_id, topic="Neural Networks", search_query=""):
        ontology_recs = self.get_ontology_recommendations(topic, search_query)
        content_recs = self.get_content_recommendations(user_id, "data/embeddings/embeddings_articles.csv", "data/embeddings/embeddings_concepts.csv")
        collaborative_recs = self.get_collaborative_recommendations(user_id)
        user_recs = self.get_user_recommendations(user_id)

        all_recs = ontology_recs + content_recs + collaborative_recs + user_recs
        recs_df = pd.DataFrame(all_recs, columns=["uri", "title", "domain", "approach"])
        if recs_df.empty:
            return []

        recs_grouped = recs_df.groupby(['uri', 'title', 'domain'])['approach'].apply(lambda x: ', '.join(sorted(set(x)))).reset_index()
        return [(row['uri'], row['title'], row['domain'], row['approach']) for _, row in recs_grouped.iterrows()]  # Return URI first

    def debug_search(self, search_topic, concepts_embeddings_file):
        """Debug function to check concept matching"""
        concepts_df = pd.read_csv(concepts_embeddings_file)
        valid_concepts = concepts_df.dropna(subset=['hasNameEmbedding']).copy()
        
        print(f"Search topic: {search_topic}")
        print(f"Total concepts: {len(valid_concepts)}")
        print(f"Sample concept labels: {valid_concepts['skos__prefLabel'].head(10).tolist()}")
        
        topic_rows = valid_concepts[valid_concepts['skos__prefLabel'].str.lower().str.contains(search_topic.lower(), na=False)]
        print(f"Matching concepts found: {len(topic_rows)}")
        if not topic_rows.empty:
            print(f"Matching labels: {topic_rows['skos__prefLabel'].tolist()}")

def main():
    engine = RecommendationEngine("bolt://localhost:7687", "neo4j", "anass2003")
    try:
        print(f"Recommendations for User_0 (Neural Networks):")
        user_recommendations = engine.get_recommendations("User_0", topic="Neural Networks")
        for uri, title, domain, approaches in user_recommendations:
            print(f"- {title} (URI: {uri}, Domaine: {domain}, Approches: {approaches})")
        pd.DataFrame(user_recommendations, columns=["uri", "title", "domain", "approaches"]).to_csv("user_recommendations.csv", index=False)

        print(f"\nSearch Recommendations for 'machine learning':")
        search_recommendations = engine.get_search_recommendations("machine learning", "data/embeddings/embeddings_articles.csv", "data/embeddings/embeddings_concepts.csv")
        for title, domain, approaches in search_recommendations:
            print(f"- {title} (Domaine: {domain}, Approches: {approaches})")
        pd.DataFrame(search_recommendations, columns=["title", "domain", "approaches"]).to_csv("search_recommendations.csv", index=False)
    finally:
        engine.close()

if __name__ == "__main__":
    main()