#!/usr/bin/env python3
"""
Continue Image Analysis - Processes remaining images in batches
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
    """Analyze a carpentry image using Mistral vision model"""
    
    base64_image = encode_image(image_path)
    
    # Comprehensive prompt
    prompt = f"""
    ANALYZE THIS CARPENTRY IMAGE FOR PORTFOLIO:
    
    Provide detailed JSON analysis with these sections:
    
    {{
      "filename": "{filename}",
      "image_type": "[Close-up detail/Full project view/Work-in-progress/Tool/Material showcase]",
      "primary_subject": "[What is shown - be specific]",
      "completion_stage": "[Rough cut/Assembly/Sanding/Finishing/Completed]",
      
      "technical_details": {{
        "materials": ["material1", "material2"],
        "joinery_techniques": ["technique1", "technique2"],
        "construction_methods": ["method1", "method2"]
      }},
      
      "craftsmanship_quality": {{
        "precision": "[High/Medium/Low] - [observations]",
        "surface_quality": "[High/Medium/Low] - [observations]",
        "attention_to_detail": "[High/Medium/Low] - [observations]"
      }},
      
      "design_elements": {{
        "style": "[Traditional/Modern/Rustic/Industrial/Other]",
        "functional_features": ["feature1", "feature2"],
        "aesthetic_features": ["feature1", "feature2"]
      }},
      
      "portfolio_presentation": {{
        "best_use": "[Hero/Detail/Process/Comparison]",
        "accompanying_text": "[2-3 sentence description for website]",
        "quality_rating": [1-10]
      }},
      
      "keywords": ["keyword1", "keyword2", "keyword3"]
    }}
    
    Be specific, technical, and detailed. Return ONLY valid JSON.
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
        
        response_text = chat_response.choices[0].message.content.strip()
        
        # Clean up JSON response
        if response_text.startswith('```json'):
            response_text = response_text[7:].strip()
        if response_text.endswith('```'):
            response_text = response_text[:-3].strip()
        
        analysis_data = json.loads(response_text)
        
        # Add metadata
        analysis_data['timestamp'] = datetime.now().isoformat()
        analysis_data['file_size'] = os.path.getsize(image_path)
        
        return analysis_data
        
    except Exception as e:
        print(f"Error analyzing {filename}: {str(e)}")
        return None

def load_existing_results():
    """Load existing analysis results"""
    if os.path.exists("image_analysis_results.json"):
        with open("image_analysis_results.json", "r") as f:
            return json.load(f)
    return None

def save_results(data):
    """Save analysis results"""
    with open("image_analysis_results.json", "w") as f:
        json.dump(data, f, indent=2)

def update_summary(data):
    """Update summary statistics"""
    images = data['images']
    
    # Update summary
    summary = {
        "total_images_analyzed": len(images),
        "image_types": {},
        "materials_identified": set(),
        "techniques_identified": set(),
        "quality_distribution": {}
    }
    
    for image in images:
        analysis = image['analysis']
        
        # Count image types
        img_type = analysis['image_type']
        summary['image_types'][img_type] = summary['image_types'].get(img_type, 0) + 1
        
        # Collect materials
        if 'technical_details' in analysis:
            materials = analysis['technical_details'].get('materials', [])
            for material in materials:
                summary['materials_identified'].add(material)
            
            techniques = analysis['technical_details'].get('joinery_techniques', [])
            for technique in techniques:
                summary['techniques_identified'].add(technique)
        
        # Quality distribution
        if 'portfolio_presentation' in analysis:
            quality = analysis['portfolio_presentation'].get('quality_rating', 0)
            summary['quality_distribution'][quality] = summary['quality_distribution'].get(quality, 0) + 1
    
    # Convert sets to sorted lists
    summary['materials_identified'] = sorted(list(summary['materials_identified']))
    summary['techniques_identified'] = sorted(list(summary['techniques_identified']))
    
    data['summary_statistics'] = summary
    data['metadata']['analysis_status'] = "partial" if len(images) < 64 else "complete"

def main():
    """Main function to continue analysis"""
    
    # Load existing data
    existing_data = load_existing_results()
    
    if existing_data is None:
        print("No existing analysis found. Starting fresh...")
        existing_data = {
            "metadata": {
                "project": "Carpenter Portfolio Image Analysis",
                "created_by": "Mistral AI Vision Analysis",
                "date_created": datetime.now().isoformat(),
                "total_images": 64,
                "analysis_status": "in_progress",
                "description": "Comprehensive analysis of carpentry portfolio images"
            },
            "images": []
        }
    
    # Get all image files
    all_image_files = sorted(glob.glob("photos/WhatsApp Image*.jpeg"))
    
    # Get already processed files
    processed_files = {img['filename'] for img in existing_data['images']}
    remaining_files = [f for f in all_image_files if os.path.basename(f) not in processed_files]
    
    print(f"Total images: {len(all_image_files)}")
    print(f"Already processed: {len(processed_files)}")
    print(f"Remaining to process: {len(remaining_files)}")
    
    if not remaining_files:
        print("All images have been processed!")
        return
    
    # Process remaining images in batches
    batch_size = 3
    total_batches = (len(remaining_files) + batch_size - 1) // batch_size
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(remaining_files))
        batch_files = remaining_files[start_idx:end_idx]
        
        print(f"\n=== Processing batch {batch_num + 1}/{total_batches} ===")
        print(f"Images in this batch: {len(batch_files)}")
        
        batch_results = []
        
        for image_path in batch_files:
            filename = os.path.basename(image_path)
            print(f"\nProcessing: {filename}")
            
            analysis = analyze_carpentry_image(image_path, filename)
            
            if analysis:
                batch_results.append(analysis)
                print(f"✓ Successfully analyzed {filename}")
            else:
                print(f"✗ Failed to analyze {filename}")
            
            # Rate limiting
            time.sleep(5)
        
        # Add batch results to existing data
        for result in batch_results:
            existing_data['images'].append({
                'filename': result['filename'],
                'timestamp': result['timestamp'],
                'file_size': result['file_size'],
                'analysis': result
            })
        
        # Update summary
        update_summary(existing_data)
        
        # Save progress
        save_results(existing_data)
        print(f"Saved progress. Total analyzed: {len(existing_data['images'])}")
        
        if batch_num < total_batches - 1:
            print(f"Pausing before next batch...")
            time.sleep(10)
    
    print(f"\n=== ANALYSIS COMPLETE ===")
    print(f"Total images analyzed: {len(existing_data['images'])}")
    print(f"Results saved to: image_analysis_results.json")
    
    # Print summary
    summary = existing_data['summary_statistics']
    print(f"\n=== SUMMARY ===")
    print(f"Image types: {summary['image_types']}")
    print(f"Materials found: {len(summary['materials_identified'])}")
    print(f"Techniques found: {len(summary['techniques_identified'])}")
    print(f"Quality distribution: {summary['quality_distribution']}")

if __name__ == "__main__":
    main()
