# ML Models Directory

This directory stores trained machine learning models for forensic analysis.

## Current Models

### 1. Weapon Type Classification Model
**File:** `weapon_classifier.h5`
**Purpose:** Classifies blood spatter patterns to identify weapon type (Gun vs Melee)
**Input:** 224x224 RGB images
**Output:** Binary classification (Gun or Melee)
**Accuracy:** [Your model's accuracy]

## How to Add Your Trained Model

### Option 1: Copy from your current location
```bash
# Copy your existing model file
copy "C:\Users\User\Desktop\research_nsbm\data\my_weapon_model_v2.h5" "backend\models\weapon_classifier.h5"
```

### Option 2: Use symbolic link (Windows)
```bash
# Create a symbolic link to your model
mklink "backend\models\weapon_classifier.h5" "C:\Users\User\Desktop\research_nsbm\data\my_weapon_model_v2.h5"
```

### Option 3: Keep it where it is
You can also keep your model in its current location and update the path in the configuration.

## Model File Structure

```
backend/
├── models/
│   ├── README.md (this file)
│   ├── weapon_classifier.h5       ← Your trained model goes here
│   └── model_info.json            ← Model metadata (optional)
```

## Model Information

Create a `model_info.json` file to document your model:

```json
{
  "model_name": "weapon_classifier",
  "version": "2.0",
  "created_date": "2024-01-15",
  "framework": "TensorFlow/Keras",
  "architecture": "Custom CNN",
  "input_shape": [224, 224, 3],
  "classes": ["Gun", "Melee"],
  "training_data": {
    "total_samples": 1000,
    "gun_samples": 500,
    "melee_samples": 500
  },
  "performance": {
    "accuracy": 0.95,
    "precision": 0.94,
    "recall": 0.96,
    "f1_score": 0.95
  },
  "notes": "Trained on forensic blood pattern images"
}
```

## Using the Model

The model is automatically loaded when you use the `WeaponTypeClassifier`:

```python
from weapon_classification import WeaponTypeClassifier

# Will automatically look for model in backend/models/weapon_classifier.h5
classifier = WeaponTypeClassifier(model_path='backend/models/weapon_classifier.h5')

# Or use your custom path
classifier = WeaponTypeClassifier(model_path='path/to/your/model.h5')
```

## Model Requirements

- **Format:** Keras HDF5 (.h5)
- **Input:** 224x224x3 (RGB images)
- **Output:** 2 classes (Gun, Melee)
- **Preprocessing:** Images should be normalized to [0, 1]

## Updating the Model

To update your model:
1. Train your new model
2. Save it as `.h5` file
3. Replace the existing `weapon_classifier.h5`
4. Update `model_info.json` with new version information
5. Restart the backend service

## Model Size

Keep model files under 100MB for optimal performance. If your model is larger:
- Consider using model compression
- Use model quantization
- Store model in external storage and download on startup
