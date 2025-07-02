#!/usr/bin/env python3
"""
Setup script for Scientific Article Recommender
This script helps set up the project after cloning from GitHub
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def check_python_version():
    """Check if Python version is 3.8+"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required. Current version:", sys.version)
        return False
    print("✅ Python version check passed")
    return True

def create_virtual_environment():
    """Create virtual environment"""
    if not os.path.exists("venv"):
        print("🔧 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", "venv"])
        print("✅ Virtual environment created")
    else:
        print("✅ Virtual environment already exists")

def install_requirements():
    """Install requirements"""
    pip_path = "venv\\Scripts\\pip" if os.name == "nt" else "venv/bin/pip"
    if os.path.exists("requirements.txt"):
        print("📦 Installing requirements...")
        subprocess.run([pip_path, "install", "-r", "requirements.txt"])
        print("✅ Requirements installed")
    else:
        print("❌ requirements.txt not found")

def setup_environment_file():
    """Set up environment file"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("🔧 Setting up environment file...")
            with open(".env.example", "r") as src, open(".env", "w") as dst:
                dst.write(src.read())
            print("✅ .env file created from template")
            print("⚠️  Please update .env with your actual Neo4j credentials")
        else:
            print("❌ .env.example not found")
    else:
        print("✅ .env file already exists")

def create_data_directories():
    """Create necessary data directories"""
    directories = [
        "data",
        "data/cleaned data",
        "data/embeddings", 
        "data/fetched data",
        "Website/data",
        "Website/data/embeddings"
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
    
    print("✅ Data directories created")

def check_neo4j():
    """Check if Neo4j is accessible"""
    try:
        from neo4j import GraphDatabase
        # Try to connect with default credentials
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "neo4j"))
        with driver.session() as session:
            result = session.run("RETURN 1")
            driver.close()
        print("✅ Neo4j connection successful")
        return True
    except Exception as e:
        print(f"⚠️  Neo4j connection failed: {e}")
        print("💡 Please make sure Neo4j is running and update your .env file")
        return False

def main():
    """Main setup function"""
    print("🚀 Setting up Scientific Article Recommender...")
    print("=" * 50)
    
    if not check_python_version():
        return
    
    create_virtual_environment()
    install_requirements()
    setup_environment_file()
    create_data_directories()
    
    print("\n" + "=" * 50)
    print("🎉 Setup completed!")
    print("\nNext steps:")
    print("1. Update .env file with your Neo4j credentials")
    print("2. Start Neo4j database")
    print("3. Run data preparation scripts:")
    print("   - python existing_scripts/generate_embeddings.py")
    print("   - python existing_scripts/import_data_to_neo4j.py")
    print("4. Start the web application:")
    print("   - cd Website && python app.py")

if __name__ == "__main__":
    main()
