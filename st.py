
import os
import cv2
import streamlit as st
from imgsrh import get_nomic_image_embedding, get_nomic_text_embedding
from ch import search_image_embeddings
from upload import get_face
# --- Import or define your functions here ---
# from your_module import get_nomic_image_embedding, get_nomic_text_embedding, upload_image_embedding, search_image_embeddings

st.title("Image Search")

mode = st.radio("Search mode:", ["By Image", "By Text Prompt"])

embedding = None
image_path = None
prompt = None

upload_to_db = False

if mode == "By Image":
    uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        temp_path = f"temp_uploaded_{uploaded_file.name}"
        img_bytes = uploaded_file.read()
        with open(temp_path, "wb") as f:
            f.write(img_bytes)
        image_path = temp_path
        face = get_face(img_bytes)
        image_path = 'face.jpg'
        with open(image_path, "wb") as f:
            cv2.imwrite(image_path, face)
        embedding = get_nomic_image_embedding(image_path)
        st.image(temp_path, caption="Uploaded Image", width = 300)
elif mode == "By Text Prompt":
    prompt = st.text_input("Enter text prompt:")
    if prompt:
        result = get_nomic_text_embedding([prompt])
        embedding = result["embeddings"][0]
        st.write(f"Prompt embedding: {embedding[:8]}...")

# top_k = st.number_input("How many similar images to return?", min_value=1, max_value=100, value=10)

top_k = 1
if embedding is not None and st.button("Search Similar Images"):
    
    st.write("Searching...")
    results = search_image_embeddings(embedding, top_k=top_k)
    if results:
        
        for result in results:
            path = result[0].replace('\\', '/')
            st.write(f"Image Path: {path}")
            st.write(f"Similarity Score: {result[2] * 100:.2f}%")
            # Optionally display thumbnails if accessible by path
            st.image(os.path.join('images', path), caption=path, width=300,)
    else:
        st.warning("No similar images found.")
