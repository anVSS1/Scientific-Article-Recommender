"""
Neo4j Data Importer for Scientific Article Recommender

This script imports processed scientific articles, concepts, and their relationships
into a Neo4j graph database. It creates a comprehensive knowledge graph that
enables graph-based queries and recommendations.

Graph Schema:
- Work nodes: Scientific articles with metadata
- Concept nodes: Scientific concepts and topics  
- Author nodes: Article authors
- Institution nodes: Research institutions
- Relationships: hasTopic, hasAuthor, hasInstitution, etc.

Features:
- Batch processing for efficient imports
- Duplicate detection and handling
- Progress tracking with tqdm
- Error handling and logging
- Relationship creation between entities

Input Data:
- processed_articles.json: Clean article data
- processed_concepts.json: Clean concept data

Output:
- Populated Neo4j database ready for recommendations
"""

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

class Neo4jImporter:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="anass2003"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_concepts(self, tx, concepts):
        for _, row in tqdm(concepts.iterrows(), total=len(concepts), desc="Creating Concepts"):
            c_id = re.sub(r'\W+', '_', str(row["id"]))
            tx.run(
                """
                MERGE (c:Concept {uri: $uri})
                SET c.hasOpenAlexId = $id, c.skos__prefLabel = $name, c.hasLevel = $level, c.hasWikidataId = $wikidata
                """,
                uri=f"http://www.semanticweb.org/vss/ontology/scientific_recommender#{c_id}",
                id=str(row["id"]), name=str(row["name"] or ""), level=int(row["level"] or 0),
                wikidata=str(row["wikidata"] or "")
            )

    def create_works(self, tx, articles):
        for _, row in tqdm(articles.iterrows(), total=len(articles), desc="Creating Works"):
            w_id = re.sub(r'\W+', '_', str(row["id"]))
            tx.run(
                """
                MERGE (w:Work {uri: $uri})
                SET w.hasOpenAlexId = $id, w.hasTitle = $title, w.hasAbstract = $abstract,
                    w.publishedInYear = $year, w.citedByCount = $cited_by_count, w.domain = $domain
                """,
                uri=f"http://www.semanticweb.org/vss/ontology/scientific_recommender#{w_id}",
                id=str(row["id"]), title=str(row["title"] or ""), abstract=str(row["abstract"] or ""),
                year=int(row["publication_year"] or 0), cited_by_count=int(row["cited_by_count"] or 0),
                domain=str(row["domain"] or "")
            )

            for a in row["authors"] or []:
                if a.get("id"):
                    a_id = re.sub(r'\W+', '_', str(a["id"]))
                    tx.run(
                        """
                        MERGE (a:Author {uri: $uri})
                        SET a.hasOpenAlexId = $id, a.foaf__name = $name
                        """,
                        uri=f"http://www.semanticweb.org/vss/ontology/scientific_recommender#{a_id}",
                        id=str(a["id"]), name=str(a["name"] or "")
                    )
                    tx.run(
                        """
                        MATCH (w:Work {uri: $w_uri}), (a:Author {uri: $a_uri})
                        MERGE (w)-[:hasAuthor]->(a)
                        """,
                        w_uri=f"http://www.semanticweb.org/vss/ontology/scientific_recommender#{w_id}",
                        a_uri=f"http://www.semanticweb.org/vss/ontology/scientific_recommender#{a_id}"
                    )

            for i in row["institutions"] or []:
                if i.get("id"):
                    i_id = re.sub(r'\W+', '_', str(i["id"]))
                    tx.run(
                        """
                        MERGE (i:Institution {uri: $uri})
                        SET i.hasOpenAlexId = $id, i.foaf__name = $name
                        """,
                        uri=f"http://www.semanticweb.org/vss/ontology/scientific_recommender#{i_id}",
                        id=str(i["id"]), name=str(i["name"] or "")
                    )
                    for a in row["authors"] or []:
                        if a.get("id"):
                            tx.run(
                                """
                                MATCH (a:Author {uri: $a_uri}), (i:Institution {uri: $i_uri})
                                MERGE (a)-[:worksAt]->(i)
                                """,
                                a_uri=f"http://www.semanticweb.org/vss/ontology/scientific_recommender#{re.sub(r'\W+', '_', str(a['id']))}",
                                i_uri=f"http://www.semanticweb.org/vss/ontology/scientific_recommender#{i_id}"
                            )

            for t in row["topics"] or []:
                t_id = re.sub(r'\W+', '_', str(t))
                tx.run(
                    """
                    MATCH (w:Work {uri: $w_uri}), (c:Concept {uri: $c_uri})
                    MERGE (w)-[:hasTopic]->(c)
                    """,
                    w_uri=f"http://www.semanticweb.org/vss/ontology/scientific_recommender#{w_id}",
                    c_uri=f"http://www.semanticweb.org/vss/ontology/scientific_recommender#{t_id}"
                )
            for c in row["concepts"] or []:
                c_id = re.sub(r'\W+', '_', str(c))
                tx.run(
                    """
                    MATCH (w:Work {uri: $w_uri}), (c:Concept {uri: $c_uri})
                    MERGE (w)-[:hasConcept]->(c)
                    """,
                    w_uri=f"http://www.semanticweb.org/vss/ontology/scientific_recommender#{w_id}",
                    c_uri=f"http://www.semanticweb.org/vss/ontology/scientific_recommender#{c_id}"
                )
                for t in row["topics"] or []:
                    tx.run(
                        """
                        MATCH (c:Concept {uri: $c_uri}), (t:Concept {uri: $t_uri})
                        MERGE (c)-[:isSubclassOf]->(t)
                        """,
                        c_uri=f"http://www.semanticweb.org/vss/ontology/scientific_recommender#{c_id}",
                        t_uri=f"http://www.semanticweb.org/vss/ontology/scientific_recommender#{re.sub(r'\W+', '_', str(t))}"
                    )

    def populate_graph(self, articles_file=r"C:\Users\VSS\Desktop\WebAPP\VER 2\data\cleaned data\processed_articles.json", concepts_file=r"C:\Users\VSS\Desktop\WebAPP\VER 2\data\cleaned data\processed_concepts.json", batch_size=100):
        try:
            articles = pd.read_json(articles_file)
            concepts = pd.read_json(concepts_file)
        except Exception as e:
            print(f"Error loading files: {e}")
            return

        with self.driver.session() as session:
            session.execute_write(self.create_concepts, concepts)
            print("Concepts created!")
            for start_idx in range(0, len(articles), batch_size):
                end_idx = min(start_idx + batch_size, len(articles))
                batch = articles.iloc[start_idx:end_idx]
                session.execute_write(self.create_works, batch)
                print(f"Processed articles {start_idx} to {end_idx}")

        print("Neo4j graph populated!")

if __name__ == "__main__":
    importer = Neo4jImporter(password="anass2003")
    try:
        importer.populate_graph()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        importer.close()