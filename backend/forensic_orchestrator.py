"""
Forensic Analysis Orchestrator
Coordinates blood detection, string method, and weapon classification analyses
"""
import cv2
import numpy as np
from typing import Dict, Any, Optional, Tuple
import logging
from datetime import datetime
import base64
from io import BytesIO
from PIL import Image as PILImage

from blood_detection import BloodDetectionAnalyzer
from string_method_analysis import StringMethodAnalyzer
from weapon_classification import WeaponTypeClassifier

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ForensicAnalysisOrchestrator:
    """
    Orchestrates all forensic analysis modules in the correct sequence:
    1. Blood Detection (must pass to continue)
    2. Weapon Classification (runs if blood detected)
    3. String Method Analysis (runs if blood detected)
    """
    
    def __init__(self, weapon_model_path: str):
        """
        Initialize all analysis modules
        
        Args:
            weapon_model_path: Path to the trained weapon classification model
        """
        logger.info("Initializing Forensic Analysis Orchestrator...")
        
        # Initialize all analyzers
        self.blood_analyzer = BloodDetectionAnalyzer()
        self.string_analyzer = StringMethodAnalyzer()
        self.weapon_classifier = WeaponTypeClassifier(model_path=weapon_model_path)
        
        self.target_size = (512, 512)
        logger.info(f"All modules initialized. Target image size: {self.target_size}")
    
    def resize_image(self, image: np.ndarray) -> np.ndarray:
        """
        Resize image to standard 512x512 if needed
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Resized image
        """
        current_height, current_width = image.shape[:2]
        
        if (current_height, current_width) != self.target_size:
            logger.info(f"Resizing image from {current_width}x{current_height} to {self.target_size[0]}x{self.target_size[1]}")
            resized = cv2.resize(image, self.target_size, interpolation=cv2.INTER_AREA)
            return resized
        
        logger.info(f"Image already at target size: {self.target_size}")
        return image
    
    def load_and_prepare_image(
        self, 
        image_path: str = None, 
        image_bytes: bytes = None
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Load image from path or bytes and resize to 512x512
        
        Args:
            image_path: Path to image file (optional)
            image_bytes: Image as bytes (optional)
            
        Returns:
            Tuple of (original_image, resized_image) both in BGR format
        """
        # Load image
        if image_path:
            original_image = cv2.imread(image_path)
            if original_image is None:
                raise ValueError(f"Could not load image: {image_path}")
            logger.info(f"Loaded image from path: {image_path}")
        elif image_bytes:
            nparr = np.frombuffer(image_bytes, np.uint8)
            original_image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            if original_image is None:
                raise ValueError("Could not decode image from bytes")
            logger.info("Loaded image from bytes")
        else:
            raise ValueError("Either image_path or image_bytes must be provided")
        
        # Resize to 512x512
        resized_image = self.resize_image(original_image)
        
        return original_image, resized_image
    
    def analyze(
        self,
        image_path: str = None,
        image_bytes: bytes = None,
        confidence_threshold: float = 65.0,
        generate_plots: bool = True
    ) -> Dict[str, Any]:
        """
        Run complete forensic analysis pipeline
        
        Args:
            image_path: Path to image file (optional)
            image_bytes: Image as bytes (optional)
            confidence_threshold: Minimum confidence for blood detection to proceed
            generate_plots: Whether to generate visualization plots
            
        Returns:
            Dictionary containing all analysis results
        """
        try:
            start_time = datetime.now()
            logger.info("="*70)
            logger.info("Starting Forensic Analysis Pipeline")
            logger.info("="*70)
            
            # Load and prepare image
            original_image, resized_image = self.load_and_prepare_image(image_path, image_bytes)
            
            # Convert resized image to bytes for analysis
            _, buffer = cv2.imencode('.png', resized_image)
            resized_bytes = buffer.tobytes()
            
            # STEP 1: Blood Detection (REQUIRED)
            logger.info("\n[STEP 1/3] Running Blood Detection Analysis...")
            blood_result = self.blood_analyzer.detect_blood(
                image_bytes=resized_bytes,
                generate_plot=generate_plots
            )
            
            blood_confidence = blood_result.get('confidence', 0)
            logger.info(f"Blood Detection: {blood_result.get('verdict')} (Confidence: {blood_confidence}%)")
            
            # Check if blood was detected with sufficient confidence
            if blood_confidence < confidence_threshold:
                logger.warning(f"Blood confidence ({blood_confidence}%) below threshold ({confidence_threshold}%)")
                logger.warning("Stopping analysis - no blood detected")
                
                end_time = datetime.now()
                duration = (end_time - start_time).total_seconds()
                
                return {
                    'status': 'no_blood_detected',
                    'message': f'Blood confidence ({blood_confidence}%) below threshold. Analysis stopped.',
                    'blood_detection': blood_result,
                    'weapon_classification': None,
                    'string_method': None,
                    'analysis_complete': False,
                    'timestamp': start_time.isoformat(),
                    'duration_seconds': duration,
                    'image_size': f"{self.target_size[0]}x{self.target_size[1]}"
                }
            
            # Blood detected - continue with other analyses
            logger.info(f"✓ Blood detected! Continuing with weapon and origin analysis...")
            
            # STEP 2: Weapon Classification
            logger.info("\n[STEP 2/3] Running Weapon Classification Analysis...")
            weapon_result = self.weapon_classifier.analyze(
                image_bytes=resized_bytes,
                generate_plot=generate_plots
            )
            logger.info(f"Weapon Classification: {weapon_result.get('weapon_type')} "
                       f"(Confidence: {weapon_result.get('confidence', 0):.1%})")
            
            # STEP 3: String Method Analysis
            logger.info("\n[STEP 3/3] Running String Method Analysis...")
            string_result = self.string_analyzer.analyze(
                image_bytes=resized_bytes,
                min_elongation=1.2,
                threshold=None,
                generate_plot=generate_plots
            )
            
            if string_result.get('status') == 'success':
                logger.info(f"String Method: Origin at {string_result['origin']['coordinates']}")
            else:
                logger.info(f"String Method: {string_result.get('status')} - {string_result.get('message', 'N/A')}")
            
            # Calculate total duration
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            logger.info("="*70)
            logger.info(f"Analysis Complete! Total time: {duration:.2f} seconds")
            logger.info("="*70)
            
            # Compile complete results
            result = {
                'status': 'success',
                'message': 'Complete forensic analysis performed successfully',
                'blood_detection': blood_result,
                'weapon_classification': weapon_result,
                'string_method': string_result,
                'analysis_complete': True,
                'timestamp': start_time.isoformat(),
                'duration_seconds': duration,
                'image_size': f"{self.target_size[0]}x{self.target_size[1]}",
                'summary': self._generate_summary(blood_result, weapon_result, string_result)
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in forensic analysis: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                'status': 'error',
                'message': f'Analysis failed: {str(e)}',
                'error': str(e),
                'blood_detection': None,
                'weapon_classification': None,
                'string_method': None,
                'analysis_complete': False,
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_summary(
        self, 
        blood_result: Dict[str, Any],
        weapon_result: Dict[str, Any],
        string_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate a summary of all analysis results
        
        Args:
            blood_result: Blood detection results
            weapon_result: Weapon classification results
            string_result: String method results
            
        Returns:
            Summary dictionary
        """
        summary = {
            'blood_detected': blood_result.get('verdict', 'Unknown'),
            'blood_confidence': blood_result.get('confidence', 0),
            'weapon_type': weapon_result.get('weapon_type', 'Unknown'),
            'weapon_confidence': weapon_result.get('confidence', 0),
        }
        
        # Add origin if available
        if string_result.get('status') == 'success':
            summary['origin_found'] = True
            summary['origin_coordinates'] = string_result['origin']['coordinates']
            summary['droplets_analyzed'] = string_result['statistics']['droplets_analyzed']
        else:
            summary['origin_found'] = False
            summary['origin_message'] = string_result.get('message', 'Could not determine origin')
        
        return summary
    
    def generate_comprehensive_report(self, analysis_result: Dict[str, Any]) -> str:
        """
        Generate a comprehensive text report from all analysis results
        
        Args:
            analysis_result: Complete analysis results dictionary
            
        Returns:
            Formatted text report
        """
        if analysis_result['status'] == 'error':
            return f"ERROR: {analysis_result.get('message', 'Unknown error')}"
        
        report_lines = [
            "=" * 80,
            "COMPREHENSIVE FORENSIC ANALYSIS REPORT",
            "=" * 80,
            f"Analysis Date: {analysis_result.get('timestamp', 'N/A')}",
            f"Analysis Duration: {analysis_result.get('duration_seconds', 0):.2f} seconds",
            f"Image Size: {analysis_result.get('image_size', 'N/A')}",
            "",
        ]
        
        # Blood Detection Section
        if analysis_result['blood_detection']:
            blood_result = analysis_result['blood_detection']
            report_lines.extend([
                "─" * 80,
                "1. BLOOD DETECTION ANALYSIS",
                "─" * 80,
                self.blood_analyzer.generate_report(blood_result),
                ""
            ])
        
        # Weapon Classification Section
        if analysis_result['weapon_classification']:
            weapon_result = analysis_result['weapon_classification']
            report_lines.extend([
                "─" * 80,
                "2. WEAPON TYPE CLASSIFICATION",
                "─" * 80,
                self.weapon_classifier.generate_report(weapon_result),
                ""
            ])
        
        # String Method Section
        if analysis_result['string_method']:
            string_result = analysis_result['string_method']
            report_lines.extend([
                "─" * 80,
                "3. POINT OF ORIGIN ANALYSIS",
                "─" * 80,
                self.string_analyzer.generate_report(string_result),
                ""
            ])
        
        # Executive Summary
        if analysis_result.get('summary'):
            summary = analysis_result['summary']
            report_lines.extend([
                "=" * 80,
                "EXECUTIVE SUMMARY",
                "=" * 80,
                f"Blood Detection: {summary.get('blood_detected')} ({summary.get('blood_confidence')}% confidence)",
                f"Weapon Type: {summary.get('weapon_type')} ({summary.get('weapon_confidence', 0):.1%} confidence)",
            ])
            
            if summary.get('origin_found'):
                report_lines.append(f"Point of Origin: {summary.get('origin_coordinates')}")
                report_lines.append(f"Droplets Analyzed: {summary.get('droplets_analyzed')}")
            else:
                report_lines.append(f"Point of Origin: {summary.get('origin_message')}")
            
            report_lines.extend([
                "",
                "=" * 80
            ])
        
        return "\n".join(report_lines)


# Example usage
if __name__ == "__main__":
    # Initialize orchestrator with your model path
    MODEL_PATH = 'models/weapon_classifier.h5'
    
    # Check if model exists
    import os
    if not os.path.exists(MODEL_PATH):
        print(f"ERROR: Model not found at {MODEL_PATH}")
        print("Please copy your trained model to backend/models/weapon_classifier.h5")
        exit(1)
    
    # Initialize orchestrator
    orchestrator = ForensicAnalysisOrchestrator(weapon_model_path=MODEL_PATH)
    
    # Example: Analyze an image
    # Replace with actual image path for testing
    TEST_IMAGE = 'test_image.jpg'
    
    if os.path.exists(TEST_IMAGE):
        print("\n" + "="*80)
        print("Running Comprehensive Forensic Analysis")
        print("="*80)
        
        # Run analysis
        result = orchestrator.analyze(image_path=TEST_IMAGE)
        
        # Generate report
        report = orchestrator.generate_comprehensive_report(result)
        print("\n" + report)
        
        # Save report to file
        with open('forensic_analysis_report.txt', 'w') as f:
            f.write(report)
        print("\nReport saved to: forensic_analysis_report.txt")
    else:
        print(f"Test image not found: {TEST_IMAGE}")
        print("Please provide a test image to run the analysis")
