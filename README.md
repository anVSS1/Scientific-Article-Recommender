# 🔬 Scientific Article Recommender

A hybrid recommendation system for scientific papers that combines semantic embeddings, knowledge graphs, and user behavior analysis to provide personalized research paper recommendations.

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Flask](https://img.shields.io/badge/flask-v2.3+-green.svg)
![Neo4j](https://img.shields.io/badge/neo4j-v5.14+-red.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

- **Hybrid Recommendation Engine**: Combines content-based filtering using SciBERT embeddings with collaborative filtering
- **Knowledge Graph Integration**: Uses Neo4j to store and query relationships between papers, concepts, and authors
- **Semantic Search**: Leverages SciBERT embeddings for semantic similarity between research papers
- **Ontology-based Recommendations**: Integrates scientific concept hierarchies for better recommendations
- **Modern Web Interface**: Clean, responsive UI built with Flask and TailwindCSS
- **Real-time Recommendations**: Instant paper suggestions based on topics and user preferences

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask Web App │────│  Recommendation │────│   Neo4j Graph   │
│                 │    │     Engine      │    │    Database     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
    ┌─────────┐          ┌──────────────┐        ┌──────────────┐
    │   UI    │          │   SciBERT    │        │   OpenAlex   │
    │Templates│          │  Embeddings  │        │     API      │
    └─────────┘          └──────────────┘        └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Neo4j Database (local or cloud)
- Git

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/scientific-article-recommender.git
   cd scientific-article-recommender
   ```

2. **Create virtual environment**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Neo4j Database**

   - Install Neo4j Desktop or use Neo4j Aura
   - Create a new database
   - Update connection credentials in `Website/app.py`

5. **Prepare the data**

   ```bash
   # Generate embeddings for articles
   python existing_scripts/generate_embeddings.py

   # Import data to Neo4j
   python existing_scripts/import_data_to_neo4j.py

   # Load embeddings to Neo4j
   python existing_scripts/load_embeddings_to_neo4j.py

   # Generate fake user data for testing
   python existing_scripts/fake_user_generator.py

   # Populate user profiles
   python existing_scripts/populate_user_profiles_neo4j.py
   ```

6. **Run the application**

   ```bash
   cd Website
   python app.py
   ```

7. **Open your browser**
   Navigate to `http://localhost:5050`

## 📁 Project Structure

```
scientific-article-recommender/
├── Website/                          # Main Flask application
│   ├── app.py                       # Flask app entry point
│   ├── backend/
│   │   └── reco.py                  # Recommendation engine
│   ├── templates/
│   │   ├── index.html               # Main interface
│   │   └── ontology.html            # Ontology explorer
│   └── data/                        # Runtime data files
├── existing_scripts/                # Data processing scripts
│   ├── generate_embeddings.py       # SciBERT embedding generation
│   ├── import_data_to_neo4j.py     # Data import to Neo4j
│   ├── load_embeddings_to_neo4j.py # Embedding data loader
│   ├── fake_user_generator.py      # Test user data generator
│   ├── populate_user_profiles_neo4j.py # User profile setup
│   ├── recommendation_engine.py     # Core recommendation logic
│   ├── ontology.py                 # Ontology handling
│   └── openalec-fetcher.ipynb      # Data fetching notebook
├── data/                           # Source data files
│   ├── cleaned data/               # Processed datasets
│   ├── embeddings/                 # Generated embeddings
│   └── fetched data/               # Raw OpenAlex data
├── requirements.txt                # Python dependencies
└── README.md                      # This file
```

## 🧪 Usage

### Topic-based Search

1. Navigate to the main page
2. Select "Topic Search"
3. Enter a research topic (e.g., "Neural Networks", "Machine Learning")
4. Get relevant paper recommendations

### Personalized Recommendations

1. Select "Personalized" mode
2. Choose a user profile
3. Enter a search query
4. Receive personalized recommendations based on user history

### Ontology Explorer

- Click "Explore Ontology" to browse scientific concept hierarchies
- Search for specific concepts and explore relationships

## 🔧 Configuration

### Database Configuration

Update the Neo4j connection settings in `Website/app.py`:

```python
neo4j_driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "your_password"))
```

### Embedding Model

The system uses SciBERT by default. To change the model, modify `existing_scripts/generate_embeddings.py`:

```python
self.tokenizer = AutoTokenizer.from_pretrained("your-model-name")
self.model = AutoModel.from_pretrained("your-model-name")
```

## 📊 Data Sources

- **OpenAlex**: Scientific papers and metadata
- **Scientific Concept Hierarchies**: Domain-specific ontologies
- **User Interaction Logs**: Simulated user behavior data

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAlex](https://openalex.org/) for providing open scientific data
- [SciBERT](https://github.com/allenai/scibert) for scientific text embeddings
- [Neo4j](https://neo4j.com/) for graph database technology
- [Flask](https://flask.palletsprojects.com/) for the web framework

## 📧 Contact

Your Name - your.email@example.com

Project Link: [https://github.com/yourusername/scientific-article-recommender](https://github.com/yourusername/scientific-article-recommender)

---

⭐ **Star this repo if you find it helpful!**
