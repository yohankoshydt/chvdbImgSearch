
import streamlit as st
from imgsrh import get_nomic_image_embedding, get_nomic_text_embedding
from ch import search_image_embeddings
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
        with open(temp_path, "wb") as f:
            f.write(uploaded_file.read())
        image_path = temp_path
        embedding = get_nomic_image_embedding(image_path)
        st.image(temp_path, caption="Uploaded Image", use_container_width=True)
elif mode == "By Text Prompt":
    prompt = st.text_input("Enter text prompt:")
    if prompt:
        result = get_nomic_text_embedding([prompt])
        embedding = result["embeddings"][0]
        st.write(f"Prompt embedding: {embedding[:8]}...")

top_k = st.number_input("How many similar images to return?", min_value=1, max_value=100, value=10)

if embedding is not None and st.button("Search Similar Images"):
    
    st.write("Searching...")
    results = search_image_embeddings(embedding, top_k=top_k)
    if results:
        
        for result in results:
            st.write(f"Image Path: {result[0]}")
            # Optionally display thumbnails if accessible by path
            st.image(result[0])
    else:
        st.warning("No similar images found.")
