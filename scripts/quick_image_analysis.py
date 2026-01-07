#!/usr/bin/env python3
"""
Quick Image Analysis - Gets basic descriptions for all images
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
    """Get a quick description of a carpentry image"""
    
    base64_image = encode_image(image_path)
    
    # Simple prompt for quick analysis
    prompt = f"""
    DESCRIBE THIS CARPENTRY IMAGE:
    
    Provide a concise JSON with these fields:
    - filename: "{filename}"
    - description: "[2-3 sentence description of what's shown]"
    - image_type: "[Close-up/Full view/Work-in-progress/Tool/Material/Other]"
    - primary_subject: "[Main subject of the image]"
    - materials: "[List of visible materials]"
    - techniques: "[List of visible carpentry techniques]"
    - keywords: "[3-5 relevant keywords for SEO]"
    
    Return ONLY valid JSON, no additional text.
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
        
        # Extract and parse the JSON response
        response_text = chat_response.choices[0].message.content
        
        # Clean up the response
        response_text = response_text.strip()
        if response_text.startswith('```json'):
            response_text = response_text[7:].strip()
        if response_text.endswith('```'):
            response_text = response_text[:-3].strip()
        
        # Parse JSON
        analysis_data = json.loads(response_text)
        
        # Add metadata
        analysis_data['timestamp'] = datetime.now().isoformat()
        analysis_data['file_size'] = os.path.getsize(image_path)
        
        return analysis_data
        
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
    if os.path.exists("quick_image_analysis.json"):
        with open("quick_image_analysis.json", "r") as f:
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
            
            # Save after each image
            with open("quick_image_analysis.json", "w") as f:
                json.dump(results, f, indent=2)
            
            print(f"Saved results ({len(results)} images total)")
        else:
            print(f"✗ Failed to analyze {filename}")
        
        # Rate limiting - be gentle with API
        if i < total_images - 1:
            time.sleep(4)  # 4 second delay between images
    
    print(f"\n=== ANALYSIS COMPLETE ===")
    print(f"Successfully analyzed {len(results)} images")
    print(f"Results saved to: quick_image_analysis.json")
    
    # Create summary
    create_summary(results)

def create_summary(results):
    """Create a summary report"""
    
    summary = {
        "total_images": len(results),
        "analysis_date": datetime.now().isoformat(),
        "image_types": {},
        "materials_found": set(),
        "techniques_found": set(),
        "keywords_frequency": {}
    }
    
    for result in results:
        # Count image types
        img_type = result.get('image_type', 'Unknown')
        summary['image_types'][img_type] = summary['image_types'].get(img_type, 0) + 1
        
        # Collect materials (handle both string and list formats)
        materials = result.get('materials', '')
        if isinstance(materials, list):
            for material in materials:
                summary['materials_found'].add(material)
        elif isinstance(materials, str):
            # Split string by commas
            for material in [m.strip() for m in materials.split(',')]:
                summary['materials_found'].add(material)
        
        # Collect techniques
        techniques = result.get('techniques', '')
        if isinstance(techniques, list):
            for technique in techniques:
                summary['techniques_found'].add(technique)
        elif isinstance(techniques, str):
            # Split string by commas
            for technique in [t.strip() for t in techniques.split(',')]:
                summary['techniques_found'].add(technique)
        
        # Keywords frequency
        keywords = result.get('keywords', '')
        if isinstance(keywords, list):
            for keyword in keywords:
                summary['keywords_frequency'][keyword] = summary['keywords_frequency'].get(keyword, 0) + 1
        elif isinstance(keywords, str):
            # Split string by commas
            for keyword in [k.strip() for k in keywords.split(',')]:
                summary['keywords_frequency'][keyword] = summary['keywords_frequency'].get(keyword, 0) + 1
    
    # Convert sets to sorted lists
    summary['materials_found'] = sorted(list(summary['materials_found']))
    summary['techniques_found'] = sorted(list(summary['techniques_found']))
    summary['keywords_frequency'] = dict(sorted(summary['keywords_frequency'].items(), 
                                               key=lambda x: x[1], reverse=True))
    
    with open("quick_image_analysis_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("Summary report created: quick_image_analysis_summary.json")
    
    # Print summary stats
    print(f"\n=== SUMMARY STATISTICS ===")
    print(f"Total images analyzed: {summary['total_images']}")
    print(f"Image types found:")
    for img_type, count in summary['image_types'].items():
        print(f"  - {img_type}: {count}")
    
    print(f"Materials identified: {len(summary['materials_found'])}")
    print(f"Techniques identified: {len(summary['techniques_found'])}")
    
    print(f"Top 10 keywords:")
    for keyword, count in list(summary['keywords_frequency'].items())[:10]:
        print(f"  - {keyword}: {count}")

if __name__ == "__main__":
    main()
