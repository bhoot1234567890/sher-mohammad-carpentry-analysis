"""
Divide image_analysis_results.json into separate files
Separates:
- metadata.json: Contains project metadata
- analysis_prompt.json: Contains the analysis criteria/prompt
- individual image files: Each image analysis in separate files
- images_summary.json: List of all images with basic info
"""
import json
import os
from pathlib import Path

def divide_analysis_results():
    # Load the main file
    print("Loading image_analysis_results.json...")
    with open('image_analysis_results.json', 'r') as f:
        data = json.load(f)
    
    # Create output directory
    output_dir = Path('divided_results')
    output_dir.mkdir(exist_ok=True)
    
    images_dir = output_dir / 'images'
    images_dir.mkdir(exist_ok=True)
    
    # 1. Save metadata
    print("Saving metadata...")
    with open(output_dir / 'metadata.json', 'w') as f:
        json.dump(data.get('metadata', {}), f, indent=2)
    
    # 2. Save analysis prompt
    print("Saving analysis prompt...")
    with open(output_dir / 'analysis_prompt.json', 'w') as f:
        json.dump(data.get('analysis_prompt', {}), f, indent=2)
    
    # 3. Process images
    images = data.get('images', [])
    print(f"Processing {len(images)} images...")
    
    # Create summary list
    images_summary = []
    
    for idx, image in enumerate(images, 1):
        filename = image.get('filename', f'image_{idx}')
        # Create safe filename from original filename
        safe_filename = filename.replace(' ', '_').replace('.jpeg', '').replace('.jpg', '').replace('.png', '')
        
        # Save individual image analysis
        output_path = images_dir / f'{safe_filename}.json'
        with open(output_path, 'w') as f:
            json.dump(image, f, indent=2)
        
        # Add to summary
        images_summary.append({
            'index': idx,
            'filename': filename,
            'output_file': f'images/{safe_filename}.json',
            'timestamp': image.get('timestamp', ''),
            'file_size': image.get('file_size', 0)
        })
        
        if idx % 10 == 0:
            print(f"  Processed {idx}/{len(images)} images...")
    
    # 4. Save images summary
    print("Saving images summary...")
    with open(output_dir / 'images_summary.json', 'w') as f:
        json.dump(images_summary, f, indent=2)
    
    # 5. Create a master index
    print("Creating master index...")
    master_index = {
        'total_images': len(images),
        'files_created': {
            'metadata': 'metadata.json',
            'analysis_prompt': 'analysis_prompt.json',
            'images_summary': 'images_summary.json',
            'individual_images': f'images/ directory ({len(images)} files)'
        },
        'summary': images_summary
    }
    
    with open(output_dir / 'index.json', 'w') as f:
        json.dump(master_index, f, indent=2)
    
    print(f"\n✓ Successfully divided analysis results!")
    print(f"  - Created {len(images)} individual image files")
    print(f"  - Output directory: {output_dir}")
    print(f"\nFiles created:")
    print(f"  - metadata.json")
    print(f"  - analysis_prompt.json")
    print(f"  - images_summary.json")
    print(f"  - index.json (master index)")
    print(f"  - images/ directory with {len(images)} files")

if __name__ == '__main__':
    divide_analysis_results()
