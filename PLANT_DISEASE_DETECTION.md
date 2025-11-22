# Plant Disease Detection System

## Overview

The Plant Disease Detection System allows you to scan plant images to identify diseases and receive treatment solutions. The system uses image analysis to detect common plant health issues and provides actionable solutions.

## Features

### 🌿 Disease Detection
- **Image Analysis**: Upload plant photos to scan for diseases
- **Multiple Disease Detection**: Identifies various plant diseases and conditions
- **Confidence Scoring**: Provides confidence levels for each detection
- **Health Status**: Categorizes plants as healthy or unhealthy

### 💊 Treatment Solutions
- **Detailed Solutions**: Step-by-step treatment recommendations
- **Symptom Identification**: Lists common symptoms for each disease
- **Severity Assessment**: Categorizes disease severity (none, mild, moderate, severe)
- **Treatment Plans**: Specific treatment recommendations

## Supported Diseases

The system can detect the following conditions:

1. **Healthy Plant** - No issues detected
2. **Leaf Spot Disease** - Brown/black spots on leaves
3. **Powdery Mildew** - White powdery coating
4. **Root Rot** - Wilting, yellowing, mushy roots
5. **Aphid Infestation** - Small insects, sticky residue
6. **Spider Mite Infestation** - Fine webbing, yellow stippling
7. **Nutrient Deficiency** - Yellowing leaves, stunted growth
8. **Overwatering** - Yellowing, wilting, mold
9. **Underwatering** - Dry, crispy leaves, wilting
10. **Sunburn** - Brown/white patches, crispy edges

## How to Use

### From Dashboard
1. Navigate to the **Plant Health Scanner** section on the main dashboard
2. Click **"Upload Plant Image"** button
3. Select an image file (PNG, JPG, JPEG, GIF, WEBP)
4. Click **"Scan for Diseases"** button
5. View the detection results and solutions

### Advanced Scanner Page
1. Click **"Advanced Plant Scanner"** link from dashboard
2. Upload image by clicking the upload area or drag & drop
3. Click **"Scan for Diseases"** button
4. Review detailed results with symptoms and solutions

## API Endpoints

### Scan Plant Image
```
POST /api/plant/scan
Content-Type: multipart/form-data

Body: image file
```

**Response:**
```json
{
  "success": true,
  "disease": {
    "name": "Leaf Spot Disease",
    "confidence": 75.0,
    "severity": "moderate",
    "symptoms": [...],
    "solutions": [...],
    "treatment": "...",
    "detected_at": "2025-11-22 02:46:00"
  },
  "health_status": "unhealthy"
}
```

### Get All Diseases
```
GET /api/plant/diseases
```

### Get Disease Info
```
GET /api/plant/disease/<disease_name>
```

## Technical Details

### Detection Method
- **Rule-Based Analysis**: Uses color analysis and pattern detection
- **Image Processing**: Analyzes image features (color ratios, patterns)
- **ML Support**: Can use TensorFlow models if available (optional)

### Image Processing
- Converts images to RGB format
- Analyzes color patterns (yellow, brown, white, dark areas)
- Detects disease indicators based on visual features
- Provides confidence scores for detections

### File Handling
- Uploads stored in `uploads/` directory
- Maximum file size: 16MB
- Supported formats: PNG, JPG, JPEG, GIF, WEBP

## Dependencies

### Required
- `Pillow` - Image processing
- `numpy` - Numerical operations

### Optional
- `tensorflow` - For advanced ML-based detection (if model available)

## Future Enhancements

1. **Machine Learning Model**: Train a custom CNN model for better accuracy
2. **Disease Database Expansion**: Add more plant diseases and conditions
3. **Plant Species Identification**: Identify plant type before disease detection
4. **Historical Tracking**: Track plant health over time
5. **Treatment Progress**: Monitor treatment effectiveness
6. **Integration with Sensors**: Combine with sensor data for comprehensive health analysis

## Notes

- The system uses rule-based detection by default
- For production use, consider training a custom ML model
- Image quality affects detection accuracy
- Ensure good lighting and clear images for best results
- Multiple detections may be shown if several conditions are possible

