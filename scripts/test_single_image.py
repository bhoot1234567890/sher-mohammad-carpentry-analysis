#!/usr/bin/env python3
"""
Test Single Image - Quick demonstration of the analysis system
"""

import base64
import json
import os
import glob
from mistralai import Mistral
import dotenv
from datetime import datetime

# Load environment variables
dotenv.load_dotenv()

# Configuration
api_key = os.environ.get("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("MISTRAL_API_KEY environment variable not set")

model = "mistral-small-latest"
client = Mistral(api_key=api_key)

def encode_image(image_path):
    """Encode image to base64 for API transmission"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def test_single_image():
    """Test analysis on a single image"""
    
    # Get first image
    image_files = sorted(glob.glob("photos/WhatsApp Image*.jpeg"))
    
    if not image_files:
        print("No images found in photos/ directory")
        return
    
    image_path = image_files[0]  # Use the first image
    filename = os.path.basename(image_path)
    
    print(f"Testing analysis on: {filename}")
    print(f"Image size: {os.path.getsize(image_path)} bytes")
    
    # Encode image
    base64_image = encode_image(image_path)
    
    # Simple test prompt
    prompt = """
    DESCRIBE THIS CARPENTRY IMAGE:
    
    Provide a detailed 2-3 sentence description focusing on:
    - What is shown (be specific about the carpentry work)
    - Materials used
    - Visible techniques or craftsmanship details
    - Overall quality and aesthetic appeal
    
    Be technical and specific where possible.
    """
    
    messages = [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": f"data:image/jpeg;base64,{base64_image}"
                }
            ]
        }
    ]
    
    try:
        print("Sending request to Mistral AI...")
        
        chat_response = client.chat.complete(
            model=model,
            messages=messages,
            temperature=0.3
        )
        
        description = chat_response.choices[0].message.content.strip()
        
        print("\n=== ANALYSIS RESULT ===")
        print(f"Filename: {filename}")
        print(f"Description: {description}")
        print("\n=== SUCCESS ===")
        print("The analysis system is working correctly!")
        print("You can now run the full analysis using:")
        print("python continue_image_analysis.py")
        
        # Save this test result
        test_result = {
            "filename": filename,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "status": "test_successful",
            "message": "API connection and analysis working correctly"
        }
        
        with open("test_result.json", "w") as f:
            json.dump(test_result, f, indent=2)
        
        print(f"\nTest result saved to: test_result.json")
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        print("Please check:")
        print("- Your Mistral API key is valid")
        print("- You have sufficient API quota")
        print("- Your internet connection is stable")
        
        # Save error result
        error_result = {
            "filename": filename,
            "error": str(e),
            "timestamp": datetime.now().isoformat(),
            "status": "test_failed"
        }
        
        with open("test_error.json", "w") as f:
            json.dump(error_result, f, indent=2)
        
        print(f"Error details saved to: test_error.json")

if __name__ == "__main__":
    test_single_image()
