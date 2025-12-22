# src/report_generator.py

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os

def generate_report(image_path, confidence, output_pdf="results/report.pdf"):
    os.makedirs("results", exist_ok=True)

    c = canvas.Canvas(output_pdf, pagesize=A4)
    width, height = A4

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, height - 50, "CivilAI – Crack Detection Report")

    # Subtitle
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 90, "AI-Based Structural Health Monitoring")

    # Image
    c.drawImage(image_path, 50, height - 450, width=400, height=300)

    # Details
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 480, f"Detected Class: Crack")
    c.drawString(50, height - 500, f"Confidence Score: {confidence:.2f}")
    c.drawString(50, height - 520, "Model: YOLOv8 (Custom Trained)")
    c.drawString(50, height - 540, "Project: CivilAI – StructScan")

    # Footer
    c.setFont("Helvetica-Oblique", 10)
    c.drawString(50, 50, "Generated automatically using CivilAI")

    c.save()

    return output_pdf

