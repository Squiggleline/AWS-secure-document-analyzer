#!/usr/bin/env python
"""
Create a simple test PDF for Textract testing
"""

# We'll use reportlab to create a simple PDF
# First, let's check if it's installed, if not we'll install it

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    
    # Create a simple PDF
    c = canvas.Canvas("backend/test_document.pdf", pagesize=letter)
    c.drawString(100, 750, "Amazon Web Services is a cloud computing platform based in Seattle, Washington.")
    c.drawString(100, 700, "It provides a wide range of services including computing power, storage, and databases.")
    c.drawString(100, 650, "AWS is used by millions of customers worldwide for building scalable applications.")
    c.save()
    
    print("Created test_document.pdf successfully!")
    
except ImportError:
    print("reportlab not installed. Installing...")
    import subprocess
    subprocess.run(["pip", "install", "reportlab"])
    print("Please run this script again after installation.")