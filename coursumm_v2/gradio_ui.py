"""
Gradio Web UI for CourseSumm v2 - Phase 4

Professional web interface for course processing with:
- Folder picker for course materials
- Course metadata input
- Progress monitoring
- Batch queue
- Download results
"""

import gradio as gr
import os
import json
import time
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import threading
import queue

from .config import Config
from .pipeline import Pipeline
from .generate import ContentGenerator
from .companion_generator import CompanionGenerator, generate_all_companions
from .cover_generator import CoverGenerator
from .enhanced_formatter import format_enhanced_document
from .companion_formatter import format_all_companions_to_word


class BatchProcessor:
    """Manages batch processing queue"""
    
    def __init__(self):
        self.queue = queue.Queue()
        self.current_job = None
        self.completed_jobs = []
        self.is_processing = False
        self.progress_callback = None
    
    def add_job(self, job_config: Dict):
        """Add a job to the queue"""
        job_id = f"job_{int(time.time())}_{len(self.completed_jobs)}"
        job = {
            'id': job_id,
            'config': job_config,
            'status': 'queued',
            'added_at': datetime.now().isoformat(),
            'started_at': None,
            'completed_at': None,
            'error': None
        }
        self.queue.put(job)
        return job_id
    
    def start_processing(self, progress_callback=None):
        """Start processing jobs in queue"""
        if self.is_processing:
            return
        
        self.progress_callback = progress_callback
        self.is_processing = True
        
        thread = threading.Thread(target=self._process_queue, daemon=True)
        thread.start()
    
    def _process_queue(self):
        """Process jobs from queue"""
        while not self.queue.empty():
            job = self.queue.get()
            self.current_job = job
            
            job['status'] = 'processing'
            job['started_at'] = datetime.now().isoformat()
            
            try:
                # Process the job
                self._process_job(job)
                
                job['status'] = 'completed'
                job['completed_at'] = datetime.now().isoformat()
                
            except Exception as e:
                job['status'] = 'failed'
                job['error'] = str(e)
                job['completed_at'] = datetime.now().isoformat()
            
            self.completed_jobs.append(job)
            self.current_job = None
        
        self.is_processing = False
    
    def _process_job(self, job: Dict):
        """Process a single job"""
        config = job['config']
        
        # Update progress
        if self.progress_callback:
            self.progress_callback(f"Processing: {config['course_title']}")
        
        # Run pipeline
        # (This would integrate with the actual pipeline)
        # For now, just simulate processing
        time.sleep(2)
    
    def get_status(self) -> Dict:
        """Get current processing status"""
        return {
            'is_processing': self.is_processing,
            'current_job': self.current_job,
            'queue_size': self.queue.qsize(),
            'completed_count': len(self.completed_jobs)
        }


class CourseSummUI:
    """Gradio UI for CourseSumm v2"""
    
    def __init__(self):
        self.batch_processor = BatchProcessor()
        self.current_output_dir = None
    
    def process_course(self, input_folder: str, course_title: str, 
                      author: str, companion_types: List[str],
                      provider: str, model: str, whisper_model: str,
                      skip_audio: bool, skip_transcription: bool,
                      progress=gr.Progress()) -> Tuple[str, str]:
        """
        Process a course through the full pipeline
        
        Returns:
            Tuple of (status_message, download_path)
        """
        try:
            # Validate inputs
            if not input_folder or not os.path.exists(input_folder):
                return "❌ Error: Invalid input folder", None
            
            if not course_title:
                course_title = "Course Summary"
            
            # Create output directory
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = os.path.join("./outputs", f"{course_title}_{timestamp}")
            os.makedirs(output_dir, exist_ok=True)
            self.current_output_dir = output_dir
            
            progress(0.1, desc="Initializing...")
            
            # Initialize config
            config = Config()
            config.provider = provider.lower()
            config.model = model
            config.whisper_model = whisper_model
            
            # Initialize content generator
            content_generator = ContentGenerator(provider=provider.lower(), model=model)
            
            # Process based on companion types selected
            if "Private Notes" in companion_types:
                progress(0.2, desc="Processing Private Notes...")
                
                # Run Phase 1 pipeline
                pipeline = Pipeline(config, input_folder, output_dir, course_title)
                
                if not skip_audio:
                    progress(0.3, desc="Extracting audio...")
                    pipeline.process_audio()
                
                if not skip_transcription:
                    progress(0.4, desc="Transcribing (this may take a while)...")
                    pipeline.process_transcription()
                
                progress(0.6, desc="Generating private notes...")
                pipeline.process_generation()
                
                progress(0.7, desc="Formatting Word documents...")
                pipeline.process_word_formatting()
            
            # Generate covers
            progress(0.75, desc="Generating book covers...")
            cover_gen = CoverGenerator()
            covers_dir = os.path.join(output_dir, 'covers')
            cover_paths = cover_gen.generate_all_covers(course_title, author, covers_dir)
            
            # Process public companions
            if any(ct in companion_types for ct in ["Public V1", "Public V2", "Public V3"]):
                progress(0.8, desc="Generating public companions...")
                
                transcripts_dir = os.path.join(output_dir, 'transcripts')
                companions_dir = os.path.join(output_dir, 'companions')
                
                companions_data = generate_all_companions(
                    transcripts_dir,
                    companions_dir,
                    course_title,
                    content_generator
                )
                
                progress(0.9, desc="Formatting public companions...")
                
                # Format to Word documents
                docs_dir = os.path.join(output_dir, 'documents')
                format_all_companions_to_word(
                    companions_data,
                    course_title,
                    docs_dir,
                    author,
                    cover_paths
                )
            
            progress(1.0, desc="Complete!")
            
            # Create a summary file
            summary = {
                'course_title': course_title,
                'author': author,
                'processed_at': datetime.now().isoformat(),
                'output_directory': output_dir,
                'companion_types': companion_types
            }
            
            summary_path = os.path.join(output_dir, 'processing_summary.json')
            with open(summary_path, 'w') as f:
                json.dump(summary, f, indent=2)
            
            return f"✅ Processing complete! Output saved to: {output_dir}", output_dir
            
        except Exception as e:
            return f"❌ Error: {str(e)}", None
    
    def add_to_batch(self, input_folder: str, course_title: str,
                    author: str, companion_types: List[str]) -> str:
        """Add a course to the batch queue"""
        job_config = {
            'input_folder': input_folder,
            'course_title': course_title,
            'author': author,
            'companion_types': companion_types
        }
        
        job_id = self.batch_processor.add_job(job_config)
        
        return f"✅ Added to batch queue (Job ID: {job_id})\nQueue size: {self.batch_processor.queue.qsize()}"
    
    def start_batch_processing(self) -> str:
        """Start processing the batch queue"""
        if self.batch_processor.is_processing:
            return "⚠️ Batch processing already in progress"
        
        if self.batch_processor.queue.qsize() == 0:
            return "⚠️ No jobs in queue"
        
        self.batch_processor.start_processing()
        return f"✅ Started batch processing {self.batch_processor.queue.qsize()} jobs"
    
    def get_batch_status(self) -> str:
        """Get current batch processing status"""
        status = self.batch_processor.get_status()
        
        lines = [
            f"**Batch Processing Status**",
            f"",
            f"Currently Processing: {'Yes' if status['is_processing'] else 'No'}",
            f"Jobs in Queue: {status['queue_size']}",
            f"Completed Jobs: {status['completed_count']}",
        ]
        
        if status['current_job']:
            job = status['current_job']
            lines.extend([
                f"",
                f"**Current Job:**",
                f"Course: {job['config']['course_title']}",
                f"Started: {job.get('started_at', 'N/A')}"
            ])
        
        return "\n".join(lines)
    
    def create_ui(self):
        """Create the Gradio interface"""
        
        # Custom CSS for professional styling
        css = """
        .gradio-container {
            font-family: 'Georgia', serif;
        }
        .header {
            text-align: center;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            margin-bottom: 2rem;
        }
        .section-header {
            background: #f8f9fa;
            padding: 1rem;
            border-left: 4px solid #667eea;
            margin: 1.5rem 0 1rem 0;
            font-weight: bold;
        }
        .status-box {
            background: #e8f5e9;
            border: 1px solid #4caf50;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        .error-box {
            background: #ffebee;
            border: 1px solid #f44336;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        """
        
        with gr.Blocks(css=css, title="CourseSumm v2 - Professional Course Companion Generator") as app:
            
            # Header
            gr.HTML("""
                <div class="header">
                    <h1>📚 CourseSumm v2</h1>
                    <p style="font-size: 1.2em; margin-top: 0.5rem;">
                        Transform course lectures into professional study companions
                    </p>
                </div>
            """)
            
            with gr.Tabs():
                
                # Tab 1: Single Course Processing
                with gr.Tab("📝 Process Course"):
                    gr.HTML('<div class="section-header">Course Information</div>')
                    
                    with gr.Row():
                        with gr.Column(scale=2):
                            input_folder = gr.Textbox(
                                label="Input Folder",
                                placeholder="/path/to/course/materials",
                                info="Folder containing audio/video files or transcripts"
                            )
                        with gr.Column(scale=1):
                            browse_btn = gr.Button("📁 Browse", size="sm")
                    
                    with gr.Row():
                        course_title = gr.Textbox(
                            label="Course Title",
                            placeholder="e.g., The Big Questions of Philosophy",
                            info="Title for the course companion"
                        )
                        author = gr.Textbox(
                            label="Author/Instructor",
                            placeholder="e.g., Prof. David K. Johnson",
                            info="Optional: Instructor or author name"
                        )
                    
                    gr.HTML('<div class="section-header">Companion Types</div>')
                    
                    companion_types = gr.CheckboxGroup(
                        choices=["Private Notes", "Public V1", "Public V2", "Public V3"],
                        value=["Private Notes"],
                        label="Select companion types to generate",
                        info="Private: Detailed study notes | V1: Lecture companion | V2: Deeper synthesis | V3: Complete (V1+V2)"
                    )
                    
                    gr.HTML('<div class="section-header">Processing Options</div>')
                    
                    with gr.Row():
                        provider = gr.Dropdown(
                            choices=["OpenAI", "Anthropic"],
                            value="OpenAI",
                            label="LLM Provider"
                        )
                        model = gr.Dropdown(
                            choices=["gpt-4", "gpt-3.5-turbo", "claude-3-opus-20240229", "claude-3-sonnet-20240229"],
                            value="gpt-4",
                            label="Model"
                        )
                        whisper_model = gr.Dropdown(
                            choices=["tiny", "base", "small", "medium", "large"],
                            value="medium",
                            label="Whisper Model"
                        )
                    
                    with gr.Row():
                        skip_audio = gr.Checkbox(label="Skip audio extraction", value=False)
                        skip_transcription = gr.Checkbox(label="Skip transcription", value=False)
                    
                    process_btn = gr.Button("🚀 Process Course", variant="primary", size="lg")
                    
                    status_output = gr.Textbox(label="Status", lines=3)
                    download_output = gr.File(label="Download Results")
                    
                    process_btn.click(
                        fn=self.process_course,
                        inputs=[
                            input_folder, course_title, author, companion_types,
                            provider, model, whisper_model,
                            skip_audio, skip_transcription
                        ],
                        outputs=[status_output, download_output]
                    )
                
                # Tab 2: Batch Queue
                with gr.Tab("📦 Batch Queue"):
                    gr.HTML('<div class="section-header">Add Courses to Batch Queue</div>')
                    gr.Markdown("Process multiple courses overnight. Add courses to the queue and start batch processing.")
                    
                    with gr.Row():
                        batch_input_folder = gr.Textbox(label="Input Folder", scale=2)
                        batch_browse_btn = gr.Button("📁 Browse", size="sm", scale=1)
                    
                    with gr.Row():
                        batch_course_title = gr.Textbox(label="Course Title")
                        batch_author = gr.Textbox(label="Author/Instructor")
                    
                    batch_companion_types = gr.CheckboxGroup(
                        choices=["Private Notes", "Public V1", "Public V2", "Public V3"],
                        value=["Private Notes"],
                        label="Companion Types"
                    )
                    
                    with gr.Row():
                        add_to_batch_btn = gr.Button("➕ Add to Queue", variant="secondary")
                        start_batch_btn = gr.Button("▶️ Start Batch Processing", variant="primary")
                    
                    batch_status = gr.Textbox(label="Queue Status", lines=8)
                    refresh_status_btn = gr.Button("🔄 Refresh Status")
                    
                    add_to_batch_btn.click(
                        fn=self.add_to_batch,
                        inputs=[batch_input_folder, batch_course_title, batch_author, batch_companion_types],
                        outputs=batch_status
                    )
                    
                    start_batch_btn.click(
                        fn=self.start_batch_processing,
                        outputs=batch_status
                    )
                    
                    refresh_status_btn.click(
                        fn=self.get_batch_status,
                        outputs=batch_status
                    )
                
                # Tab 3: Help & Documentation
                with gr.Tab("❓ Help"):
                    gr.Markdown("""
                    # CourseSumm v2 - Help & Documentation
                    
                    ## Quick Start
                    
                    1. **Prepare your course materials**
                       - Put all audio/video files (MP4, MP3, etc.) in a folder
                       - Or use existing transcript files (.txt)
                    
                    2. **Select companion types**
                       - **Private Notes**: Detailed lecture-by-lecture study notes
                       - **Public V1**: Sellable lecture companion (more accessible)
                       - **Public V2**: "Going Deeper" - thematic synthesis
                       - **Public V3**: Complete companion (V1 + V2 combined)
                    
                    3. **Click Process**
                       - Processing time depends on course length and selected options
                       - Transcription is the slowest step (use GPU if available)
                    
                    ## Batch Processing
                    
                    - Add multiple courses to the queue
                    - Start batch processing and let it run overnight
                    - Check status anytime to see progress
                    
                    ## Output Files
                    
                    - **documents/**: Professional Word documents (.docx)
                    - **covers/**: Book cover images (.png)
                    - **transcripts/**: Lecture transcripts (.txt)
                    - **companions/**: Raw JSON data for companions
                    
                    ## Tips
                    
                    - Use **GPT-4** for best quality (slower, more expensive)
                    - Use **GPT-3.5** for faster/cheaper processing
                    - **Medium Whisper** model is good balance of speed/accuracy
                    - Use **GPU** for faster transcription (if available)
                    
                    ## Requirements
                    
                    - OpenAI API key (set as environment variable: `OPENAI_API_KEY`)
                    - FFmpeg installed (for audio extraction)
                    - Sufficient disk space for outputs
                    """)
            
            return app
    
    def launch(self, **kwargs):
        """Launch the Gradio interface"""
        app = self.create_ui()
        app.launch(**kwargs)


def launch_ui():
    """Launch the CourseSumm v2 web UI"""
    ui = CourseSummUI()
    ui.launch(
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        show_error=True
    )


if __name__ == "__main__":
    launch_ui()
