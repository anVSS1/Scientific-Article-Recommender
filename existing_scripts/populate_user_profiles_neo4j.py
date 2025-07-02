from neo4j import GraphDatabase
import pandas as pd
from tqdm import tqdm
import re

import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..")) # Goes up to VER 2/
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from backend_api.config import Config

class UserProfileImporter:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="anass2003"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def populate_users(self, logs_file=r"C:\Users\VSS\Desktop\WebAPP\VER 2\data\fake_user_logs.csv"):
        try:
            df = pd.read_csv(logs_file)
            user_topics = df.groupby("user_id")["topic"].value_counts().groupby(level=0).head(3).reset_index()
        except Exception as e:
            print(f"Error loading user logs: {e}")
            return

        def create_user_profiles(tx):
            # Ensure User_0 likes Neural Networks
            tx.run(
                """
                MERGE (u:User {uri: $uri, has_id: $id})
                SET u.foaf__name = $name
                WITH u
                MATCH (c:Concept)
                WHERE toLower(c.skos__prefLabel) CONTAINS 'neural networks'
                MERGE (u)-[:hasInterest]->(c)
                """,
                uri="http://www.semanticweb.org/vss/ontology/scientific_recommender#User_0",
                id="User_0", name="User_0"
            )

            for user_id in tqdm(user_topics["user_id"].unique(), desc="Creating Users"):
                if user_id != "User_0":
                    tx.run(
                        """
                        MERGE (u:User {uri: $uri, has_id: $id})
                        SET u.foaf__name = $name
                        """,
                        uri=f"http://www.semanticweb.org/vss/ontology/scientific_recommender#{user_id}",
                        id=user_id, name=user_id
                    )
                    user_top_topics = user_topics[user_topics["user_id"] == user_id]["topic"]
                    for topic in user_top_topics:
                        tx.run(
                            """
                            MATCH (u:User {uri: $u_uri}), (c:Concept)
                            WHERE toLower(c.skos__prefLabel) CONTAINS toLower($topic)
                            MERGE (u)-[:hasInterest]->(c)
                            """,
                            u_uri=f"http://www.semanticweb.org/vss/ontology/scientific_recommender#{user_id}",
                            topic=str(topic)
                        )

        with self.driver.session() as session:
            session.execute_write(create_user_profiles)
        print("User profiles and interests stored in Neo4j!")

if __name__ == "__main__":
    importer = UserProfileImporter(password="anass2003")
    try:
        importer.populate_users()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        importer.close()