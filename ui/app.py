import os
import sys
import streamlit as st
import streamlit.components.v1 as components

# ==================================================
# PATH FIX
# ==================================================
PROJECT_ROOT = os.getcwd()
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from src.pipeline import load_models, run_pipeline
from src.report_generator import generate_pdf_report

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="StructScan AI",
    page_icon="🏗️",
    layout="wide",
)
def render_severity_gauge(severity, risk):
    color = {
        "Low": "#22c55e",     # green
        "Medium": "#f59e0b",  # orange
        "High": "#ef4444"     # red
    }[risk]

    angle = -90 + (severity / 100) * 180

    return f"""
    <div style="display:flex;justify-content:center;">
      <div style="position:relative;width:260px;height:130px;">

        <div style="
            width:260px;
            height:130px;
            border-radius:260px 260px 0 0;
            background:conic-gradient(
                #22c55e 0deg 60deg,
                #f59e0b 60deg 120deg,
                #ef4444 120deg 180deg
            );
        "></div>

        <div id="needle" style="
           position:absolute;
    width:4px;
    height:110px;
    background:{color};
    bottom:0;
    left:50%;
    transform-origin:bottom center;
    transform:rotate(-90deg);
    transition:transform 2.8s cubic-bezier(0.19, 1, 0.22, 1);
    box-shadow: 0 0 10px {color};
        "></div>

        <div style="
            position:absolute;
            width:14px;
            height:14px;
            background:white;
            border-radius:50%;
            bottom:-7px;
            left:calc(50% - 7px);
        "></div>

        <div style="
            text-align:center;
            margin-top:10px;
            font-size:1.2rem;
            font-weight:700;
        ">
            Severity: {severity:.1f} / 100
        </div>

        <script>
             setTimeout(() => {{
        document.getElementById("needle").style.transform =
        "rotate({angle}deg)";
    }}, 400);
        </script>

      </div>
    </div>
    """ 

# ==================================================
# SESSION STATE (PAGE CONTROL)
# ==================================================
if "page" not in st.session_state:
    st.session_state.page = "landing"

# ==================================================
# GLOBAL CSS (ANIMATION + THEME)
# ==================================================
st.markdown("""
<style>
@keyframes gradientMove {
    0% { background-position: 0% 50%; }
    50% { background-position: 100% 50%; }
    100% { background-position: 0% 50%; }
}

.stApp {
    background: linear-gradient(
        -45deg,
        #0f2027,
        #203a43,
        #2c5364,
        #16222a
    );
    background-size: 400% 400%;
    animation: gradientMove 18s ease infinite;
    color: white;
}

.glass {
    background: rgba(255,255,255,0.08);
    backdrop-filter: blur(16px);
    border-radius: 18px;
    padding: 32px;
    border: 1px solid rgba(255,255,255,0.15);
    box-shadow: 0 12px 45px rgba(0,0,0,0.35);
    margin-bottom: 24px;
}

.section-title {
    font-size: 1.6rem;
    font-weight: 700;
    margin-bottom: 18px;
}
</style>
""", unsafe_allow_html=True)

# ==================================================
# LANDING PAGE
# ==================================================
if st.session_state.page == "landing":

    components.html(
        """
        <div style="height:90vh;display:flex;align-items:center;justify-content:center;">
            <div style="
                background: rgba(255,255,255,0.08);
                backdrop-filter: blur(16px);
                border-radius: 18px;
                padding: 40px;
                border: 1px solid rgba(255,255,255,0.15);
                box-shadow: 0 12px 45px rgba(0,0,0,0.35);
                max-width: 900px;
                text-align: center;
                color: white;">
                <h1 style="font-size:3rem;">🏗️ StructScan AI</h1>
                <p style="font-size:1.2rem;opacity:0.85;">
                    AI-powered structural crack detection and damage assessment
                </p>
                <div style="display:flex;gap:40px;justify-content:center;flex-wrap:wrap;">
                    <div><h3>⚡ Fast</h3><p>Instant AI analysis</p></div>
                    <div><h3>🎯 Accurate</h3><p>Severity-driven scoring</p></div>
                    <div><h3>📄 Professional</h3><p>Auto-generated reports</p></div>
                </div>
            </div>
        </div>
        """,
        height=600,
    )

    if st.button("🚀 Start Inspection"):
        st.session_state.page = "inspection"
        st.rerun()

    st.stop()

# ==================================================
# INSPECTION PAGE
# ==================================================
st.markdown("""
<div style="text-align:center;margin-bottom:30px;">
    <h1>🏗️ StructScan AI</h1>
    <h4 style="opacity:0.8;">Structural Crack Inspection Dashboard</h4>
</div>
""", unsafe_allow_html=True)

# ==================================================
# INSPECTION DETAILS
# ==================================================
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📋 Inspection Details</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    engineer_name = st.text_input("👷 Engineer Name", "Rishi Poddar")
with col2:
    project_id = st.text_input("🆔 Project ID", "CIV-021")
with col3:
    construction_type = st.selectbox(
        "🏗️ Type of Construction",
        [
            "Residential Building",
            "Commercial Building",
            "Bridge / Flyover",
            "Industrial Structure",
            "Heritage Structure",
            "Other"
        ]
    )
st.markdown('</div>', unsafe_allow_html=True)

# ==================================================
# IMAGE UPLOAD
# ==================================================
st.markdown('<div class="glass">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📤 Upload Structural Image</div>', unsafe_allow_html=True)
uploaded_image = st.file_uploader("Upload image", type=["jpg", "jpeg", "png"])
st.markdown('</div>', unsafe_allow_html=True)

# ==================================================
# LOAD MODEL
# ==================================================
@st.cache_resource
def get_model():
    return load_models()

model = get_model()

# ==================================================
# RUN ANALYSIS
# ==================================================
if uploaded_image:
    temp_dir = os.path.join(PROJECT_ROOT, "results")
    os.makedirs(temp_dir, exist_ok=True)

    temp_image_path = os.path.join(temp_dir, "temp_uploaded.jpg")
    with open(temp_image_path, "wb") as f:
        f.write(uploaded_image.read())

    st.image(temp_image_path, use_container_width=True)

    if st.button("🚀 Run Structural Analysis"):
        with st.spinner("🔍 Analyzing cracks using AI..."):
            st.session_state.result = run_pipeline(
                model=model,
                image_path=temp_image_path,
                output_path=os.path.join(temp_dir, "annotated_output.jpg")
            )

# ==================================================
# RESULTS + HEATMAP + PDF
# ==================================================
if "result" in st.session_state:
    r = st.session_state.result

    # ---------- Severity Gauge ----------
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📈 Severity Gauge</div>', unsafe_allow_html=True)

    components.html(
        render_severity_gauge(
            severity=r["severity_score"],
            risk=r["risk_level"]
        ),
        height=280,
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- Metrics ----------
    c1, c2, c3 = st.columns(3)
    c1.metric("Crack Coverage (%)", f"{r['crack_percentage']:.2f}")
    c2.metric("Severity Score", f"{r['severity_score']:.1f}/100")
    c3.metric("Risk Level", r["risk_level"])

    # ---------- Risk Explanation ----------
    risk_explanation = {
        "Low": {
            "title": "🟢 Low Structural Risk",
            "text": "Minor surface-level cracks detected. Routine monitoring is sufficient."
        },
        "Medium": {
            "title": "🟡 Medium Structural Risk",
            "text": "Moderate cracks detected. Preventive repair and periodic inspection recommended."
        },
        "High": {
            "title": "🔴 High Structural Risk",
            "text": "Severe cracks detected. Immediate professional inspection required."
        }
    }

    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🧾 Risk Explanation</div>', unsafe_allow_html=True)
    st.markdown(
        f"*{risk_explanation[r['risk_level']]['title']}*  \n"
        f"{risk_explanation[r['risk_level']]['text']}"
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- Crack Visualization ----------
    heatmap_path = r.get("heatmap_path", None)

    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🧠 Crack Visualization</div>', unsafe_allow_html=True)

    view_mode = st.radio(
        "Visualization Mode",
        ["Bounding Boxes", "Heatmap"],
        horizontal=True
    )

    if view_mode == "Bounding Boxes":
        st.image(r["annotated_image"], use_container_width=True)
    elif heatmap_path:
        st.image(heatmap_path, use_container_width=True)
    else:
        st.warning("Heatmap not available.")

    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- Export Dashboard Snapshot ----------
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📸 Export Dashboard Snapshot</div>', unsafe_allow_html=True)

    if st.button("📸 Generate Dashboard Snapshot"):
        import cv2, numpy as np

        export_dir = os.path.join(PROJECT_ROOT, "reports")
        os.makedirs(export_dir, exist_ok=True)
        export_path = os.path.join(export_dir, "StructScan_Dashboard.png")

        annotated = r["annotated_image"]
        heatmap = cv2.imread(heatmap_path) if heatmap_path else None

        if heatmap is not None:
            combined = np.hstack([
                cv2.resize(annotated, (500, 400)),
                cv2.resize(heatmap, (500, 400))
            ])
        else:
            combined = cv2.resize(annotated, (1000, 400))

        cv2.imwrite(export_path, combined)

        with open(export_path, "rb") as img:
            st.download_button(
                "⬇️ Download Dashboard Snapshot",
                img,
                file_name="StructScan_Dashboard.png",
                mime="image/png"
            )

    st.markdown('</div>', unsafe_allow_html=True)

    # ---------- PDF ----------
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📄 Inspection Report</div>', unsafe_allow_html=True)

    if st.button("📥 Generate PDF Report"):
        report_path = os.path.join(PROJECT_ROOT, "reports", "StructScan_Report.pdf")

        generate_pdf_report(
            output_path=report_path,
            engineer_name=engineer_name,
            project_id=project_id,
            crack_percentage=float(r["crack_percentage"]),
            severity_score=float(r["severity_score"]),
            risk_level=str(r["risk_level"]),
            annotated_image_path=r["annotated_image_path"],
            heatmap_path=heatmap_path
        )

        with open(report_path, "rb") as f:
            st.download_button(
                "⬇️ Download PDF",
                f,
                file_name="StructScan_Report.pdf",
                mime="application/pdf"
            )

# ==================================================
# FOOTER
# ==================================================
st.markdown("""
<hr style="opacity:0.2;">
<center>
<small>© 2025 StructScan AI · AI-Based Structural Health Monitoring Platform</small>
</center>
""", unsafe_allow_html=True)