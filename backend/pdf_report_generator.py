"""
PDF Report Generator for Forensic Analysis
Generates comprehensive PDF reports with visualizations
"""
from reportlab.lib.pagesizes import letter, A4, landscape
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, PageBreak
from reportlab.platypus import Table, TableStyle
from reportlab.lib.colors import HexColor
from datetime import datetime
import base64
from io import BytesIO
from typing import Dict, Any
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ForensicPDFReportGenerator:
    """
    Generates professional PDF reports for forensic analysis results
    """
    
    def __init__(self):
        """Initialize PDF report generator"""
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        # Title style
        if 'CustomTitle' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=24,
                textColor=HexColor('#8B0000'),
                spaceAfter=30,
                alignment=TA_CENTER,
                fontName='Helvetica-Bold'
            ))
        
        # Section header style
        if 'SectionHeader' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SectionHeader',
                parent=self.styles['Heading2'],
                fontSize=16,
                textColor=HexColor('#8B0000'),
                spaceAfter=12,
                spaceBefore=12,
                fontName='Helvetica-Bold'
            ))
        
        # Subsection style
        if 'SubSection' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='SubSection',
                parent=self.styles['Heading3'],
                fontSize=14,
                textColor=HexColor('#000080'),
                spaceAfter=8,
                spaceBefore=8,
                fontName='Helvetica-Bold'
            ))
        
        # Body text style
        if 'BodyText' not in self.styles:
            self.styles.add(ParagraphStyle(
                name='BodyText',
                parent=self.styles['Normal'],
                fontSize=11,
                spaceAfter=6,
                alignment=TA_JUSTIFY
            ))
    
    def _add_header(self, story):
        """Add report header"""
        story.append(Paragraph("FORENSIC ANALYSIS REPORT", self.styles['CustomTitle']))
        story.append(Paragraph("Blood Pattern Analysis & Classification", self.styles['Heading3']))
        story.append(Spacer(1, 0.3*inch))
        
        # Add timestamp
        timestamp = datetime.now().strftime("%B %d, %Y at %I:%M %p")
        story.append(Paragraph(f"<b>Report Generated:</b> {timestamp}", self.styles['BodyText']))
        story.append(Spacer(1, 0.3*inch))
    
    def _add_summary_table(self, story, summary: Dict[str, Any]):
        """Add executive summary table"""
        story.append(Paragraph("EXECUTIVE SUMMARY", self.styles['SectionHeader']))
        
        data = [
            ['Analysis Component', 'Result', 'Confidence'],
            [
                'Blood Detection',
                summary.get('blood_detected', 'N/A'),
                f"{summary.get('blood_confidence', 0)}%"
            ],
            [
                'Weapon Type',
                summary.get('weapon_type', 'N/A'),
                f"{summary.get('weapon_confidence', 0):.1%}"
            ]
        ]
        
        # Add origin if available
        if summary.get('origin_found'):
            data.append([
                'Point of Origin',
                summary.get('origin_coordinates', 'N/A'),
                f"{summary.get('droplets_analyzed', 0)} droplets"
            ])
        else:
            data.append([
                'Point of Origin',
                summary.get('origin_message', 'Not determined'),
                'N/A'
            ])
        
        table = Table(data, colWidths=[2.5*inch, 2.5*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#8B0000')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), HexColor('#f0f0f0')),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('TOPPADDING', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ]))
        
        story.append(table)
        story.append(Spacer(1, 0.3*inch))
    
    def _add_blood_detection_section(self, story, blood_result: Dict[str, Any]):
        """Add blood detection analysis section"""
        story.append(PageBreak())
        story.append(Paragraph("1. BLOOD DETECTION ANALYSIS", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        # Add verdict
        verdict = blood_result.get('verdict', 'Unknown')
        confidence = blood_result.get('confidence', 0)
        story.append(Paragraph(f"<b>Verdict:</b> {verdict}", self.styles['BodyText']))
        story.append(Paragraph(f"<b>Confidence:</b> {confidence}%", self.styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))
        
        # Add analysis details
        analysis = blood_result.get('analysis', {})
        
        # Color analysis
        if 'color_analysis' in analysis:
            story.append(Paragraph("Color Analysis:", self.styles['SubSection']))
            color_data = analysis['color_analysis']
            story.append(Paragraph(f"Coverage: {color_data.get('coverage', 0):.2f}%", self.styles['BodyText']))
            story.append(Paragraph(f"Score: {color_data.get('score', 0):.1f}%", self.styles['BodyText']))
            
            if color_data.get('matched_types'):
                story.append(Paragraph("Detected Blood Types:", self.styles['BodyText']))
                for blood_type, percentage in color_data['matched_types']:
                    story.append(Paragraph(f"  • {blood_type}: {percentage:.2f}%", self.styles['BodyText']))
            
            story.append(Spacer(1, 0.1*inch))
        
        # Pattern analysis
        if 'pattern_analysis' in analysis:
            story.append(Paragraph("Pattern Analysis:", self.styles['SubSection']))
            pattern_data = analysis['pattern_analysis']
            story.append(Paragraph(f"Score: {pattern_data.get('score', 0):.1f}%", self.styles['BodyText']))
            
            stats = pattern_data.get('statistics', {})
            if stats:
                story.append(Paragraph(f"Components: {stats.get('num_components', 0)}", self.styles['BodyText']))
                story.append(Paragraph(f"Satellites: {stats.get('num_satellites', 0)}", self.styles['BodyText']))
            
            story.append(Spacer(1, 0.1*inch))
        
        # Add visualization if available
        if blood_result.get('visualization'):
            story.append(PageBreak())  # Put on separate page for full size
            story.append(Paragraph("Blood Detection Visualization", self.styles['SubSection']))
            story.append(Spacer(1, 0.1*inch))
            self._add_image_from_base64(story, blood_result['visualization'], 
                                        "Blood Detection Analysis")
    
    def _add_weapon_classification_section(self, story, weapon_result: Dict[str, Any]):
        """Add weapon classification section"""
        story.append(PageBreak())
        story.append(Paragraph("2. WEAPON TYPE CLASSIFICATION", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        # Add classification result
        weapon_type = weapon_result.get('weapon_type', 'Unknown')
        confidence = weapon_result.get('confidence', 0)
        story.append(Paragraph(f"<b>Weapon Type:</b> {weapon_type}", self.styles['BodyText']))
        story.append(Paragraph(f"<b>Confidence:</b> {confidence:.1%}", self.styles['BodyText']))
        story.append(Spacer(1, 0.2*inch))
        
        # Add probabilities
        story.append(Paragraph("Detailed Probabilities:", self.styles['SubSection']))
        probs = weapon_result.get('probabilities', {})
        for weapon, prob in probs.items():
            story.append(Paragraph(f"  • {weapon}: {prob:.2%}", self.styles['BodyText']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Add interpretation
        interpretation = weapon_result.get('interpretation', '')
        if interpretation:
            story.append(Paragraph("Interpretation:", self.styles['SubSection']))
            story.append(Paragraph(interpretation, self.styles['BodyText']))
        
        story.append(Spacer(1, 0.2*inch))
        
        # Add visualization if available
        if weapon_result.get('visualization'):
            story.append(PageBreak())  # Put on separate page for full size
            story.append(Paragraph("Weapon Classification Visualization", self.styles['SubSection']))
            story.append(Spacer(1, 0.1*inch))
            self._add_image_from_base64(story, weapon_result['visualization'],
                                        "Weapon Classification Analysis")
    
    def _add_string_method_section(self, story, string_result: Dict[str, Any]):
        """Add string method analysis section"""
        story.append(PageBreak())
        story.append(Paragraph("3. POINT OF ORIGIN ANALYSIS", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        if string_result.get('status') == 'success':
            # Add origin coordinates
            origin = string_result.get('origin', {})
            story.append(Paragraph(f"<b>Point of Origin:</b> {origin.get('coordinates', 'N/A')}", 
                                 self.styles['BodyText']))
            story.append(Spacer(1, 0.2*inch))
            
            # Add statistics
            story.append(Paragraph("Analysis Statistics:", self.styles['SubSection']))
            stats = string_result.get('statistics', {})
            story.append(Paragraph(f"Droplets Analyzed: {stats.get('droplets_analyzed', 0)}", 
                                 self.styles['BodyText']))
            story.append(Paragraph(f"Intersection Points: {stats.get('intersections_found', 0)}", 
                                 self.styles['BodyText']))
            story.append(Paragraph(f"Average Impact Angle: {stats.get('average_impact_angle', 0):.1f}°", 
                                 self.styles['BodyText']))
            story.append(Paragraph(f"Angle Range: {stats.get('min_impact_angle', 0):.1f}° - {stats.get('max_impact_angle', 0):.1f}°", 
                                 self.styles['BodyText']))
            
            story.append(Spacer(1, 0.2*inch))
            
            # Add visualization if available - Maximum size that fits page!
            if string_result.get('visualization'):
                story.append(PageBreak())  # Put on its own page for maximum clarity
                story.append(Paragraph("Point of Origin Visualization", self.styles['SubSection']))
                story.append(Spacer(1, 0.1*inch))
                self._add_image_from_base64(story, string_result['visualization'],
                                            "String Method Analysis - Trajectory lines and origin point")
        else:
            status = string_result.get('status', 'unknown')
            message = string_result.get('message', 'Analysis could not be completed')
            story.append(Paragraph(f"<b>Status:</b> {status}", self.styles['BodyText']))
            story.append(Paragraph(f"<b>Message:</b> {message}", self.styles['BodyText']))
    
    def _add_image_from_base64(self, story, base64_string: str, caption: str, use_original_size=False):
        """Add image from base64 string scaled to fit page while maintaining aspect ratio"""
        try:
            # Decode base64 image
            image_data = base64.b64decode(base64_string)
            image_buffer = BytesIO(image_data)
            
            # Create ReportLab image
            img = RLImage(image_buffer)
            
            # Page dimensions (Letter size with margins)
            # Letter: 8.5 x 11 inches, with 0.75 inch margins = 7 x 9.5 inches usable
            usable_width = 7 * inch
            usable_height = 9.5 * inch
            
            # Get original image dimensions in points
            original_width = img.imageWidth * 0.75  # Convert pixels to points
            original_height = img.imageHeight * 0.75
            
            # Calculate aspect ratio
            aspect_ratio = original_height / original_width
            
            # Scale to fit within usable area while maintaining aspect ratio
            if original_width > usable_width or original_height > usable_height:
                # Image is larger than page - scale down to fit
                width_scale = usable_width / original_width
                height_scale = usable_height / original_height
                scale = min(width_scale, height_scale)
                
                img.drawWidth = original_width * scale
                img.drawHeight = original_height * scale
            else:
                # Image fits on page - use original size
                img.drawWidth = original_width
                img.drawHeight = original_height
            
            logger.info(f"Image scaled to: {img.drawWidth/inch:.2f}\" x {img.drawHeight/inch:.2f}\" (original: {original_width/inch:.2f}\" x {original_height/inch:.2f}\")")
            
            story.append(img)
            
            # Add caption
            story.append(Spacer(1, 0.1*inch))
            story.append(Paragraph(f"<i>{caption}</i>", self.styles['BodyText']))
            story.append(Spacer(1, 0.2*inch))
        except Exception as e:
            logger.error(f"Error adding image: {str(e)}")
            story.append(Paragraph(f"<i>Image could not be loaded: {caption}</i>", 
                                 self.styles['BodyText']))
    
    def _add_disclaimer(self, story):
        """Add disclaimer section"""
        story.append(PageBreak())
        story.append(Paragraph("DISCLAIMER", self.styles['SectionHeader']))
        story.append(Spacer(1, 0.1*inch))
        
        disclaimer_text = """
        This forensic analysis report was generated using AI-assisted computational 
        methods for blood pattern analysis. The results presented are based on image 
        analysis algorithms and machine learning models trained on forensic datasets.
        
        <b>Important Notes:</b><br/>
        • This report should be used as a supplementary tool in forensic investigations<br/>
        • Results must be verified by qualified forensic experts<br/>
        • This report is not intended for sole use in legal proceedings<br/>
        • Professional forensic confirmation is required for official documentation<br/>
        • The accuracy of results depends on image quality and pattern clarity
        
        <b>Model Information:</b><br/>
        • Blood Detection: Computer vision analysis (HSV color space, pattern recognition)<br/>
        • Weapon Classification: Deep learning CNN (TensorFlow)<br/>
        • String Method: Classical forensic trajectory analysis with DBSCAN clustering
        
        For questions or concerns about this analysis, consult with certified forensic analysts.
        """
        
        story.append(Paragraph(disclaimer_text, self.styles['BodyText']))
    
    def generate_pdf(
        self, 
        analysis_result: Dict[str, Any], 
        output_path: str = "forensic_analysis_report.pdf"
    ) -> str:
        """
        Generate PDF report from analysis results
        
        Args:
            analysis_result: Complete analysis results dictionary
            output_path: Path where PDF will be saved
            
        Returns:
            Path to generated PDF file
        """
        try:
            logger.info(f"Generating PDF report: {output_path}")
            
            # Create PDF document
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            story = []
            
            # Add header
            self._add_header(story)
            
            # Add summary if available
            if analysis_result.get('summary'):
                self._add_summary_table(story, analysis_result['summary'])
            
            # Add analysis sections
            if analysis_result.get('blood_detection'):
                self._add_blood_detection_section(story, analysis_result['blood_detection'])
            
            if analysis_result.get('weapon_classification'):
                self._add_weapon_classification_section(story, analysis_result['weapon_classification'])
            
            if analysis_result.get('string_method'):
                self._add_string_method_section(story, analysis_result['string_method'])
            
            # Add disclaimer
            self._add_disclaimer(story)
            
            # Build PDF
            doc.build(story)
            
            logger.info(f"PDF report generated successfully: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise


# Example usage
if __name__ == "__main__":
    # This is just for testing - normally called from orchestrator
    print("PDF Report Generator initialized")
    print("Use ForensicPDFReportGenerator().generate_pdf(analysis_result) to create reports")
