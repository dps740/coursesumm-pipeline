"""
EPUB Generator for CourseSumm v2

Creates sale-ready EPUB files with:
- Cover image
- Table of contents
- Proper chapter structure
- Metadata for stores
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from ebooklib import epub
import html


class EPUBGenerator:
    """Generate professional EPUB files"""
    
    SERIES_NAME = "Great Course Companions"
    PUBLISHER = "Independent Publishing"
    
    CSS_STYLES = '''
@namespace epub "http://www.idpf.org/2007/ops";

body {
    font-family: Georgia, serif;
    font-size: 1em;
    line-height: 1.6;
    margin: 1em;
}

h1 {
    font-family: Arial, sans-serif;
    font-size: 1.8em;
    color: #2C3E50;
    margin-top: 2em;
    margin-bottom: 0.5em;
    page-break-before: always;
}

h1.title-page {
    font-size: 2.2em;
    text-align: center;
    margin-top: 3em;
    page-break-before: avoid;
}

h2 {
    font-family: Arial, sans-serif;
    font-size: 1.3em;
    color: #34495E;
    margin-top: 1.5em;
    margin-bottom: 0.5em;
}

h3 {
    font-family: Arial, sans-serif;
    font-size: 1.1em;
    margin-top: 1em;
    margin-bottom: 0.3em;
}

.subtitle {
    font-size: 1.2em;
    font-style: italic;
    text-align: center;
    color: #666;
    margin-bottom: 2em;
}

.author {
    font-size: 1.1em;
    text-align: center;
    margin-top: 3em;
}

.series {
    font-size: 0.9em;
    font-style: italic;
    text-align: center;
    color: #999;
    margin-top: 1em;
}

.copyright {
    font-size: 0.85em;
    margin-top: 3em;
    text-align: center;
}

.disclaimer {
    font-size: 0.8em;
    font-style: italic;
    margin: 2em 1em;
    padding: 1em;
    background: #f5f5f5;
    border-left: 3px solid #ccc;
}

blockquote {
    font-style: italic;
    margin: 1em 2em;
    padding-left: 1em;
    border-left: 3px solid #ddd;
}

.key-point {
    margin: 1em 0;
}

.key-point strong {
    color: #2C3E50;
}

.concept {
    margin: 0.8em 0;
    padding-left: 1em;
}

.discussion-question {
    margin: 0.5em 0;
    padding-left: 1.5em;
}

.lecture-number {
    font-size: 1em;
    color: #666;
    display: block;
    margin-bottom: 0.3em;
}

.about-author {
    margin-top: 2em;
    padding: 1em;
    background: #f9f9f9;
}
'''

    DISCLAIMER = """This companion guide is an independent educational resource created to enhance your learning experience. It is not affiliated with, endorsed by, or connected to The Great Courses, The Teaching Company, or any course instructor. All original content, analysis, discussion questions, and synthesis in this guide are the intellectual property of the author."""

    def __init__(self,
                 course_title: str,
                 author: str = "Seo-Yun Kim",
                 companion_type: str = "Lecture Companion"):
        self.course_title = course_title
        self.author = author
        self.companion_type = companion_type
        self.book = epub.EpubBook()
        self.chapters = []
        self._setup_metadata()
    
    def _setup_metadata(self):
        """Set up EPUB metadata"""
        # Generate unique identifier
        identifier = f"coursesumm-{self.course_title.lower().replace(' ', '-')}-{self.companion_type.lower().replace(' ', '-')}"
        
        self.book.set_identifier(identifier)
        self.book.set_title(f"{self.course_title}: {self.companion_type}")
        self.book.set_language('en')
        self.book.add_author(self.author)
        
        # Add metadata
        self.book.add_metadata('DC', 'publisher', self.PUBLISHER)
        self.book.add_metadata('DC', 'date', datetime.now().strftime('%Y-%m-%d'))
        self.book.add_metadata('DC', 'description', 
            f"A {self.companion_type} guide for {self.course_title}. Part of the {self.SERIES_NAME} series.")
        self.book.add_metadata('DC', 'subject', 'Education')
        self.book.add_metadata('DC', 'subject', 'Philosophy')
        self.book.add_metadata('DC', 'subject', 'Study Guides')
    
    def set_cover(self, cover_path: str):
        """Set the cover image"""
        if cover_path and os.path.exists(cover_path):
            with open(cover_path, 'rb') as f:
                cover_content = f.read()
            
            # Determine image type
            ext = os.path.splitext(cover_path)[1].lower()
            media_type = 'image/png' if ext == '.png' else 'image/jpeg'
            
            self.book.set_cover('cover.png', cover_content)
    
    def _create_title_page(self) -> epub.EpubHtml:
        """Create title page chapter"""
        content = f'''
<html>
<head><title>Title Page</title></head>
<body>
    <p class="series">{self.SERIES_NAME}</p>
    <h1 class="title-page">{html.escape(self.course_title)}</h1>
    <p class="subtitle">{self.companion_type}</p>
    <p class="author">By {html.escape(self.author)}</p>
</body>
</html>
'''
        chapter = epub.EpubHtml(title='Title Page', file_name='title.xhtml')
        chapter.content = content
        return chapter
    
    def _create_copyright_page(self) -> epub.EpubHtml:
        """Create copyright page"""
        year = datetime.now().year
        content = f'''
<html>
<head><title>Copyright</title></head>
<body>
    <div class="copyright">
        <p>Copyright © {year} {html.escape(self.author)}</p>
        <p>All rights reserved.</p>
        <p>Published by {self.PUBLISHER}</p>
        <p>First Edition: {datetime.now().strftime('%B %Y')}</p>
    </div>
    <div class="disclaimer">
        <p><strong>Important Notice</strong></p>
        <p>{self.DISCLAIMER}</p>
    </div>
</body>
</html>
'''
        chapter = epub.EpubHtml(title='Copyright', file_name='copyright.xhtml')
        chapter.content = content
        return chapter
    
    def add_lecture_chapter(self, lecture_num: int, lecture_data: Dict[str, Any]):
        """Add a lecture as a chapter"""
        title = lecture_data.get('title', f'Lecture {lecture_num}')
        
        content_parts = [f'''
<html>
<head><title>Lecture {lecture_num}</title></head>
<body>
    <h1><span class="lecture-number">Lecture {lecture_num}</span>{html.escape(title)}</h1>
''']
        
        # Introduction
        if 'introduction' in lecture_data:
            content_parts.append(f'<blockquote>{html.escape(lecture_data["introduction"])}</blockquote>')
        
        # Main Points
        if 'main_points' in lecture_data:
            content_parts.append('<h2>Key Points</h2>')
            for i, point in enumerate(lecture_data['main_points'], 1):
                if isinstance(point, dict):
                    content_parts.append(f'''
<div class="key-point">
    <strong>{i}. {html.escape(point.get("point", ""))}</strong>
    <p>{html.escape(point.get("explanation", ""))}</p>
</div>''')
                else:
                    content_parts.append(f'<p class="key-point">{i}. {html.escape(str(point))}</p>')
        
        # Key Concepts
        if 'key_concepts' in lecture_data:
            content_parts.append('<h2>Core Concepts</h2>')
            for concept in lecture_data['key_concepts']:
                if isinstance(concept, dict):
                    content_parts.append(f'''
<div class="concept">
    <strong>{html.escape(concept.get("concept", ""))}:</strong> {html.escape(concept.get("definition", ""))}
</div>''')
                else:
                    content_parts.append(f'<p class="concept">• {html.escape(str(concept))}</p>')
        
        # Practical Applications
        if 'practical_applications' in lecture_data:
            content_parts.append('<h2>Practical Applications</h2>')
            for app in lecture_data['practical_applications']:
                if isinstance(app, dict):
                    content_parts.append(f'''
<div class="concept">
    <strong>{html.escape(app.get("application", ""))}:</strong> {html.escape(app.get("explanation", ""))}
</div>''')
                else:
                    content_parts.append(f'<p>• {html.escape(str(app))}</p>')
        
        # Discussion Questions
        if 'discussion_questions' in lecture_data:
            content_parts.append('<h2>Discussion Questions</h2>')
            for i, q in enumerate(lecture_data['discussion_questions'], 1):
                content_parts.append(f'<p class="discussion-question">{i}. {html.escape(str(q))}</p>')
        
        # Further Exploration
        if 'further_exploration' in lecture_data:
            content_parts.append('<h2>Further Exploration</h2>')
            for item in lecture_data['further_exploration']:
                content_parts.append(f'<p>• {html.escape(str(item))}</p>')
        
        content_parts.append('</body></html>')
        
        chapter = epub.EpubHtml(
            title=f'Lecture {lecture_num}: {title}',
            file_name=f'lecture_{lecture_num:02d}.xhtml'
        )
        chapter.content = '\n'.join(content_parts)
        self.chapters.append(chapter)
        return chapter
    
    def add_synthesis_chapter(self, synthesis_data: Dict[str, Any]):
        """Add synthesis/going deeper content"""
        content_parts = ['<html><head><title>Course Synthesis</title></head><body>']
        
        # Introduction
        if 'introduction' in synthesis_data:
            content_parts.append('<h1>Course Overview</h1>')
            content_parts.append(f'<p>{html.escape(synthesis_data["introduction"])}</p>')
        
        # Major Themes
        if 'major_themes' in synthesis_data:
            content_parts.append('<h1>Major Themes</h1>')
            for theme in synthesis_data['major_themes']:
                if isinstance(theme, dict):
                    content_parts.append(f'<h2>{html.escape(theme.get("theme", ""))}</h2>')
                    if theme.get('description'):
                        content_parts.append(f'<p>{html.escape(theme["description"])}</p>')
                    if theme.get('key_lectures'):
                        content_parts.append(f'<p><strong>Key Lectures:</strong> {html.escape(theme["key_lectures"])}</p>')
                    if theme.get('connections'):
                        content_parts.append(f'<p><strong>Connections:</strong> {html.escape(theme["connections"])}</p>')
        
        # Deeper Questions
        if 'deeper_questions' in synthesis_data:
            content_parts.append('<h1>Deeper Questions</h1>')
            for q in synthesis_data['deeper_questions']:
                if isinstance(q, dict):
                    content_parts.append(f'<h2>{html.escape(q.get("question", ""))}</h2>')
                    if q.get('exploration'):
                        content_parts.append(f'<p>{html.escape(q["exploration"])}</p>')
                    if q.get('further_reading'):
                        content_parts.append(f'<p><em>Further Reading: {html.escape(q["further_reading"])}</em></p>')
        
        # Synthesis
        if 'synthesis' in synthesis_data:
            content_parts.append('<h1>Synthesis</h1>')
            content_parts.append(f'<p>{html.escape(synthesis_data["synthesis"])}</p>')
        
        content_parts.append('</body></html>')
        
        chapter = epub.EpubHtml(title='Course Synthesis', file_name='synthesis.xhtml')
        chapter.content = '\n'.join(content_parts)
        self.chapters.append(chapter)
        return chapter
    
    def _create_about_author(self) -> epub.EpubHtml:
        """Create About the Author page"""
        content = f'''
<html>
<head><title>About the Author</title></head>
<body>
    <h1>About the Author</h1>
    <div class="about-author">
        <p>{html.escape(self.author)} is an independent educational writer and course companion author 
        specializing in making complex academic content accessible to lifelong learners.</p>
        
        <p>With a passion for philosophy, science, and the humanities, {html.escape(self.author.split()[0])} 
        creates study guides that help students and curious minds engage more deeply with great courses 
        and lectures from top professors.</p>
        
        <p>The {self.SERIES_NAME} series provides thoughtful analysis, discussion questions, and synthesis 
        to transform passive viewing into active learning.</p>
    </div>
</body>
</html>
'''
        chapter = epub.EpubHtml(title='About the Author', file_name='about.xhtml')
        chapter.content = content
        return chapter
    
    def build(self, cover_path: str = None) -> epub.EpubBook:
        """Build the complete EPUB"""
        # Set cover
        if cover_path:
            self.set_cover(cover_path)
        
        # Add CSS
        style = epub.EpubItem(
            uid="style",
            file_name="style/main.css",
            media_type="text/css",
            content=self.CSS_STYLES
        )
        self.book.add_item(style)
        
        # Create front matter
        title_page = self._create_title_page()
        copyright_page = self._create_copyright_page()
        about_page = self._create_about_author()
        
        # Add all chapters to book
        all_chapters = [title_page, copyright_page] + self.chapters + [about_page]
        
        for chapter in all_chapters:
            chapter.add_item(style)
            self.book.add_item(chapter)
        
        # Create TOC
        self.book.toc = [
            epub.Link('title.xhtml', 'Title Page', 'title'),
            epub.Link('copyright.xhtml', 'Copyright', 'copyright'),
        ]
        
        # Add content chapters to TOC
        for chapter in self.chapters:
            self.book.toc.append(epub.Link(chapter.file_name, chapter.title, chapter.file_name.replace('.xhtml', '')))
        
        self.book.toc.append(epub.Link('about.xhtml', 'About the Author', 'about'))
        
        # Add navigation
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())
        
        # Set spine
        self.book.spine = ['nav'] + all_chapters
        
        return self.book
    
    def save(self, output_path: str):
        """Save the EPUB file"""
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else '.', exist_ok=True)
        epub.write_epub(output_path, self.book)
        return output_path


def create_epub_v1(course_title: str, 
                   lectures: List[Dict],
                   output_path: str,
                   author: str = "Seo-Yun Kim",
                   cover_path: str = None) -> str:
    """Create V1 (Lecture Companion) EPUB"""
    gen = EPUBGenerator(course_title, author, "Lecture Companion")
    
    for i, lecture in enumerate(lectures, 1):
        gen.add_lecture_chapter(i, lecture)
    
    gen.build(cover_path)
    gen.save(output_path)
    return output_path


def create_epub_v2(course_title: str,
                   synthesis_data: Dict,
                   output_path: str,
                   author: str = "Seo-Yun Kim",
                   cover_path: str = None) -> str:
    """Create V2 (Going Deeper) EPUB"""
    gen = EPUBGenerator(course_title, author, "Going Deeper")
    gen.add_synthesis_chapter(synthesis_data)
    gen.build(cover_path)
    gen.save(output_path)
    return output_path


def create_epub_v3(course_title: str,
                   lectures: List[Dict],
                   synthesis_data: Dict,
                   output_path: str,
                   author: str = "Seo-Yun Kim",
                   cover_path: str = None) -> str:
    """Create V3 (Complete Companion) EPUB"""
    gen = EPUBGenerator(course_title, author, "Complete Companion")
    
    for i, lecture in enumerate(lectures, 1):
        gen.add_lecture_chapter(i, lecture)
    
    gen.add_synthesis_chapter(synthesis_data)
    gen.build(cover_path)
    gen.save(output_path)
    return output_path
