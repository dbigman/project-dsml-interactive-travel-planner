import chromadb

# Load News Articles ChromaDB
news_client = chromadb.PersistentClient(path="./chromadb")  # Replace with the correct path
news_articles_collection = news_client.get_or_create_collection("news_articles")

# Load Municipalities ChromaDB
municipalities_client = chromadb.PersistentClient(path="./chromadb_municipalities")  # Replace with correct path
municipalities_collection = municipalities_client.get_or_create_collection("municipalities")

# Load Landmarks ChromaDB
landmarks_client = chromadb.PersistentClient(path="./chromadb_landmarks")  # Replace with correct path
landmarks_collection = landmarks_client.get_or_create_collection("landmarks")

# Verify if collections exist
print("News Collections:", news_client.list_collections())
print("Municipalities Collections:", municipalities_client.list_collections())
print("Landmarks Collections:", landmarks_client.list_collections())