"""
Cover Generator for CourseSumm v2

Generates professional book covers with course title and author.
Uses PIL (Pillow) for image generation.
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
from pathlib import Path
import textwrap


class CoverGenerator:
    """Generate professional book covers"""
    
    # Color schemes for different cover styles
    COLOR_SCHEMES = {
        'blue_gradient': {
            'bg_top': (41, 128, 185),      # Professional blue
            'bg_bottom': (52, 73, 94),     # Dark blue-grey
            'title': (255, 255, 255),       # White
            'author': (236, 240, 241),      # Light grey
            'accent': (241, 196, 15)        # Golden accent
        },
        'purple_elegant': {
            'bg_top': (142, 68, 173),       # Purple
            'bg_bottom': (44, 62, 80),      # Dark grey
            'title': (255, 255, 255),
            'author': (236, 240, 241),
            'accent': (230, 126, 34)        # Orange accent
        },
        'green_modern': {
            'bg_top': (39, 174, 96),        # Green
            'bg_bottom': (22, 160, 133),    # Teal
            'title': (255, 255, 255),
            'author': (236, 240, 241),
            'accent': (241, 196, 15)
        },
        'red_bold': {
            'bg_top': (192, 57, 43),        # Red
            'bg_bottom': (44, 62, 80),      # Dark grey
            'title': (255, 255, 255),
            'author': (236, 240, 241),
            'accent': (241, 196, 15)
        },
        'teal_professional': {
            'bg_top': (26, 188, 156),       # Teal
            'bg_bottom': (22, 160, 133),    # Dark teal
            'title': (255, 255, 255),
            'author': (236, 240, 241),
            'accent': (241, 196, 15)
        }
    }
    
    def __init__(self, width=1600, height=2400):
        """
        Initialize cover generator
        
        Args:
            width: Cover width in pixels (default 1600 for 6.67" at 240 DPI)
            height: Cover height in pixels (default 2400 for 10" at 240 DPI)
        """
        self.width = width
        self.height = height
        
    def create_gradient_background(self, color_top, color_bottom):
        """Create vertical gradient background"""
        img = Image.new('RGB', (self.width, self.height), color_top)
        draw = ImageDraw.Draw(img)
        
        # Create gradient
        for i in range(self.height):
            ratio = i / self.height
            r = int(color_top[0] * (1 - ratio) + color_bottom[0] * ratio)
            g = int(color_top[1] * (1 - ratio) + color_bottom[1] * ratio)
            b = int(color_top[2] * (1 - ratio) + color_bottom[2] * ratio)
            draw.line([(0, i), (self.width, i)], fill=(r, g, b))
        
        return img
    
    def get_font(self, size, bold=False):
        """Get font with fallback to default"""
        font_names = [
            # Try these fonts in order
            '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf',
            '/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf' if bold else '/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf',
            '/System/Library/Fonts/Supplemental/Georgia Bold.ttf' if bold else '/System/Library/Fonts/Supplemental/Georgia.ttf',
            'C:\\Windows\\Fonts\\georgiab.ttf' if bold else 'C:\\Windows\\Fonts\\georgia.ttf',
        ]
        
        for font_path in font_names:
            if os.path.exists(font_path):
                try:
                    return ImageFont.truetype(font_path, size)
                except:
                    pass
        
        # Fallback to default
        return ImageFont.load_default()
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within max_width"""
        draw = ImageDraw.Draw(Image.new('RGB', (1, 1)))
        lines = []
        
        # Split into words
        words = text.split()
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
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
    
    def generate_cover(self, title, subtitle=None, author=None, 
                      companion_type=None, style='blue_gradient',
                      output_path=None):
        """
        Generate a professional book cover
        
        Args:
            title: Main title text
            subtitle: Optional subtitle
            author: Author name
            companion_type: Type of companion (e.g., "Complete Course Notes", "Going Deeper", etc.)
            style: Color scheme name
            output_path: Where to save the cover image
            
        Returns:
            PIL Image object
        """
        # Get color scheme
        colors = self.COLOR_SCHEMES.get(style, self.COLOR_SCHEMES['blue_gradient'])
        
        # Create gradient background
        img = self.create_gradient_background(colors['bg_top'], colors['bg_bottom'])
        draw = ImageDraw.Draw(img)
        
        # Add subtle texture/noise
        # (Optional - could add texture overlay here)
        
        # Define text areas
        margin = int(self.width * 0.1)  # 10% margin
        usable_width = self.width - (2 * margin)
        
        # Title font (large and bold)
        title_font = self.get_font(int(self.width * 0.1), bold=True)
        
        # Wrap title text
        title_lines = self.wrap_text(title, title_font, usable_width)
        
        # Calculate title position (upper third)
        title_y = int(self.height * 0.25)
        line_height = int(self.width * 0.12)
        
        # Draw title
        for i, line in enumerate(title_lines):
            bbox = draw.textbbox((0, 0), line, font=title_font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            y = title_y + (i * line_height)
            
            # Add shadow for depth
            shadow_offset = 4
            draw.text((x + shadow_offset, y + shadow_offset), line, 
                     font=title_font, fill=(0, 0, 0, 128))
            draw.text((x, y), line, font=title_font, fill=colors['title'])
        
        # Companion type (if provided)
        if companion_type:
            comp_font = self.get_font(int(self.width * 0.04))
            bbox = draw.textbbox((0, 0), companion_type, font=comp_font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            y = title_y - int(self.height * 0.08)
            draw.text((x, y), companion_type.upper(), 
                     font=comp_font, fill=colors['accent'])
        
        # Subtitle (if provided)
        if subtitle:
            subtitle_font = self.get_font(int(self.width * 0.05))
            subtitle_lines = self.wrap_text(subtitle, subtitle_font, usable_width)
            sub_y = title_y + (len(title_lines) * line_height) + int(self.height * 0.05)
            sub_line_height = int(self.width * 0.06)
            
            for i, line in enumerate(subtitle_lines):
                bbox = draw.textbbox((0, 0), line, font=subtitle_font)
                text_width = bbox[2] - bbox[0]
                x = (self.width - text_width) // 2
                y = sub_y + (i * sub_line_height)
                draw.text((x, y), line, font=subtitle_font, fill=colors['author'])
        
        # Author name (bottom)
        if author:
            author_font = self.get_font(int(self.width * 0.05))
            bbox = draw.textbbox((0, 0), author, font=author_font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            y = int(self.height * 0.85)
            draw.text((x, y), author, font=author_font, fill=colors['author'])
        
        # Add decorative line
        line_y = int(self.height * 0.80)
        line_width = int(self.width * 0.3)
        line_x1 = (self.width - line_width) // 2
        line_x2 = line_x1 + line_width
        draw.line([(line_x1, line_y), (line_x2, line_y)], 
                 fill=colors['accent'], width=3)
        
        # Save if output path provided
        if output_path:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path, 'PNG', quality=95)
        
        return img
    
    def generate_all_covers(self, course_title, author=None, output_dir=None):
        """
        Generate all companion type covers
        
        Args:
            course_title: Course title
            author: Author name
            output_dir: Directory to save covers
            
        Returns:
            Dictionary of cover paths by type
        """
        covers = {}
        
        companion_types = {
            'private': ('Private Notes', 'blue_gradient'),
            'public_v1': ('Lecture Companion', 'purple_elegant'),
            'public_v2': ('Going Deeper', 'green_modern'),
            'public_v3': ('Complete Companion', 'red_bold')
        }
        
        for key, (comp_type, style) in companion_types.items():
            if output_dir:
                output_path = os.path.join(output_dir, f'cover_{key}.png')
            else:
                output_path = None
            
            img = self.generate_cover(
                title=course_title,
                author=author,
                companion_type=comp_type,
                style=style,
                output_path=output_path
            )
            
            if output_path:
                covers[key] = output_path
        
        return covers


def generate_cover(title, author=None, companion_type=None, 
                   output_path=None, style='blue_gradient'):
    """
    Convenience function to generate a single cover
    
    Args:
        title: Course title
        author: Author name
        companion_type: Type of companion
        output_path: Where to save
        style: Color scheme
        
    Returns:
        PIL Image
    """
    generator = CoverGenerator()
    return generator.generate_cover(title, author=author, 
                                   companion_type=companion_type,
                                   output_path=output_path, style=style)
