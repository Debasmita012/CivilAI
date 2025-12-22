import sys
import os
import cv2
import time
import streamlit as st
import numpy as np

# --------------------------------------------------
# Project Root (important for imports)
# --------------------------------------------------
PROJECT_ROOT = os.getcwd()
sys.path.insert(0, PROJECT_ROOT)

from src.pipeline import load_models, detect_and_save
from src.report_generator import generate_pdf_report

# --------------------------------------------------
# Streamlit Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="CiviAI | Structural Crack Detection",
    page_icon="🏗️",
    layout="wide"
)

# --------------------------------------------------
# Basic CSS
# --------------------------------------------------
st.markdown("""
<style>
.card {
    background-color: #0e1117;
    padding: 1.2rem;
    border-radius: 12px;
    margin-bottom: 20px;
}
.header {
    background: linear-gradient(90deg, #1f4037, #99f2c8);
    padding: 1.5rem;
    border-radius: 14px;
    color: white;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown("""
<div class="header">
    <h1>🏗️ CiviAI – Structural Crack Detection</h1>
    <p>AI-based crack detection & risk analysis</p>
</div>
""", unsafe_allow_html=True)

# --------------------------------------------------
# Load Model
# --------------------------------------------------
@st.cache_resource
def load_yolo():
    return load_models()

with st.spinner("Loading AI model..."):
    models = load_yolo()

# --------------------------------------------------
# Upload Image
# --------------------------------------------------
st.markdown('<div class="card">', unsafe_allow_html=True)

uploaded_file = st.file_uploader(
    "📤 Upload structural image",
    type=["jpg", "jpeg", "png"]
)

st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# Paths
# --------------------------------------------------
UPLOAD_PATH = os.path.join(PROJECT_ROOT, "temp_uploaded.jpg")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "results")
OUTPUT_IMAGE = os.path.join(OUTPUT_DIR, "annotated.jpg")
PDF_PATH = os.path.join(OUTPUT_DIR, "CiviAI_Report.pdf")

os.makedirs(OUTPUT_DIR, exist_ok=True)

# --------------------------------------------------
# Detection
# --------------------------------------------------
if uploaded_file is not None:

    # Save image
    with open(UPLOAD_PATH, "wb") as f:
        f.write(uploaded_file.getbuffer())

    st.success("Image uploaded successfully")

    with st.spinner("Analyzing cracks..."):
        annotated_img, crack_percentage, risk_level, severity_score = detect_and_save(
            UPLOAD_PATH,
            models,
            OUTPUT_IMAGE
        )

    annotated_img = cv2.cvtColor(annotated_img, cv2.COLOR_BGR2RGB)

    # --------------------------------------------------
    # Results
    # --------------------------------------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🔍 Detection Result")
    st.image(annotated_img, caption="Detected cracks")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    col1.metric("Crack Percentage", f"{crack_percentage:.2f}%")
    col2.metric("Severity Score", f"{severity_score:.1f}/100")

    if risk_level == "Low":
        col3.success("🟢 LOW RISK")
    elif risk_level == "Medium":
        col3.warning("🟡 MEDIUM RISK")
    else:
        col3.error("🔴 HIGH RISK")

    # --------------------------------------------------
    # Engineer & Project Info  ✅ (YOUR REQUEST)
    # --------------------------------------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("👷 Engineer & Project Information")

    engineer_name = st.text_input("👷 Engineer Name", "Rishi Poddar")
    project_id = st.text_input("📌 Project ID", "CIV-001")

    st.markdown('</div>', unsafe_allow_html=True)

    # --------------------------------------------------
    # PDF Report
    # --------------------------------------------------
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("📄 Inspection Report")

    if st.button("Generate PDF Report"):
        generate_pdf_report(
            PDF_PATH,
            crack_percentage,
            risk_level,
            severity_score,
            OUTPUT_IMAGE,
            engineer_name,
            project_id
        )

        with open(PDF_PATH, "rb") as pdf:
            st.download_button(
                "⬇️ Download Report",
                data=pdf,
                file_name="CiviAI_Report.pdf",
                mime="application/pdf"
            )

    st.markdown('</div>', unsafe_allow_html=True)

# --------------------------------------------------
# Footer
# --------------------------------------------------
st.markdown("""
<hr>
<center>🚀 CiviAI – Civil Engineering AI Project</center>
""", unsafe_allow_html=True)