# CourseSumm v2 - Architecture Plan

**Date:** 2026-01-30
**Status:** Planning
**Test Course:** The Big Questions of Philosophy (36 lectures)

---

## Overview

Fully automated pipeline: **Video/Audio → Transcripts → 4 Outputs**

```
┌─────────────────────────────────────────────────────────────────┐
│                        WEB UI (Gradio)                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────┐   │
│  │ Folder   │  │ Batch    │  │ Progress │  │ Download     │   │
│  │ Picker   │  │ Queue    │  │ Monitor  │  │ Results      │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      PROCESSING PIPELINE                        │
│                                                                 │
│  1. VIDEO/AUDIO INPUT                                          │
│     └── Extract audio from MP4 (if needed) → MP3               │
│                                                                 │
│  2. TRANSCRIPTION (Local Whisper)                              │
│     └── MP3 → TXT (one per lecture)                            │
│                                                                 │
│  3. CONTENT GENERATION (GPT/Claude)                            │
│     ├── Private Notes (lecture-by-lecture + summary)           │
│     ├── Public Companion v1 (lecture sequence)                 │
│     └── Public Companion v2 (topic-reorganized)                │
│                                                                 │
│  4. DOCUMENT FORMATTING                                        │
│     ├── Book-ready Word docs (professional typography)         │
│     └── Auto-generated covers                                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         OUTPUTS                                 │
│                                                                 │
│  📁 output/                                                     │
│  ├── transcripts/           # Raw transcripts                  │
│  ├── private_notes/         # Personal study notes             │
│  │   └── Course_Name_Private_Notes.docx                        │
│  ├── companion_v1/          # Lecture notes only               │
│  │   ├── Course_Name_Lecture_Guide.docx                        │
│  │   └── cover.png                                             │
│  ├── companion_v2/          # Going Deeper only                │
│  │   ├── Course_Name_Going_Deeper.docx                         │
│  │   └── cover.png                                             │
│  └── companion_v3/          # Combined (V1 + V2)               │
│      ├── Course_Name_Complete_Companion.docx                   │
│      └── cover.png                                             │
└─────────────────────────────────────────────────────────────────┘

## Output Definitions

### Private Notes (personal use)
- Lecture-by-lecture summaries
- Key concepts, definitions, arguments
- Study questions
- NOT for sale

### Public Companion V1 - Lecture Guide
- Lecture-by-lecture notes (like original repo)
- Quick reference companion
- Sellable as budget option

### Public Companion V2 - Going Deeper
- Post-course synthesis
- Cross-lecture connections
- Implications and applications
- Questions the course raises but doesn't answer
- Connections to other philosophical traditions
- Suggested further reading
- "If you found X interesting, explore Y"
- Transformative original content

### Public Companion V3 - Complete Companion (MAIN PRODUCT)
- Part 1: Lecture Guide (V1 content)
- Part 2: Going Deeper (V2 content)
- The premium companion book
- Best value for Amazon KDP
```

---

## Components

### 1. Web UI (Gradio)

**Features:**
- Folder picker (select course materials directory)
- Course metadata input (title, author, etc.)
- Batch queue (add multiple courses)
- Real-time progress monitoring
- Download completed outputs

**Screens:**
1. **Add Course** - Select folder, enter metadata
2. **Queue** - View pending/processing/completed courses
3. **Progress** - Live status for current course
4. **Results** - Download outputs

### 2. Audio Extraction

**Input:** MP4 video files or MP3 audio files (mixed)
**Output:** MP3 audio files

**Tool:** FFmpeg
```bash
ffmpeg -i lecture.mp4 -vn -acodec libmp3lame -q:a 2 lecture.mp3
```

### 3. Transcription

**Tool:** Local Whisper (whisper.cpp or OpenAI Whisper)
**Model:** medium or large (configurable based on machine)

**From original repo (batch_transcribe.py):**
- Processes folder of audio files
- Outputs .txt files per lecture
- Progress tracking

### 4. Content Generation

**Private Notes:**
- Lecture-by-lecture summaries (like original)
- **NEW:** Overall course summary section at end
- Key concepts, arguments, definitions
- Study questions

**Public Companion v1 (Lecture Sequence):**
- Match original repo output quality
- Chapter per lecture
- Professional book formatting
- Cover with course title

**Public Companion v2 (Topic Reorganized):**
- Group lectures by philosophical theme:
  - Part I: How to Think (Lectures 1-4)
  - Part II: What Can We Know? (Lectures 5-10)
  - Part III: God and Faith (Lectures 11-16)
  - Part IV: Mind and Self (Lectures 17-25)
  - Part V: Right and Wrong (Lectures 26-30)
  - Part VI: Society and Justice (Lectures 31-35)
  - Part VII: The Big Picture (Lecture 36)
- Synthesize related lectures into chapters
- Cross-reference arguments across lectures
- Transformative (not lecture-mapped)

### 5. Document Formatting

**Book-Ready Word Doc Requirements:**
- Professional fonts (Georgia body, Arial headings)
- Chapter title pages with decorative elements
- Proper margins for print (1" all sides)
- 1.5 line spacing
- First-line paragraph indentation
- Styled quote boxes
- Page breaks between chapters
- Table of contents
- Consistent heading hierarchy

**Cover Generation:**
- Course title
- "A Companion Guide" subtitle
- Professional design template
- PNG output (1600x2560 for Amazon KDP)

---

## File Structure

```
coursumm-pipeline/
├── app.py                    # Gradio web UI
├── config.yaml               # Settings (Whisper model, LLM, etc.)
├── requirements.txt
├── coursumm/
│   ├── __init__.py
│   ├── audio.py              # Audio extraction (ffmpeg)
│   ├── transcribe.py         # Whisper transcription
│   ├── generate.py           # LLM content generation
│   ├── format_word.py        # Word document formatting
│   ├── format_cover.py       # Cover generation
│   ├── topic_mapper.py       # Topic reorganization logic
│   └── pipeline.py           # End-to-end orchestration
├── templates/
│   ├── cover_template.png    # Cover background
│   └── chapter_styles.json   # Word formatting specs
└── output/                   # Generated files
```

---

## Development Phases

### Phase 1: Core Pipeline (MVP)
- [ ] Audio extraction (MP4 → MP3)
- [ ] Integrate local Whisper transcription
- [ ] Basic private notes generation
- [ ] Basic Word output (match original quality)

### Phase 2: Professional Formatting
- [ ] Book-ready Word formatting
- [ ] Chapter title pages
- [ ] Cover generation
- [ ] Table of contents

### Phase 3: Topic Reorganization
- [ ] Topic mapping logic
- [ ] Companion v2 generation
- [ ] Cross-lecture synthesis

### Phase 4: Web UI
- [ ] Gradio interface
- [ ] Folder picker
- [ ] Progress monitoring
- [ ] Batch queue

### Phase 5: Polish
- [ ] Error handling
- [ ] Resume interrupted jobs
- [ ] Configurable LLM (GPT/Claude)
- [ ] Documentation

---

## Questions Resolved

1. ✅ Input: Mix of MP4/MP3
2. ✅ Transcription: Local Whisper
3. ✅ Output format: Word (user converts to EPUB via Calibre)
4. ✅ Two companion versions: lecture-sequence + topic-reorganized
5. ✅ Cover: Auto-generated
6. ✅ Automation: Fully automated with batch queue
7. ✅ Test course: Philosophy (36 lectures)

---

## Dependencies

```
# Core
whisper                 # Local transcription
openai                  # GPT for content generation
anthropic               # Claude alternative
python-docx             # Word document generation
Pillow                  # Cover image generation

# UI
gradio                  # Web interface

# Audio
ffmpeg-python           # Audio extraction

# Utilities
pyyaml                  # Config
tqdm                    # Progress bars
```

---

## Next Steps

1. Review original repo code for reusable components
2. Set up project structure
3. Implement Phase 1 (MVP)
4. Test with Philosophy course
