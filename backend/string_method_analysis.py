"""
String Method Analysis Module - Forensic Bloodstain Pattern Analysis
Calculates point of origin using classical string method for blood spatter analysis
"""
import cv2
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend for server environments
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse, Circle
from matplotlib.gridspec import GridSpec
from sklearn.cluster import DBSCAN
import warnings
import io
import base64
from typing import Dict, Any, Tuple, List, Optional
import logging

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StringMethodAnalyzer:
    """
    String Method Analyzer for determining point of origin in bloodstain patterns.
    
    Uses classical forensic techniques:
    1. Detect blood droplets
    2. Analyze droplet geometry (elongation, impact angle)
    3. Trace backward trajectories
    4. Find intersection point (origin)
    """
    
    def __init__(self, min_droplet_area: int = 30, max_droplet_area: int = 5000):
        """
        Initialize the String Method Analyzer
        
        Args:
            min_droplet_area: Minimum area for valid droplet (pixels)
            max_droplet_area: Maximum area for valid droplet (pixels)
        """
        self.min_droplet_area = min_droplet_area
        self.max_droplet_area = max_droplet_area
        self.droplets = []
        self.traced_lines = []
        self.intersections = []
        self.origin = None
        logger.info(f"StringMethodAnalyzer initialized (area range: {min_droplet_area}-{max_droplet_area})")
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for droplet detection
        
        Args:
            image: Input image (BGR or grayscale)
            
        Returns:
            Preprocessed grayscale image
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Enhance contrast
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Reduce noise
        blurred = cv2.GaussianBlur(enhanced, (5, 5), 0)
        
        return blurred
    
    def detect_blood_droplets(
        self, 
        image: np.ndarray, 
        threshold_value: Optional[int] = None
    ) -> Tuple[List, np.ndarray]:
        """
        Detect blood droplets in image
        
        Args:
            image: Input image
            threshold_value: Manual threshold value (optional)
            
        Returns:
            Tuple of (valid_contours, binary_image)
        """
        preprocessed = self.preprocess_image(image)
        
        # Apply thresholding
        if threshold_value is None:
            binary = cv2.adaptiveThreshold(
                preprocessed, 255,
                cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                cv2.THRESH_BINARY_INV, 11, 2
            )
        else:
            _, binary = cv2.threshold(
                preprocessed, threshold_value, 255,
                cv2.THRESH_BINARY_INV
            )
        
        # Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        binary = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Filter by area
        valid_contours = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if self.min_droplet_area < area < self.max_droplet_area:
                valid_contours.append(contour)
        
        logger.info(f"Detected {len(valid_contours)} valid droplets")
        return valid_contours, binary
    
    def find_droplet_tail_direction(
        self, 
        contour: np.ndarray, 
        center: Tuple[float, float], 
        angle: float, 
        length: float
    ) -> Tuple[float, float]:
        """
        Determine which end of the ellipse is the tail (direction of origin)
        
        Args:
            contour: Droplet contour
            center: Ellipse center
            angle: Ellipse angle
            length: Ellipse length
            
        Returns:
            Direction vector (dx, dy) pointing toward origin
        """
        angle_rad = np.radians(angle)
        dx = np.cos(angle_rad)
        dy = np.sin(angle_rad)
        
        # Calculate both ends of the major axis
        end1 = np.array([center[0] + length/2 * dx, center[1] + length/2 * dy])
        end2 = np.array([center[0] - length/2 * dx, center[1] - length/2 * dy])
        
        # Get contour points
        contour_points = contour.reshape(-1, 2)
        
        # Calculate distances to both ends
        dist_to_end1 = np.array([np.linalg.norm(pt - end1) for pt in contour_points])
        dist_to_end2 = np.array([np.linalg.norm(pt - end2) for pt in contour_points])
        
        # Count points near each end
        threshold_dist = length * 0.3
        near_end1 = np.sum(dist_to_end1 < threshold_dist)
        near_end2 = np.sum(dist_to_end2 < threshold_dist)
        
        # Calculate average distances
        avg_dist_end1 = np.mean(dist_to_end1)
        avg_dist_end2 = np.mean(dist_to_end2)
        
        # Score each end (tail has more mass nearby)
        score_end1 = near_end1 * 0.6 + (1.0 / (avg_dist_end1 + 1)) * 0.4
        score_end2 = near_end2 * 0.6 + (1.0 / (avg_dist_end2 + 1)) * 0.4
        
        # Choose direction toward the end with less mass (tail points away from mass)
        if score_end1 < score_end2:
            return -dx, -dy
        else:
            return dx, dy
    
    def analyze_droplet_geometry(self, contour: np.ndarray) -> Optional[Dict[str, Any]]:
        """
        Analyze geometric properties of a droplet
        
        Args:
            contour: Droplet contour
            
        Returns:
            Dictionary of droplet properties or None if invalid
        """
        if len(contour) < 5:
            return None
        
        try:
            ellipse = cv2.fitEllipse(contour)
        except:
            return None
        
        (center_x, center_y), (axis1, axis2), angle = ellipse
        
        # Ensure length > width
        if axis1 > axis2:
            width, length = axis2, axis1
            angle = (angle + 90) % 180
        else:
            width, length = axis1, axis2
        
        # Calculate elongation
        if width > 0:
            elongation = length / width
        else:
            elongation = 1.0
        
        # Calculate impact angle using width/length ratio
        if length > 0 and width <= length:
            aspect_ratio = width / length
            impact_angle_rad = np.arcsin(min(aspect_ratio, 1.0))
            impact_angle_deg = np.degrees(impact_angle_rad)
        else:
            impact_angle_deg = 90.0
        
        return {
            'center': (center_x, center_y),
            'width': width,
            'length': length,
            'angle': angle,
            'impact_angle': impact_angle_deg,
            'elongation': elongation,
            'area': cv2.contourArea(contour),
            'contour': contour
        }
    
    def select_useful_droplets(
        self, 
        contours: List[np.ndarray], 
        min_elongation: float = 1.3
    ) -> List[Dict[str, Any]]:
        """
        Select elongated droplets useful for trajectory analysis
        
        Args:
            contours: List of droplet contours
            min_elongation: Minimum elongation ratio
            
        Returns:
            List of useful droplet data
        """
        useful_droplets = []
        
        for contour in contours:
            droplet_data = self.analyze_droplet_geometry(contour)
            
            if droplet_data is None:
                continue
            
            if droplet_data['elongation'] >= min_elongation:
                useful_droplets.append(droplet_data)
        
        # Sort by elongation (most elongated first)
        useful_droplets.sort(key=lambda x: x['elongation'], reverse=True)
        
        logger.info(f"Selected {len(useful_droplets)} elongated droplets (elongation ≥ {min_elongation})")
        
        self.droplets = useful_droplets
        return useful_droplets
    
    def trace_backward_line(
        self, 
        droplet: Dict[str, Any], 
        line_length: int = 2000
    ) -> Dict[str, Any]:
        """
        Trace a line backward from droplet toward origin
        
        Args:
            droplet: Droplet data dictionary
            line_length: Length of traced line
            
        Returns:
            Line data dictionary
        """
        center = droplet['center']
        angle = droplet['angle']
        length = droplet['length']
        contour = droplet['contour']
        
        # Determine tail direction
        dx, dy = self.find_droplet_tail_direction(contour, center, angle, length)
        
        # Normalize direction vector
        magnitude = np.sqrt(dx**2 + dy**2)
        if magnitude > 0:
            dx, dy = dx / magnitude, dy / magnitude
        
        # Calculate line endpoints
        start_point = center
        end_x = center[0] + line_length * dx
        end_y = center[1] + line_length * dy
        end_point = (end_x, end_y)
        
        backward_angle = np.degrees(np.arctan2(dy, dx))
        
        return {
            'start': start_point,
            'end': end_point,
            'direction': (dx, dy),
            'backward_angle': backward_angle,
            'droplet': droplet
        }
    
    def trace_all_droplets(self, line_length: int = 2000) -> List[Dict[str, Any]]:
        """
        Trace backward lines for all droplets
        
        Args:
            line_length: Length of each traced line
            
        Returns:
            List of traced line data
        """
        self.traced_lines = []
        
        for droplet in self.droplets:
            line = self.trace_backward_line(droplet, line_length)
            self.traced_lines.append(line)
        
        logger.info(f"Traced {len(self.traced_lines)} backward lines")
        return self.traced_lines
    
    def calculate_line_intersection(
        self, 
        line1: Dict[str, Any], 
        line2: Dict[str, Any]
    ) -> Optional[np.ndarray]:
        """
        Calculate intersection point of two lines
        
        Args:
            line1: First line data
            line2: Second line data
            
        Returns:
            Intersection point or None if parallel
        """
        p1 = np.array(line1['start'])
        d1 = np.array(line1['direction'])
        
        p2 = np.array(line2['start'])
        d2 = np.array(line2['direction'])
        
        try:
            # Solve: p1 + t*d1 = p2 + s*d2
            A = np.column_stack([d1, -d2])
            b = p2 - p1
            
            params = np.linalg.solve(A, b)
            t = params[0]
            
            intersection = p1 + t * d1
            
            # Only accept if intersection is in forward direction
            if t > 0:
                return intersection
            
        except np.linalg.LinAlgError:
            pass
        
        return None
    
    def find_all_intersections(self) -> Optional[np.ndarray]:
        """
        Find all pairwise line intersections
        
        Returns:
            Array of intersection points or None
        """
        self.intersections = []
        
        n = len(self.traced_lines)
        
        for i in range(n):
            for j in range(i + 1, n):
                intersection = self.calculate_line_intersection(
                    self.traced_lines[i],
                    self.traced_lines[j]
                )
                
                if intersection is not None:
                    self.intersections.append(intersection)
        
        logger.info(f"Found {len(self.intersections)} intersection points")
        
        return np.array(self.intersections) if self.intersections else None
    
    def find_origin_by_clustering(
        self, 
        intersections: np.ndarray
    ) -> Optional[np.ndarray]:
        """
        Find point of origin using DBSCAN clustering
        
        Args:
            intersections: Array of intersection points
            
        Returns:
            Origin point or None
        """
        if intersections is None or len(intersections) < 3:
            logger.warning("Too few intersections for clustering")
            if intersections is not None and len(intersections) > 0:
                return np.median(intersections, axis=0)
            return None
        
        # Cluster intersections
        clustering = DBSCAN(eps=100, min_samples=3).fit(intersections)
        labels = clustering.labels_
        
        unique_labels = [l for l in set(labels) if l != -1]
        
        if len(unique_labels) == 0:
            logger.info("No clusters found, using median")
            return np.median(intersections, axis=0)
        
        # Find largest cluster
        cluster_sizes = [(label, np.sum(labels == label)) for label in unique_labels]
        largest_cluster_label = max(cluster_sizes, key=lambda x: x[1])[0]
        
        # Calculate centroid of largest cluster
        cluster_points = intersections[labels == largest_cluster_label]
        origin = np.mean(cluster_points, axis=0)
        
        logger.info(f"Origin calculated from {len(cluster_points)} intersection points in largest cluster")
        
        return origin
    
    def calculate_point_of_origin(self) -> Optional[np.ndarray]:
        """
        Main method to calculate point of origin
        
        Returns:
            Origin coordinates or None
        """
        # Trace all droplet trajectories
        self.trace_all_droplets()
        
        if len(self.traced_lines) < 2:
            logger.error("Need at least 2 droplets for origin calculation")
            return None
        
        # Find all line intersections
        intersections = self.find_all_intersections()
        
        if intersections is None or len(intersections) == 0:
            logger.error("No intersections found")
            return None
        
        # Cluster intersections to find origin
        self.origin = self.find_origin_by_clustering(intersections)
        
        if self.origin is not None:
            logger.info(f"Point of Origin: ({self.origin[0]:.1f}, {self.origin[1]:.1f})")
        
        return self.origin
    
    def generate_visualization(
        self, 
        image: np.ndarray, 
        binary: np.ndarray
    ) -> str:
        """
        Generate string method visualization showing trajectory lines converging at origin
        
        Args:
            image: Original image
            binary: Binary threshold image
            
        Returns:
            Base64 encoded PNG image
        """
        # Create single large figure for string method visualization only
        fig, ax = plt.subplots(1, 1, figsize=(12, 12), facecolor='#1a1a1a')
        
        # Display base image
        if len(image.shape) == 2:
            ax.imshow(image, cmap='gray')
        else:
            ax.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
        
        img_height, img_width = image.shape[:2]
        
        # Draw traced lines
        for i, line in enumerate(self.traced_lines):
            start = line['start']
            direction = line['direction']
            
            if self.origin is not None:
                end = self.origin
            else:
                max_length = max(img_width, img_height)
                end = (start[0] + max_length * direction[0],
                      start[1] + max_length * direction[1])
            
            ax.plot([start[0], end[0]], [start[1], end[1]], 
                   'b-', alpha=0.4, linewidth=1.5)
        
        # Draw droplets with numbers
        for i, droplet in enumerate(self.droplets):
            center = droplet['center']
            
            ellipse = Ellipse(center, droplet['width'], droplet['length'],
                            angle=droplet['angle'],
                            fill=False, edgecolor='green', linewidth=2)
            ax.add_patch(ellipse)
            
            # Draw backward direction arrow
            if i < len(self.traced_lines):
                line = self.traced_lines[i]
                dx, dy = line['direction']
                arrow_length = min(droplet['length'] * 1.5, 50)
                arrow_end = (center[0] + arrow_length * dx, 
                           center[1] + arrow_length * dy)
                
                ax.annotate('', xy=arrow_end, xytext=center,
                          arrowprops=dict(arrowstyle='->', color='orange', 
                                        lw=2, alpha=0.8))
            
            # Add droplet number labels
            ax.text(center[0], center[1], f"{i+1}", 
                   color='white', fontsize=10, fontweight='bold',
                   ha='center', va='center',
                   bbox=dict(boxstyle='circle', facecolor='red', alpha=0.7))
        
        # Draw intersection points
        if len(self.intersections) > 0:
            intersections = np.array(self.intersections)
            margin = max(img_width, img_height) * 0.5
            valid_mask = (
                (intersections[:, 0] > -margin) & 
                (intersections[:, 0] < img_width + margin) & 
                (intersections[:, 1] > -margin) & 
                (intersections[:, 1] < img_height + margin)
            )
            
            valid_intersections = intersections[valid_mask]
            
            if len(valid_intersections) > 0:
                ax.scatter(valid_intersections[:, 0], valid_intersections[:, 1], 
                          c='yellow', s=50, alpha=0.7, marker='x', linewidths=3)
        
        # Draw point of origin with crosshairs and circles
        if self.origin is not None:
            origin = self.origin
            
            # Large star marker for origin
            ax.plot(origin[0], origin[1], 'r*', markersize=40,
                   markeredgecolor='yellow', markeredgewidth=3, zorder=10)
            
            # Concentric circles around origin
            for radius in [50, 100, 150]:
                circle = Circle(origin, radius, fill=False, 
                              edgecolor='red', linewidth=2, 
                              linestyle='--', alpha=0.5)
                ax.add_patch(circle)
            
            # Crosshairs at origin
            ax.plot([origin[0]-80, origin[0]+80], [origin[1], origin[1]], 
                   'r-', linewidth=2, alpha=0.7)
            ax.plot([origin[0], origin[0]], [origin[1]-80, origin[1]+80], 
                   'r-', linewidth=2, alpha=0.7)
        
        # Set axis limits with margin
        margin = 200
        ax.set_xlim(-margin, img_width + margin)
        ax.set_ylim(img_height + margin, -margin)
        
        ax.set_title('String Method: Traced Lines Converging at Origin', 
                    fontsize=16, fontweight='bold', color='white')
        ax.grid(True, alpha=0.3, linestyle='--', color='white')
        ax.axis('on')
        ax.tick_params(colors='white')
        
        plt.tight_layout()
        
        # Save to bytes with high DPI for clarity
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
        min_elongation: float = 1.3,
        threshold: Optional[int] = None,
        generate_plot: bool = True
    ) -> Dict[str, Any]:
        """
        Main analysis method
        
        Args:
            image_path: Path to image file (optional)
            image_bytes: Image as bytes (optional)
            min_elongation: Minimum elongation for droplet selection
            threshold: Manual threshold value (optional)
            generate_plot: Whether to generate visualization
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            # Load image
            if image_path:
                image = cv2.imread(image_path)
                if image is None:
                    raise ValueError(f"Could not load image: {image_path}")
            elif image_bytes:
                nparr = np.frombuffer(image_bytes, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if image is None:
                    raise ValueError("Could not decode image from bytes")
            else:
                raise ValueError("Either image_path or image_bytes must be provided")
            
            logger.info(f"Analyzing image of size: {image.shape}")
            
            # Detect droplets
            contours, binary = self.detect_blood_droplets(image, threshold)
            
            # Select useful droplets
            useful_droplets = self.select_useful_droplets(contours, min_elongation)
            
            if len(useful_droplets) < 2:
                return {
                    'status': 'insufficient_data',
                    'message': 'Not enough elongated droplets found for analysis',
                    'droplets_found': len(useful_droplets),
                    'droplets_needed': 2
                }
            
            # Calculate point of origin
            origin = self.calculate_point_of_origin()
            
            if origin is None:
                return {
                    'status': 'error',
                    'message': 'Could not calculate point of origin'
                }
            
            # Calculate statistics
            impact_angles = [d['impact_angle'] for d in self.droplets]
            avg_angle = np.mean(impact_angles)
            
            # Generate visualization if requested
            plot_base64 = None
            if generate_plot:
                plot_base64 = self.generate_visualization(image, binary)
            
            # Compile results
            result = {
                'status': 'success',
                'origin': {
                    'x': float(self.origin[0]),
                    'y': float(self.origin[1]),
                    'coordinates': f"({self.origin[0]:.1f}, {self.origin[1]:.1f})"
                },
                'statistics': {
                    'droplets_analyzed': len(self.droplets),
                    'intersections_found': len(self.intersections),
                    'average_impact_angle': round(avg_angle, 1),
                    'min_impact_angle': round(min(impact_angles), 1),
                    'max_impact_angle': round(max(impact_angles), 1),
                    'angle_range': round(max(impact_angles) - min(impact_angles), 1)
                },
                'droplets': [
                    {
                        'id': i + 1,
                        'center': droplet['center'],
                        'area': round(droplet['area'], 1),
                        'length': round(droplet['length'], 1),
                        'width': round(droplet['width'], 1),
                        'elongation': round(droplet['elongation'], 2),
                        'impact_angle': round(droplet['impact_angle'], 1)
                    }
                    for i, droplet in enumerate(self.droplets[:10])  # Top 10
                ],
                'visualization': plot_base64
            }
            
            logger.info(f"Analysis complete: Origin at ({self.origin[0]:.1f}, {self.origin[1]:.1f})")
            return result
            
        except Exception as e:
            logger.error(f"Error in string method analysis: {str(e)}")
            return {
                'status': 'error',
                'error': str(e),
                'message': 'Failed to perform string method analysis'
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
        
        if result['status'] == 'insufficient_data':
            return f"Insufficient Data: {result.get('message', 'Not enough droplets')}"
        
        origin = result['origin']
        stats = result['statistics']
        
        report_lines = [
            "=" * 70,
            "STRING METHOD ANALYSIS REPORT",
            "Forensic Bloodstain Pattern Analysis - Point of Origin",
            "=" * 70,
            "",
            "POINT OF ORIGIN:",
            f"  Coordinates: {origin['coordinates']}",
            f"  X: {origin['x']:.1f} pixels",
            f"  Y: {origin['y']:.1f} pixels",
            "",
            "-" * 70,
            "ANALYSIS STATISTICS:",
            "-" * 70,
            f"  Droplets Analyzed: {stats['droplets_analyzed']}",
            f"  Intersection Points Found: {stats['intersections_found']}",
            f"  Average Impact Angle: {stats['average_impact_angle']}°",
            f"  Impact Angle Range: {stats['min_impact_angle']}° - {stats['max_impact_angle']}°",
            f"  Angle Spread: {stats['angle_range']}°",
            "",
            "-" * 70,
            "TOP DROPLETS (by elongation):",
            "-" * 70,
        ]
        
        for droplet in result['droplets']:
            report_lines.append(
                f"  #{droplet['id']:2d}: "
                f"Area={droplet['area']:6.1f}px², "
                f"Length={droplet['length']:5.1f}px, "
                f"Width={droplet['width']:5.1f}px, "
                f"Elongation={droplet['elongation']:.2f}, "
                f"Impact={droplet['impact_angle']:4.1f}°"
            )
        
        report_lines.extend([
            "",
            "=" * 70,
            "INTERPRETATION:",
            "=" * 70,
            "The string method has successfully determined the point of origin",
            "for the bloodstain pattern. This represents the approximate location",
            "in 2D space where the blood originated from.",
            "",
            "Key observations:",
        ])
        
        if stats['angle_range'] < 20:
            report_lines.append("  - Low angle variation suggests a single impact event")
        else:
            report_lines.append("  - High angle variation may indicate multiple impacts")
        
        if stats['average_impact_angle'] < 30:
            report_lines.append("  - Low impact angles suggest oblique/tangential impact")
        elif stats['average_impact_angle'] > 60:
            report_lines.append("  - High impact angles suggest perpendicular impact")
        else:
            report_lines.append("  - Moderate impact angles suggest angled impact")
        
        report_lines.extend([
            "",
            "=" * 70
        ])
        
        return "\n".join(report_lines)


# Example usage and testing
if __name__ == "__main__":
    analyzer = StringMethodAnalyzer()
    
    # Test with an image
    IMAGE_PATH = r'C:\Users\User\Desktop\research_nsbm\data\test\image18.png'
    
    try:
        result = analyzer.analyze(
            image_path=IMAGE_PATH, 
            min_elongation=1.2,
            generate_plot=True
        )
        
        # Print report
        report = analyzer.generate_report(result)
        print(report)
        
        # Save visualization if generated
        if result.get('visualization'):
            with open('string_method_result.png', 'wb') as f:
                f.write(base64.b64decode(result['visualization']))
            print("\nVisualization saved to: string_method_result.png")
            
    except Exception as e:
        print(f"Error: {str(e)}")
