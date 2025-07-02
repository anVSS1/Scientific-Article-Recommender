"""
Fake User Data Generator for Scientific Article Recommender

This script generates synthetic user profiles and interaction data for testing
and demonstrating the recommendation system. It creates realistic user archetypes
with different research interests and interaction patterns.

User Archetypes:
- AI_Researcher: Focused on AI, ML, Neural Networks, Deep Learning
- Data_Scientist: Interested in AI, Data Mining, Statistical Modeling  
- Physicist: Specialized in Quantum Computing, Quantum Mechanics
- Bioinformatician: Works with Bioinformatics, Genomics
- Mathematician: Focused on Graph Theory and mathematical concepts

Features:
- Weighted archetype distribution (biased toward AI researchers)
- Cold start users (minimal interaction history)
- Realistic interaction patterns with temporal elements
- Configurable number of users and interactions

Output:
- fake_user_logs.csv: User interaction history for recommendation training
"""

from faker import Faker
import pandas as pd
import random
from datetime import datetime, timedelta
from tqdm import tqdm

import sys
import os
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "..")) # Goes up to VER 2/
if project_root not in sys.path:
    sys.path.insert(0, project_root)
from backend_api.config import Config

def generate_fake_users(articles_file=r"C:\Users\VSS\Desktop\WebAPP\VER 2\data\cleaned data\processed_articles.json", num_users=50, num_interactions=3000, cold_start_percentage=0.1):
    try:
        fake = Faker()
        articles = pd.read_json(articles_file)
        article_ids = articles["id"].tolist()
        concepts = pd.read_json(r"C:\Users\VSS\Desktop\WebAPP\VER 2\data\cleaned data\processed_concepts.json")
        topics = concepts["name"].tolist()  # Use concept names

        archetypes = {
            "AI_Researcher": ["Artificial Intelligence", "Machine Learning", "Neural Networks", "Deep Learning"],
            "Data_Scientist": ["Artificial Intelligence", "Data Mining", "Statistical Modeling"],
            "Physicist": ["Quantum Computing", "Quantum Mechanics"],
            "Bioinformatician": ["Bioinformatics", "Genomics"],
            "Mathematician": ["Graph Theory"]
        }

        users = []
        for i in range(num_users):
            archetype = random.choices(
                list(archetypes.keys()),
                weights=[0.4, 0.3, 0.1, 0.1, 0.1],  # Bias toward AI
                k=1
            )[0]
            is_cold_start = random.random() < cold_start_percentage
            users.append({
                "user_id": f"User_{i}",
                "archetype": archetype,
                "preferred_topics": [t for t in archetypes[archetype] if t in topics],  # Ensure valid topics
                "is_cold_start": is_cold_start
            })

        interactions = []
        for user in tqdm(users, desc="Generating user interactions"):
            num_user_interactions = random.randint(1, 5) if user["is_cold_start"] else random.randint(10, 50)
            for _ in range(num_user_interactions):
                if user["archetype"] in ["AI_Researcher", "Data_Scientist"]:
                    ai_articles = articles[articles["domain"] == "Artificial Intelligence"]["id"].tolist()
                    article = random.choice(ai_articles) if ai_articles else random.choice(article_ids)
                else:
                    article = random.choice(article_ids)
                interaction_type = random.choices(
                    ["read", "click", "cite"], weights=[0.6, 0.3, 0.1], k=1
                )[0]
                timestamp = fake.date_time_between(start_date="-30d", end_date="now")
                duration = random.randint(30, 600) if interaction_type == "read" else 0
                topic = random.choice(user["preferred_topics"]) if user["preferred_topics"] else random.choice(topics)
                interactions.append({
                    "user_id": user["user_id"],
                    "article_id": article,
                    "interaction_type": interaction_type,
                    "timestamp": timestamp,
                    "duration_seconds": duration,
                    "topic": topic
                })

        df = pd.DataFrame(interactions)
        output_path = r"C:\Users\VSS\Desktop\WebAPP\VER 2\data\fake_user_logs.csv"
        df.to_csv(output_path, index=False)
        print(f"Generated {len(interactions)} interactions for {num_users} users. Saved to {output_path}!")
    except Exception as e:
        print(f"Error generating fake users: {e}")

if __name__ == "__main__":
    generate_fake_users()