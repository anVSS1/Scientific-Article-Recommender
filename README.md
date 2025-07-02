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

## 🚀 Complete Setup Guide

### Prerequisites

- **Python 3.8+**
- **Neo4j Database** (Desktop or Cloud)
- **Git**
- **8GB+ RAM** (for SciBERT embedding generation)

### 1. Clone and Setup Repository

```bash
git clone https://github.com/anVSS1/Scientific-Article-Recommender.git
cd Scientific-Article-Recommender

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Setup Neo4j Database

1. **Download Neo4j Desktop**: https://neo4j.com/download/
2. **Create a new database**
3. **Set password** (remember this!)
4. **Start the database**

### 3. Configure Environment Variables

```bash
# Copy environment template
cp .env.example .env

# Edit .env file with your settings:
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_actual_password
FLASK_DEBUG=True
FLASK_PORT=5050
```

## 📊 Data Setup (IMPORTANT!)

**⚠️ This repository contains NO data files - you need to fetch and generate your own data.**

### Step 1: Fetch Scientific Articles

1. **Edit the notebook**: `existing_scripts/openalec-fetcher.ipynb`
2. **Add your email** (required by OpenAlex API):
   ```python
   EMAIL_FOR_OPENALEX = "your_email@example.com"  # Replace this!
   ```
3. **Configure domains** you want to fetch:
   ```python
   DOMAINS = [
       ("Computer Science", "https://openalex.org/C41008148", 1400),
       ("Artificial Intelligence", "https://openalex.org/C154945302", 400),
       ("Physics", "https://openalex.org/C121332964", 200),
       # Add more domains as needed
   ]
   ```
4. **Run the notebook** to fetch articles and concepts

### Step 2: Update File Paths in Scripts

**All scripts have hardcoded paths that you MUST change to match your setup:**

#### `existing_scripts/generate_embeddings.py`

```python
# Change these paths to match your data location:
articles_file = "data/cleaned data/processed_articles.json"  # Update path
concepts_file = "data/cleaned data/processed_concepts.json"  # Update path
output_dir = "data/embeddings/"  # Update path
```

#### `existing_scripts/import_data_to_neo4j.py`

```python
# Update these paths:
articles_file = "data/cleaned data/processed_articles.json"
concepts_file = "data/cleaned data/processed_concepts.json"
```

#### `existing_scripts/fake_user_generator.py`

```python
# Update these paths:
articles_file = "data/cleaned data/processed_articles.json"
concepts_file = "data/cleaned data/processed_concepts.json"
output_file = "data/fake_user_logs.csv"
```

#### `Website/app.py`

```python
# Update paths in the Flask app:
embeddings_file = "data/embeddings/embeddings_articles.csv"
concepts_embeddings_file = "data/embeddings/embeddings_concepts.csv"
```

### Step 3: Generate Embeddings

```bash
# Generate SciBERT embeddings for your articles
python existing_scripts/generate_embeddings.py
```

**Note**: This process can take several hours depending on your dataset size and hardware.

### Step 4: Import Data to Neo4j

```bash
# Import articles and concepts to Neo4j
python existing_scripts/import_data_to_neo4j.py

# Load embeddings to Neo4j
python existing_scripts/load_embeddings_to_neo4j.py

# Generate fake user data for testing
python existing_scripts/fake_user_generator.py

# Create user profiles in Neo4j
python existing_scripts/populate_user_profiles_neo4j.py
```

### Step 5: Run the Application

```bash
cd Website
python app.py
```

Navigate to `http://localhost:5050`

## 📁 Project Structure

```
Scientific-Article-Recommender/
├── Website/                          # Flask web application
│   ├── app.py                       # Main Flask app
│   ├── backend/reco.py              # Recommendation engine
│   └── templates/                   # HTML templates
├── existing_scripts/                # Data processing scripts
│   ├── openalec-fetcher.ipynb      # Fetch data from OpenAlex
│   ├── generate_embeddings.py       # Generate SciBERT embeddings
│   ├── import_data_to_neo4j.py     # Import to Neo4j
│   ├── load_embeddings_to_neo4j.py # Load embeddings
│   ├── fake_user_generator.py      # Generate test users
│   └── populate_user_profiles_neo4j.py # Setup user profiles
├── data/                           # YOUR DATA GOES HERE
│   ├── fetched data/               # Raw OpenAlex data
│   ├── cleaned data/               # Processed articles/concepts
│   └── embeddings/                 # Generated embeddings
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment template
└── README.md                      # This file
```

## 🔧 Customization Options

### Change Research Domains

Edit `openalec-fetcher.ipynb` to fetch different scientific domains:

```python
DOMAINS = [
    ("Your Domain", "OpenAlex_Concept_ID", target_count),
    ("Biology", "https://openalex.org/C86803240", 500),
    ("Medicine", "https://openalex.org/C71924100", 300),
]
```

### Modify Embedding Model

Change the SciBERT model in `generate_embeddings.py`:

```python
self.tokenizer = AutoTokenizer.from_pretrained("your-preferred-model")
self.model = AutoModel.from_pretrained("your-preferred-model")
```

### Adjust Recommendation Weights

Modify the hybrid recommendation weights in `Website/backend/reco.py`:

```python
content_weight = 0.6  # Content-based filtering weight
ontology_weight = 0.4  # Ontology-based weight
```

## 🧪 Usage Examples

### Topic-based Search

1. Navigate to the main page
2. Select "Topic Search"
3. Enter: "Neural Networks", "Machine Learning", etc.
4. Get semantically similar papers

### Personalized Recommendations

1. Select "Personalized" mode
2. Choose a user profile (generated by fake_user_generator.py)
3. Enter a search query
4. Receive recommendations based on user history

### Ontology Explorer

- Click "Explore Ontology" to browse concept hierarchies
- Search for concepts and explore relationships

## 🔍 Troubleshooting

### Common Issues

**"No module named 'neo4j'"**

```bash
pip install neo4j
```

**"Connection refused" to Neo4j**

- Make sure Neo4j is running
- Check your .env file credentials
- Verify the URI (usually bolt://localhost:7687)

**"File not found" errors**

- Update all file paths in the scripts to match your setup
- Make sure you've run the data fetching steps

**SciBERT model download fails**

```bash
# Install transformers properly
pip install transformers torch
```

**Embedding generation is slow**

- Use GPU if available (install `torch` with CUDA)
- Reduce batch size in generate_embeddings.py
- Process smaller datasets first

### Performance Tips

- **Use GPU**: Install PyTorch with CUDA for faster embedding generation
- **Increase RAM**: 8GB+ recommended for large datasets
- **SSD Storage**: Faster I/O for large data processing
- **Batch Processing**: Adjust batch sizes based on your hardware

## 📊 Data Sources & APIs

### OpenAlex Integration

- **Website**: https://openalex.org/
- **API Docs**: https://docs.openalex.org/
- **Rate Limits**: Be respectful, use your email
- **Data License**: CC0 (public domain)

### Scientific Domains Available

- Computer Science
- Artificial Intelligence
- Physics
- Biology
- Medicine
- Mathematics
- Engineering
- And many more...

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Update file paths in your modifications
4. Test with your own data
5. Commit changes (`git commit -m 'Add AmazingFeature'`)
6. Push to branch (`git push origin feature/AmazingFeature`)
7. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [OpenAlex](https://openalex.org/) for providing open scientific data
- [SciBERT](https://github.com/allenai/scibert) for scientific text embeddings
- [Neo4j](https://neo4j.com/) for graph database technology
- [Flask](https://flask.palletsprojects.com/) for the web framework

## 📧 Contact

Project Link: [https://github.com/anVSS1/Scientific-Article-Recommender](https://github.com/anVSS1/Scientific-Article-Recommender)

---

## ⚠️ IMPORTANT NOTES

1. **No Data Included**: This repository contains only code. You must fetch and generate your own data.

2. **Update All Paths**: Every script has hardcoded file paths that need to be updated for your system.

3. **OpenAlex Email Required**: You must add your email to the OpenAlex fetcher script.

4. **Hardware Requirements**: Embedding generation requires significant computational resources.

5. **Neo4j Setup**: You must install and configure Neo4j before running the application.

⭐ **Star this repo if you find it helpful!**

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
