#!/usr/bin/env python
"""
Quick test script for the MVP flow
"""

import os
import sys

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from s3_upload import upload_document
from textract_analyzer import extract_text_simple

# Test the flow - use PDF file
file_path = 'backend/test_document.pdf'
bucket_name = 'ai-security-uploads-2026'

print("Testing MVP Flow: Upload -> S3 -> Textract -> Text")
print("=" * 50)

# Step 1: Upload
print("\nStep 1: Uploading document...")
result = upload_document(file_path, bucket_name)
print(f"Upload result: {result}")

# Step 2: Extract text
if result:
    print("\nStep 2: Extracting text...")
    # Use just the filename for S3
    s3_key = os.path.basename(file_path)
    text = extract_text_simple(bucket_name, s3_key)
    if text:
        print("\nExtracted text:")
        print(text)
    else:
        print("Failed to extract text")