import requests
import os

from dotenv import load_dotenv
load_dotenv()

NOMIC_API_KEY = os.getenv("NOMIC_API_KEY")  # Or paste your API key string here

def get_nomic_image_embedding(image_path):
    """
    Get image embedding from Nomic Atlas API.
    :param image_path: Path to the image file.
    :return: Embedding vector as a list.
    """
    url = "https://api-atlas.nomic.ai/v1/embedding/image"
    headers = {
        "Authorization": f"Bearer {NOMIC_API_KEY}",
    }
    files = {
        "model": (None, "nomic-embed-vision-v1.5"),
        "images": open(image_path, "rb"),
    }
    
    response = requests.post(url, headers=headers, files=files)
    response.raise_for_status()
    
    return response.json().get("embeddings", [])[0]


def get_nomic_text_embedding(texts, 
                              
                             max_tokens_per_text=8192, 
                             dimensionality=768):
    """
    Get text embeddings from Nomic API.

    Args:
        api_key (str): Your Bearer token.
        texts (list): List of text strings to embed.
        task_type (str): Nomic task type (default: "search_document").
        max_tokens_per_text (int): Max tokens per text.
        dimensionality (int): Embedding dimensionality.

    Returns:
        dict: API response with embeddings.
    """
    url = "https://api-atlas.nomic.ai/v1/embedding/text"
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {NOMIC_API_KEY}",
    }
    data = {
        "texts": texts,
        "task_type": "search_query",
        "max_tokens_per_text": max_tokens_per_text,
        "dimensionality": dimensionality
    }

    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()  # Raises error if not 2xx

    return response.json()

def get_nomic_image_embeddings(image_dir, batch_size=20, exts=(".jpg", ".jpeg", ".png")):
    load_dotenv()
    NOMIC_API_KEY = os.getenv("NOMIC_API_KEY")
    url = "https://api-atlas.nomic.ai/v1/embedding/image"
    headers = {
        "Authorization": f"Bearer {NOMIC_API_KEY}",
    }

    # Gather image files
    image_files = [os.path.join(image_dir, f)
                   for f in os.listdir(image_dir)
                   if f.lower().endswith(exts)]
    results = {}

    # Batch processing
    for i in range(0, len(image_files)//3, batch_size):
        batch_files = image_files[i:i+batch_size]
        files = [("model", (None, "nomic-embed-vision-v1.5"))]
        file_objs = []
        try:
            # Open all image files in this batch
            for fname in batch_files:
                fobj = open(fname, "rb")
                files.append(("images", fobj))
                file_objs.append(fobj)
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
            embeddings = response.json().get("embeddings", [])
            for fname, emb in zip(batch_files, embeddings):
                results[fname] = emb
        finally:
            # Always close files
            for fobj in file_objs:
                fobj.close()
    return results



from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://yohankoshy:S9tUl13m8Cpt6Q5q@all.sze161o.mongodb.net/?retryWrites=true&w=majority&appName=All"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))

# # Send a ping to confirm a successful connection
# try:
#     client.admin.command('ping')
#     print("Pinged your deployment. You successfully connected to MongoDB!")
# except Exception as e:
#     print(e)


def upload_image_embedding(image_path, embedding):
    """
    Uploads an image's embedding and file path to MongoDB, but only if image_path does NOT exist.
    """
    mongo_uri, db_name, collection_name = uri, "vectors", "image_embeddings"
    # If embedding is numpy array, convert to list
    if not isinstance(embedding, list):
        embedding = embedding.tolist()

    client = MongoClient(mongo_uri)
    collection = client[db_name][collection_name]

    # Check if this image_path is already present
    existing = collection.find_one({"image_path": image_path})
    if existing:
        print(f"Embedding for {image_path} already exists in collection (id={existing['_id']})")
        return

    doc = {
        "image_path": image_path,
        "embedding": embedding
    }

    result = collection.insert_one(doc)
    print(f"Inserted document with id {result.inserted_id}")


def embed_image_or_text(image_path_or_text):
    """
    Embeds an image or text using Nomic Atlas API.
    
    :param image_path_or_text: Path to the image file or text string.
    :return: Embedding vector as a list.
    """
    if os.path.isfile(image_path_or_text):
        return get_nomic_image_embedding(image_path_or_text)
    else:
        # For text, you can implement a similar function if needed
        raise ValueError("Currently only image embedding is supported.")

def search_image_embeddings(query_embedding, top_k=10):
    client = MongoClient(uri)
    collection = client["vectors"]["image_embeddings"]

    if not isinstance(query_embedding, list):
        query_embedding = query_embedding.tolist()

    db = client["vectors"]
    results = db.image_embeddings.aggregate([
    {
        "$vectorSearch": {
        "index": "vector_index",
        "path": "embedding",
        "queryVector": query_embedding,
        "numCandidates": 50,
        "limit": top_k
        }
    }
    ])

    return results




if __name__ == "__main__":
    pass

    # for file in os.listdir("photos_no_class"):
    #     if file.endswith((".jpg", ".jpeg", ".png")):
    #         image_path = os.path.join("photos_no_class", file)
    #         embedding = get_nomic_image_embedding(image_path)
    #         upload_image_embedding(image_path, embedding)