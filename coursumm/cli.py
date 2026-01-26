"""Command-line interface for CourSumm pipeline."""

import asyncio
import json
from pathlib import Path
from typing import Optional
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from coursumm.config import Config, set_config, get_config
from coursumm.models import ValidationStatus
from coursumm.pipeline.parser import parse_transcripts
from coursumm.pipeline.primitives import extract_lecture_primitives
from coursumm.pipeline.clustering import cluster_primitives
from coursumm.pipeline.private_gen import generate_private_notes, format_private_notes_md
from coursumm.pipeline.public_gen import generate_public_chapter, format_public_chapter_md
from coursumm.pipeline.validator import (
    validate_public_chapter, generate_trace_report, format_trace_report_json
)


console = Console()


@click.command()
@click.argument('transcripts_dir', type=click.Path(exists=True))
@click.option('--mode', type=click.Choice(['private', 'public', 'both']), default='both',
              help='Output mode: private notes, public companion, or both')
@click.option('--config', 'config_path', type=click.Path(), default=None,
              help='Path to config YAML file')
@click.option('--output', 'output_dir', type=click.Path(), default='./output',
              help='Output directory')
@click.option('--public-safe/--no-public-safe', default=True,
              help='Enable safety checks for public output')
@click.option('--similarity-threshold', type=float, default=0.80,
              help='Max cosine similarity for public content')
@click.option('--ngram-threshold', type=float, default=0.02,
              help='Max 3-gram overlap for public content')
def main(
    transcripts_dir: str,
    mode: str,
    config_path: Optional[str],
    output_dir: str,
    public_safe: bool,
    similarity_threshold: float,
    ngram_threshold: float,
):
    """
    CourSumm - Transform transcripts into private notes and public companions.
    
    TRANSCRIPTS_DIR: Directory containing transcript files (L##_title.txt)
    """
    # Load config
    config = Config.load(Path(config_path) if config_path else None)
    config.transcripts_dir = Path(transcripts_dir)
    config.output_dir = Path(output_dir)
    config.public_safety.enabled = public_safe
    config.public_safety.max_cosine_similarity = similarity_threshold
    config.public_safety.max_ngram_overlap = ngram_threshold
    set_config(config)
    
    # Create output directories
    (config.output_dir / "private").mkdir(parents=True, exist_ok=True)
    (config.output_dir / "public").mkdir(parents=True, exist_ok=True)
    (config.output_dir / "intermediate").mkdir(parents=True, exist_ok=True)
    
    # Run pipeline
    asyncio.run(run_pipeline(mode))


async def run_pipeline(mode: str):
    """Run the main pipeline."""
    config = get_config()
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # Step 1: Parse transcripts
        task = progress.add_task("Parsing transcripts...", total=None)
        chunks, lecture_titles = parse_transcripts(config.transcripts_dir)
        console.print(f"  ✓ Parsed {len(chunks)} chunks from {len(lecture_titles)} lectures")
        progress.remove_task(task)
        
        # Group chunks by lecture
        chunks_by_lecture = {}
        for chunk in chunks:
            if chunk.lecture_id not in chunks_by_lecture:
                chunks_by_lecture[chunk.lecture_id] = []
            chunks_by_lecture[chunk.lecture_id].append(chunk)
        
        # Step 2: Extract primitives
        task = progress.add_task("Extracting argument primitives...", total=len(chunks_by_lecture))
        all_primitives = []
        for lecture_id, lecture_chunks in chunks_by_lecture.items():
            primitives = await extract_lecture_primitives(lecture_chunks)
            all_primitives.append(primitives)
            
            # Save intermediate
            with open(config.output_dir / "intermediate" / f"{lecture_id}_primitives.json", "w") as f:
                f.write(primitives.model_dump_json(indent=2))
            
            progress.advance(task)
        
        total_primitives = sum(
            len(p.claims) + len(p.premises) + len(p.definitions) + len(p.objections) + len(p.examples)
            for p in all_primitives
        )
        console.print(f"  ✓ Extracted {total_primitives} primitives")
        progress.remove_task(task)
        
        # Step 3: Generate private notes (if requested)
        if mode in ['private', 'both']:
            task = progress.add_task("Generating private notes...", total=len(chunks_by_lecture))
            for lecture_id, lecture_chunks in chunks_by_lecture.items():
                primitives = next(p for p in all_primitives if p.lecture_id == lecture_id)
                title = lecture_titles.get(lecture_id, lecture_id)
                
                notes = await generate_private_notes(lecture_id, title, lecture_chunks, primitives)
                
                # Save
                md_content = format_private_notes_md(notes)
                (config.output_dir / "private" / f"{lecture_id}.md").write_text(md_content)
                
                progress.advance(task)
            
            console.print(f"  ✓ Generated private notes for {len(chunks_by_lecture)} lectures")
            progress.remove_task(task)
        
        # Step 4: Topic clustering (for public)
        if mode in ['public', 'both']:
            task = progress.add_task("Clustering by topic...", total=None)
            topic_map = await cluster_primitives(all_primitives)
            
            # Save intermediate
            with open(config.output_dir / "intermediate" / "topics.json", "w") as f:
                f.write(topic_map.model_dump_json(indent=2))
            
            active_clusters = [c for c in topic_map.clusters if c.linked_primitives]
            console.print(f"  ✓ Created {len(active_clusters)} topic clusters")
            progress.remove_task(task)
            
            # Step 5: Generate public chapters
            task = progress.add_task("Generating public chapters...", total=len(active_clusters))
            chapters = []
            for cluster in active_clusters:
                chapter = await generate_public_chapter(cluster, all_primitives)
                chapters.append(chapter)
                progress.advance(task)
            
            console.print(f"  ✓ Generated {len(chapters)} public chapters")
            progress.remove_task(task)
            
            # Step 6: Validate (if safety enabled)
            validations = []
            if config.public_safety.enabled:
                task = progress.add_task("Validating public content...", total=len(chapters))
                for chapter in chapters:
                    validation = validate_public_chapter(
                        chapter, chunks, list(lecture_titles.values())
                    )
                    validations.append(validation)
                    chapter.validation_status = validation.status
                    chapter.validation_issues = validation.issues
                    progress.advance(task)
                
                passed = sum(1 for v in validations if v.status == ValidationStatus.PASS)
                console.print(f"  ✓ Validation: {passed}/{len(chapters)} chapters passed")
                progress.remove_task(task)
            
            # Step 7: Write public output
            task = progress.add_task("Writing public companion...", total=None)
            
            # Write individual chapters
            all_chapter_md = []
            for chapter in chapters:
                md_content = format_public_chapter_md(chapter)
                all_chapter_md.append(md_content)
                (config.output_dir / "public" / f"{chapter.chapter_id}.md").write_text(md_content)
            
            # Write combined book
            book_md = "# Philosophy Companion\n\n" + "\n\n---\n\n".join(all_chapter_md)
            (config.output_dir / "public" / "book.md").write_text(book_md)
            
            # Write trace report
            if validations:
                report = generate_trace_report(
                    chapters, validations, config.model_dump()
                )
                (config.output_dir / "public" / "public_trace_report.json").write_text(
                    format_trace_report_json(report)
                )
            
            console.print(f"  ✓ Public companion saved to {config.output_dir}/public/")
            progress.remove_task(task)
    
    console.print("\n[bold green]Pipeline complete![/bold green]")


if __name__ == "__main__":
    main()
