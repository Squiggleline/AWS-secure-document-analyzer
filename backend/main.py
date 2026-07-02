#!/usr/bin/env python
"""
Secure Document Analyzer - Main Module
This is the main entry point that combines all the modules.
"""

# Import our modules
from s3_upload import upload_document
from textract_analyzer import extract_text_simple
from comprehend_analyzer import detect_language, detect_sentiment, extract_entities, extract_key_phrases

def analyze_document(file_path, bucket_name, document_name=None):
    """
    Complete workflow: upload document and analyze its content.
    
    Parameters:
        file_path (str): Path to the local document file
        bucket_name (str): Name of your S3 bucket
        document_name (str, optional): Name for the document in S3
    
    Returns:
        dict: Analysis results including text, sentiment, entities, and key phrases
    """
    
    # Step 1: Upload the document to S3
    print("Step 1: Uploading document to S3...")
    if not upload_document(file_path, bucket_name, document_name):
        return None
    
    # Step 2: Extract text using Textract
    print("\nStep 2: Extracting text with Textract...")
    if document_name is None:
        document_name = file_path.split('/')[-1]  # Get filename from path
    
    extracted_text = extract_text_simple(bucket_name, document_name)
    if not extracted_text:
        return None
    
    # Step 3: Analyze the text with Comprehend
    print("\nStep 3: Analyzing text with Comprehend...")
    
    # Detect language
    language = detect_language(extracted_text)
    print(f"Language detected: {language}")
    
    # Detect sentiment
    sentiment = detect_sentiment(extracted_text, language)
    
    # Extract entities
    entities = extract_entities(extracted_text, language)
    
    # Extract key phrases
    key_phrases = extract_key_phrases(extracted_text, language)
    
    # Return all results
    return {
        'text': extracted_text,
        'language': language,
        'sentiment': sentiment,
        'entities': entities,
        'key_phrases': key_phrases
    }

# This code runs when you execute the script directly
if __name__ == "__main__":
    print("Secure Document Analyzer")
    print("=" * 50)
    
    print("\nUsage:")
    print("  analyze_document('path/to/file.pdf', 'your-bucket-name')")
    print("\nOr run the Comprehend test to see text analysis in action:")
    print("  python comprehend_analyzer.py")