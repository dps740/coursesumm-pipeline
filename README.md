# CourSumm - Transcript-to-Companion Pipeline v2

Transform course transcripts into two outputs:
1. **Private Notes** - High-fidelity, lecture-aligned notes for personal use
2. **Public Companion** - Transformative, topic-based workbook for sale

## Philosophy

The key innovation is the **"Argument Primitives" intermediate layer**. Instead of generating public content directly from transcript text (which risks close paraphrase), we:

1. Extract abstract primitives (claims, premises, definitions, objections)
2. Cluster by philosophical problem/topic
3. Generate public content from primitives only

This ensures the public output is **necessarily transformative** - not paraphrase.

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Copy example config
cp config.example.yaml config.yaml

# Run pipeline (both outputs)
python -m coursumm --mode both transcripts/

# Or just private notes
python -m coursumm --mode private transcripts/

# Or just public companion
python -m coursumm --mode public transcripts/
```

## Project Structure

```
coursumm-pipeline/
├── coursumm/
│   ├── __init__.py
│   ├── cli.py                 # Command-line interface
│   ├── config.py              # Configuration
│   ├── models.py              # Data models
│   ├── pipeline/
│   │   ├── parser.py          # Transcript parsing
│   │   ├── primitives.py      # Argument primitive extraction
│   │   ├── clustering.py      # Topic clustering
│   │   ├── private_gen.py     # Private notes generation
│   │   ├── public_gen.py      # Public chapter generation
│   │   └── validator.py       # Public safety validator
│   └── utils/
│       ├── llm.py             # LLM integration
│       └── similarity.py      # N-gram and embedding similarity
├── tests/
├── config.example.yaml
├── requirements.txt
└── transcripts/               # Input directory
    └── L01_introduction.txt
```

## Outputs

### Private Notes (`output/private/`)

```
L01.md
L02.md
...
```

Each contains:
- Summary (bullet + narrative)
- Key arguments (structured)
- Key distinctions/definitions
- Quick quiz

### Public Companion (`output/public/`)

```
book.md
public_trace_report.json
```

Structure:
- Part I: Orientation
- Part II: The Big Questions (chapters by topic)
- Part III: Synthesis
- Appendix: Glossary, argument patterns, reading list

## Safety Checks (Public Output)

The public safety validator ensures:

1. **No lecture mapping**: No "Lecture X", no lecture titles, no lecture order
2. **Paraphrase distance**: 
   - Max 8 consecutive words from transcript
   - 3-gram overlap < 2% per section
   - Cosine similarity < 0.80 to any transcript chunk
3. **Transformative value**: Each chapter has argument maps, exercises, synthesis

Failed sections are regenerated up to 3 times, then flagged for manual review.

## Configuration

```yaml
# config.yaml
transcripts_dir: "./transcripts"
output_dir: "./output"

# LLM settings
llm_provider: "openai"  # or "anthropic"
llm_model: "gpt-4o-mini"

# Safety thresholds (public mode)
public_safety:
  enabled: true
  max_ngram_overlap: 0.02      # 2%
  max_cosine_similarity: 0.80
  max_consecutive_words: 8
  regeneration_attempts: 3

# Topic categories for philosophy courses
topics:
  - truth
  - knowledge
  - mind
  - free_will
  - god_religion
  - morality
  - meaning
```

## CLI Options

```bash
# Mode selection
--mode private|public|both

# Safety settings
--public-safe              # Enable safety checks (default for public)
--similarity-threshold 0.80
--ngram-threshold 0.02

# Output format
--format md|docx|both
```

## License

MIT
