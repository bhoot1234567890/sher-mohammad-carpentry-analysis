# Carpenter Portfolio Project

AI-powered analysis and organization of carpentry portfolio images for website integration.

## 📁 Project Structure

```
carpenter-portfolio/
├── scripts/              # Python scripts for image analysis
│   ├── analyze_*.py     # Image analysis scripts
│   ├── get_schema.py    # Extract JSON schema
│   └── divide_analysis_results.py  # Split JSON into files
│
├── data/                 # Data files and results
│   ├── raw/             # Raw data and intermediate files
│   │   ├── image_analysis_results.json
│   │   ├── image_analysis_schema.json
│   │   └── image_descriptions.json
│   └── results/         # Processed and organized results
│       └── divided_results/  # Split analysis by image
│
├── assets/              # Media assets
│   ├── photos/         # Portfolio photos (64 images)
│   └── face photo for website.png
│
├── docs/                # Documentation
│   ├── ANALYSIS_SUMMARY.md
│   ├── IMAGE_ANALYSIS_README.md
│   ├── FILE_INDEX.md
│   └── resume_*.pdf
│
└── README.md           # This file
```

## 🚀 Quick Start

### 1. Analyze Images
```bash
cd scripts
python analyze_carpentry_images.py
```

### 2. Get JSON Schema
```bash
python get_schema.py
```

### 3. Divide Results
```bash
python divide_analysis_results.py
```

## 📊 Data Organization

- **Raw Data**: Original analysis results in `data/raw/`
- **Processed Data**: Individual image analyses in `data/results/divided_results/`
- **Images**: Portfolio photos in `assets/photos/`

## 🔧 Scripts

- `analyze_carpentry_images.py` - Main image analysis
- `analyze_carpentry_images_batch.py` - Batch processing
- `continue_image_analysis.py` - Resume interrupted analysis
- `get_image_descriptions.py` - Extract descriptions
- `get_schema.py` - Generate JSON schema
- `divide_analysis_results.py` - Split large JSON files

## 📝 Documentation

See `docs/` folder for detailed documentation:
- `IMAGE_ANALYSIS_README.md` - Analysis process and usage
- `ANALYSIS_SUMMARY.md` - Summary of findings
- `FILE_INDEX.md` - Complete file index

## 🎯 Project Goals

Comprehensive AI analysis of carpentry portfolio images for:
- Website integration
- SEO optimization
- Quality assessment
- Content organization
