# CourseSumm v2 - Setup Guide

## Quick Start

### 1. Create Virtual Environment

```bash
cd ~/clawd/projects/coursumm-pipeline
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements_v2.txt
```

### 3. Set API Key

```bash
# OpenAI (recommended for testing)
export OPENAI_API_KEY="sk-..."

# OR Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
```

To make it permanent, add to `~/.bashrc` or `~/.profile`:
```bash
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc
source ~/.bashrc
```

### 4. Verify Setup

```bash
# Check FFmpeg
ffmpeg -version

# Check Python packages
python -c "import openai, anthropic, whisper, docx; print('✓ All packages installed')"

# Check API key
python -c "import os; print('API Key:', 'SET' if os.getenv('OPENAI_API_KEY') else 'NOT SET')"
```

### 5. Run Test

```bash
python test_phase1.py
```

This will:
- Process 2 test transcripts
- Generate notes using GPT-3.5
- Create Word documents
- Output to `./test_output/`

## System Requirements

### Required

- Python 3.8+
- FFmpeg (for audio extraction)
- 8GB RAM minimum
- Internet connection (for LLM API calls)

### Recommended

- Python 3.10+
- 16GB RAM
- NVIDIA GPU with 8GB+ VRAM (for faster Whisper transcription)
- SSD storage

## FFmpeg Installation

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

### MacOS
```bash
brew install ffmpeg
```

### Windows
Download from: https://ffmpeg.org/download.html

Add to PATH after installation.

## GPU Support (Optional)

For faster Whisper transcription with NVIDIA GPU:

```bash
# Check if CUDA is available
python -c "import torch; print('CUDA available:', torch.cuda.is_available())"

# If not available, install PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

## Troubleshooting

### "externally-managed-environment" error

Use virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements_v2.txt
```

### FFmpeg not found

Verify installation:
```bash
which ffmpeg
ffmpeg -version
```

If not found, follow installation instructions above.

### Whisper out of memory

Use smaller model:
```bash
python run_phase1.py input/ output/ --whisper-model small
```

Or use CPU-only PyTorch:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### OpenAI rate limit errors

- Use GPT-3.5 instead of GPT-4 (cheaper, faster)
- Wait between requests
- Check your OpenAI usage dashboard

### Import errors

Activate virtual environment:
```bash
source venv/bin/activate
```

## Development

### Running from source

```bash
# Activate venv
source venv/bin/activate

# Run pipeline
python run_phase1.py input/ output/ --title "Course"

# Run tests
python test_phase1.py
```

### Adding to PATH

To run from anywhere:
```bash
# Add to ~/.bashrc
export PATH="$HOME/clawd/projects/coursumm-pipeline/venv/bin:$PATH"
```

## Next Steps

After setup completes:

1. **Test with sample data** - Run `python test_phase1.py`
2. **Process your course** - Use existing transcripts or audio files
3. **Check output** - Review generated Word documents
4. **Move to Phase 2** - Professional formatting and covers (coming soon)

## Support

Check logs in `coursumm_v2.log` for detailed error messages.
