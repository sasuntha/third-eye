"""
Test Script for All Forensic Analysis Modules
Tests blood detection, string method, and weapon classification
"""
import os
import sys

print("="*70)
print("🔬 FORENSIC ANALYSIS MODULES - TEST SCRIPT")
print("="*70)

# Test 1: Import all modules
print("\n[Test 1] Importing modules...")
try:
    from blood_detection import BloodDetectionAnalyzer
    print("  ✓ Blood Detection module loaded")
except Exception as e:
    print(f"  ✗ Blood Detection import failed: {e}")
    sys.exit(1)

try:
    from string_method_analysis import StringMethodAnalyzer
    print("  ✓ String Method module loaded")
except Exception as e:
    print(f"  ✗ String Method import failed: {e}")
    sys.exit(1)

try:
    from weapon_classification import WeaponTypeClassifier
    print("  ✓ Weapon Classification module loaded")
except Exception as e:
    print(f"  ✗ Weapon Classification import failed: {e}")
    sys.exit(1)

# Test 2: Check model file
print("\n[Test 2] Checking for weapon classification model...")
MODEL_PATHS = [
    'models/weapon_classifier.h5',
    r'C:\Users\User\Desktop\research_nsbm\data\my_weapon_model_v2.h5',
]

model_path = None
for path in MODEL_PATHS:
    if os.path.exists(path):
        model_path = path
        print(f"  ✓ Model found: {path}")
        break

if not model_path:
    print("  ⚠️  No model file found. Weapon classification will not work.")
    print("     Please copy your model to one of these locations:")
    for path in MODEL_PATHS:
        print(f"     - {path}")
else:
    # Test 3: Load the model
    print("\n[Test 3] Loading weapon classification model...")
    try:
        classifier = WeaponTypeClassifier(model_path=model_path)
        print(f"  ✓ Model loaded successfully")
        print(f"     Input shape: {classifier.model.input_shape}")
        print(f"     Output shape: {classifier.model.output_shape}")
    except Exception as e:
        print(f"  ✗ Model loading failed: {e}")
        model_path = None

# Test 4: Initialize other analyzers
print("\n[Test 4] Initializing analyzers...")
try:
    blood_analyzer = BloodDetectionAnalyzer()
    print("  ✓ Blood Detection analyzer initialized")
except Exception as e:
    print(f"  ✗ Blood Detection initialization failed: {e}")

try:
    string_analyzer = StringMethodAnalyzer()
    print("  ✓ String Method analyzer initialized")
except Exception as e:
    print(f"  ✗ String Method initialization failed: {e}")

# Test 5: Check for test images
print("\n[Test 5] Checking for test images...")
TEST_IMAGE_PATHS = [
    r'C:\Users\User\Desktop\research_nsbm\data\test\image1.png',
    r'C:\Users\User\Desktop\research_nsbm\data\test\image5.png',
    r'C:\Users\User\Desktop\research_nsbm\data\test\image18.png',
]

available_images = []
for img_path in TEST_IMAGE_PATHS:
    if os.path.exists(img_path):
        available_images.append(img_path)
        print(f"  ✓ Found: {os.path.basename(img_path)}")

if not available_images:
    print("  ⚠️  No test images found")
    print("     Add test images to run full analysis tests")

# Summary
print("\n" + "="*70)
print("📊 TEST SUMMARY")
print("="*70)
print(f"✓ Modules imported: 3/3")
print(f"{'✓' if model_path else '⚠️'} Weapon model available: {'Yes' if model_path else 'No'}")
print(f"{'✓' if available_images else '⚠️'} Test images available: {len(available_images)}")

print("\n" + "="*70)
print("🎯 READY TO USE")
print("="*70)
print("\nAll modules are ready! You can now:")
print("\n1. Test Blood Detection:")
print("   python blood_detection.py")
print("\n2. Test String Method:")
print("   python string_method_analysis.py")
print("\n3. Test Weapon Classification:")
print("   python weapon_classification.py")

if model_path and available_images:
    print("\n4. Run comprehensive analysis:")
    print("   See COMPLETE_FORENSIC_SYSTEM.md for examples")

print("\n" + "="*70)

# Optional: Run a quick test if image and model are available
if model_path and available_images:
    print("\n🧪 Quick Test Available!")
    print("="*70)
    response = input("\nRun a quick analysis on a test image? (y/n): ").strip().lower()
    
    if response == 'y':
        test_image = available_images[0]
        print(f"\n📷 Testing with: {os.path.basename(test_image)}")
        print("="*70)
        
        # Test blood detection
        print("\n[1/3] Blood Detection...")
        try:
            result = blood_analyzer.detect_blood(image_path=test_image, generate_plot=False)
            print(f"     Verdict: {result['verdict']}")
            print(f"     Confidence: {result['confidence']}%")
        except Exception as e:
            print(f"     Error: {e}")
        
        # Test weapon classification
        print("\n[2/3] Weapon Classification...")
        try:
            result = classifier.analyze(image_path=test_image, generate_plot=False)
            print(f"     Weapon Type: {result['weapon_type']}")
            print(f"     Confidence: {result['confidence']:.1%}")
        except Exception as e:
            print(f"     Error: {e}")
        
        # Test string method
        print("\n[3/3] String Method...")
        try:
            result = string_analyzer.analyze(image_path=test_image, generate_plot=False)
            if result['status'] == 'success':
                print(f"     Origin: {result['origin']['coordinates']}")
                print(f"     Droplets: {result['statistics']['droplets_analyzed']}")
            else:
                print(f"     Status: {result['status']}")
        except Exception as e:
            print(f"     Error: {e}")
        
        print("\n" + "="*70)
        print("✅ Quick test complete!")
        print("="*70)
