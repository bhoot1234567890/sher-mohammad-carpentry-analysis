# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Carpenter portfolio project for Sher Mohammad (9 years experience, specialized in wood work, modular kitchens, wardrobes, furniture, doors, windows, PVC panels). The project uses Mistral AI's vision model to analyze carpentry work photos and generate structured, portfolio-ready metadata for website integration.

**Current Status**: System complete and tested. 64 of 64 images analyzed (100% completion). Ready for website integration.

## Tech Stack

- **Python 3** with Mistral AI SDK
- **Mistral AI Vision Model** (`mistral-small-latest`) for image analysis
- **python-dotenv** for environment variable management
- **tqdm** for progress bars (optional, in some scripts)

## Development Setup

1. Install dependencies:
   ```bash
   pip install mistralai python-dotenv tqdm
   ```

2. Set up environment variables:
   - Create a `.env` file in the project root
   - Add: `MISTRAL_API_KEY=your_api_key_here`

## Common Commands

### Test the system (validates API and processes one image):
```bash
cd scripts
python test_single_image.py
```

### Continue batch analysis (processes remaining images):
```bash
cd scripts
python continue_image_analysis.py
```

### Get simple descriptions only (faster, less detailed):
```bash
cd scripts
python get_image_descriptions.py
```

### Quick analysis with basic metadata:
```bash
cd scripts
python quick_image_analysis.py
```

### Full analysis from scratch:
```bash
cd scripts
python analyze_carpentry_images.py
```

### Extract JSON schema from analysis results:
```bash
cd scripts
python get_schema.py
```

### Split large analysis JSON into individual files:
```bash
cd scripts
python divide_analysis_results.py
```

## Project Structure

```
carpenter portfolio/
├── scripts/                                    # Python analysis scripts
│   ├── continue_image_analysis.py             # Primary: Resume & process remaining
│   ├── analyze_carpentry_images.py           # Full analysis from scratch with progress bar
│   ├── get_image_descriptions.py             # Simple descriptions only
│   ├── quick_image_analysis.py                # Fast analysis with basic metadata
│   ├── test_single_image.py                   # System validation
│   ├── divide_analysis_results.py            # Split JSON into files
│   ├── get_schema.py                         # Extract JSON schema
│   └── mistral vision model example.py       # Original basic example
│
├── data/
│   ├── raw/                             # Original analysis results
│   │   ├── image_analysis_results.json   # Main results (64/64 analyzed)
│   │   ├── image_analysis_schema.json   # Generated schema
│   │   ├── image_descriptions.json      # Basic descriptions
│   │   └── sample_image_analysis.json   # Sample analysis
│   └── results/
│       └── divided_results/             # Individual image files
│
├── assets/
│   ├── photos/                         # 64 WhatsApp-exported carpentry images
│   └── face photo for website.png       # Profile photo
│
├── docs/                              # Documentation
│   ├── ANALYSIS_SUMMARY.md
│   ├── IMAGE_ANALYSIS_README.md
│   ├── FILE_INDEX.md
│   └── image_analysis_prompt.md
│
├── .env                               # Mistral API key (not in git)
├── .gitignore                        # Excludes sensitive files
└── README.md                         # Project overview
```

## Architecture Patterns

### Vision API Integration
All scripts follow the same pattern for Mistral vision API calls:
```python
from mistralai import Mistral
import base64

# Encode image
with open(image_path, "rb") as f:
    base64_image = base64.b64encode(f.read()).decode('utf-8')

# API call with text + image
messages = [{
    "role": "user",
    "content": [
        {"type": "text", "text": prompt},
        {"type": "image_url", "image_url": f"data:image/jpeg;base64,{base64_image}"}
    ]
}]
response = client.chat.complete(model=model, messages=messages)
```

### Batch Processing Pattern
[`scripts/continue_image_analysis.py`](scripts/continue_image_analysis.py) implements resumable batch processing:
- Loads existing `image_analysis_results.json` to skip processed images
- Processes in batches of 3 (configurable via `batch_size`)
- 5-second delay between images, 10-second delay between batches
- Saves progress after each batch
- Updates summary statistics automatically

### JSON Response Structure
The main analysis output in [`data/raw/image_analysis_results.json`](data/raw/image_analysis_results.json) uses this structure:
```json
{
  "metadata": {...},
  "images": [
    {
      "filename": "...",
      "timestamp": "...",
      "file_size": ...,
      "analysis": {
        "image_type": "[Close-up detail/Full project view/...]",
        "primary_subject": "...",
        "completion_stage": "...",
        "technical_details": {
          "materials": [...],
          "joinery_techniques": [...],
          "construction_methods": [...]
        },
        "craftsmanship_quality": {...},
        "design_elements": {...},
        "portfolio_presentation": {
          "best_use": "[Hero/Detail/Process/Comparison]",
          "accompanying_text": "...",
          "quality_rating": 1-10
        },
        "keywords": [...]
      }
    }
  ],
  "summary_statistics": {
    "total_images_analyzed": ...,
    "image_types": {...},
    "materials_identified": [...],
    "techniques_identified": [...]
  }
}
```

See [`docs/image_analysis_prompt.md`](docs/image_analysis_prompt.md) for the complete analysis criteria framework.

### Error Handling Pattern
All scripts handle API errors gracefully:
```python
try:
    response = client.chat.complete(...)
    # Clean and parse JSON
    response_text = response.choices[0].message.content.strip()
    if response_text.startswith('```json'):
        response_text = response_text[7:].strip()
    if response_text.endswith('```'):
        response_text = response_text[:-3].strip()
    return json.loads(response_text)
except Exception as e:
    print(f"Error analyzing {filename}: {str(e)}")
    return None  # Skip and continue
```

## Important Context

### Resume Data
Sher Mohammad's resume is located in the hash-named directory `data/raw/3423c424e267df800f2b429db4b0490974dd93fd60a6126402c290e4729d02ae/`:
- Markdown format: `resume_Sher_Mohamad_copy_1_1_260107_072548.md`
- Contact: 8527285231, shermohammadtuku@gmail.com
- Location: Majnu Ka Tila, Delhi - 110054
- Specializations: Wood work, modular kitchen, wardrobe, bed, wood flooring, TV unit, window/door work, PVC panel, furniture repair

### Analysis Framework
The analysis system evaluates images across 10 dimensions (see [`docs/image_analysis_prompt.md`](docs/image_analysis_prompt.md)):
1. Basic identification (type, subject, completion stage)
2. Technical details (materials, joinery, construction methods)
3. Craftsmanship quality (precision, surface quality, attention to detail)
4. Design elements (style, features, finish)
5. Project context (type, scale, use case)
6. Tool and equipment analysis
7. Workflow and process insights
8. Aesthetic evaluation
9. Technical challenges
10. Portfolio presentation suggestions (including quality rating 1-10, SEO keywords)

### Rate Limiting
Mistral API has rate limits. Scripts implement delays:
- `continue_image_analysis.py`: 5 seconds between images, 10 seconds between batches
- `analyze_carpentry_images.py`: 2 seconds between images
- Adjust these in the scripts if encountering rate limit errors

## Notes

- Not a git repository (no version control configured)
- No build system, tests, or linting configured
- Resume data was extracted from PDF in a previous process (multiple format variants exist)
- The `data/raw/image_analysis_results.json` file is the single source of truth for analysis progress - scripts check it to skip already-processed images
