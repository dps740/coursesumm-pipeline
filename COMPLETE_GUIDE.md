  # CourseSumm v2 - Complete Guide

**Status:** ✅ ALL PHASES COMPLETE

Transform university course lectures into professional, sellable study companions.

## What Is This?

CourseSumm v2 processes course audio/video files through a multi-phase pipeline to create professional book-ready companion guides:

- **Phase 1**: Core pipeline (audio → transcripts → private notes)
- **Phase 2**: Professional formatting (covers, typography, book-ready layout)
- **Phase 3**: Public companions (V1: Lecture notes, V2: Going deeper, V3: Combined)
- **Phase 4**: Gradio web interface (batch processing, progress monitoring)

## Quick Start

### Installation

```bash
cd ~/clawd/projects/coursumm-pipeline

# Install all dependencies
source venv/bin/activate
pip install -r requirements_full.txt

# Set API key
export OPENAI_API_KEY="sk-..."
```

### Process a Course

```bash
# Full pipeline: all companion types
python run_full_pipeline.py ./audio ./output \
    --title "The Big Questions of Philosophy" \
    --author "Prof. David K. Johnson" \
    --companions all

# Private notes only (fastest)
python run_full_pipeline.py ./audio ./output \
    --title "Philosophy" \
    --companions private

# Public companions only (from existing transcripts)
python run_full_pipeline.py ./transcripts ./output \
    --title "Philosophy" \
    --skip-audio --skip-transcription \
    --companions v1,v2,v3
```

### Launch Web UI

```bash
python gradio_app.py
# Access at http://localhost:7860
```

## Output Types

### Private Notes (Phase 1)
**Purpose:** Your personal study notes  
**Content:**
- Detailed lecture summaries (300-500 words)
- 5 key themes with explanations
- Key takeaways with examples
- Knowledge check Q&A
- Memorable quotes

**Format:** Professional Word document with Georgia typography, 1.5 line spacing

### Public V1: Lecture Companion
**Purpose:** Sellable budget companion  
**Content:**
- Clear introductions
- 5-7 main points with explanations
- 3-5 key concepts with definitions
- Practical applications
- Discussion questions
- Further exploration suggestions

**Format:** Book-ready Word document with professional cover

### Public V2: Going Deeper
**Purpose:** Premium thematic synthesis  
**Content:**
- Course-wide major themes (4-6)
- Deeper questions with explorations
- Intellectual connections
- Related fields and thinkers
- Modern relevance
- Final synthesis

**Format:** Professional book with thematic organization

### Public V3: Complete Companion
**Purpose:** Premium product (V1 + V2)  
**Content:**
- Part I: Lecture-by-lecture companion (V1)
- Part II: Going deeper synthesis (V2)

**Format:** Complete professional book

## Architecture

```
┌─────────────────┐
│  Input Files    │  MP4, MP3, WAV, or TXT
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Phase 1        │  FFmpeg → Whisper → GPT/Claude → Word
│  Core Pipeline  │
└────────┬────────┘
         │
         ├─→ Private Notes (detailed study notes)
         │
         ▼
┌─────────────────┐
│  Phase 2        │  PIL → Professional Covers
│  Formatting     │  python-docx → Book Typography
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Phase 3        │  LLM → V1 (Lecture companion)
│  Companions     │  LLM → V2 (Going deeper)
│                 │  Combine → V3 (Complete)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Phase 4        │  Gradio UI
│  Web Interface  │  Batch Queue
└─────────────────┘
```

## File Structure

```
output/
├── audio/                          # Extracted audio (Phase 1)
│   ├── Lect01.mp3
│   └── ...
├── transcripts/                    # Whisper transcripts (Phase 1)
│   ├── Lect01.txt
│   └── ...
├── notes/                          # Private notes JSON (Phase 1)
│   ├── Lect01_notes.json
│   └── ...
├── covers/                         # Book covers (Phase 2)
│   ├── cover_private.png
│   ├── cover_public_v1.png
│   ├── cover_public_v2.png
│   └── cover_public_v3.png
├── companions/                     # Public companion JSON (Phase 3)
│   ├── public_v1/
│   │   ├── lecture_01_public_v1.json
│   │   └── ...
│   ├── public_v2/
│   │   └── synthesis.json
│   └── public_v3/
│       └── complete.json
└── documents/                      # Final Word documents
    ├── Course_Title_Private_Notes.docx
    ├── Course_Title_Public_V1_Lecture_Companion.docx
    ├── Course_Title_Public_V2_Going_Deeper.docx
    └── Course_Title_Public_V3_Complete_Companion.docx
```

## Command Reference

### run_full_pipeline.py

```bash
python run_full_pipeline.py INPUT OUTPUT [OPTIONS]

Required:
  INPUT              Input folder (audio/video/transcripts)
  OUTPUT             Output folder

Options:
  --title TEXT       Course title (default: "Course Summary")
  --author TEXT      Author/instructor name
  --companions LIST  Companion types: private,v1,v2,v3,all
  --provider TEXT    LLM provider: openai or anthropic
  --model TEXT       LLM model (default: gpt-4)
  --whisper-model    Whisper size: tiny/base/small/medium/large
  --cover-style      Cover design: blue_gradient, purple_elegant, etc.
  --skip-audio       Skip audio extraction
  --skip-transcription  Skip transcription
  --skip-generation  Skip LLM generation
  -v, --verbose      Verbose logging
```

### gradio_app.py

```bash
python gradio_app.py

Launches web interface at http://localhost:7860
- Single course processing
- Batch queue for multiple courses
- Progress monitoring
- Download results
```

## Performance & Cost

### Processing Time (36-lecture course)

| Phase | CPU Time | GPU Time |
|-------|----------|----------|
| Audio extraction | ~5 min | ~5 min |
| Transcription (medium) | ~6 hours | ~1 hour |
| Private notes (GPT-4) | ~30 min | ~30 min |
| Public V1 (GPT-4) | ~1 hour | ~1 hour |
| Public V2 (GPT-4) | ~15 min | ~15 min |
| Formatting | ~2 min | ~2 min |
| **Total (all companions)** | **~8 hours** | **~2.5 hours** |

### Cost Estimates (36 lectures)

| Item | Cost |
|------|------|
| Transcription (Whisper) | $0 (local) |
| Private notes (GPT-4) | ~$5-10 |
| Public V1 (GPT-4) | ~$10-15 |
| Public V2 (GPT-4) | ~$5-10 |
| **Total (all companions)** | **~$20-35** |

**Cost savings:**
- Use GPT-3.5: ~$3-5 total (lower quality)
- Use smaller Whisper model: faster, same quality
- GPU transcription: 6x faster (if available)

## Quality Standards

### Word Documents
- **Typography:** Georgia body text (12pt), 1.5 line spacing
- **Margins:** 1 inch all around (print-ready)
- **Chapter titles:** Professional title pages with decorative elements
- **Quotes:** Styled quote boxes with light background
- **First-line indent:** 0.25 inch (book standard)
- **Justification:** Fully justified text

### Book Covers
- **Size:** 1600x2400 pixels (240 DPI, 6.67" x 10")
- **Design:** Gradient backgrounds, professional typography
- **Elements:** Course title, companion type, author name
- **Styles:** 5 color schemes (blue, purple, green, red, teal)

### Content Quality
- **Summaries:** 3-5 paragraphs, 300-500 words
- **Themes:** 5 key themes with detailed explanations
- **Clarity:** Written for students, not professors
- **Engagement:** Discussion questions, practical applications

## Tips & Best Practices

### For Best Results
1. **Use GPT-4** for highest quality (worth the extra cost)
2. **Medium Whisper** is the sweet spot (accuracy vs speed)
3. **GPU** dramatically speeds up transcription
4. **Review outputs** and iterate if needed

### Batch Processing
1. Add courses to queue during the day
2. Start batch processing before bed
3. Wake up to completed companions
4. Great for processing multiple courses

### Selling Companions
- **Private notes:** Keep for yourself
- **Public V1:** Budget option ($9.99-14.99)
- **Public V2:** Premium synthesis ($19.99-29.99)
- **Public V3:** Complete package ($29.99-49.99)

Convert Word docs to:
- **EPUB** for ebook readers
- **PDF** for print-on-demand
- **Kindle MOBI** for Amazon

## Troubleshooting

### Common Issues

**FFmpeg not found**
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# MacOS
brew install ffmpeg
```

**OpenAI API key not set**
```bash
export OPENAI_API_KEY="sk-..."
# Add to ~/.bashrc or ~/.zshrc for persistence
```

**Out of memory (Whisper)**
```bash
# Use smaller model
--whisper-model small  # or tiny
```

**LLM rate limits**
```bash
# Add delays between requests (in code)
# Or use GPT-3.5 which has higher limits
--model gpt-3.5-turbo
```

**Gradio not accessible**
```bash
# Check firewall settings
# Or use share=True in gradio_ui.py for public URL
```

## Testing

### Quick Test (2 lectures, ~5 minutes)

```bash
# Uses existing transcripts in ./transcripts/
python test_phase1.py
```

### Full Course Test (download from Google Drive)

```bash
# Download 3 MP3 files from Google Drive folder
# ID: 1LsAmsNR4HddqT339ci_7aNumAk8Hcbo5

# Process through full pipeline
python run_full_pipeline.py ./test_audio ./test_output \
    --title "The Big Questions of Philosophy" \
    --author "Prof. David K. Johnson" \
    --companions all
```

## API Keys

### OpenAI
```bash
export OPENAI_API_KEY="sk-..."
```

Get key: https://platform.openai.com/api-keys

### Anthropic (optional)
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

Get key: https://console.anthropic.com/

## Requirements

- **Python:** 3.8+
- **FFmpeg:** For audio extraction
- **Disk space:** ~500MB per course (audio + transcripts + outputs)
- **RAM:** 4GB+ (8GB+ recommended for large Whisper models)
- **GPU:** Optional but recommended (6x faster transcription)

## License

See LICENSE file.

## Credits

Built by Scout (AI agent) for David  
Based on original CourseSumm pipeline  
Using: OpenAI Whisper, GPT-4, python-docx, Pillow, Gradio

## Support

Questions? Check:
1. This guide
2. `PHASE1_README.md` for Phase 1 details
3. `SUBAGENT_REPORT.md` for architecture
4. Gradio UI Help tab
5. Log files: `coursumm_full.log`

---

**Happy course processing! 📚✨**
