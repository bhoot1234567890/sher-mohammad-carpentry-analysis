#!/usr/bin/env python3
"""
Carpentry Portfolio Image Analyzer - Batch Version
Processes images in smaller batches with better error handling
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

def analyze_carpentry_image(image_path, filename):
    """Analyze a single carpentry image using Mistral vision model"""
    
    base64_image = encode_image(image_path)
    
    # Simplified prompt for faster processing
    prompt = f"""
    ANALYZE THIS CARPENTRY IMAGE:
    
    Provide a concise JSON analysis with these fields:
    - image_type: [Close-up/Full view/Work-in-progress/Tool/Material]
    - primary_subject: [What is shown]
    - materials: [list of materials]
    - techniques: [list of carpentry techniques]
    - quality_rating: [1-10]
    - keywords: [3-5 relevant keywords]
    - description: [2-3 sentence description for website]
    
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
            temperature=0.3  # More deterministic results
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
        analysis_data['filename'] = filename
        analysis_data['timestamp'] = datetime.now().isoformat()
        analysis_data['file_size'] = os.path.getsize(image_path)
        
        return analysis_data
        
    except Exception as e:
        print(f"Error analyzing {filename}: {str(e)}")
        return None

def process_batch(image_files, batch_size=5):
    """Process images in batches"""
    
    all_results = []
    
    # Load existing results if available
    if os.path.exists("image_analysis_results.json"):
        with open("image_analysis_results.json", "r") as f:
            all_results = json.load(f)
        
        # Get already processed files
        processed_files = {result['filename'] for result in all_results}
        image_files = [f for f in image_files if os.path.basename(f) not in processed_files]
        
        print(f"Resuming from previous run. {len(processed_files)} files already processed.")
    
    total_images = len(image_files)
    print(f"Processing {total_images} images in batches of {batch_size}")
    
    for i in range(0, total_images, batch_size):
        batch = image_files[i:i + batch_size]
        batch_results = []
        
        print(f"\n=== Processing batch {i//batch_size + 1} ({len(batch)} images) ===")
        
        for image_path in batch:
            filename = os.path.basename(image_path)
            print(f"Processing: {filename}")
            
            analysis = analyze_carpentry_image(image_path, filename)
            
            if analysis:
                batch_results.append(analysis)
                print(f"✓ Successfully analyzed {filename}")
            else:
                print(f"✗ Failed to analyze {filename}")
            
            # Rate limiting
            time.sleep(3)  # 3 second delay between images
        
        # Save batch results
        if batch_results:
            all_results.extend(batch_results)
            
            # Save intermediate results
            with open("image_analysis_results.json", "w") as f:
                json.dump(all_results, f, indent=2)
            
            print(f"Saved batch results. Total analyzed: {len(all_results)}")
        
        # Longer pause between batches
        if i + batch_size < total_images:
            print(f"Pausing before next batch...")
            time.sleep(10)  # 10 second pause between batches
    
    return all_results

def create_summary(results):
    """Create a summary report"""
    
    summary = {
        "total_images": len(results),
        "analysis_date": datetime.now().isoformat(),
        "image_types": {},
        "materials_found": set(),
        "techniques_found": set(),
        "quality_distribution": {},
        "keywords_frequency": {}
    }
    
    for result in results:
        # Count image types
        img_type = result.get('image_type', 'Unknown')
        summary['image_types'][img_type] = summary['image_types'].get(img_type, 0) + 1
        
        # Collect materials
        materials = result.get('materials', [])
        for material in materials:
            summary['materials_found'].add(material)
        
        # Collect techniques
        techniques = result.get('techniques', [])
        for technique in techniques:
            summary['techniques_found'].add(technique)
        
        # Quality distribution
        quality = result.get('quality_rating', 0)
        summary['quality_distribution'][quality] = summary['quality_distribution'].get(quality, 0) + 1
        
        # Keywords frequency
        keywords = result.get('keywords', [])
        for keyword in keywords:
            summary['keywords_frequency'][keyword] = summary['keywords_frequency'].get(keyword, 0) + 1
    
    # Convert sets to sorted lists
    summary['materials_found'] = sorted(list(summary['materials_found']))
    summary['techniques_found'] = sorted(list(summary['techniques_found']))
    summary['keywords_frequency'] = dict(sorted(summary['keywords_frequency'].items(), 
                                               key=lambda x: x[1], reverse=True))
    
    with open("image_analysis_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("Summary report created: image_analysis_summary.json")
    return summary

def main():
    """Main function"""
    
    # Get all image files
    image_files = sorted(glob.glob("photos/WhatsApp Image*.jpeg"))
    
    if not image_files:
        print("No images found in photos/ directory")
        return
    
    print(f"Found {len(image_files)} images to analyze")
    
    # Process in batches
    results = process_batch(image_files, batch_size=3)  # Smaller batch size
    
    print(f"\n=== ANALYSIS COMPLETE ===")
    print(f"Successfully analyzed {len(results)} images")
    
    # Create summary
    summary = create_summary(results)
    
    # Print summary stats
    print(f"\n=== SUMMARY STATISTICS ===")
    print(f"Total images analyzed: {summary['total_images']}")
    print(f"Image types found: {len(summary['image_types'])}")
    for img_type, count in summary['image_types'].items():
        print(f"  - {img_type}: {count}")
    
    print(f"Materials identified: {len(summary['materials_found'])}")
    print(f"Techniques identified: {len(summary['techniques_found'])}")
    
    print(f"Top 5 keywords:")
    for keyword, count in list(summary['keywords_frequency'].items())[:5]:
        print(f"  - {keyword}: {count}")

if __name__ == "__main__":
    main()
