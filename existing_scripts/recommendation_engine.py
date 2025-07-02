from neo4j import GraphDatabase
import pandas as pd
import numpy as np
from scipy.spatial.distance import cosine
from tqdm import tqdm

class HybridRecommender:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="anass2003"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def get_user_embeddings(self, user_id):
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {has_id: $user_id})-[:hasInterest]->(c:Concept)
                RETURN c.uri, c.hasNameEmbedding
                """,
                user_id=user_id
            )
            embeddings = []
            for record in result:
                emb = record["c.hasNameEmbedding"]
                if emb and isinstance(emb, list) and len(emb) == 768:
                    embeddings.append(np.array(emb))
            return np.mean(embeddings, axis=0) if embeddings else np.zeros(768)

    def get_similar_users(self, user_id, logs_file=r"C:\Users\VSS\Desktop\WebAPP\VER 2\data\fake_user_logs.csv", top_n=5):
        try:
            df = pd.read_csv(logs_file)
            user_topics = df[df["user_id"] == user_id]["topic"].value_counts().index.tolist()
            if not user_topics:
                print(f"Warning: No topics for user {user_id}")
                return []
            
            other_users = df[df["user_id"] != user_id].groupby("user_id")["topic"].value_counts().reset_index()
            user_similarities = []
            for other_user in other_users["user_id"].unique():
                other_topics = other_users[other_users["user_id"] == other_user]["topic"].tolist()
                overlap = len(set(user_topics).intersection(other_topics)) / len(set(user_topics).union(other_topics))
                user_similarities.append((other_user, overlap))
            
            return [u for u, _ in sorted(user_similarities, key=lambda x: x[1], reverse=True)[:top_n]]
        except Exception as e:
            print(f"Error in get_similar_users: {e}")
            return []

    def get_recommendations(self, user_id, search_query_text=None, top_n=5, content_weight=0.6, ontology_weight=0.4):
        user_embedding = self.get_user_embeddings(user_id)
        if not np.any(user_embedding):
            print(f"Warning: No valid embedding for user {user_id}")

        content_recs = []
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (w:Work)
                WHERE w.hasAbstractEmbedding IS NOT NULL
                RETURN w.uri, w.hasTitle, w.citedByCount, w.hasAbstractEmbedding, w.domain
                """
            )
            article_count = 0
            valid_emb_count = 0
            for record in result:
                article_count += 1
                emb = record["w.hasAbstractEmbedding"]
                if not emb or not isinstance(emb, list) or len(emb) != 768:
                    print(f"Warning: Invalid embedding for article {record['w.hasTitle'] or 'Unknown'}")
                    continue
                emb = np.array(emb)
                if not np.any(emb):
                    print(f"Warning: Empty embedding for article {record['w.hasTitle'] or 'Unknown'}")
                    continue
                valid_emb_count += 1
                sim = 1 - cosine(user_embedding, emb) if np.any(user_embedding) else 0
                domain = record["w.domain"] if record["w.domain"] else "Unknown"
                score_boost = 1.1 if domain == "Artificial Intelligence" else 1.0
                content_recs.append({
                    "article_id": record["w.uri"],
                    "title": record["w.hasTitle"] or "Unknown Title",
                    "cited_by_count": record["w.citedByCount"] or 0,
                    "score": sim * score_boost
                })
            print(f"Processed {article_count} articles, {valid_emb_count} valid embeddings, {len(content_recs)} content recs")

        content_recs = pd.DataFrame(content_recs)
        if not content_recs.empty and "score" in content_recs.columns:
            content_recs = content_recs[content_recs["score"] > 0].sort_values(by="score", ascending=False).head(top_n)
        else:
            print("Warning: No valid content-based recs, proceeding with other methods")
            content_recs = pd.DataFrame(columns=["article_id", "title", "cited_by_count", "score"])

        ontology_recs = []
        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (u:User {has_id: $user_id})-[:hasInterest]->(c:Concept)
                RETURN c.skos__prefLabel AS topic
                """,
                user_id=user_id
            )
            user_topics = [record["topic"] for record in result]
            if not user_topics:
                user_topics = ["Neural Networks"]
                print(f"Warning: No topics for user {user_id}, defaulting to Neural Networks")

            for topic in user_topics:
                query = """
                MATCH (w:Work)-[:hasTopic|:hasConcept]->(c:Concept)
                WHERE toLower(c.skos__prefLabel) CONTAINS toLower($topic)
                RETURN w.uri, w.hasTitle, w.citedByCount, w.domain, 1.0 AS score
                ORDER BY w.citedByCount DESC
                LIMIT $top_n
                """
                params = {"topic": topic, "top_n": top_n}
                if search_query_text:
                    query = """
                    MATCH (w:Work)-[:hasTopic|:hasConcept]->(c:Concept)
                    WHERE toLower(c.skos__prefLabel) CONTAINS toLower($topic)
                    AND (toLower(w.hasTitle) CONTAINS toLower($search_query) OR toLower(w.hasAbstract) CONTAINS toLower($search_query))
                    RETURN w.uri, w.hasTitle, w.citedByCount, w.domain, 1.0 AS score
                    ORDER BY w.citedByCount DESC
                    LIMIT $top_n
                    """
                    params["search_query"] = search_query_text

                try:
                    result = session.run(query, **params)
                    for record in result:
                        domain = record["w.domain"] if record["w.domain"] else "Unknown"
                        score_boost = 1.1 if domain == "Artificial Intelligence" else 1.0
                        ontology_recs.append({
                            "article_id": record["w.uri"],
                            "title": record["w.hasTitle"] or "Unknown Title",
                            "cited_by_count": record["w.citedByCount"] or 0,
                            "score": record["score"] * score_boost
                        })
                except Exception as e:
                    print(f"Error in ontology query for topic {topic}: {e}")

        ontology_recs = pd.DataFrame(ontology_recs).drop_duplicates(subset=["article_id"]).head(top_n)

        collab_recs = []
        similar_users = self.get_similar_users(user_id)
        if similar_users:
            with self.driver.session() as session:
                for sim_user in similar_users:
                    try:
                        result = session.run(
                            """
                            MATCH (u:User {has_id: $user_id})-[:hasInterest]->(c:Concept)<-[:hasTopic|:hasConcept]-(w:Work)
                            RETURN w.uri, w.hasTitle, w.citedByCount, w.domain, 0.8 AS score
                            LIMIT $top_n
                            """,
                            user_id=sim_user,
                            top_n=top_n
                        )
                        for record in result:
                            domain = record["w.domain"] if record["w.domain"] else "Unknown"
                            score_boost = 1.1 if domain == "Artificial Intelligence" else 1.0
                            collab_recs.append({
                                "article_id": record["w.uri"],
                                "title": record["w.hasTitle"] or "Unknown Title",
                                "cited_by_count": record["w.citedByCount"] or 0,
                                "score": record["score"] * score_boost
                            })
                    except Exception as e:
                        print(f"Error in collaborative query for user {sim_user}: {e}")

        collab_recs = pd.DataFrame(collab_recs).drop_duplicates(subset=["article_id"]).head(top_n)

        all_recs = pd.concat([
            content_recs[["article_id", "title", "cited_by_count", "score"]],
            ontology_recs[["article_id", "title", "cited_by_count", "score"]],
            collab_recs[["article_id", "title", "cited_by_count", "score"]]
        ], ignore_index=True).drop_duplicates(subset=["article_id"])

        if all_recs.empty:
            print("Error: No recommendations generated")
            return []

        all_recs["score"] = [
            record["score"] * content_weight if record["article_id"] in content_recs["article_id"].values
            else record["score"] * ontology_weight for _, record in all_recs.iterrows()
        ]
        all_recs = all_recs.sort_values(by="score", ascending=False).head(top_n)
        return all_recs.to_dict(orient="records")

if __name__ == "__main__":
    recommender = HybridRecommender(password="anass2003")
    try:
        recs = recommender.get_recommendations(user_id="User_0", search_query_text="neural networks")
        print("Recommendations for User_0:")
        for rec in recs:
            print(f"- {rec['title']} (Score: {rec['score']:.3f}, Citations: {rec['cited_by_count']})")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        recommender.close()