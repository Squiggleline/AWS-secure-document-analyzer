#!/usr/bin/env python
"""
Secure Document Analyzer - Comprehend Module
This module handles text analysis using Amazon Comprehend.
"""

import boto3
from botocore.exceptions import ClientError

# Create a Comprehend client - this is our connection to AWS Comprehend
comprehend_client = boto3.client('comprehend')

def detect_language(text):
    """
    Detect the language of the text.
    
    Parameters:
        text (str): The text to analyze
    
    Returns:
        str: The detected language code (e.g., 'en' for English)
    """
    
    try:
        response = comprehend_client.detect_dominant_language(Text=text)
        languages = response.get('Languages', [])
        if languages:
            return languages[0]['LanguageCode']
        return None
        
    except ClientError as e:
        print(f"✗ Error detecting language: {e}")
        return None

def detect_sentiment(text, language_code='en'):
    """
    Detect the sentiment of the text.
    
    Parameters:
        text (str): The text to analyze
        language_code (str): Language code (default: 'en' for English)
    
    Returns:
        dict: Sentiment analysis results (POSITIVE, NEGATIVE, NEUTRAL, MIXED)
    """
    
    try:
        response = comprehend_client.detect_sentiment(
            Text=text,
            LanguageCode=language_code
        )
        
        sentiment = response['Sentiment']
        confidence = response['SentimentScore']
        
        print(f"✓ Sentiment detected: {sentiment}")
        return {
            'sentiment': sentiment,
            'confidence': confidence
        }
        
    except ClientError as e:
        print(f"✗ Error detecting sentiment: {e}")
        return None

def extract_entities(text, language_code='en'):
    """
    Extract named entities from the text.
    
    Parameters:
        text (str): The text to analyze
        language_code (str): Language code (default: 'en' for English)
    
    Returns:
        list: List of entities found (PERSON, LOCATION, ORGANIZATION, etc.)
    """
    
    try:
        response = comprehend_client.detect_entities(
            Text=text,
            LanguageCode=language_code
        )
        
        entities = response.get('Entities', [])
        print(f"✓ Found {len(entities)} entities")
        return entities
        
    except ClientError as e:
        print(f"✗ Error extracting entities: {e}")
        return None

def extract_key_phrases(text, language_code='en'):
    """
    Extract key phrases from the text.
    
    Parameters:
        text (str): The text to analyze
        language_code (str): Language code (default: 'en' for English)
    
    Returns:
        list: List of key phrases found
    """
    
    try:
        response = comprehend_client.detect_key_phrases(
            Text=text,
            LanguageCode=language_code
        )
        
        key_phrases = response.get('KeyPhrases', [])
        print(f"✓ Found {len(key_phrases)} key phrases")
        return key_phrases
        
    except ClientError as e:
        print(f"✗ Error extracting key phrases: {e}")
        return None

# This code runs when you execute the script directly
if __name__ == "__main__":
    print("Comprehend Module for Secure Document Analyzer")
    print("=" * 50)
    
    # Example text for testing
    sample_text = "Amazon Web Services is a cloud computing platform based in Seattle, Washington."
    
    print(f"\nAnalyzing sample text: '{sample_text}'")
    
    # Detect language
    language = detect_language(sample_text)
    print(f"Detected language: {language}")
    
    # Detect sentiment
    sentiment = detect_sentiment(sample_text)
    if sentiment:
        print(f"Sentiment: {sentiment['sentiment']}")
    
    # Extract entities
    entities = extract_entities(sample_text)
    if entities:
        print("Entities found:")
        for entity in entities:
            print(f"  - {entity['Text']} ({entity['Type']})")