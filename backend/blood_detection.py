"""
Blood Detection Analysis Module
Analyzes images for blood presence using color, pattern, and texture analysis
"""
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server environments
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from skimage import measure
import warnings
import io
import base64
from typing import Dict, Any, Tuple, List
import logging

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BloodDetectionAnalyzer:
    """
    Blood Detection Analyzer using Computer Vision techniques.
    
    Analyzes images for blood presence through:
    1. Color analysis (HSV color space)
    2. Splatter pattern detection
    3. Texture analysis
    """
    
    # Blood color ranges in HSV color space
    BLOOD_HSV_RANGES = [
        (np.array([0,   80,  40]),  np.array([12,  255, 220]),  'Fresh Blood (Bright Red)'),
        (np.array([168, 80,  40]),  np.array([180, 255, 220]),  'Fresh Blood (Deep Red)'),
        (np.array([0,   40,  20]),  np.array([18,  180, 130]),  'Dried Blood (Brown-Red)'),
        (np.array([0,   30,  15]),  np.array([20,  120,  80]),  'Very Dried Blood (Dark Brown)'),
    ]
    
    def __init__(self):
        """Initialize the blood detection analyzer"""
        logger.info("Blood Detection Analyzer initialized")
    
    def load_image(self, image_path: str) -> np.ndarray:
        """
        Load image from file path
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Image as numpy array in BGR format
        """
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f'Could not load image from: {image_path}')
        return img
    
    def load_image_from_bytes(self, image_bytes: bytes) -> np.ndarray:
        """
        Load image from bytes
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Image as numpy array in BGR format
        """
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError('Could not decode image from bytes')
        return img
    
    def analyze_blood_color(self, bgr_img: np.ndarray) -> Tuple[np.ndarray, float, List[Tuple[str, float]]]:
        """
        Analyze image for blood-like colors in HSV space
        
        Args:
            bgr_img: Input image in BGR format
            
        Returns:
            Tuple of (mask, coverage_percentage, matched_types)
        """
        hsv = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2HSV)
        h, w = hsv.shape[:2]
        total_pixels = h * w
        combined_mask = np.zeros((h, w), dtype=np.uint8)
        matched_types = []
        
        for lo, hi, label in self.BLOOD_HSV_RANGES:
            mask = cv2.inRange(hsv, lo, hi)
            count = np.count_nonzero(mask)
            
            # Only include if coverage is significant (>0.5%)
            if count / total_pixels > 0.005:
                combined_mask = cv2.bitwise_or(combined_mask, mask)
                matched_types.append((label, count / total_pixels * 100))
        
        coverage = np.count_nonzero(combined_mask) / total_pixels
        return combined_mask, coverage, matched_types
    
    def analyze_splatter_pattern(self, mask: np.ndarray) -> Tuple[float, Dict[str, Any]]:
        """
        Analyze blood splatter pattern characteristics
        
        Args:
            mask: Binary mask of detected blood regions
            
        Returns:
            Tuple of (pattern_score, statistics_dict)
        """
        # Clean up mask
        kernel = np.ones((3, 3), np.uint8)
        cleaned = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
        
        # Label connected components
        labeled = measure.label(cleaned)
        regions = measure.regionprops(labeled)
        
        if not regions:
            return 0.0, {
                'num_components': 0,
                'spread_ratio': 0,
                'satellite_ratio': 0
            }
        
        # Analyze component sizes
        areas = [r.area for r in regions]
        max_area = max(areas)
        satellites = sum(1 for a in areas if a < max_area * 0.05)
        satellite_ratio = satellites / len(regions)
        
        # Analyze spatial spread
        ys, xs = np.where(cleaned > 0)
        if len(xs) == 0:
            return 0.0, {}
        
        spread_x = (xs.max() - xs.min()) / cleaned.shape[1]
        spread_y = (ys.max() - ys.min()) / cleaned.shape[0]
        spread_ratio = (spread_x + spread_y) / 2
        
        # Calculate pattern score
        score = min(1.0, satellite_ratio * 0.5 + spread_ratio * 0.5)
        
        return score, {
            'num_components': len(regions),
            'num_satellites': satellites,
            'satellite_ratio': round(satellite_ratio * 100, 1),
            'spread_ratio': round(spread_ratio * 100, 1),
        }
    
    def analyze_texture(self, bgr_img: np.ndarray, mask: np.ndarray) -> Tuple[float, Dict[str, Any]]:
        """
        Analyze texture characteristics of detected regions
        
        Args:
            bgr_img: Original image in BGR format
            mask: Binary mask of detected blood regions
            
        Returns:
            Tuple of (texture_score, statistics_dict)
        """
        gray = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2GRAY)
        
        if np.count_nonzero(mask) < 100:
            return 0.0, {}
        
        # Analyze pixel intensity variation
        region_pixels = gray[mask > 0]
        pixel_std = float(np.std(region_pixels))
        
        # Analyze edge density
        edges = cv2.Canny(gray, 30, 100)
        edges_in_region = cv2.bitwise_and(edges, edges, mask=mask)
        edge_density = np.count_nonzero(edges_in_region) / np.count_nonzero(mask)
        
        # Calculate texture score
        std_score = min(1.0, pixel_std / 60.0)
        edge_score = min(1.0, edge_density / 0.3)
        score = (std_score * 0.5 + edge_score * 0.5)
        
        return score, {
            'pixel_std': round(pixel_std, 2),
            'edge_density': round(edge_density * 100, 2)
        }
    
    def compute_final_verdict(
        self, 
        color_coverage: float, 
        pattern_score: float, 
        texture_score: float
    ) -> Tuple[str, float, str, Dict[str, float]]:
        """
        Compute final verdict based on all analysis scores
        
        Args:
            color_coverage: Blood color coverage percentage
            pattern_score: Splatter pattern score
            texture_score: Texture analysis score
            
        Returns:
            Tuple of (verdict, confidence, color, scores_dict)
        """
        color_score = min(1.0, color_coverage / 0.30)
        confidence = round(
            (color_score * 0.40 + pattern_score * 0.35 + texture_score * 0.25) * 100,
            1
        )
        
        if confidence >= 65:
            verdict, color = '🩸 LIKELY BLOOD', 'crimson'
        elif confidence >= 40:
            verdict, color = '⚠️  POSSIBLE BLOOD', 'darkorange'
        else:
            verdict, color = '✅ NOT BLOOD', 'green'
        
        return verdict, confidence, color, {
            'color_score': round(color_score * 100, 1),
            'pattern_score': round(pattern_score * 100, 1),
            'texture_score': round(texture_score * 100, 1),
        }
    
    def generate_visualization(
        self,
        rgb: np.ndarray,
        mask: np.ndarray,
        coverage: float,
        verdict: str,
        confidence: float,
        verdict_color: str,
        scores: Dict[str, float]
    ) -> str:
        """
        Generate single clear visualization showing blood detection overlay
        
        Args:
            rgb: Original image in RGB format
            mask: Blood detection mask
            coverage: Blood coverage percentage
            verdict: Final verdict string
            confidence: Confidence percentage
            verdict_color: Color for verdict display
            scores: Dictionary of all scores
            
        Returns:
            Base64 encoded PNG image
        """
        # Create single large figure showing blood overlay
        fig, ax = plt.subplots(1, 1, figsize=(10, 10), facecolor='#1a1a1a')
        
        # Create overlay of original image with blood regions highlighted
        overlay = rgb.copy()
        overlay[mask > 0] = [255, 50, 50]  # Highlight blood regions in red
        blended = cv2.addWeighted(rgb, 0.6, overlay, 0.4, 0)
        
        ax.imshow(blended)
        ax.axis('off')
        
        # Add verdict and confidence as title
        title_text = f'{verdict}   |   Confidence: {confidence}%\nCoverage: {coverage*100:.1f}%'
        ax.set_title(title_text, 
                    fontsize=18, fontweight='bold', 
                    color=verdict_color, pad=20)
        
        # Add score breakdown as text annotation
        scores_text = (f"Color Score: {scores['color_score']:.1f}%\n"
                      f"Pattern Score: {scores['pattern_score']:.1f}%\n"
                      f"Texture Score: {scores['texture_score']:.1f}%")
        
        ax.text(0.02, 0.98, scores_text,
               transform=ax.transAxes,
               fontsize=12, color='white',
               verticalalignment='top',
               bbox=dict(boxstyle='round', facecolor='black', alpha=0.7))
        
        plt.tight_layout()
        
        # Save to bytes with high DPI
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor='#1a1a1a', dpi=150, bbox_inches='tight')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close(fig)
        
        return img_base64
    
    def detect_blood(
        self,
        image_path: str = None,
        image_bytes: bytes = None,
        generate_plot: bool = True
    ) -> Dict[str, Any]:
        """
        Main blood detection function
        
        Args:
            image_path: Path to image file (optional)
            image_bytes: Image as bytes (optional)
            generate_plot: Whether to generate visualization plot
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Load image
            if image_path:
                bgr = self.load_image(image_path)
            elif image_bytes:
                bgr = self.load_image_from_bytes(image_bytes)
            else:
                raise ValueError("Either image_path or image_bytes must be provided")
            
            rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
            
            # Perform analysis
            logger.info("Analyzing blood color...")
            mask, coverage, matched_types = self.analyze_blood_color(bgr)
            
            logger.info("Analyzing splatter pattern...")
            pattern_score, pattern_stats = self.analyze_splatter_pattern(mask)
            
            logger.info("Analyzing texture...")
            texture_score, texture_stats = self.analyze_texture(bgr, mask)
            
            logger.info("Computing final verdict...")
            verdict, confidence, verdict_color, scores = self.compute_final_verdict(
                coverage, pattern_score, texture_score
            )
            
            # Generate visualization if requested
            plot_base64 = None
            if generate_plot:
                logger.info("Generating visualization...")
                plot_base64 = self.generate_visualization(
                    rgb, mask, coverage, verdict, confidence, verdict_color, scores
                )
            
            # Compile results
            result = {
                'status': 'success',
                'verdict': verdict,
                'confidence': confidence,
                'verdict_color': verdict_color,
                'analysis': {
                    'color_analysis': {
                        'coverage': round(coverage * 100, 2),
                        'score': scores['color_score'],
                        'matched_types': matched_types
                    },
                    'pattern_analysis': {
                        'score': scores['pattern_score'],
                        'statistics': pattern_stats
                    },
                    'texture_analysis': {
                        'score': scores['texture_score'],
                        'statistics': texture_stats
                    }
                },
                'scores': scores,
                'visualization': plot_base64
            }
            
            logger.info(f"Analysis complete: {verdict} | Confidence: {confidence}%")
            return result
            
        except Exception as e:
            logger.error(f"Error in blood detection: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to analyze image for blood detection'
            }
    
    def generate_report(self, result: Dict[str, Any]) -> str:
        """
        Generate human-readable text report
        
        Args:
            result: Analysis result dictionary
            
        Returns:
            Formatted text report
        """
        if result['status'] == 'error':
            return f"Error: {result.get('message', 'Unknown error')}"
        
        analysis = result['analysis']
        scores = result['scores']
        
        report_lines = [
            "=" * 60,
            "BLOOD DETECTION ANALYSIS REPORT",
            "=" * 60,
            "",
            f"VERDICT: {result['verdict']}",
            f"CONFIDENCE: {result['confidence']}%",
            "",
            "-" * 60,
            "DETAILED ANALYSIS:",
            "-" * 60,
            "",
            "1. COLOR ANALYSIS:",
            f"   Coverage: {analysis['color_analysis']['coverage']:.2f}%",
            f"   Score: {scores['color_score']:.1f}%",
        ]
        
        if analysis['color_analysis']['matched_types']:
            report_lines.append("   Detected Blood Types:")
            for blood_type, percentage in analysis['color_analysis']['matched_types']:
                report_lines.append(f"     - {blood_type}: {percentage:.2f}%")
        
        report_lines.extend([
            "",
            "2. PATTERN ANALYSIS:",
            f"   Score: {scores['pattern_score']:.1f}%",
            f"   Components: {analysis['pattern_analysis']['statistics'].get('num_components', 0)}",
            f"   Satellites: {analysis['pattern_analysis']['statistics'].get('num_satellites', 0)}",
            f"   Satellite Ratio: {analysis['pattern_analysis']['statistics'].get('satellite_ratio', 0):.1f}%",
            f"   Spread Ratio: {analysis['pattern_analysis']['statistics'].get('spread_ratio', 0):.1f}%",
            "",
            "3. TEXTURE ANALYSIS:",
            f"   Score: {scores['texture_score']:.1f}%",
        ])
        
        if analysis['texture_analysis']['statistics']:
            report_lines.extend([
                f"   Pixel Std Dev: {analysis['texture_analysis']['statistics'].get('pixel_std', 0):.2f}",
                f"   Edge Density: {analysis['texture_analysis']['statistics'].get('edge_density', 0):.2f}%",
            ])
        
        report_lines.extend([
            "",
            "=" * 60,
            "INTERPRETATION:",
            "=" * 60,
        ])
        
        if result['confidence'] >= 65:
            report_lines.append("The analysis indicates a HIGH probability of blood presence.")
            report_lines.append("Recommend professional forensic analysis.")
        elif result['confidence'] >= 40:
            report_lines.append("The analysis suggests POSSIBLE blood presence.")
            report_lines.append("Further testing recommended for confirmation.")
        else:
            report_lines.append("The analysis indicates LOW probability of blood presence.")
            report_lines.append("The substance is likely not blood.")
        
        report_lines.extend([
            "",
            "=" * 60
        ])
        
        return "\n".join(report_lines)


# Example usage and testing
if __name__ == "__main__":
    analyzer = BloodDetectionAnalyzer()
    
    # Test with an image
    IMAGE_PATH = r'C:\Users\User\Desktop\research_nsbm\data\test\image1.png'
    
    try:
        result = analyzer.detect_blood(image_path=IMAGE_PATH, generate_plot=True)
        
        # Print report
        report = analyzer.generate_report(result)
        print(report)
        
        # Save visualization if generated
        if result.get('visualization'):
            with open('blood_detection_result.png', 'wb') as f:
                f.write(base64.b64decode(result['visualization']))
            print("\nVisualization saved to: blood_detection_result.png")
            
    except Exception as e:
        print(f"Error: {str(e)}")
