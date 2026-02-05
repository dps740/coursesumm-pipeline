#!/bin/bash
# CourseSumm v2 - Quick Start Script

set -e

echo "================================================"
echo "CourseSumm v2 - Phase 1 Quick Start"
echo "================================================"
echo ""

# Check if we're in the right directory
if [ ! -f "run_phase1.py" ]; then
    echo "❌ Error: Please run from coursumm-pipeline directory"
    exit 1
fi

# Check FFmpeg
echo "Checking dependencies..."
if ! command -v ffmpeg &> /dev/null; then
    echo "❌ FFmpeg not found!"
    echo "Install with: sudo apt-get install ffmpeg"
    exit 1
else
    echo "✓ FFmpeg installed"
fi

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found!"
    exit 1
else
    echo "✓ Python 3 installed ($(python3 --version))"
fi

# Create venv if needed
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
fi

# Activate venv
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing Python packages..."
pip install -q -r requirements_v2.txt
echo "✓ Dependencies installed"

# Check API key
echo ""
if [ -z "$OPENAI_API_KEY" ]; then
    echo "⚠️  OPENAI_API_KEY not set"
    echo ""
    echo "Please set your API key:"
    echo "  export OPENAI_API_KEY='sk-...'"
    echo ""
    echo "Or add to ~/.bashrc:"
    echo "  echo 'export OPENAI_API_KEY=\"sk-...\"' >> ~/.bashrc"
    echo "  source ~/.bashrc"
    echo ""
    exit 1
else
    echo "✓ OPENAI_API_KEY is set"
fi

# Verify packages
echo ""
echo "Verifying installation..."
python3 -c "import openai, whisper, docx; print('✓ All packages ready')" || {
    echo "❌ Package import failed"
    exit 1
}

# Run test
echo ""
echo "================================================"
echo "Running Phase 1 Test"
echo "================================================"
echo ""
echo "This will:"
echo "  - Process 2 test transcripts"
echo "  - Generate notes using GPT-3.5"
echo "  - Create Word documents"
echo "  - Output to ./test_output/"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."
echo ""

python3 test_phase1.py

echo ""
echo "================================================"
echo "✅ Setup and test complete!"
echo "================================================"
echo ""
echo "Next steps:"
echo "  1. Check output in ./test_output/documents/"
echo "  2. Review generated Word documents"
echo "  3. Process your full course:"
echo "     python run_phase1.py <input> <output> --title 'Course Title'"
echo ""
