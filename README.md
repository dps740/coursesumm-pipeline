# CourSumm - Transcript-to-Companion Pipeline v2

Transform course transcripts into two outputs:
1. **Private Notes** - High-fidelity, lecture-aligned notes for personal use
2. **Public Companion** - Transformative, topic-based workbook for sale

---

## What This Does

**Input:** Raw lecture transcripts (`.txt` or `.md` files)

**Outputs:**
1. **Private Notes** (`output/private/`) - Lecture-by-lecture summaries with key arguments, definitions, and quizzes
2. **Public Companion** (`output/public/`) - Transformative topic-based workbook with argument maps, exercises, and synthesis

**Key Innovation:** Uses "Argument Primitives" layer to ensure public content is transformative (not paraphrase) by extracting abstract claims/premises and reorganizing by topic.

---

## Quick Start (5 Minutes)

### 1. Install Dependencies

```bash
cd ~/clawd/projects/coursumm-pipeline
pip install -r requirements.txt
```

### 2. Set Up Configuration

```bash
# Copy example config
cp config.example.yaml config.yaml

# Edit config.yaml and add your API key
nano config.yaml
```

**Required changes in `config.yaml`:**
```yaml
llm_provider: "openai"      # or "anthropic"
llm_model: "gpt-4o-mini"    # or your preferred model
openai_api_key: "sk-..."    # ADD YOUR KEY HERE
```

### 3. Add Transcripts

Place your lecture transcripts in the `transcripts/` directory:
- One file per lecture (e.g., `L01_introduction.txt`, `L02_arguments.md`)
- Plain text or markdown format
- Filename format: `L##_title.txt` (e.g., `L01_intro.txt`)

**See "Testing with Sample Data" below for example transcripts.**

### 4. Run the Pipeline

```bash
# Generate both private notes and public companion
python -m coursumm --mode both

# Or just private notes (faster)
python -m coursumm --mode private

# Or just public companion
python -m coursumm --mode public
```

### 5. Check Output

```bash
# Private notes
ls output/private/

# Public companion
cat output/public/book.md
```

---

## Testing with Sample Data

Don't have transcripts yet? Create a test transcript:

```bash
mkdir -p transcripts/

cat > transcripts/L01_truth.txt << 'EOF'
Welcome to Philosophy 101. Today we're discussing truth.

What is truth? The correspondence theory says truth is when a statement matches reality. 
If I say "the sky is blue" and the sky really is blue, that statement is true.

But there are problems with this view. First, what does "matches" mean? How do we compare 
a statement to reality? Second, what about statements like "2+2=4"? What reality does that match?

The coherence theory offers an alternative. Truth is coherence with other beliefs. 
A statement is true if it fits consistently with everything else we believe.

But this has issues too. A delusional person might have a perfectly coherent system 
of false beliefs.

Next lecture, we'll explore pragmatist theories of truth.
EOF

cat > transcripts/L02_knowledge.txt << 'EOF'
Last time we discussed truth. Today: knowledge.

What is knowledge? The traditional definition is "justified true belief." 
You know something if: (1) it's true, (2) you believe it, (3) you have good reasons.

But Gettier (1963) showed this isn't enough. Here's his example: 
Smith believes Jones owns a Ford (good evidence - he's seen Jones driving it). 
Smith also believes "Jones owns a Ford OR Brown is in Barcelona" (disjunction is true if either part is).
But Jones doesn't own a Ford - he was borrowing it. Brown happens to be in Barcelona.
So Smith has a justified true belief that's not knowledge!

This sparked decades of work trying to fix the JTB definition. We'll explore some 
attempts next lecture.
EOF
```

**Now test:**
```bash
# Run on sample data
python -m coursumm --mode both

# Check outputs
ls output/private/    # Should see L01.md, L02.md
ls output/public/     # Should see book.md, trace_report.json
```

---

## What You'll Get

### Private Notes Example

```markdown
# L01: Truth

## Summary
Discussion of two theories of truth: correspondence (truth = matching reality) 
and coherence (truth = fitting with other beliefs). Both have significant problems.

## Key Arguments

**Argument 1: Problems with Correspondence Theory**
- Premise: Correspondence theory says truth means "matching reality"
- Objection: Unclear what "matching" means - how do we compare statements to reality?
- Objection: Abstract truths (e.g., math) don't obviously match any reality

**Argument 2: Problems with Coherence Theory**
- Premise: Coherence theory says truth = consistency with other beliefs
- Objection: A delusional person can have perfectly coherent false beliefs
...
```

### Public Companion Example

```markdown
# Part II: The Big Questions

## Chapter 1: What Is Truth?

### The Matching Game: Correspondence Theory

When we say something is "true," what do we really mean? One ancient answer: 
truth is when our words match the world...

**Try This:** Consider the statement "There are exactly 47 chairs in your house."
- If you've never counted, is it true or false?
- What would make it true?
- How would you verify it?

[Reorganized by topic, not lecture order]
[Includes exercises, argument maps, synthesis]
...
```

---

## Project Structure

```
coursumm-pipeline/
├── coursumm/
│   ├── cli.py                 # Command-line interface
│   ├── config.py              # Configuration management
│   ├── models.py              # Data structures
│   ├── pipeline/
│   │   ├── parser.py          # Parse transcripts
│   │   ├── primitives.py      # Extract argument primitives
│   │   ├── clustering.py      # Cluster by topic
│   │   ├── private_gen.py     # Generate private notes
│   │   ├── public_gen.py      # Generate public chapters
│   │   └── validator.py       # Safety validator (anti-paraphrase)
│   └── utils/
│       ├── llm.py             # LLM API integration
│       └── similarity.py      # Text similarity checking
├── transcripts/               # INPUT: Place your lecture files here
├── output/
│   ├── private/              # OUTPUT: Lecture-by-lecture notes
│   └── public/               # OUTPUT: Topic-based companion book
├── config.yaml               # YOUR SETTINGS (copy from config.example.yaml)
└── requirements.txt          # Python dependencies
```

---

## Configuration Options

**`config.yaml`:**

```yaml
# Input/Output
transcripts_dir: "./transcripts"
output_dir: "./output"

# LLM Settings
llm_provider: "openai"         # or "anthropic"
llm_model: "gpt-4o-mini"       # or "claude-sonnet-4"
openai_api_key: "sk-..."       # REQUIRED
anthropic_api_key: "sk-..."    # If using Anthropic

# Public Safety Validator (prevents paraphrase)
public_safety:
  enabled: true
  max_ngram_overlap: 0.02         # Max 2% word overlap with transcripts
  max_cosine_similarity: 0.80     # Semantic similarity threshold
  max_consecutive_words: 8        # Longest exact quote allowed
  regeneration_attempts: 3        # Retry if safety fails

# Topic Categories (customize for your course)
topics:
  - truth
  - knowledge
  - mind
  - free_will
  - god_religion
  - morality
  - meaning
  - justice
  - consciousness
```

---

## CLI Commands

```bash
# Basic usage
python -m coursumm --mode both              # Generate both outputs

# Mode selection
python -m coursumm --mode private           # Only private notes (faster)
python -m coursumm --mode public            # Only public companion

# Safety options
python -m coursumm --mode public --similarity-threshold 0.75  # Stricter safety
python -m coursumm --mode public --ngram-threshold 0.01       # Lower overlap allowed

# Specify input directory
python -m coursumm --mode both --input ./my-transcripts/

# Output format (future)
python -m coursumm --mode both --format docx   # Export to Word
```

---

## How It Works

### Philosophy: Argument Primitives Layer

**Problem:** Generating public content directly from transcripts risks close paraphrase (copyright violation).

**Solution:** Intermediate representation
1. **Extract** abstract argument primitives (claims, premises, definitions, objections, examples)
2. **Cluster** primitives by philosophical topic (not lecture order)
3. **Generate** public content from primitives only (never from transcript text)

This ensures the public output is **necessarily transformative** - reorganized structure, new examples, pedagogical exercises.

### Pipeline Steps

```
Transcripts
    ↓
[Parse] → Extract lecture metadata, clean text
    ↓
[Primitives] → Identify claims, premises, definitions, objections
    ↓
         ┌─────────────┬─────────────┐
         ↓             ↓             ↓
    [Private]    [Clustering]   [Public]
      Notes      By Topic       Companion
         ↓             ↓             ↓
    output/private/   output/public/
    L01.md, L02.md    book.md
```

### Safety Validator (Public Only)

Checks every generated section for:
1. **No lecture references** - No "Lecture X", no lecture titles in text
2. **Paraphrase distance** - Max 8 consecutive words, <2% n-gram overlap, <0.80 cosine similarity
3. **Transformative value** - Must include exercises, argument maps, or synthesis

Failed sections are regenerated (up to 3 attempts) or flagged for manual review.

---

## Troubleshooting

### "No API key found"

**Solution:** Add your API key to `config.yaml`:
```yaml
openai_api_key: "sk-your-key-here"
```

### "No transcripts found"

**Solution:** Add `.txt` or `.md` files to `transcripts/` directory. 
Filename format: `L##_title.txt` (e.g., `L01_intro.txt`)

### "Safety check failed: High n-gram overlap"

**What it means:** Generated text too similar to transcript (paraphrase risk).

**Solution:** System auto-regenerates up to 3 times. Check `output/public/trace_report.json` for flagged sections.

**Manual fix:** If repeated failures, try:
```bash
# Stricter safety settings
python -m coursumm --mode public --ngram-threshold 0.01 --similarity-threshold 0.70
```

### "LLM API error"

**Solution:** 
1. Check API key in config.yaml
2. Check internet connection
3. Verify API credit balance
4. Check model name (e.g., `gpt-4o-mini` for OpenAI)

### Private notes are too detailed / Public chapters too abstract

**Solution:** Edit `config.yaml` topics list to match your course content. Add/remove topics as needed.

---

## Expected Costs

**Typical philosophy course (15 lectures, ~10k words each):**

- **Private notes only:** ~$0.50-1.00 (gpt-4o-mini)
- **Public companion only:** ~$2.00-4.00 (includes safety regenerations)
- **Both outputs:** ~$3.00-5.00 total

**Using GPT-4 instead of gpt-4o-mini:** 10-20x more expensive (~$30-100)

**Tip:** Test with `--mode private` first on a few lectures to verify setup before running full public pipeline.

---

## Example Workflow: Full Course Processing

```bash
# 1. Organize your transcripts
cd ~/clawd/projects/coursumm-pipeline
mkdir transcripts
# Copy your lecture files (L01_intro.txt, L02_truth.txt, etc.)

# 2. Set up config
cp config.example.yaml config.yaml
nano config.yaml  # Add API key

# 3. Test on one lecture first
mv transcripts/L02*.txt transcripts_backup/  # Temporarily move others
python -m coursumm --mode private             # Quick test
# Check output/private/L01.md

# 4. Run full private notes (fast)
mv transcripts_backup/* transcripts/
python -m coursumm --mode private
# Check output/private/ for all lectures

# 5. Generate public companion (slower, includes safety checks)
python -m coursumm --mode public
# Check output/public/book.md

# 6. Review safety report
cat output/public/trace_report.json
# Look for "flagged" sections that need manual review

# 7. Export (future feature)
# python -m coursumm --mode public --format docx
```

---

## Testing Checklist

- [ ] Python 3.9+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Config file created (`config.yaml`) with API key
- [ ] At least one transcript in `transcripts/` directory
- [ ] Run pipeline: `python -m coursumm --mode private`
- [ ] Check output: `ls output/private/`
- [ ] (Optional) Test public mode: `python -m coursumm --mode public`
- [ ] (Optional) Review safety: `cat output/public/trace_report.json`

---

## Next Steps

1. **Process your course** - Add all lecture transcripts and run pipeline
2. **Customize topics** - Edit `config.yaml` topics list to match your content
3. **Review outputs** - Check private notes for accuracy, public companion for safety
4. **Export** - (Future) Generate DOCX or PDF for distribution
5. **Iterate** - Adjust safety thresholds based on trace report

---

## License

MIT

---

## Questions?

Common questions answered above in Troubleshooting. For other issues, check the trace report (`output/public/trace_report.json`) for detailed processing logs.

