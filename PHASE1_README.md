# CourseSumm v2 - Phase 1 MVP

**Status:** ✅ READY FOR TESTING

Phase 1 implements the core pipeline: Video/Audio → Transcripts → Private Notes → Word Documents

## Features

✅ **Audio Extraction** - Extract audio from MP4 videos using FFmpeg  
✅ **MP3 Support** - Direct processing of MP3 audio files  
✅ **Local Whisper** - Transcription using Whisper (GPU/CPU)  
✅ **LLM Generation** - Generate comprehensive private notes (GPT/Claude)  
✅ **Word Output** - Professional book-ready Word documents  
✅ **Batch Processing** - Handle entire course folders automatically  

## Installation

### 1. Install FFmpeg (for audio extraction)

```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# MacOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/download.html
```

### 2. Install Python dependencies

```bash
pip install -r requirements_v2.txt
```

### 3. Set API key

```bash
export OPENAI_API_KEY="sk-..."
# OR
export ANTHROPIC_API_KEY="sk-ant-..."
```

## Usage

### Basic usage

```bash
python run_phase1.py <input_folder> <output_folder> --title "Course Title"
```

### Examples

#### Process audio/video files from scratch

```bash
python run_phase1.py ./audio_files ./output --title "The Big Questions of Philosophy"
```

#### Process existing transcripts (skip audio extraction and transcription)

```bash
python run_phase1.py ./transcripts ./output \
    --title "Philosophy" \
    --skip-audio \
    --skip-transcription
```

#### Use GPT-3.5 (faster, cheaper)

```bash
python run_phase1.py ./audio ./output \
    --title "Philosophy" \
    --model gpt-3.5-turbo
```

#### Use Anthropic Claude

```bash
python run_phase1.py ./audio ./output \
    --title "Philosophy" \
    --provider anthropic \
    --model claude-3-opus-20240229
```

#### Use smaller Whisper model (faster)

```bash
python run_phase1.py ./audio ./output \
    --title "Philosophy" \
    --whisper-model small
```

## Options

```
Required:
  input_folder          Input folder (audio/video files or transcripts)
  output_folder         Output folder for all generated content

Optional:
  --title TEXT          Course title (default: "Course Summary")
  --provider TEXT       LLM provider: openai or anthropic (default: openai)
  --model TEXT          LLM model (default: gpt-4)
  --whisper-model TEXT  Whisper size: tiny/base/small/medium/large (default: medium)
  --skip-audio          Skip audio extraction (use existing MP3s)
  --skip-transcription  Skip transcription (use existing transcripts)
  --skip-generation     Skip generation (use existing notes data)
  -v, --verbose         Verbose logging
```

## Output Structure

```
output/
├── audio/                          # Extracted MP3 files
│   ├── Lect01.mp3
│   ├── Lect02.mp3
│   └── ...
├── transcripts/                    # Whisper transcripts
│   ├── Lect01.txt
│   ├── Lect02.txt
│   └── ...
├── notes/                          # Generated notes (JSON)
│   ├── Lect01_notes.json
│   ├── Lect02_notes.json
│   └── ...
└── documents/
    ├── Course_Title_Complete.docx  # Compiled document
    └── chapters/                   # Individual chapters
        ├── Lect01.docx
        ├── Lect02.docx
        └── ...
```

## Generated Content

Each lecture generates:

- **Title** - Extracted or inferred from content
- **Quote** - Memorable quote from the content
- **Summary** - 3-5 paragraphs (300-500 words)
- **Key Themes** - 5 themes with detailed explanations
- **Key Takeaways** - Main points with examples
- **Knowledge Check** - Q&A pairs for review

## Testing with Philosophy Course

The test data is available on Google Drive (folder ID: 1LsAmsNR4HddqT339ci_7aNumAk8Hcbo5):
- 10 sample MP3 files
- 36 existing transcripts

### Test with existing transcripts

```bash
# Download transcripts to ./test_transcripts/
python run_phase1.py ./test_transcripts ./test_output \
    --title "The Big Questions of Philosophy" \
    --skip-audio \
    --skip-transcription
```

This will process the transcripts and generate Word documents.

## Performance

**Whisper transcription times (per hour of audio):**
- tiny: ~2 minutes (CPU)
- small: ~5 minutes (CPU)
- medium: ~10 minutes (CPU) / ~2 minutes (GPU)
- large: ~20 minutes (CPU) / ~4 minutes (GPU)

**LLM generation:**
- ~30-60 seconds per lecture (GPT-4)
- ~15-30 seconds per lecture (GPT-3.5)

**Full course (36 lectures):**
- Transcription: ~6 hours (medium/CPU) or ~1 hour (medium/GPU)
- Generation: ~30 minutes (GPT-4)
- Total: ~6-7 hours end-to-end (CPU) or ~1.5 hours (GPU)

## Troubleshooting

### FFmpeg not found

Install FFmpeg for your platform (see Installation section).

### Whisper out of memory

Use a smaller model:
```bash
--whisper-model small  # or tiny
```

### OpenAI rate limits

Use GPT-3.5 or add delays between requests.

### Torch CUDA errors

Install CPU-only version:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

## Next Phases

- **Phase 2**: Professional Word formatting (book-ready typography, covers)
- **Phase 3**: Public companions (V1 lecture notes, V2 going deeper, V3 combined)
- **Phase 4**: Gradio web UI with batch queue

## Log Files

All output is logged to `coursumm_v2.log` in the current directory.

## Architecture

```
┌─────────────────┐
│  Audio/Video    │
│  Files (MP4,    │
│  MP3, etc.)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Audio           │  FFmpeg
│ Extraction      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ MP3 Files       │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Whisper         │  Local Whisper
│ Transcription   │  (GPU/CPU)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Transcripts     │
│ (.txt)          │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ LLM Content     │  GPT-4 / Claude
│ Generation      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Word Doc        │  python-docx
│ Formatting      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Private Notes   │
│ (.docx)         │
└─────────────────┘
```
