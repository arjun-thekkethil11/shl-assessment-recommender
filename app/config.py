# app/config.py

# Whether to use sentence-transformer embeddings instead of TF-IDF
USE_EMBEDDINGS = False  # keep False for now unless you've installed sentence-transformers

# Name of the sentence-transformers model (used only if USE_EMBEDDINGS = True)
EMBEDDING_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

# Path to your scraped/built catalog
CATALOG_PATH = "data/catalog.csv"

# Maximum number of recommendations to return
MAX_K = 10
