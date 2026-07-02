#!/usr/bin/env python
"""
Test script to verify Boto3 is installed and working.
This is our first step in building the secure document analyzer!
"""

# Import the boto3 library - this is how we talk to AWS services
import boto3

# Print the version to confirm it's working
print(f"Boto3 version: {boto3.__version__}")

# Let's also check if we can create an S3 client
# This will verify AWS credentials are configured
try:
    s3_client = boto3.client('s3')
    print("✓ Successfully created S3 client!")
    print("  (This means AWS credentials are configured)")
except Exception as e:
    print(f"✗ Could not create S3 client: {e}")
    print("  (You may need to configure AWS credentials)")

print("\nEnvironment setup is ready for the secure document analyzer!")