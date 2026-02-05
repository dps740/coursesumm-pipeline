# Companion Book Plan: "The Big Questions of Philosophy"

## Vision

A **true companion** to the lecture series — not a summary, not a regurgitation, but a book that stands alongside the lectures and makes them richer. It should feel like sitting down with a brilliant friend who also took the course and says *"OK, but let me tell you what I found when I went deeper..."*

The book **calls back to the lectures** ("As Professor [name] argues in Lecture 34, Mill's harm principle...") then **goes beyond them** — more philosophers, more arguments, modern applications, original analysis. Someone who reads this alongside the lectures gets 10x more than either alone.

---

## Source Material

**36 lecture transcripts** from "The Big Questions of Philosophy" (Great Courses / Teaching Company)
- Located in Google Drive (need to pull all 36)
- 3 already local: Lectures 34 (Liberty), 35 (Justice), 36 (Meaning of Life)
- Each transcript ~26,000 characters (~6,000 words)
- Total corpus: ~216,000 words of lecture material

---

## Book Structure

### Organizing Principle: Thematic, Not Sequential

The lectures follow a course sequence. The book reorganizes by **philosophical theme**, creating a coherent narrative arc that works as a standalone book. However, each chapter explicitly references which lectures it companions ("This chapter expands on themes from Lectures 12-14").

### Proposed Chapter Structure (~8-12 chapters)

**Note:** Final chapter breakdown depends on analyzing all 36 transcripts. Below is a projected structure based on the course title and the 3 available transcripts:

**Part I: What Can We Know?**
- Ch 1: The Problem of Knowledge (epistemology lectures)
- Ch 2: Truth, Belief, and the Limits of Reason

**Part II: What Is Real?**  
- Ch 3: Mind, Body, and Consciousness
- Ch 4: Free Will and Determinism

**Part III: Does God Exist?**
- Ch 5: Arguments For and Against
- Ch 6: Faith, Doubt, and the Modern World

**Part IV: What Should We Do?**
- Ch 7: Moral Foundations (ethics lectures)
- Ch 8: Liberty, Rights, and the Harm Principle (expands Lecture 34)
- Ch 9: Justice and the Fair Society (expands Lecture 35)

**Part V: What Does It All Mean?**
- Ch 10: The Meaning of Life (expands Lecture 36)
- Ch 11: Philosophy in the 21st Century (original synthesis chapter)

**Front Matter:**
- Title page
- Copyright & disclaimer ("This is an independently produced companion guide...")
- Table of Contents
- Introduction: "How to Use This Book" (explains the companion concept)

**Back Matter:**
- Glossary of Key Terms
- Annotated Bibliography / Further Reading
- Lecture Cross-Reference Index (which chapters map to which lectures)
- About the Author

---

## Content Approach Per Chapter

Each chapter follows this pattern:

### 1. Lecture Callback (10-15% of chapter)
Ground the reader in what the lectures covered. Reference specific lecture numbers and the lecturer's key arguments.

> *"In Lecture 34, we encountered Mill's powerful argument that 'the only purpose for which power can be rightfully exercised over any member of a civilized community, against his will, is to prevent harm to others.' The lecturer applied this to marijuana legalization, gay marriage, and free speech. But Mill's harm principle opens up far more territory than a single lecture can explore..."*

This serves two purposes:
- For someone taking the course: "Ah yes, I remember that lecture" → instant connection
- For someone who hasn't taken the course: enough context to follow along

### 2. Deeper Philosophical Context (25-30%)
Bring in philosophers and arguments the lectures didn't have time for:
- Primary source material (actual quotes from Mill, Rawls, Nozick, etc.)
- Historical context (what was happening when these ideas emerged?)
- Philosophers the lecturer didn't cover (or only mentioned briefly)
- Intellectual genealogy (who influenced whom, how ideas evolved)

### 3. Arguments and Counterarguments (25-30%)
The meaty philosophical engagement:
- Steel-man the strongest objections to the lecture's positions
- Present genuine debates between philosophical traditions
- Original thought experiments that test the ideas
- Edge cases and hard problems the lecture glossed over

### 4. Modern Applications (15-20%)
Connect to contemporary issues:
- How does Mill's harm principle apply to social media moderation?
- What would Rawls say about AI replacing jobs?
- Does the free speech debate change when algorithms amplify extremism?
- Real-world case studies and current events

### 5. Reflection & Engagement (5-10%)
End each chapter with:
- "Key Tensions" — unresolved questions to sit with
- "Going Further" — specific books/papers for the curious reader
- A provocative closing thought or question

---

## Voice and Style

**Target:** Popular philosophy — accessible but not dumbed down. Think:
- Nigel Warburton's "A Little History of Philosophy" (clarity, warmth)
- Simon Blackburn's "Think" (intellectual rigor + readability)
- Michael Sandel's "Justice" (engaging real-world examples)

**Tone:**
- Intellectually confident but not arrogant
- Genuinely curious — presents questions as fascinating, not academic obligations
- Conversational without being sloppy
- Uses "we" and "us" — the reader is a thinking partner
- Occasional wit (philosophy doesn't have to be dry)

**What to avoid:**
- Textbook voice ("In this chapter we will examine...")
- Summary voice ("The lecturer argues that...")  
- AI slop ("delves into", "rich tapestry", "In conclusion")
- Hedging everything ("It could be argued that perhaps...")

**Chapter length:** 5,000-8,000 words each
**Total book:** 60,000-80,000 words (standard non-fiction)

---

## Production Pipeline

### Step 1: Transcript Analysis (Opus)
- Pull all 36 transcripts from Google Drive
- Opus reads all transcripts and produces:
  - Complete topic map (every philosophical concept, argument, and thinker mentioned)
  - Proposed chapter structure with lecture cross-references
  - Gaps and expansion opportunities per theme

### Step 2: Chapter Outline (Opus)
- For each chapter, Opus produces a detailed 500-word outline:
  - Lecture callbacks (specific references)
  - Expansion points (which philosophers, arguments, examples to add)
  - Modern applications
  - Key quotes to include (from primary sources, not the lectures)
- David reviews and approves structure before writing begins

### Step 3: Chapter Writing (Opus)
- One chapter at a time
- Each chapter gets its own prompt with:
  - The relevant lecture transcripts
  - The approved outline
  - Style guide (voice, tone, what to avoid)
  - Previous chapters (for continuity and cross-referencing)
- Opus writes the full chapter in Markdown
- Target: ~6,000 words per chapter

### Step 4: Editorial Pass (Opus)
- Opus reviews each chapter for:
  - Consistency with other chapters
  - Voice/tone consistency
  - Factual accuracy of philosophical claims
  - Flow and readability
  - Proper lecture callbacks

### Step 5: Formatting
- **Markdown → EPUB** (Pandoc + professional CSS)
- **Markdown → PDF** (Typst, for print-on-demand)
- Professional CSS/Typst template built once, reused for all books in series

### Step 6: Cover Generation
- AI image generation (FAL.ai) for philosophical artwork
- Professional typography overlay
- Series branding (for future course companions)

---

## Format Details

### EPUB (Primary — Amazon Kindle)
Professional CSS with:
- **Typography:** EB Garamond or Crimson Pro (body), clean sans-serif for headings
- **Drop caps** on chapter openings
- **Pull quote boxes** for key philosophical arguments
- **"Key Concept" callout boxes** — styled with subtle background + border
- **"Think About It" prompts** — styled distinctively
- **Chapter title pages** with decorative separators (CSS ornaments, no images needed)
- **Proper front/back matter** styling
- **Footnotes** for scholarly references (EPUB supports these natively)

### PDF (Secondary — Print on Demand)
Typst template with:
- Professional page layout (6"×9" trim, standard trade paperback)
- Running headers (book title left, chapter title right)
- Page numbers
- Same typography choices as EPUB
- Print-ready margins

### Why Not Word
- python-docx cannot produce publishing-quality typography
- No orphan/widow control, no proper drop caps, no real page layout
- EPUB + PDF covers both digital and print distribution
- Markdown intermediate format is easily editable if Word is ever needed

---

## Legal & Copyright

### What makes this legally safe:
1. **No transcript reproduction** — we never quote the lecturer at length
2. **Original analysis** — the philosophical arguments are public domain; our analysis is original
3. **Transformative work** — reorganized by theme, expanded with new material
4. **Clear labeling** — "An independently produced companion guide" (not affiliated with the course/publisher)
5. **Primary sources** — we quote Mill, Rawls, etc. directly (public domain), not the lecturer's paraphrase

### Disclaimer (front matter):
> *This is an independently produced companion guide. It is not affiliated with, endorsed by, or connected to The Great Courses, The Teaching Company, or the original course instructor. All philosophical arguments discussed are drawn from publicly available primary sources and the author's original analysis.*

---

## Amazon KDP Details

### Listing Strategy:
- **Title:** "Beyond the Big Questions: A Philosophical Companion"
- **Series:** "The Great Courses Companion Series"
- **Category:** Philosophy > Introduction, Philosophy > Ethics
- **Keywords:** philosophy companion guide, big questions philosophy, Mill harm principle, Rawls justice, meaning of life philosophy, great courses companion
- **Price:** $9.99 Kindle, $14.99 paperback

### Series Potential:
This is a template. Any Great Courses course could get the same treatment under "The Great Courses Companion Series":
- "Beyond Consciousness: A Companion to the Neuroscience of Mind"
- "Beyond the Greeks: A Companion to Ancient Philosophy"
- "Beyond the Numbers: A Companion to the Joy of Mathematics"
- etc.

---

## Execution Timeline

| Phase | Task | Time | Model |
|-------|------|------|-------|
| 0 | Pull all 36 transcripts from Drive | 15 min | — |
| 1 | Transcript analysis + topic map | 30 min | Opus |
| 2 | Chapter outline (David reviews) | 1 hr | Opus |
| 3 | Write all chapters | 4-6 hrs | Opus |
| 4 | Editorial pass | 1-2 hrs | Opus |
| 5 | Build EPUB/PDF templates + format | 2 hrs | Code |
| 6 | Cover generation | 30 min | FAL.ai |
| **Total** | | **~10-12 hrs** | |

### Credit Usage Estimate (Opus 4.5):
- Input: ~216k words of transcripts × multiple passes ≈ ~1M input tokens
- Output: ~80k words of book + outlines + analysis ≈ ~400k output tokens
- This is substantial — prioritize chapter writing for Opus credits
- Template building and formatting don't need Opus (can use Sonnet or code)

---

## Session Handoff Instructions

**GOAL: One-shot the entire book in a single session.** David has Opus credits resetting at 10 AM MT (5 PM UTC) Feb 5. Use them aggressively.

When starting the new session to execute this:

1. **Read this file first** — it's the complete plan
2. **Pull ALL 36 transcripts from Google Drive** — search for "Big Questions" or "philosophy lecture" transcripts
3. **Phase 1:** Feed ALL transcripts to Opus, get topic map + chapter structure (fast — 30 min)
4. **Phase 2:** Present chapter outline to David for quick approval, then GO
5. **Phase 3:** Write ALL chapters back to back. Don't stop between chapters. Each in its own Markdown file under `output/book/`. This is the bulk of the work — 4-6 hours of Opus generation.
6. **Phase 4-6:** Polish, format (EPUB + PDF), generate cover
7. **Save each chapter as you go** — if session dies, next session picks up from last saved chapter
8. **Do NOT wait for feedback between chapters** — write them all, David reviews the complete manuscript after

### File Structure:
```
projects/coursumm-pipeline/
├── transcripts/          # All 36 lecture transcripts
├── output/
│   └── book/
│       ├── outline.md          # Approved chapter structure
│       ├── topic_map.md        # Full analysis of all transcripts
│       ├── ch01_knowledge.md   # Chapter drafts
│       ├── ch02_truth.md
│       ├── ...
│       ├── front_matter.md     # Title, copyright, intro
│       ├── back_matter.md      # Glossary, bibliography, index
│       └── full_book.md        # Assembled final manuscript
├── templates/
│   ├── book.css               # EPUB stylesheet
│   └── book.typ               # Typst template
└── final/
    ├── companion_book.epub
    ├── companion_book.pdf
    └── cover.png
```

---

## Key Decisions (Confirmed)

1. ✅ **Thematic structure** (not lecture-by-lecture) — confirmed
2. ✅ **Lecture callbacks + expansion** — confirmed ("true companion")
3. ✅ **Series name:** "The Great Courses Companion Series"
4. ✅ **Book title:** "Beyond the Big Questions: A Philosophical Companion"
5. ✅ **Author:** Seo-Yun Kim (same pseudonym across all projects)
6. ✅ **Format:** EPUB + PDF. No more Word.
7. ✅ **Approach:** One-shot the entire book in a single session. Maximize Opus credit usage before reset (tomorrow 10 AM MT / 5 PM UTC).
8. ⬜ **Chapter structure** — finalize after Phase 1 topic analysis
9. ⬜ **Voice/style preference** — any adjustments to style guide above?
