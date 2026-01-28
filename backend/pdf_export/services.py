from io import BytesIO
from decimal import Decimal
from typing import List, Dict, Any, Optional
import json


class PDFGenerator:
    """Service for generating PDFs with professional print features"""
    
    # Paper sizes in mm
    PAPER_SIZES = {
        'letter': (215.9, 279.4),
        'legal': (215.9, 355.6),
        'tabloid': (279.4, 431.8),
        'a3': (297, 420),
        'a4': (210, 297),
        'a5': (148, 210),
    }
    
    # Color conversion matrices
    RGB_TO_CMYK_MATRIX = [
        [0.4124, 0.3576, 0.1805],
        [0.2126, 0.7152, 0.0722],
        [0.0193, 0.1192, 0.9505],
    ]
    
    def __init__(self, export_job):
        self.export_job = export_job
        self.project = export_job.project
        self.preset = export_job.preset
        self.settings = self._merge_settings()
    
    def _merge_settings(self) -> Dict[str, Any]:
        """Merge preset settings with override settings"""
        settings = {}
        
        if self.preset:
            settings = {
                'paper_size': self.preset.paper_size,
                'custom_width': self.preset.custom_width,
                'custom_height': self.preset.custom_height,
                'orientation': self.preset.orientation,
                'color_mode': self.preset.color_mode,
                'bleed_enabled': self.preset.bleed_enabled,
                'bleed_top': float(self.preset.bleed_top),
                'bleed_bottom': float(self.preset.bleed_bottom),
                'bleed_left': float(self.preset.bleed_left),
                'bleed_right': float(self.preset.bleed_right),
                'crop_marks': self.preset.crop_marks,
                'bleed_marks': self.preset.bleed_marks,
                'registration_marks': self.preset.registration_marks,
                'quality': self.preset.quality,
                'pdf_standard': self.preset.pdf_standard,
            }
        
        # Override with job-specific settings
        if self.export_job.export_settings:
            settings.update(self.export_job.export_settings)
        
        return settings
    
    def get_page_dimensions(self) -> tuple:
        """Get page dimensions in mm"""
        paper_size = self.settings.get('paper_size', 'letter')
        
        if paper_size == 'custom':
            width = float(self.settings.get('custom_width', 210))
            height = float(self.settings.get('custom_height', 297))
        else:
            width, height = self.PAPER_SIZES.get(paper_size, self.PAPER_SIZES['letter'])
        
        if self.settings.get('orientation') == 'landscape':
            width, height = height, width
        
        return (width, height)
    
    def get_bleed_dimensions(self) -> Dict[str, float]:
        """Get bleed dimensions"""
        if not self.settings.get('bleed_enabled'):
            return {'top': 0, 'bottom': 0, 'left': 0, 'right': 0}
        
        return {
            'top': self.settings.get('bleed_top', 3.0),
            'bottom': self.settings.get('bleed_bottom', 3.0),
            'left': self.settings.get('bleed_left', 3.0),
            'right': self.settings.get('bleed_right', 3.0),
        }
    
    def get_total_dimensions(self) -> tuple:
        """Get total page dimensions including bleed"""
        page_width, page_height = self.get_page_dimensions()
        bleed = self.get_bleed_dimensions()
        
        total_width = page_width + bleed['left'] + bleed['right']
        total_height = page_height + bleed['top'] + bleed['bottom']
        
        return (total_width, total_height)
    
    def generate(self) -> bytes:
        """Generate PDF (placeholder - would integrate with actual PDF library)"""
        from django.utils import timezone
        
        # Update status
        self.export_job.status = 'processing'
        self.export_job.started_at = timezone.now()
        self.export_job.save()
        
        try:
            # Get pages to export
            pages = self._get_pages_to_export()
            
            # Generate PDF content
            pdf_data = self._generate_pdf_content(pages)
            
            # Update job
            self.export_job.status = 'completed'
            self.export_job.completed_at = timezone.now()
            self.export_job.page_count = len(pages)
            self.export_job.progress = 100
            self.export_job.save()
            
            return pdf_data
            
        except Exception as e:
            self.export_job.status = 'failed'
            self.export_job.error_message = str(e)
            self.export_job.save()
            raise
    
    def _get_pages_to_export(self) -> List[Dict]:
        """Get list of pages to export"""
        # In production, would fetch actual page data from project
        if self.export_job.pages:
            return self.export_job.pages
        
        if self.export_job.page_range:
            return self._parse_page_range(self.export_job.page_range)
        
        # Default to all pages
        return [{'id': i, 'number': i} for i in range(1, 11)]
    
    def _parse_page_range(self, range_str: str) -> List[Dict]:
        """Parse page range string"""
        pages = []
        parts = range_str.replace(' ', '').split(',')
        
        for part in parts:
            if '-' in part:
                start, end = part.split('-', 1)
                pages.extend(range(int(start), int(end) + 1))
            else:
                pages.append(int(part))
        
        return [{'id': p, 'number': p} for p in sorted(set(pages))]
    
    def _generate_pdf_content(self, pages: List[Dict]) -> bytes:
        """Generate actual PDF content"""
        # This is a placeholder - would use a library like reportlab, weasyprint, or PyPDF2
        
        pdf_content = BytesIO()
        
        # PDF header
        pdf_content.write(b'%PDF-1.7\n')
        
        # In production, would generate actual PDF content with:
        # - Page content rendering
        # - Bleed area handling
        # - Crop marks
        # - Color space conversion
        # - Font embedding
        # - Image optimization
        
        return pdf_content.getvalue()
    
    def convert_rgb_to_cmyk(self, r: int, g: int, b: int) -> tuple:
        """Convert RGB color to CMYK"""
        r_norm = r / 255.0
        g_norm = g / 255.0
        b_norm = b / 255.0
        
        k = 1 - max(r_norm, g_norm, b_norm)
        
        if k == 1:
            return (0, 0, 0, 100)
        
        c = (1 - r_norm - k) / (1 - k) * 100
        m = (1 - g_norm - k) / (1 - k) * 100
        y = (1 - b_norm - k) / (1 - k) * 100
        k = k * 100
        
        return (round(c), round(m), round(y), round(k))


class PreflightChecker:
    """Check designs for print-readiness"""
    
    def __init__(self, project, settings: Dict[str, Any]):
        self.project = project
        self.settings = settings
        self.warnings = []
        self.errors = []
        self.info = {}
    
    def run_checks(self) -> Dict[str, Any]:
        """Run all preflight checks"""
        self._check_resolution()
        self._check_color_space()
        self._check_bleed()
        self._check_fonts()
        self._check_transparency()
        self._check_overprint()
        
        return {
            'passed': len(self.errors) == 0,
            'warnings': self.warnings,
            'errors': self.errors,
            'info': self.info,
        }
    
    def _check_resolution(self):
        """Check image resolution"""
        min_dpi = self.settings.get('quality', 300)
        
        # In production, would check actual image resolutions
        # Placeholder check
        self.info['target_resolution'] = min_dpi
        
        # Example warning
        # if image_dpi < min_dpi:
        #     self.warnings.append({
        #         'type': 'low_resolution',
        #         'message': f'Image has resolution {image_dpi}dpi, minimum is {min_dpi}dpi',
        #         'element_id': image_id,
        #     })
    
    def _check_color_space(self):
        """Check color space compatibility"""
        color_mode = self.settings.get('color_mode', 'rgb')
        self.info['color_mode'] = color_mode
        
        if color_mode == 'cmyk':
            # Would check for RGB-only images that need conversion
            pass
    
    def _check_bleed(self):
        """Check if elements extend to bleed"""
        if not self.settings.get('bleed_enabled'):
            return
        
        bleed_amount = self.settings.get('bleed_top', 3.0)
        self.info['bleed_amount'] = bleed_amount
        
        # Would check if edge elements extend into bleed area
    
    def _check_fonts(self):
        """Check font availability and embedding"""
        # Would verify all fonts are available for embedding
        self.info['fonts_embedded'] = True
    
    def _check_transparency(self):
        """Check for transparency issues"""
        pdf_standard = self.settings.get('pdf_standard', 'pdf_1_7')
        
        if pdf_standard in ['pdf_x_1a']:
            # PDF/X-1a doesn't support transparency
            # Would check for transparent elements
            pass
    
    def _check_overprint(self):
        """Check overprint settings"""
        # Would verify overprint settings are correct
        pass


class ImpositionService:
    """Service for creating imposition layouts"""
    
    def __init__(self, layout):
        self.layout = layout
    
    def calculate_positions(self, pages: List[int]) -> List[Dict]:
        """Calculate page positions on sheet"""
        positions = []
        
        cols = self.layout.columns
        rows = self.layout.rows
        pages_per_sheet = cols * rows
        
        # Sheet dimensions
        sheet_w = float(self.layout.sheet_width)
        sheet_h = float(self.layout.sheet_height)
        
        # Margins
        margin_t = float(self.layout.margin_top)
        margin_b = float(self.layout.margin_bottom)
        margin_l = float(self.layout.margin_left)
        margin_r = float(self.layout.margin_right)
        
        # Available space
        avail_w = sheet_w - margin_l - margin_r
        avail_h = sheet_h - margin_t - margin_b
        
        # Gaps
        h_gap = float(self.layout.horizontal_gap)
        v_gap = float(self.layout.vertical_gap)
        
        # Page size
        page_w = (avail_w - (cols - 1) * h_gap) / cols
        page_h = (avail_h - (rows - 1) * v_gap) / rows
        
        for sheet_num in range((len(pages) + pages_per_sheet - 1) // pages_per_sheet):
            sheet_pages = pages[sheet_num * pages_per_sheet:(sheet_num + 1) * pages_per_sheet]
            
            for idx, page_num in enumerate(sheet_pages):
                col = idx % cols
                row = idx // cols
                
                x = margin_l + col * (page_w + h_gap)
                y = margin_t + row * (page_h + v_gap)
                
                positions.append({
                    'sheet': sheet_num + 1,
                    'page': page_num,
                    'x': x,
                    'y': y,
                    'width': page_w,
                    'height': page_h,
                })
        
        return positions
    
    def generate_saddle_stitch_order(self, total_pages: int) -> List[int]:
        """Generate page order for saddle stitch binding"""
        # Round up to nearest multiple of 4
        padded_pages = ((total_pages + 3) // 4) * 4
        sheets = padded_pages // 4
        
        order = []
        for sheet in range(sheets):
            # Front side
            order.append(padded_pages - (sheet * 2))
            order.append(1 + (sheet * 2))
            # Back side
            order.append(2 + (sheet * 2))
            order.append(padded_pages - 1 - (sheet * 2))
        
        return order
