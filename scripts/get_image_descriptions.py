#!/usr/bin/env python3
"""
Get Image Descriptions - Simple text descriptions for all images
"""

import base64
import json
import os
import glob
from mistralai import Mistral
import dotenv
from datetime import datetime
import time

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

def get_image_description(image_path, filename):
    """Get a text description of a carpentry image"""
    
    base64_image = encode_image(image_path)
    
    # Simple text prompt
    prompt = f"""
    DESCRIBE THIS CARPENTRY IMAGE:
    
    Provide a detailed 2-3 sentence description focusing on:
    - What is shown (furniture type, architectural element, tool, material, etc.)
    - Materials used (wood types, finishes, hardware)
    - Visible techniques or craftsmanship details
    - Overall quality and aesthetic appeal
    - Any unique or notable features
    
    Be specific and technical where possible.
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
        chat_response = client.chat.complete(
            model=model,
            messages=messages,
            temperature=0.3
        )
        
        description = chat_response.choices[0].message.content.strip()
        
        return {
            "filename": filename,
            "description": description,
            "timestamp": datetime.now().isoformat(),
            "file_size": os.path.getsize(image_path)
        }
        
    except Exception as e:
        print(f"Error analyzing {filename}: {str(e)}")
        return None

def main():
    """Main function"""
    
    # Get all image files
    image_files = sorted(glob.glob("photos/WhatsApp Image*.jpeg"))
    
    print(f"Found {len(image_files)} images to analyze")
    
    results = []
    
    # Load existing results if available
    if os.path.exists("image_descriptions.json"):
        with open("image_descriptions.json", "r") as f:
            results = json.load(f)
        
        processed_files = {result['filename'] for result in results}
        image_files = [f for f in image_files if os.path.basename(f) not in processed_files]
        
        print(f"Resuming from previous run. {len(processed_files)} files already processed.")
    
    total_images = len(image_files)
    
    for i, image_path in enumerate(image_files):
        filename = os.path.basename(image_path)
        
        print(f"\nProcessing image {i+1}/{total_images}: {filename}")
        
        analysis = get_image_description(image_path, filename)
        
        if analysis:
            results.append(analysis)
            print(f"✓ Successfully analyzed {filename}")
            print(f"Description: {analysis['description'][:100]}...")
            
            # Save after each image
            with open("image_descriptions.json", "w") as f:
                json.dump(results, f, indent=2)
            
            print(f"Saved results ({len(results)} images total)")
        else:
            print(f"✗ Failed to analyze {filename}")
        
        # Rate limiting - be gentle with API
        if i < total_images - 1:
            print(f"Waiting 5 seconds before next image...")
            time.sleep(5)
    
    print(f"\n=== ANALYSIS COMPLETE ===")
    print(f"Successfully analyzed {len(results)} images")
    print(f"Results saved to: image_descriptions.json")
    
    # Print some sample descriptions
    print(f"\n=== SAMPLE DESCRIPTIONS ===")
    for i, result in enumerate(results[:3]):  # Show first 3 samples
        print(f"\n{result['filename']}:")
        print(f"{result['description']}")

if __name__ == "__main__":
    main()
