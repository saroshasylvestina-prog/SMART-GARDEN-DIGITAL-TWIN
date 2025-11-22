"""
Plant Disease Detection Module
Scans plant images to identify diseases and provides solutions
"""
import os
import numpy as np
from datetime import datetime
from PIL import Image
import io
import base64

# Try to import machine learning libraries
try:
    import tensorflow as tf
    from tensorflow import keras
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("[PLANT DISEASE] TensorFlow not available, using rule-based detection")

class PlantDiseaseDetector:
    """Plant disease detection and health analysis system"""
    
    def __init__(self):
        """Initialize the disease detector"""
        self.disease_database = self._load_disease_database()
        self.model = None
        self.model_loaded = False
        
        # Try to load a pre-trained model if available
        if ML_AVAILABLE:
            self._try_load_model()
        
        print("[PLANT DISEASE] Detector initialized")
    
    def _load_disease_database(self):
        """Load database of plant diseases with symptoms and solutions"""
        return {
            'healthy': {
                'name': 'Healthy Plant',
                'confidence': 0.0,
                'symptoms': ['Green leaves', 'No spots', 'Normal growth'],
                'solutions': [
                    'Continue current care routine',
                    'Maintain proper watering schedule',
                    'Ensure adequate sunlight',
                    'Monitor soil moisture levels'
                ],
                'severity': 'none',
                'treatment': 'No treatment needed'
            },
            'leaf_spot': {
                'name': 'Leaf Spot Disease',
                'confidence': 0.0,
                'symptoms': [
                    'Brown or black spots on leaves',
                    'Yellowing around spots',
                    'Leaves may drop prematurely'
                ],
                'solutions': [
                    'Remove affected leaves immediately',
                    'Improve air circulation around plant',
                    'Avoid overhead watering',
                    'Apply fungicide (copper-based)',
                    'Water at base of plant, not on leaves',
                    'Ensure proper drainage'
                ],
                'severity': 'moderate',
                'treatment': 'Fungicide application and improved care'
            },
            'powdery_mildew': {
                'name': 'Powdery Mildew',
                'confidence': 0.0,
                'symptoms': [
                    'White powdery coating on leaves',
                    'Leaves may curl or distort',
                    'Stunted growth'
                ],
                'solutions': [
                    'Increase air circulation',
                    'Reduce humidity around plant',
                    'Apply neem oil or baking soda solution',
                    'Remove severely affected leaves',
                    'Water early in the day',
                    'Space plants properly for airflow'
                ],
                'severity': 'moderate',
                'treatment': 'Organic fungicide and environmental control'
            },
            'root_rot': {
                'name': 'Root Rot',
                'confidence': 0.0,
                'symptoms': [
                    'Wilting despite adequate water',
                    'Yellowing leaves',
                    'Brown, mushy roots',
                    'Foul odor from soil'
                ],
                'solutions': [
                    'Stop watering immediately',
                    'Remove plant from pot',
                    'Trim away rotten roots',
                    'Repot in fresh, well-draining soil',
                    'Improve drainage',
                    'Reduce watering frequency',
                    'Use fungicide for severe cases'
                ],
                'severity': 'severe',
                'treatment': 'Immediate repotting and root treatment'
            },
            'aphids': {
                'name': 'Aphid Infestation',
                'type': 'insect',
                'confidence': 0.0,
                'symptoms': [
                    'Small green, black, or white insects on leaves/stems',
                    'Sticky residue (honeydew) on leaves',
                    'Curled or distorted leaves',
                    'Ants on plant (attracted to honeydew)',
                    'Clusters of tiny insects on new growth'
                ],
                'solutions': [
                    'Spray with strong water stream to dislodge insects',
                    'Apply insecticidal soap (spray every 3-5 days)',
                    'Use neem oil spray (mix 2 tsp neem oil with 1 liter water)',
                    'Introduce beneficial insects (ladybugs, lacewings)',
                    'Remove heavily infested leaves',
                    'Apply horticultural oil',
                    'Use yellow sticky traps',
                    'Prune affected areas'
                ],
                'severity': 'moderate',
                'treatment': 'Insecticide application and manual removal'
            },
            'spider_mites': {
                'name': 'Spider Mite Infestation',
                'type': 'insect',
                'confidence': 0.0,
                'symptoms': [
                    'Fine webbing on leaves and stems',
                    'Yellow stippling or speckling on leaves',
                    'Leaves may drop prematurely',
                    'Tiny moving dots on underside of leaves',
                    'Bronze or yellow discoloration',
                    'Dry, dusty appearance'
                ],
                'solutions': [
                    'Increase humidity around plant (mites hate moisture)',
                    'Spray with water regularly (daily if possible)',
                    'Apply miticide or neem oil',
                    'Isolate affected plant immediately',
                    'Wipe leaves with damp cloth',
                    'Use predatory mites for biological control',
                    'Apply insecticidal soap',
                    'Keep plant well-watered'
                ],
                'severity': 'moderate',
                'treatment': 'Miticide application and humidity control'
            },
            'whiteflies': {
                'name': 'Whitefly Infestation',
                'type': 'insect',
                'confidence': 0.0,
                'symptoms': [
                    'Tiny white flying insects when plant is disturbed',
                    'Sticky honeydew on leaves',
                    'Yellowing leaves',
                    'Sooty mold (black coating) on leaves',
                    'Stunted growth',
                    'White eggs on underside of leaves'
                ],
                'solutions': [
                    'Use yellow sticky traps to catch adults',
                    'Spray with insecticidal soap',
                    'Apply neem oil spray',
                    'Introduce beneficial insects (ladybugs, parasitic wasps)',
                    'Vacuum adults with handheld vacuum',
                    'Remove heavily infested leaves',
                    'Apply horticultural oil',
                    'Use reflective mulch to deter them'
                ],
                'severity': 'moderate',
                'treatment': 'Insecticide and trapping'
            },
            'mealybugs': {
                'name': 'Mealybug Infestation',
                'type': 'insect',
                'confidence': 0.0,
                'symptoms': [
                    'White cottony masses on stems and leaves',
                    'Sticky honeydew on leaves',
                    'Yellowing or wilting leaves',
                    'Ants attracted to honeydew',
                    'Sooty mold development',
                    'White waxy coating on plant'
                ],
                'solutions': [
                    'Remove with cotton swab dipped in alcohol',
                    'Spray with insecticidal soap',
                    'Apply neem oil spray',
                    'Use systemic insecticide for severe cases',
                    'Introduce beneficial insects (ladybugs, lacewings)',
                    'Prune heavily infested areas',
                    'Isolate affected plant',
                    'Wipe leaves with alcohol-soaked cloth'
                ],
                'severity': 'moderate',
                'treatment': 'Manual removal and insecticide'
            },
            'scale_insects': {
                'name': 'Scale Insect Infestation',
                'type': 'insect',
                'confidence': 0.0,
                'symptoms': [
                    'Brown, tan, or white bumps on stems and leaves',
                    'Sticky honeydew on leaves',
                    'Yellowing leaves',
                    'Stunted growth',
                    'Sooty mold on leaves',
                    'Hard shell-like covering on insects'
                ],
                'solutions': [
                    'Scrape off with fingernail or soft brush',
                    'Apply horticultural oil (smothers them)',
                    'Use insecticidal soap',
                    'Apply neem oil spray',
                    'Prune heavily infested branches',
                    'Introduce beneficial insects (ladybugs)',
                    'Use systemic insecticide',
                    'Wipe with alcohol-soaked cloth'
                ],
                'severity': 'moderate',
                'treatment': 'Manual removal and oil treatment'
            },
            'thrips': {
                'name': 'Thrip Infestation',
                'type': 'insect',
                'confidence': 0.0,
                'symptoms': [
                    'Tiny black or yellow insects',
                    'Silvery streaks or patches on leaves',
                    'Distorted or curled leaves',
                    'Black specks (insect waste) on leaves',
                    'Flower buds fail to open',
                    'Stunted growth'
                ],
                'solutions': [
                    'Use blue sticky traps',
                    'Spray with insecticidal soap',
                    'Apply neem oil spray',
                    'Introduce beneficial insects (predatory mites)',
                    'Remove and destroy affected leaves',
                    'Increase humidity',
                    'Apply spinosad-based insecticide',
                    'Prune affected areas'
                ],
                'severity': 'moderate',
                'treatment': 'Insecticide and trapping'
            },
            'caterpillars': {
                'name': 'Caterpillar Infestation',
                'type': 'insect',
                'confidence': 0.0,
                'symptoms': [
                    'Visible caterpillars on plant',
                    'Holes in leaves',
                    'Chewed leaf edges',
                    'Droppings (frass) on leaves',
                    'Skeletonized leaves',
                    'Missing foliage'
                ],
                'solutions': [
                    'Handpick caterpillars (wear gloves)',
                    'Apply Bt (Bacillus thuringiensis) insecticide',
                    'Use neem oil spray',
                    'Introduce beneficial insects (parasitic wasps)',
                    'Remove affected leaves',
                    'Apply spinosad-based insecticide',
                    'Use row covers to prevent egg laying',
                    'Encourage birds in garden area'
                ],
                'severity': 'moderate',
                'treatment': 'Manual removal and biological control'
            },
            'fungus_gnats': {
                'name': 'Fungus Gnat Infestation',
                'type': 'insect',
                'confidence': 0.0,
                'symptoms': [
                    'Small black flies around plant',
                    'Larvae in soil (white with black heads)',
                    'Yellowing leaves',
                    'Stunted growth',
                    'Root damage',
                    'Flies emerge when watering'
                ],
                'solutions': [
                    'Let soil dry between waterings',
                    'Use yellow sticky traps',
                    'Apply beneficial nematodes to soil',
                    'Use BTI (Bacillus thuringiensis israelensis)',
                    'Cover soil with sand or diatomaceous earth',
                    'Remove top layer of soil',
                    'Avoid overwatering',
                    'Use hydrogen peroxide solution (1:4 ratio)'
                ],
                'severity': 'mild',
                'treatment': 'Soil treatment and moisture control'
            },
            'nutrient_deficiency': {
                'name': 'Nutrient Deficiency',
                'confidence': 0.0,
                'symptoms': [
                    'Yellowing leaves (chlorosis)',
                    'Stunted growth',
                    'Poor flowering/fruiting',
                    'Leaf discoloration'
                ],
                'solutions': [
                    'Test soil pH and nutrient levels',
                    'Apply balanced fertilizer',
                    'Add organic compost',
                    'Ensure proper soil drainage',
                    'Follow fertilizer schedule',
                    'Consider foliar feeding'
                ],
                'severity': 'mild',
                'treatment': 'Fertilization and soil amendment'
            },
            'overwatering': {
                'name': 'Overwatering',
                'confidence': 0.0,
                'symptoms': [
                    'Yellowing lower leaves',
                    'Wilting despite wet soil',
                    'Soft, mushy stems',
                    'Mold or algae on soil surface'
                ],
                'solutions': [
                    'Reduce watering frequency',
                    'Improve soil drainage',
                    'Check for root rot',
                    'Allow soil to dry between waterings',
                    'Use well-draining potting mix',
                    'Ensure pots have drainage holes'
                ],
                'severity': 'moderate',
                'treatment': 'Adjust watering schedule and improve drainage'
            },
            'underwatering': {
                'name': 'Underwatering',
                'confidence': 0.0,
                'symptoms': [
                    'Dry, crispy leaves',
                    'Wilting',
                    'Brown leaf edges',
                    'Soil pulling away from pot edges'
                ],
                'solutions': [
                    'Increase watering frequency',
                    'Water thoroughly until water drains',
                    'Check soil moisture regularly',
                    'Consider self-watering system',
                    'Mulch to retain moisture',
                    'Water early morning or evening'
                ],
                'severity': 'mild',
                'treatment': 'Increase watering and monitor soil moisture'
            },
            'sunburn': {
                'name': 'Sunburn / Light Stress',
                'confidence': 0.0,
                'symptoms': [
                    'Brown or white patches on leaves',
                    'Crispy, dry leaf edges',
                    'Leaves facing sun most affected',
                    'Bleaching of leaf color'
                ],
                'solutions': [
                    'Move plant to shadier location',
                    'Provide filtered light',
                    'Gradually acclimate to brighter light',
                    'Use shade cloth if needed',
                    'Water more frequently in hot weather',
                    'Avoid direct midday sun'
                ],
                'severity': 'mild',
                'treatment': 'Relocate to appropriate light conditions'
            }
        }
    
    def _try_load_model(self):
        """Try to load a pre-trained model if available"""
        model_path = 'plant_disease_model.h5'
        if os.path.exists(model_path):
            try:
                self.model = keras.models.load_model(model_path)
                self.model_loaded = True
                print("[PLANT DISEASE] Pre-trained model loaded")
            except Exception as e:
                print(f"[PLANT DISEASE] Could not load model: {e}")
                self.model_loaded = False
        else:
            print("[PLANT DISEASE] No pre-trained model found, using rule-based detection")
    
    def preprocess_image(self, image_data):
        """
        Preprocess image for analysis
        
        Args:
            image_data: Image file data (bytes or PIL Image)
        
        Returns:
            Processed image array
        """
        try:
            # Convert to PIL Image if needed
            if isinstance(image_data, bytes):
                image = Image.open(io.BytesIO(image_data))
            elif isinstance(image_data, str):
                # Base64 encoded string
                if image_data.startswith('data:image'):
                    image_data = image_data.split(',')[1]
                image = Image.open(io.BytesIO(base64.b64decode(image_data)))
            else:
                image = image_data
            
            # Convert to RGB if needed
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize for analysis (if using ML model)
            if self.model_loaded:
                image = image.resize((224, 224))
                img_array = np.array(image) / 255.0
                img_array = np.expand_dims(img_array, axis=0)
                return img_array, image
            else:
                return None, image
                
        except Exception as e:
            print(f"[PLANT DISEASE] Image preprocessing error: {e}")
            return None, None
    
    def analyze_image_features(self, image):
        """
        Analyze image for disease indicators using rule-based approach
        
        Args:
            image: PIL Image object
        
        Returns:
            Dictionary with detected features
        """
        if image is None:
            return {}
        
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Basic color analysis
            avg_color = np.mean(img_array, axis=(0, 1))
            
            # Detect yellowing (nutrient deficiency, overwatering)
            yellow_threshold = 180
            yellow_pixels = np.sum((img_array[:, :, 0] > yellow_threshold) & 
                                  (img_array[:, :, 1] > yellow_threshold) & 
                                  (img_array[:, :, 2] < 150))
            yellow_ratio = yellow_pixels / (img_array.shape[0] * img_array.shape[1])
            
            # Detect brown spots (leaf spot, sunburn)
            brown_pixels = np.sum((img_array[:, :, 0] < 150) & 
                                (img_array[:, :, 1] < 100) & 
                                (img_array[:, :, 2] < 100))
            brown_ratio = brown_pixels / (img_array.shape[0] * img_array.shape[1])
            
            # Detect white areas (powdery mildew, sunburn)
            white_pixels = np.sum((img_array[:, :, 0] > 200) & 
                                (img_array[:, :, 1] > 200) & 
                                (img_array[:, :, 2] > 200))
            white_ratio = white_pixels / (img_array.shape[0] * img_array.shape[1])
            
            # Detect dark areas (root rot, severe disease)
            dark_pixels = np.sum(np.mean(img_array, axis=2) < 50)
            dark_ratio = dark_pixels / (img_array.shape[0] * img_array.shape[1])
            
            # Detect small dark spots (potential insects)
            # Look for small clusters of dark pixels
            gray = np.mean(img_array, axis=2)
            small_dark_spots = np.sum((gray > 30) & (gray < 100))
            small_spots_ratio = small_dark_spots / (img_array.shape[0] * img_array.shape[1])
            
            # Detect white cottony masses (mealybugs, whiteflies)
            # Bright white areas that aren't uniform
            bright_white = np.sum((img_array[:, :, 0] > 240) & 
                                (img_array[:, :, 1] > 240) & 
                                (img_array[:, :, 2] > 240))
            bright_white_ratio = bright_white / (img_array.shape[0] * img_array.shape[1])
            
            # Detect holes/irregular patterns (caterpillar damage)
            # Look for areas with high contrast edges
            try:
                # Calculate edge detection for hole detection using numpy
                gray_float = gray.astype(float)
                grad_x = np.gradient(gray_float, axis=1)
                grad_y = np.gradient(gray_float, axis=0)
                edges = np.abs(grad_x) + np.abs(grad_y)
                high_contrast = np.sum(edges > 50)
                edge_ratio = high_contrast / (img_array.shape[0] * img_array.shape[1])
            except:
                edge_ratio = 0
            
            # Detect sticky/shiny areas (honeydew from insects)
            # Look for areas with unusual brightness patterns
            brightness_variance = np.var(gray)
            
            return {
                'yellow_ratio': yellow_ratio,
                'brown_ratio': brown_ratio,
                'white_ratio': white_ratio,
                'dark_ratio': dark_ratio,
                'small_spots_ratio': small_spots_ratio,
                'bright_white_ratio': bright_white_ratio,
                'edge_ratio': edge_ratio,
                'brightness_variance': brightness_variance,
                'avg_color': avg_color.tolist()
            }
            
        except Exception as e:
            print(f"[PLANT DISEASE] Feature analysis error: {e}")
            return {}
    
    def detect_disease(self, image_data):
        """
        Detect plant disease from image
        
        Args:
            image_data: Image file data (bytes, PIL Image, or base64 string)
        
        Returns:
            Dictionary with detection results
        """
        try:
            # Preprocess image
            processed_img, original_img = self.preprocess_image(image_data)
            
            if original_img is None:
                return {
                    'success': False,
                    'error': 'Could not process image'
                }
            
            # Use ML model if available
            if self.model_loaded and processed_img is not None:
                predictions = self.model.predict(processed_img, verbose=0)
                # Map predictions to diseases (would need to match model output)
                # For now, fall back to rule-based
                pass
            
            # Rule-based detection
            features = self.analyze_image_features(original_img)
            
            # Determine disease based on features
            detected_diseases = []
            
            # Check for various diseases based on image analysis
            if features.get('white_ratio', 0) > 0.15:
                detected_diseases.append(('powdery_mildew', 0.75))
            
            if features.get('brown_ratio', 0) > 0.10:
                detected_diseases.append(('leaf_spot', 0.70))
            
            if features.get('yellow_ratio', 0) > 0.20:
                # Could be multiple causes
                detected_diseases.append(('nutrient_deficiency', 0.65))
                detected_diseases.append(('overwatering', 0.60))
            
            if features.get('dark_ratio', 0) > 0.15:
                detected_diseases.append(('root_rot', 0.70))
            
            # Insect Detection Logic
            # Detect white cottony masses (mealybugs)
            if features.get('bright_white_ratio', 0) > 0.05 and features.get('bright_white_ratio', 0) < 0.20:
                detected_diseases.append(('mealybugs', 0.70))
                detected_diseases.append(('whiteflies', 0.65))
            
            # Detect small dark spots (aphids, scale insects)
            if features.get('small_spots_ratio', 0) > 0.08:
                detected_diseases.append(('aphids', 0.68))
                detected_diseases.append(('scale_insects', 0.65))
            
            # Detect webbing patterns (spider mites) - high white ratio with patterns
            if features.get('white_ratio', 0) > 0.08 and features.get('white_ratio', 0) < 0.15:
                detected_diseases.append(('spider_mites', 0.72))
            
            # Detect holes/chewed leaves (caterpillars)
            if features.get('edge_ratio', 0) > 0.12:
                detected_diseases.append(('caterpillars', 0.70))
            
            # Detect sticky residue patterns (honeydew from various insects)
            if features.get('brightness_variance', 0) > 500 and features.get('yellow_ratio', 0) > 0.10:
                detected_diseases.append(('aphids', 0.65))
                detected_diseases.append(('whiteflies', 0.60))
                detected_diseases.append(('scale_insects', 0.60))
            
            # Detect thrips (silvery streaks - high brightness variance)
            if features.get('brightness_variance', 0) > 600:
                detected_diseases.append(('thrips', 0.68))
            
            # If no significant issues detected, consider healthy
            if not detected_diseases:
                detected_diseases.append(('healthy', 0.80))
            
            # Sort by confidence and get top result
            detected_diseases.sort(key=lambda x: x[1], reverse=True)
            top_disease = detected_diseases[0][0]
            confidence = detected_diseases[0][1]
            
            # Get disease information
            disease_info = self.disease_database.get(top_disease, self.disease_database['healthy']).copy()
            disease_info['confidence'] = round(confidence * 100, 1)
            disease_info['detected_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            disease_info['all_detections'] = [
                {'disease': d[0], 'confidence': round(d[1] * 100, 1)} 
                for d in detected_diseases[:3]
            ]
            
            return {
                'success': True,
                'disease': disease_info,
                'image_features': features,
                'health_status': 'healthy' if top_disease == 'healthy' else 'unhealthy'
            }
            
        except Exception as e:
            print(f"[PLANT DISEASE] Detection error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_all_diseases(self):
        """Get information about all known diseases"""
        return self.disease_database
    
    def get_disease_info(self, disease_name):
        """Get detailed information about a specific disease"""
        return self.disease_database.get(disease_name, None)

# Global detector instance
print("\n" + "="*50)
print("INITIALIZING PLANT DISEASE DETECTOR")
print("="*50)
plant_detector = PlantDiseaseDetector()
print("="*50 + "\n")

