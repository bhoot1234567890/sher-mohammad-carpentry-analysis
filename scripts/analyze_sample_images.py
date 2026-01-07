#!/usr/bin/env python3
"""
Sample Image Analyzer - Processes first 6 images as a demonstration
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
    
    # Comprehensive prompt for carpentry image analysis
    prompt = f"""
    ANALYZE THIS CARPENTRY PORTFOLIO IMAGE:
    
    You are a professional carpentry expert. Analyze this image comprehensively:
    
    {{
      "filename": "{filename}",
      "image_type": "[Close-up detail/Full project view/Work-in-progress/Before\/After/Tool\/Equipment/Material showcase]",
      "primary_subject": "[Specific furniture type, architectural element, tool, material, or technique]",
      "completion_stage": "[Rough cut/Assembly/Sanding/Finishing/Completed]",
      
      "technical_details": {{
        "materials": ["wood_type1", "wood_type2", "hardware_type", "finish_type"],
        "joinery_techniques": ["technique1", "technique2"],
        "construction_methods": ["method1", "method2"],
        "visible_tools": ["tool1", "tool2"]
      }},
      
      "craftsmanship_quality": {{
        "precision": "[High/Medium/Low] - [specific observations]",
        "surface_quality": "[High/Medium/Low] - [specific observations]",
        "attention_to_detail": "[High/Medium/Low] - [specific observations]",
        "structural_integrity": "[High/Medium/Low] - [specific observations]"
      }},
      
      "design_elements": {{
        "style": "[Traditional/Modern/Rustic/Industrial/Scandinavian/Mid-century/Other]",
        "functional_features": ["feature1", "feature2"],
        "aesthetic_features": ["feature1", "feature2"],
        "color_finish": "[detailed description]"
      }},
      
      "project_context": {{
        "project_type": "[Custom furniture/Cabinetry/Flooring/Doors/Windows/Outdoor structures]",
        "scale": "[Small/Medium/Large]",
        "intended_use": "[Residential/Commercial/Decorative/Functional]",
        "customization_elements": ["element1", "element2"]
      }},
      
      "aesthetic_evaluation": {{
        "visual_appeal": "[High/Medium/Low] - [specific observations]",
        "craftsmanship_showcase": ["area1", "area2"],
        "unique_selling_points": ["point1", "point2"],
        "potential_client_appeal": "[description of target audience]"
      }},
      
      "technical_challenges": [
        "challenge1",
        "challenge2"
      ],
      
      "portfolio_presentation": {{
        "best_use": "[Hero image/Detail showcase/Process documentation/Before\/After comparison]",
        "accompanying_text": "[Suggested descriptive text for website]",
        "focus_areas": ["area1", "area2"],
        "quality_rating": [1-10]
      }},
      
      "keywords": ["keyword1", "keyword2", "keyword3"],
      "recommended_usage": "[Detailed suggestion for website integration]"
    }}
    
    Provide ONLY the JSON output, no additional text or explanations.
    Be as specific and detailed as possible in your analysis.
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
            messages=messages
        )
        
        # Extract and parse the JSON response
        response_text = chat_response.choices[0].message.content
        
        # Clean up the response to ensure valid JSON
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
    """Main function to process sample images"""
    
    # Get first 6 image files for demonstration
    image_files = sorted(glob.glob("photos/WhatsApp Image*.jpeg"))[:6]
    
    print(f"Processing {len(image_files)} sample images")
    
    results = []
    
    for i, image_path in enumerate(image_files):
        filename = os.path.basename(image_path)
        
        print(f"\n=== Processing image {i+1}/{len(image_files)}: {filename} ===")
        
        analysis = analyze_carpentry_image(image_path, filename)
        
        if analysis:
            results.append(analysis)
            print(f"✓ Successfully analyzed {filename}")
            
            # Save after each image
            with open("sample_image_analysis.json", "w") as f:
                json.dump(results, f, indent=2)
            
            print(f"Saved results so far ({len(results)} images)")
        else:
            print(f"✗ Failed to analyze {filename}")
        
        # Rate limiting
        if i < len(image_files) - 1:  # Don't sleep after last image
            print(f"Waiting before next image...")
            time.sleep(5)  # 5 second delay
    
    print(f"\n=== SAMPLE ANALYSIS COMPLETE ===")
    print(f"Successfully analyzed {len(results)} sample images")
    print(f"Results saved to: sample_image_analysis.json")
    
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
        "project_types": {},
        "quality_distribution": {}
    }
    
    for result in results:
        # Count image types
        img_type = result['analysis']['image_type']
        summary['image_types'][img_type] = summary['image_types'].get(img_type, 0) + 1
        
        # Collect materials
        if 'technical_details' in result['analysis']:
            materials = result['analysis']['technical_details'].get('materials', [])
            for material in materials:
                summary['materials_found'].add(material)
            
            # Collect techniques
            techniques = result['analysis']['technical_details'].get('joinery_techniques', [])
            for technique in techniques:
                summary['techniques_found'].add(technique)
        
        # Count project types
        if 'project_context' in result['analysis']:
            proj_type = result['analysis']['project_context'].get('project_type', 'Unknown')
            summary['project_types'][proj_type] = summary['project_types'].get(proj_type, 0) + 1
        
        # Quality distribution
        if 'portfolio_presentation' in result['analysis']:
            quality = result['analysis']['portfolio_presentation'].get('quality_rating', 0)
            summary['quality_distribution'][quality] = summary['quality_distribution'].get(quality, 0) + 1
    
    # Convert sets to lists
    summary['materials_found'] = sorted(list(summary['materials_found']))
    summary['techniques_found'] = sorted(list(summary['techniques_found']))
    
    with open("sample_image_analysis_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    
    print("Summary report created: sample_image_analysis_summary.json")
    
    # Print summary stats
    print(f"\n=== SUMMARY STATISTICS ===")
    print(f"Total images analyzed: {summary['total_images']}")
    print(f"Image types found:")
    for img_type, count in summary['image_types'].items():
        print(f"  - {img_type}: {count}")
    
    print(f"Materials identified: {len(summary['materials_found'])}")
    print(f"Techniques identified: {len(summary['techniques_found'])}")

if __name__ == "__main__":
    main()
