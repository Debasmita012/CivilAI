# ui/app.py
import streamlit as st
from src.pipeline import load_models, detect_and_save
from pathlib import Path

st.set_page_config(page_title="CivilAI - StructScan", layout="wide")
st.title("CivilAI — StructScan AI (Demo)")

models = load_models()

uploaded = st.file_uploader("Upload image", type=["jpg","jpeg","png"])
if uploaded:
    temp_path = "temp_uploaded.jpg"
    with open(temp_path, "wb") as f:
        f.write(uploaded.getbuffer())
    out = detect_and_save(temp_path, models, out_image="results/detections/temp_annotated.jpg")
    st.image(out, caption="Annotated result", use_column_width=True)
