"""
Weapon Type Classification Module - Blood Pattern Analysis
Classifies blood spatter patterns to identify weapon type (Gun vs Melee)
Uses deep learning CNN model trained on forensic blood pattern images
"""
import tensorflow as tf
from tensorflow import keras
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server environments
import matplotlib.pyplot as plt
import warnings
import io
import base64
from typing import Dict, Any, Tuple, Optional
import logging
import os

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class WeaponTypeClassifier:
    """
    Weapon Type Classifier for blood pattern analysis.
    
    Classifies blood spatter patterns into:
    - Gun: High/medium velocity impact spatter (gunshot wounds)
    - Melee: Cast-off or impact spatter (blunt/sharp force trauma)
    """
    
    def __init__(self, img_size: Tuple[int, int] = (224, 224), model_path: Optional[str] = None):
        """
        Initialize the Weapon Type Classifier
        
        Args:
            img_size: Input image size for the model
            model_path: Path to trained model file (.h5)
        """
        self.img_size = img_size
        self.model = None
        self.class_names = ['Gun', 'Melee']
        
        # Load model if path provided
        if model_path and os.path.exists(model_path):
            try:
                self.load_model(model_path)
                logger.info(f"Model loaded from: {model_path}")
            except Exception as e:
                logger.error(f"Failed to load model from {model_path}: {str(e)}")
                logger.warning("Classifier will not work without a valid model")
        else:
            if model_path:
                logger.error(f"Model file not found: {model_path}")
            logger.warning("No model loaded. Please load a trained model before prediction.")
    
    def load_model(self, filepath: str) -> keras.Model:
        """
        Load a trained model from file
        
        Args:
            filepath: Path to the .h5 model file
            
        Returns:
            Loaded Keras model
        """
        try:
            # Method 1: Try loading with compile=False
            self.model = keras.models.load_model(filepath, compile=False)
            
            # Recompile the model with current TensorFlow version
            self.model.compile(
                optimizer='adam',
                loss='categorical_crossentropy',
                metrics=['accuracy']
            )
            
            logger.info(f"Model loaded successfully from {filepath}")
            logger.info(f"Model input shape: {self.model.input_shape}")
            logger.info(f"Model output shape: {self.model.output_shape}")
            return self.model
            
        except Exception as e1:
            logger.error(f"Standard loading failed: {str(e1)}")
            
            # Method 2: Try with TF compatibility mode
            try:
                logger.info("Attempting TF compatibility mode...")
                import tensorflow.compat.v1 as tf_v1
                
                # Disable eager execution for compatibility
                tf.compat.v1.disable_eager_execution()
                
                self.model = keras.models.load_model(
                    filepath,
                    compile=False,
                    custom_objects=None
                )
                
                # Recompile
                self.model.compile(
                    optimizer='adam',
                    loss='categorical_crossentropy',
                    metrics=['accuracy']
                )
                
                logger.info("Model loaded using TF compatibility mode")
                return self.model
                
            except Exception as e2:
                logger.error(f"TF compatibility mode failed: {str(e2)}")
                
                # Method 3: Try loading with custom InputLayer handler
                try:
                    logger.info("Attempting custom InputLayer handler...")
                    
                    # Custom object scope for backward compatibility
                    from tensorflow.keras.layers import InputLayer
                    
                    def custom_input_layer(*args, **kwargs):
                        # Remove batch_shape if present, use input_shape instead
                        if 'batch_shape' in kwargs:
                            batch_shape = kwargs.pop('batch_shape')
                            if batch_shape and len(batch_shape) > 1:
                                kwargs['input_shape'] = batch_shape[1:]
                        return InputLayer(*args, **kwargs)
                    
                    self.model = keras.models.load_model(
                        filepath,
                        compile=False,
                        custom_objects={'InputLayer': custom_input_layer}
                    )
                    
                    # Recompile
                    self.model.compile(
                        optimizer='adam',
                        loss='categorical_crossentropy',
                        metrics=['accuracy']
                    )
                    
                    logger.info("Model loaded with custom InputLayer handler")
                    return self.model
                    
                except Exception as e3:
                    logger.error(f"Custom handler also failed: {str(e3)}")
                    raise Exception(
                        f"Could not load model with any method. "
                        f"The model may need to be re-saved with TensorFlow 2.14. "
                        f"Original error: {str(e1)}"
                    )
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for model input
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Preprocessed image ready for model
        """
        # Convert BGR to RGB
        if len(image.shape) == 3 and image.shape[2] == 3:
            img_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            img_rgb = image
        
        # Resize to model input size
        img_resized = cv2.resize(img_rgb, self.img_size)
        
        # Normalize to [0, 1]
        img_normalized = img_resized.astype(np.float32) / 255.0
        
        # Add batch dimension
        img_batch = np.expand_dims(img_normalized, axis=0)
        
        return img_batch
    
    def predict(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Predict weapon type from blood pattern image
        
        Args:
            image: Input image (BGR format)
            
        Returns:
            Dictionary containing prediction results
        """
        if self.model is None:
            raise ValueError("No model loaded. Please load a model first.")
        
        # Preprocess image
        img_batch = self.preprocess_image(image)
        
        # Make prediction
        predictions = self.model.predict(img_batch, verbose=0)
        
        # Get predicted class and confidence
        predicted_class_idx = np.argmax(predictions[0])
        confidence = float(predictions[0][predicted_class_idx])
        predicted_class = self.class_names[predicted_class_idx]
        
        result = {
            'weapon_type': predicted_class,
            'confidence': confidence,
            'probabilities': {
                'Gun': float(predictions[0][0]),
                'Melee': float(predictions[0][1])
            },
            'raw_predictions': predictions[0].tolist()
        }
        
        return result
    
    def predict_from_path(self, image_path: str) -> Tuple[Dict[str, Any], np.ndarray]:
        """
        Predict weapon type from image file path
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (prediction_results, original_image_rgb)
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            raise ValueError(f"Could not load image: {image_path}")
        
        # Convert to RGB for visualization
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Make prediction
        result = self.predict(image)
        
        return result, image_rgb
    
    def predict_from_bytes(self, image_bytes: bytes) -> Tuple[Dict[str, Any], np.ndarray]:
        """
        Predict weapon type from image bytes
        
        Args:
            image_bytes: Image data as bytes
            
        Returns:
            Tuple of (prediction_results, original_image_rgb)
        """
        # Decode image from bytes
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise ValueError("Could not decode image from bytes")
        
        # Convert to RGB for visualization
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Make prediction
        result = self.predict(image)
        
        return result, image_rgb
    
    def generate_visualization(
        self, 
        image_rgb: np.ndarray, 
        result: Dict[str, Any]
    ) -> str:
        """
        Generate single clear visualization showing the analyzed image with prediction
        
        Args:
            image_rgb: Original image in RGB format
            result: Prediction results dictionary
            
        Returns:
            Base64 encoded PNG image
        """
        # Create single large figure showing the analyzed image
        fig, ax = plt.subplots(1, 1, figsize=(10, 10), facecolor='#1a1a1a')
        
        # Display blood pattern image
        ax.imshow(image_rgb)
        ax.axis('off')
        
        # Get prediction results
        weapon_type = result['weapon_type']
        confidence = result['confidence']
        probs = result['probabilities']
        
        # Color based on weapon type
        verdict_color = '#ff4444' if weapon_type == 'Gun' else '#4444ff'
        
        # Add title with prediction
        title_text = f'Weapon Type: {weapon_type}\nConfidence: {confidence:.1%}'
        ax.set_title(title_text, 
                    fontsize=18, fontweight='bold', 
                    color=verdict_color, pad=20)
        
        # Add probability breakdown as text annotation
        prob_text = "Probabilities:\n"
        for weapon, prob in probs.items():
            prob_text += f"{weapon}: {prob:.1%}\n"
        
        ax.text(0.02, 0.98, prob_text.strip(),
               transform=ax.transAxes,
               fontsize=14, color='white',
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
    
    def analyze(
        self,
        image_path: str = None,
        image_bytes: bytes = None,
        generate_plot: bool = True
    ) -> Dict[str, Any]:
        """
        Main analysis method
        
        Args:
            image_path: Path to image file (optional)
            image_bytes: Image as bytes (optional)
            generate_plot: Whether to generate visualization
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            if self.model is None:
                return {
                    'status': 'error',
                    'error': 'No model loaded',
                    'message': 'Please load a trained model before prediction'
                }
            
            # Load image
            if image_path:
                result, image_rgb = self.predict_from_path(image_path)
                logger.info(f"Analyzed image: {image_path}")
            elif image_bytes:
                result, image_rgb = self.predict_from_bytes(image_bytes)
                logger.info("Analyzed image from bytes")
            else:
                raise ValueError("Either image_path or image_bytes must be provided")
            
            # Add status
            result['status'] = 'success'
            
            # Generate visualization if requested
            if generate_plot:
                result['visualization'] = self.generate_visualization(image_rgb, result)
            
            # Add interpretation
            if result['weapon_type'] == 'Gun':
                interpretation = (
                    "High/medium velocity impact spatter detected. "
                    "Characteristics: Fine mist, small circular droplets, "
                    "uniform distribution typical of gunshot wounds."
                )
            else:
                interpretation = (
                    "Cast-off or impact spatter detected. "
                    "Characteristics: Larger elongated droplets, directional "
                    "pattern typical of blunt/sharp force trauma."
                )
            
            result['interpretation'] = interpretation
            
            logger.info(f"Classification: {result['weapon_type']} (Confidence: {result['confidence']:.2%})")
            return result
            
        except Exception as e:
            logger.error(f"Error in weapon classification: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to classify weapon type'
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
        
        weapon_type = result['weapon_type']
        confidence = result['confidence']
        probs = result['probabilities']
        
        report_lines = [
            "=" * 70,
            "WEAPON TYPE CLASSIFICATION REPORT",
            "Blood Pattern Analysis - Deep Learning Classification",
            "=" * 70,
            "",
            "CLASSIFICATION RESULT:",
            f"  Weapon Type: {weapon_type}",
            f"  Confidence: {confidence:.2%}",
            "",
            "-" * 70,
            "DETAILED PROBABILITIES:",
            "-" * 70,
            f"  🔫 Gun (High-velocity Impact):  {probs['Gun']:.2%}",
            f"  🗡️  Melee (Cast-off/Impact):    {probs['Melee']:.2%}",
            "",
            "-" * 70,
            "INTERPRETATION:",
            "-" * 70,
            f"  {result.get('interpretation', 'No interpretation available')}",
            "",
        ]
        
        # Add confidence assessment
        if confidence >= 0.90:
            report_lines.append("  Confidence Level: VERY HIGH")
            report_lines.append("  The classification is highly reliable.")
        elif confidence >= 0.75:
            report_lines.append("  Confidence Level: HIGH")
            report_lines.append("  The classification is reliable.")
        elif confidence >= 0.60:
            report_lines.append("  Confidence Level: MODERATE")
            report_lines.append("  The classification is reasonably confident.")
        else:
            report_lines.append("  Confidence Level: LOW")
            report_lines.append("  The classification is uncertain. Manual review recommended.")
        
        report_lines.extend([
            "",
            "=" * 70,
            "FORENSIC NOTES:",
            "=" * 70,
        ])
        
        if weapon_type == 'Gun':
            report_lines.extend([
                "  Typical Gun Pattern Characteristics:",
                "  - High velocity impact creates fine mist",
                "  - Small, circular droplets (< 1mm diameter)",
                "  - Radial distribution from point of impact",
                "  - May include back spatter and forward spatter",
                "  - Usually indicates gunshot wound",
            ])
        else:
            report_lines.extend([
                "  Typical Melee Pattern Characteristics:",
                "  - Medium to low velocity impact",
                "  - Larger, elongated droplets (> 1mm)",
                "  - Directional cast-off patterns",
                "  - May show swing patterns",
                "  - Usually indicates blunt or sharp force trauma",
            ])
        
        report_lines.extend([
            "",
            "=" * 70,
            "DISCLAIMER:",
            "  This is an AI-assisted classification tool. Results should be",
            "  verified by qualified forensic experts. Not for sole use in",
            "  legal proceedings without professional confirmation.",
            "=" * 70
        ])
        
        return "\n".join(report_lines)


# Example usage and testing
if __name__ == "__main__":
    # Path to your trained model
    MODEL_PATH = r'C:\Users\User\Desktop\research_nsbm\data\my_weapon_model_v2.h5'
    IMAGE_PATH = r'C:\Users\User\Desktop\research_nsbm\data\test\image5.png'
    
    try:
        # Initialize classifier with your trained model
        classifier = WeaponTypeClassifier(model_path=MODEL_PATH)
        
        # Analyze image
        result = classifier.analyze(image_path=IMAGE_PATH, generate_plot=True)
        
        # Print report
        report = classifier.generate_report(result)
        print(report)
        
        # Save visualization if generated
        if result.get('visualization'):
            with open('weapon_classification_result.png', 'wb') as f:
                f.write(base64.b64decode(result['visualization']))
            print("\nVisualization saved to: weapon_classification_result.png")
            
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
