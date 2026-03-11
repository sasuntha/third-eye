"""
Model Conversion Script - Convert model to TensorFlow 2.14 compatible format
"""
import tensorflow as tf
from tensorflow import keras
import sys

print(f"TensorFlow version: {tf.__version__}")

# Path to your original model
original_model_path = r'C:\Users\User\Desktop\research_nsbm\data\my_weapon_model_v2.h5'
output_model_path = r'C:\Users\User\Desktop\third-eye\backend\models\weapon_classifier_compatible.h5'

print(f"\nLoading model from: {original_model_path}")

try:
    # Try loading with different methods
    try:
        # Method 1: Direct load
        model = keras.models.load_model(original_model_path)
        print("✓ Model loaded successfully")
    except Exception as e:
        print(f"Direct load failed: {e}")
        print("Trying SavedModel format...")
        
        # Method 2: Convert to SavedModel first
        model = keras.models.load_model(original_model_path, compile=False)
        print("✓ Model loaded without compilation")
    
    # Get model info
    print(f"\nModel architecture:")
    print(f"  Input shape: {model.input_shape}")
    print(f"  Output shape: {model.output_shape}")
    print(f"  Total parameters: {model.count_params():,}")
    
    # Recompile with current TensorFlow
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    print("✓ Model recompiled")
    
    # Save in compatible format
    print(f"\nSaving to: {output_model_path}")
    model.save(output_model_path, save_format='h5')
    print("✓ Model saved successfully")
    
    # Verify the saved model
    print("\nVerifying saved model...")
    test_model = keras.models.load_model(output_model_path)
    print("✓ Saved model loads correctly")
    print(f"  Input shape: {test_model.input_shape}")
    print(f"  Output shape: {test_model.output_shape}")
    
    print("\n" + "="*60)
    print("SUCCESS! Model converted and saved.")
    print("="*60)
    print(f"\nYou can now use: {output_model_path}")
    print("\nUpdate your code to use: weapon_classifier_compatible.h5")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\nThe model cannot be loaded with current TensorFlow version.")
    print("You may need to:")
    print("  1. Upgrade TensorFlow: pip install tensorflow==2.15")
    print("  2. Or re-train the model with TensorFlow 2.14")
    sys.exit(1)
