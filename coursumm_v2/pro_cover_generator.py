"""
Professional Cover Generator for CourseSumm v2

Creates book-ready covers with:
- Gradient backgrounds with subject-appropriate colors
- Professional typography hierarchy
- Series branding
- Author name
- Companion type badges
"""

import os
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple
import colorsys


class ProCoverGenerator:
    """Generate professional book covers"""
    
    # Subject color schemes (background gradient top, bottom, accent)
    SUBJECT_COLORS = {
        'philosophy': ('#1a1a2e', '#16213e', '#e94560'),
        'science': ('#0d1b2a', '#1b263b', '#00d9ff'),
        'history': ('#2d132c', '#801336', '#c72c41'),
        'literature': ('#1d3557', '#457b9d', '#a8dadc'),
        'psychology': ('#2b2d42', '#8d99ae', '#ef233c'),
        'economics': ('#212529', '#343a40', '#ffc107'),
        'default': ('#1a1a2e', '#16213e', '#e94560'),
    }
    
    # Companion type colors
    TYPE_COLORS = {
        'private': '#9b59b6',      # Purple
        'v1': '#3498db',           # Blue
        'v2': '#27ae60',           # Green
        'v3': '#e74c3c',           # Red
    }
    
    def __init__(self, width: int = 1600, height: int = 2400):
        """
        Initialize cover generator
        
        Args:
            width: Cover width in pixels (standard: 1600 for 6x9 at 300dpi)
            height: Cover height in pixels (standard: 2400 for 6x9 at 300dpi)
        """
        self.width = width
        self.height = height
    
    def _get_font(self, size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
        """Get a font, falling back to default if needed"""
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        ]
        
        for path in font_paths:
            if os.path.exists(path):
                return ImageFont.truetype(path, size)
        
        return ImageFont.load_default()
    
    def _create_gradient(self, color_top: str, color_bottom: str) -> Image.Image:
        """Create a vertical gradient background"""
        img = Image.new('RGB', (self.width, self.height))
        draw = ImageDraw.Draw(img)
        
        # Parse colors
        r1, g1, b1 = int(color_top[1:3], 16), int(color_top[3:5], 16), int(color_top[5:7], 16)
        r2, g2, b2 = int(color_bottom[1:3], 16), int(color_bottom[3:5], 16), int(color_bottom[5:7], 16)
        
        # Draw gradient
        for y in range(self.height):
            ratio = y / self.height
            r = int(r1 + (r2 - r1) * ratio)
            g = int(g1 + (g2 - g1) * ratio)
            b = int(b1 + (b2 - b1) * ratio)
            draw.line([(0, y), (self.width, y)], fill=(r, g, b))
        
        return img
    
    def _wrap_text(self, text: str, font: ImageFont.FreeTypeFont, max_width: int) -> list:
        """Wrap text to fit within max_width"""
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = font.getbbox(test_line)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def _add_decorative_elements(self, draw: ImageDraw.Draw, accent_color: str):
        """Add decorative lines and elements"""
        # Top decorative line
        draw.rectangle(
            [(self.width * 0.1, 150), (self.width * 0.9, 155)],
            fill=accent_color
        )
        
        # Bottom decorative line
        draw.rectangle(
            [(self.width * 0.1, self.height - 200), (self.width * 0.9, self.height - 195)],
            fill=accent_color
        )
        
        # Corner accents
        corner_size = 50
        
        # Top-left
        draw.polygon([
            (0, 0), (corner_size, 0), (0, corner_size)
        ], fill=accent_color)
        
        # Top-right
        draw.polygon([
            (self.width, 0), (self.width - corner_size, 0), (self.width, corner_size)
        ], fill=accent_color)
        
        # Bottom-left
        draw.polygon([
            (0, self.height), (corner_size, self.height), (0, self.height - corner_size)
        ], fill=accent_color)
        
        # Bottom-right
        draw.polygon([
            (self.width, self.height), (self.width - corner_size, self.height), (self.width, self.height - corner_size)
        ], fill=accent_color)
    
    def generate_cover(self,
                       title: str,
                       author: str = "Seo-Yun Kim",
                       companion_type: str = "v1",
                       series_name: str = "Great Course Companions",
                       subject: str = "philosophy") -> Image.Image:
        """
        Generate a professional book cover
        
        Args:
            title: Book/course title
            author: Author name
            companion_type: "private", "v1", "v2", or "v3"
            series_name: Series branding text
            subject: Subject for color scheme
        
        Returns:
            PIL Image object
        """
        # Get colors
        colors = self.SUBJECT_COLORS.get(subject.lower(), self.SUBJECT_COLORS['default'])
        type_color = self.TYPE_COLORS.get(companion_type.lower(), self.TYPE_COLORS['v1'])
        
        # Create gradient background
        img = self._create_gradient(colors[0], colors[1])
        draw = ImageDraw.Draw(img)
        
        # Add decorative elements
        self._add_decorative_elements(draw, colors[2])
        
        # Fonts
        series_font = self._get_font(36)
        title_font = self._get_font(72, bold=True)
        subtitle_font = self._get_font(42)
        type_font = self._get_font(36, bold=True)
        author_font = self._get_font(48)
        
        # Series name at top
        series_bbox = draw.textbbox((0, 0), series_name, font=series_font)
        series_x = (self.width - (series_bbox[2] - series_bbox[0])) // 2
        draw.text((series_x, 200), series_name, font=series_font, fill='#aaaaaa')
        
        # Main title (wrapped)
        title_lines = self._wrap_text(title, title_font, self.width - 200)
        title_y = 500
        line_height = 90
        
        for line in title_lines:
            bbox = draw.textbbox((0, 0), line, font=title_font)
            x = (self.width - (bbox[2] - bbox[0])) // 2
            draw.text((x, title_y), line, font=title_font, fill='white')
            title_y += line_height
        
        # Companion type badge
        type_labels = {
            'private': 'Private Lecture Notes',
            'v1': 'Lecture Companion',
            'v2': 'Going Deeper',
            'v3': 'Complete Companion',
        }
        type_label = type_labels.get(companion_type.lower(), 'Companion Guide')
        
        # Badge background
        badge_y = title_y + 100
        badge_padding = 30
        type_bbox = draw.textbbox((0, 0), type_label, font=type_font)
        badge_width = type_bbox[2] - type_bbox[0] + badge_padding * 2
        badge_height = type_bbox[3] - type_bbox[1] + badge_padding
        badge_x = (self.width - badge_width) // 2
        
        draw.rounded_rectangle(
            [(badge_x, badge_y), (badge_x + badge_width, badge_y + badge_height)],
            radius=10,
            fill=type_color
        )
        
        # Badge text
        type_x = (self.width - (type_bbox[2] - type_bbox[0])) // 2
        draw.text((type_x, badge_y + badge_padding // 2), type_label, font=type_font, fill='white')
        
        # Subtitle based on type
        subtitles = {
            'private': 'Your Personal Study Notes',
            'v1': 'Your Guide to Each Lecture',
            'v2': 'Themes, Connections & Questions',
            'v3': 'The Comprehensive Guide',
        }
        subtitle = subtitles.get(companion_type.lower(), '')
        
        if subtitle:
            sub_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
            sub_x = (self.width - (sub_bbox[2] - sub_bbox[0])) // 2
            draw.text((sub_x, badge_y + badge_height + 60), subtitle, font=subtitle_font, fill='#cccccc')
        
        # Author at bottom
        author_text = f"By {author}"
        author_bbox = draw.textbbox((0, 0), author_text, font=author_font)
        author_x = (self.width - (author_bbox[2] - author_bbox[0])) // 2
        draw.text((author_x, self.height - 350), author_text, font=author_font, fill='white')
        
        return img
    
    def generate_all_covers(self,
                           course_title: str,
                           author: str = "Seo-Yun Kim",
                           output_dir: str = None,
                           subject: str = "philosophy") -> dict:
        """
        Generate all cover types for a course
        
        Returns dict mapping type to file path
        """
        if output_dir is None:
            output_dir = "covers"
        
        os.makedirs(output_dir, exist_ok=True)
        
        covers = {}
        for cover_type in ['private', 'v1', 'v2', 'v3']:
            img = self.generate_cover(
                title=course_title,
                author=author,
                companion_type=cover_type,
                subject=subject
            )
            
            path = os.path.join(output_dir, f"cover_{cover_type}.png")
            img.save(path, 'PNG', quality=95)
            covers[cover_type] = path
            print(f"  Created: {path}")
        
        return covers


# Convenience function
def generate_pro_covers(course_title: str, 
                        author: str = "Seo-Yun Kim",
                        output_dir: str = "covers",
                        subject: str = "philosophy") -> dict:
    """Generate professional covers for all companion types"""
    generator = ProCoverGenerator()
    return generator.generate_all_covers(course_title, author, output_dir, subject)
