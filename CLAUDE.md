# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Carpenter portfolio project for Sher Mohammad (9 years experience, specialized in wood work, modular kitchens, wardrobes, furniture, doors, windows, PVC panels). The project uses Mistral AI's vision model to analyze carpentry work photos and generate structured, portfolio-ready metadata for website integration.

**Current Status**: System complete and tested. 64 of 64 images analyzed (100% completion). Website deployed and live.

**Repositories**:
- Analysis System (Parent): https://github.com/bhoot1234567890/sher-mohammad-carpentry-analysis
- Portfolio Website (Child): https://github.com/bhoot1234567890/sher-mohammad-carpenter-portfolio

**Live Website**: https://sher-mohammad-carpenter.pages.dev

## Tech Stack

- **Python 3** with Mistral AI SDK
- **Mistral AI Vision Model** (`mistral-small-latest`) for image analysis
- **python-dotenv** for environment variable management
- **tqdm** for progress bars (optional, in some scripts)
- **React 18** + TypeScript + Vite (portfolio website)
- **Cloudflare Pages** for deployment

## Development Setup

1. Install Python dependencies:
   ```bash
   pip install mistralai python-dotenv tqdm
   ```

2. Set up environment variables:
   - Create a `.env` file in the project root
   - Add: `MISTRAL_API_KEY=your_api_key_here`

3. Website setup (in `portfolio-website/`):
   ```bash
   cd portfolio-website
   npm install
   ```

## Common Commands

### Python Analysis Scripts

#### Test the system (validates API and processes one image):
```bash
cd scripts
python test_single_image.py
```

#### Continue batch analysis (processes remaining images):
```bash
cd scripts
python continue_image_analysis.py
```

#### Get simple descriptions only (faster, less detailed):
```bash
cd scripts
python get_image_descriptions.py
```

#### Quick analysis with basic metadata:
```bash
cd scripts
python quick_image_analysis.py
```

#### Full analysis from scratch:
```bash
cd scripts
python analyze_carpentry_images.py
```

#### Extract JSON schema from analysis results:
```bash
cd scripts
python get_schema.py
```

#### Split large analysis JSON into individual files:
```bash
cd scripts
python divide_analysis_results.py
```

### Website Commands

#### Development server:
```bash
cd portfolio-website
npm run dev
```

#### Build for production:
```bash
cd portfolio-website
npm run build
```

#### Deploy to Cloudflare Pages:
```bash
cd portfolio-website
npm run build
npx wrangler pages deploy dist
```

## Project Structure

```
carpenter portfolio/                                   # Parent repository (Analysis System)
├── scripts/                                          # Python analysis scripts
│   ├── continue_image_analysis.py                   # Primary: Resume & process remaining
│   ├── analyze_carpentry_images.py                 # Full analysis from scratch with progress bar
│   ├── get_image_descriptions.py                   # Simple descriptions only
│   ├── quick_image_analysis.py                     # Fast analysis with basic metadata
│   ├── test_single_image.py                        # System validation
│   ├── divide_analysis_results.py                  # Split JSON into files
│   ├── get_schema.py                               # Extract JSON schema
│   └── mistral vision model example.py             # Original basic example
│
├── data/
│   ├── raw/                                        # Original analysis results
│   │   ├── image_analysis_results.json            # Main results (64/64 analyzed)
│   │   ├── image_analysis_schema.json            # Generated schema
│   │   ├── image_descriptions.json               # Basic descriptions
│   │   └── sample_image_analysis.json            # Sample analysis
│   └── results/
│       └── divided_results/                       # Individual image files
│
├── assets/
│   ├── photos/                                    # 64 WhatsApp-exported carpentry images
│   └── face photo for website.png                  # Profile photo
│
├── docs/                                          # Documentation
│   ├── ANALYSIS_SUMMARY.md
│   ├── IMAGE_ANALYSIS_README.md
│   ├── FILE_INDEX.md
│   └── image_analysis_prompt.md
│
├── portfolio-website/                             # Child repository (Portfolio Website)
│   ├── src/
│   │   ├── components/
│   │   │   ├── ui/                               # Shared UI components
│   │   │   │   ├── Navigation.tsx                # Sticky header nav
│   │   │   │   ├── Footer.tsx                    # Site footer
│   │   │   │   ├── SectionTitle.tsx              # Reusable section headers
│   │   │   │   ├── ScrollReveal.tsx              # Scroll animation wrapper
│   │   │   │   ├── LazyImage.tsx                 # Lazy-loaded image component
│   │   │   │   └── ImageModal.tsx                # Image detail popup modal
│   │   │   └── sections/                         # Page sections
│   │   │       ├── Hero.tsx                      # Landing hero section
│   │   │       ├── About.tsx                     # About/bio section
│   │   │       ├── Services.tsx                  # Services offered
│   │   │       ├── Gallery.tsx                   # Image gallery with filters
│   │   │       ├── Testimonials.tsx              # Client reviews
│   │   │       ├── Process.tsx                   # Work process timeline
│   │   │       └── Contact.tsx                   # Contact info & WhatsApp
│   │   ├── data/
│   │   │   └── portfolioData.ts                  # Type definitions
│   │   ├── App.tsx                               # Main app component
│   │   └── index.css                            # Global styles + CSS variables
│   ├── public/
│   │   ├── images/                              # Portfolio images (65 files)
│   │   └── image_analysis_results.json          # AI analysis data
│   ├── package.json
│   └── CLAUDE.md                                # Website-specific documentation
│
├── .env                                          # Mistral API key (not in git)
├── .gitignore                                   # Excludes sensitive files + portfolio-website/
└── README.md                                    # Project overview
```

**Important**: `portfolio-website/` is a separate git repository with its own tracking. It is excluded from the parent repository via `.gitignore`.

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

### Git Repositories

**Parent Repository** (Analysis System):
- Location: `/Users/chaitanyamalhotra/Desktop/scratch projects/carpenter portfolio/`
- GitHub: https://github.com/bhoot1234567890/sher-mohammad-carpentry-analysis
- Tracks: Python scripts, analysis data, documentation, original photos
- Does NOT track: `portfolio-website/` (separate repo), `.env`

**Child Repository** (Portfolio Website):
- Location: `portfolio-website/` subdirectory
- GitHub: https://github.com/bhoot1234567890/sher-mohammad-carpenter-portfolio
- Live Site: https://sher-mohammad-carpenter.pages.dev
- Tracks: React source, built images, website-specific data
- Independent git repository with own `.git` folder

## Workflow for Adding New Images

1. **Add new photos** to `assets/photos/` in parent directory
2. **Run AI analysis** to generate metadata:
   ```bash
   cd scripts
   python continue_image_analysis.py
   ```
3. **Copy new images** to website:
   ```bash
   cp "assets/photos/new-image.jpg" "portfolio-website/public/images/"
   ```
4. **Update website data**:
   - Copy `data/raw/image_analysis_results.json` to `portfolio-website/public/`
5. **Rebuild and deploy**:
   ```bash
   cd portfolio-website
   npm run build
   npx wrangler pages deploy dist
   ```

## Deployment

### Website Deployment
The portfolio website is deployed on Cloudflare Pages:
- **URL**: https://sher-mohammad-carpenter.pages.dev
- **Build command**: `npm run build`
- **Output directory**: `dist/`
- **Deployment tool**: Wrangler CLI

### Git Workflow
```bash
# Parent repository (analysis system)
cd "/Users/chaitanyamalhotra/Desktop/scratch projects/carpenter portfolio"
git add .
git commit -m "Update analysis data"
git push

# Child repository (website)
cd portfolio-website
git add .
git commit -m "Update website content"
git push
npm run build
npx wrangler pages deploy dist
```

## Notes

- Both repositories are properly initialized and pushed to GitHub
- The website is live and fully functional with all 64 images
- Image modal with detailed analysis information is implemented
- Rate limiting is handled gracefully in analysis scripts
- The `data/raw/image_analysis_results.json` file is the single source of truth for analysis progress
