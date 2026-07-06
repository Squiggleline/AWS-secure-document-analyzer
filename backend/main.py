#!/usr/bin/env python
"""
Secure Document Analyzer - Main Module (MVP)
Simple CLI: User upload -> S3 -> Textract -> Return extracted text
"""

import sys
import os

# Import our modules
from s3_upload import upload_document
from textract_analyzer import extract_text_simple

def analyze_document(file_path, bucket_name, document_name=None):
    """
    Complete workflow: upload document and extract text.
    
    Parameters:
        file_path (str): Path to the local document file
        bucket_name (str): Name of your S3 bucket
        document_name (str, optional): Name for the document in S3
    
    Returns:
        str: The extracted text from the document
    """
    
    # Step 1: Upload the document to S3
    print("Step 1: Uploading document to S3...")
    if not upload_document(file_path, bucket_name, document_name):
        return None
    
    # Step 2: Extract text using Textract
    print("\nStep 2: Extracting text with Textract...")
    if document_name is None:
        document_name = os.path.basename(file_path)  # Get filename from path
    
    extracted_text = extract_text_simple(bucket_name, document_name)
    if not extracted_text:
        return None
    
    return extracted_text

# This code runs when you execute the script directly
if __name__ == "__main__":
    print("Secure Document Analyzer (MVP)")
    print("=" * 50)
    
    # Check if a file path was provided
    if len(sys.argv) < 2:
        print("\nUsage: python main.py <file_path> [bucket_name]")
        print("\nExample:")
        print("  python main.py my_document.pdf ai-security-uploads-2026")
        print("\nThe bucket name will default to 'ai-security-uploads-2026' if not provided.")
        sys.exit(1)
    
    file_path = sys.argv[1]
    bucket_name = sys.argv[2] if len(sys.argv) > 2 else "ai-security-uploads-2026"
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"\nError: File '{file_path}' not found.")
        sys.exit(1)
    
    # Run the analysis
    result = analyze_document(file_path, bucket_name)
    
    if result:
        print("\n" + "=" * 50)
        print("EXTRACTED TEXT:")
        print("=" * 50)
        print(result)
    else:
        print("\nFailed to extract text from document.")
        sys.exit(1)