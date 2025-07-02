"""
Scientific Ontology Manager for Article Recommender

This script manages the scientific domain ontology using OWLReady2 library.
It provides functionality for working with scientific concept hierarchies,
relationships, and semantic reasoning.

Ontology Features:
- Scientific concept taxonomy and hierarchies
- Property relationships between concepts
- Reasoning capabilities for concept inference
- Integration with knowledge graph data

Use Cases:
- Concept hierarchy navigation
- Semantic relationship discovery
- Ontology-based recommendation enhancement
- Knowledge graph enrichment

Dependencies:
- owlready2: OWL ontology manipulation library
- Integration with Neo4j graph database
"""

from owlready2 import *

# Create ontology with your namespace
onto = get_ontology("http://www.semanticweb.org/vss/ontology/scientific_recommender#")

with onto:
    # Define classes for articles, concepts, users, authors, and institutions
    class Work(Thing): pass
    class Concept(Thing): pass
    class User(Thing): pass
    class Author(Thing): pass
    class Institution(Thing): pass

    # Define object properties for relationships
    class hasTopic(ObjectProperty):
        domain = [Work]
        range = [Concept]
        comment = ["Links a Work (article) to a Concept (topic)."]
    
    class hasConcept(ObjectProperty):
        domain = [Work]
        range = [Concept]
        comment = ["Links a Work to a Concept (broader concept)."]
    
    class isSubclassOf(ObjectProperty):
        domain = [Concept]
        range = [Concept]
        comment = ["Defines hierarchy between Concepts (e.g., Neural Networks under Machine Learning)."]
    
    class hasInterest(ObjectProperty):
        domain = [User]
        range = [Concept]
        comment = ["Links a User to a Concept they’re interested in (e.g., User_0 to Neural Networks)."]
    
    class hasAuthor(ObjectProperty):
        domain = [Work]
        range = [Author]
        comment = ["Links a Work to its Author(s)."]
    
    class worksAt(ObjectProperty):
        domain = [Author]
        range = [Institution]
        comment = ["Links an Author to their Institution."]

    # Define data properties for metadata
    class hasOpenAlexId(DataProperty):
        domain = [Work, Concept, Author, Institution]
        range = [str]
        comment = ["OpenAlex ID for Works, Concepts, Authors, or Institutions."]
    
    class hasTitle(DataProperty):
        domain = [Work]
        range = [str]
        comment = ["Title of a Work (article)."]
    
    class hasAbstract(DataProperty):
        domain = [Work]
        range = [str]
        comment = ["Abstract of a Work."]
    
    class publishedInYear(DataProperty):
        domain = [Work]
        range = [int]
        comment = ["Publication year of a Work."]
    
    class citedByCount(DataProperty):
        domain = [Work]
        range = [int]
        comment = ["Number of citations for a Work."]
    
    class domain(DataProperty):
        domain = [Work]
        range = [str]
        comment = ["Scientific domain of a Work (e.g., Artificial Intelligence)."]
    
    class hasLevel(DataProperty):
        domain = [Concept]
        range = [int]
        comment = ["Hierarchical level of a Concept."]
    
    class hasWikidataId(DataProperty):
        domain = [Concept]
        range = [str]
        comment = ["Wikidata ID for a Concept."]
    
    class has_id(DataProperty):
        domain = [User]
        range = [str]
        comment = ["Unique ID for a User (e.g., User_0)."]
    
    class hasAbstractEmbedding(DataProperty):
        domain = [Work]
        range = [str]
        comment = ["SciBERT embedding for a Work’s abstract (JSON string of floats)."]
    
    class hasNameEmbedding(DataProperty):
        domain = [Concept]
        range = [str]
        comment = ["SciBERT embedding for a Concept’s name (JSON string of floats)."]
    
    class skos__prefLabel(DataProperty):
        domain = [Concept]
        range = [str]
        comment = ["Preferred label for a Concept (e.g., Neural Networks)."]
    
    class foaf__name(DataProperty):
        domain = [Author, Institution, User]
        range = [str]
        comment = ["Name of an Author, Institution, or User."]

# Save ontology to OWL file
onto.save(file="scientific_recommender.owl", format="rdfxml")
print("Ontology saved as scientific_recommender.owl! 🚀")