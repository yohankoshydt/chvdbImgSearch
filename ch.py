import clickhouse_connect
from pymongo import MongoClient
from imgsrh import get_nomic_image_embedding


import clickhouse_connect


client = clickhouse_connect.get_client(
    host='xr9uc81b3l.us-east-1.aws.clickhouse.cloud',
    user='yohan_pyclient',
    password='Abc123+=%123',
    secure=True
)
print("Result:", client.query("SELECT 1").result_set[0][0])


def mongo_all_rows():
    
    uri = "mongodb+srv://yohankoshy:S9tUl13m8Cpt6Q5q@all.sze161o.mongodb.net/?retryWrites=true&w=majority&appName=All"


    # Connect to your MongoDB
    client = MongoClient(uri)
    db = client["vectors"]               # Replace with your database name
    collection = db["image_embeddings"]  # Replace with your collection name

    # Fetch all documents
    all_docs = list(collection.find({}))

    # Example: Print all image paths
    return all_docs

# data = []
# docs = mongo_all_rows()
# for doc in docs:
#     data.append([doc['image_path'],doc['embedding']])

# client.insert('images', data, column_names=['_file', 'image_embedding'])

query_vector = get_nomic_image_embedding(r'photos_no_class\cat-g0fcd844a4_640.jpg')

def search_image_embeddings(query_embedding, top_k=10):

    query = f"""
    WITH {query_embedding} AS reference_vector
    SELECT _file, image_embedding as vectors
    FROM images
    ORDER BY cosineDistance(vectors, reference_vector)
    LIMIT {top_k}
    """

    result = client.query(query)

    return result.result_rows





