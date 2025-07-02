# 🚀 GitHub Upload Guide - Scientific Article Recommender

## 📋 Pre-Upload Checklist

Before uploading to GitHub, make sure you have:

- [x] All code files documented and commented
- [x] Personal information removed (email, passwords)
- [x] README.md created
- [x] requirements.txt created
- [x] .gitignore configured
- [x] LICENSE file added

## 🛠️ Step-by-Step GitHub Upload Process

### Step 1: Install Git (if not already installed)

Download and install Git from: https://git-scm.com/downloads

### Step 2: Open Terminal/Command Prompt

Navigate to your project directory:

```bash
cd "c:\Users\VSS\Desktop\WebAPP - Copy"
```

### Step 3: Initialize Git Repository

```bash
git init
```

### Step 4: Configure Git (First Time Setup)

Replace with your GitHub username and email:

```bash
git config --global user.name "Your GitHub Username"
git config --global user.email "your.email@example.com"
```

### Step 5: Add All Files to Git

```bash
git add .
```

### Step 6: Check What Files Will Be Committed

```bash
git status
```

This shows you what files will be uploaded. Make sure no sensitive data is listed!

### Step 7: Make Your Initial Commit

```bash
git commit -m "Initial commit: Scientific Article Recommender System

- Complete Flask web application for article recommendations
- Hybrid recommendation engine with SciBERT embeddings
- Neo4j integration for graph-based recommendations
- Comprehensive documentation and setup guides
- Data processing scripts for OpenAlex integration"
```

### Step 8: Create GitHub Repository

1. **Go to GitHub.com** and sign in
2. **Click the "+" icon** in the top right
3. **Select "New repository"**
4. **Fill in repository details:**
   - Repository name: `scientific-article-recommender`
   - Description: `A hybrid recommendation system for scientific papers using SciBERT embeddings and Neo4j`
   - Set to **Public** (or Private if you prefer)
   - **DON'T** initialize with README (you already have one)
   - **DON'T** add .gitignore (you already have one)
   - **DON'T** choose a license (you already have one)
5. **Click "Create repository"**

### Step 9: Connect Local Repository to GitHub

Copy the commands from GitHub (they'll look like this):

```bash
git remote add origin https://github.com/YOUR_USERNAME/scientific-article-recommender.git
git branch -M main
git push -u origin main
```

### Step 10: Upload to GitHub

```bash
git push -u origin main
```

## 🎯 Alternative: Using GitHub Desktop (Easier Option)

### Option A: GitHub Desktop

1. **Download GitHub Desktop**: https://desktop.github.com/
2. **Install and sign in** with your GitHub account
3. **Click "Add an Existing Repository from your hard drive"**
4. **Select your project folder**: `c:\Users\VSS\Desktop\WebAPP - Copy`
5. **Click "create a repository"** if prompted
6. **Write commit message**: "Initial commit: Scientific Article Recommender"
7. **Click "Commit to main"**
8. **Click "Publish repository"**
9. **Fill in repository name and description**
10. **Click "Publish Repository"**

## 📁 What Will Be Uploaded

### ✅ Files That WILL Be Uploaded:

```
├── Website/                     # Flask web application
│   ├── app.py
│   ├── backend/reco.py
│   ├── templates/
│   └── data/ (empty folders)
├── existing_scripts/            # Data processing scripts
│   ├── *.py files
│   └── openalec-fetcher.ipynb
├── README.md                    # Project documentation
├── requirements.txt             # Dependencies
├── .gitignore                   # File exclusions
├── LICENSE                      # MIT license
├── setup.py                     # Setup script
├── config_template.py           # Configuration template
├── .env.example                 # Environment template
├── DEVELOPER_GUIDE.md           # Development guide
└── scientific_recommender.owl   # Ontology file
```

### ❌ Files That WON'T Be Uploaded (Good!):

```
├── __pycache__/                 # Python cache files
├── data/fetched data/           # Large data files
├── data/embeddings/             # Generated embeddings
├── data/cleaned data/           # Processed data
├── .env                         # Your actual passwords
├── presentation.pptx            # Presentation file
├── web_reco.pdf                 # PDF file
└── .qodo/                       # IDE files
```

## 🔍 Verify Upload Success

1. **Check your GitHub repository** in the browser
2. **Verify README.md displays properly** on the main page
3. **Check that sensitive files are NOT visible**
4. **Test the repository by cloning it elsewhere**:
   ```bash
   git clone https://github.com/YOUR_USERNAME/scientific-article-recommender.git
   ```

## 🎉 Post-Upload Steps

### 1. Add Repository Topics/Tags

In your GitHub repository:

- Go to "Settings" > "General"
- Add topics: `machine-learning`, `recommendation-system`, `neo4j`, `flask`, `scibert`, `python`

### 2. Enable GitHub Pages (Optional)

- Go to "Settings" > "Pages"
- Deploy documentation if needed

### 3. Add Repository Description

Edit the repository description at the top to match your README

### 4. Star Your Own Repository

Give your project a star to show it's active!

## 🆘 Troubleshooting

### Problem: "Permission denied"

**Solution**: Set up SSH keys or use GitHub Desktop

### Problem: "Files too large"

**Solution**: Check if any large files sneaked in:

```bash
find . -size +100M
```

### Problem: "Authentication failed"

**Solution**: Use a Personal Access Token instead of password

### Problem: "Repository already exists"

**Solution**: Either choose a different name or delete the existing repository

## 🎯 Quick Commands Summary

```bash
# Navigate to project
cd "c:\Users\VSS\Desktop\WebAPP - Copy"

# Initialize and upload
git init
git add .
git commit -m "Initial commit: Scientific Article Recommender System"
git remote add origin https://github.com/YOUR_USERNAME/scientific-article-recommender.git
git branch -M main
git push -u origin main
```

**Your project is now ready for the world to see! 🌟**
