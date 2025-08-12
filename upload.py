import os
import clickhouse_connect
import numpy as np
import pandas as pd
from imgsrh import insightface_embedding
from tqdm import tqdm
import cv2
from io import BytesIO

def get_face(img_bytes):
    img = BytesIO(img_bytes)
    img = cv2.imdecode(np.frombuffer(img.read(), np.uint8), cv2.IMREAD_COLOR)
    if img is None:
        print("Error: Could not read image.")
        return None

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5)

    if len(faces) == 0:
        print("No face(s) found.")
        return None

    # Pick the largest face (by area), or just the first face
    x, y, w, h = max(faces, key=lambda rect: rect[2] * rect[3])  # largest face
    # x, y, w, h = faces[0]  # or just use the first detected face

    face = img[y:y+h, x:x+w]
    return face

  



if __name__ == "__main__":

    client = clickhouse_connect.get_client(
    host='xr9uc81b3l.us-east-1.aws.clickhouse.cloud',
    user='yohan_pyclient',
    password='Abc123+=%123',
    secure=True
)
    print("Result:", client.query("SELECT 1").result_set[0][0])

    data = []
    images = os.listdir('images')
    i = 0
    all_images = client.query("SELECT _file FROM images").result_set
    all_images = [img[0] for img in all_images]
    print(f"Found {len(all_images)} images in ClickHouse database.")
    images = [img for img in images if img not in all_images]
    print(f"Found {len(images)} new images to process.")
    for img in tqdm(images):
        print(f"Processing image: {img}")
        if i >= 2000:
            break
        
       
        embedding = insightface_embedding(os.path.join('images', img))
        if embedding is None:
            print(f"Skipping {img} due to no embedding found.")
            continue
        data.append([img, embedding])
        i += 1
        
    if data:
        print("Inserting data into ClickHouse...")
        print(f"Total images to insert: {len(data)}")
        # Insert data into ClickHouse
        client.insert('images', data, column_names=['_file', 'image_embedding'])
