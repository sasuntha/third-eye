# System Architecture - Complete Forensic Analysis System

## 📊 Visual System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                                 │
│                     (React - DocumentScanner.tsx)                        │
│                                                                          │
│  ┌────────────────────────────────────────────────────────────────┐    │
│  │  [Upload Image]  [Document Name]  [Analyze Button]             │    │
│  └────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  │ 1. POST /api/forensic-analysis/analyze-and-report
                                  │    FormData: image file
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        FASTAPI BACKEND                                   │
│                  (forensic_analysis.py endpoint)                         │
│                                                                          │
│  • Receives image upload                                                │
│  • Validates file type                                                  │
│  • Calls Forensic Orchestrator                                          │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     FORENSIC ORCHESTRATOR                                │
│                    (forensic_orchestrator.py)                            │
│                                                                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  STEP 0: Image Preprocessing                                     │  │
│  │  ─────────────────────────────                                   │  │
│  │  • Load image (from bytes or path)                               │  │
│  │  • Check current size                                            │  │
│  │  • Resize to 512x512 if needed                                   │  │
│  │  • Convert to standardized format                                │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                  │                                       │
│                                  ▼                                       │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  STEP 1: Blood Detection (REQUIRED)                             │  │
│  │  ────────────────────────────────────                            │  │
│  │  Module: blood_detection.py                                      │  │
│  │                                                                   │  │
│  │  Analyzes:                                                        │  │
│  │  • Color (HSV color space for blood-like hues)                   │  │
│  │  • Pattern (splatter characteristics)                            │  │
│  │  • Texture (surface variation and edges)                         │  │
│  │                                                                   │  │
│  │  Outputs:                                                         │  │
│  │  • Verdict: "🩸 LIKELY BLOOD" / "⚠️ POSSIBLE" / "✅ NOT BLOOD"    │  │
│  │  • Confidence: 0-100%                                            │  │
│  │  • Visualization: Base64 PNG                                      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                  │                                       │
│                     Confidence Check: >= 65%?                            │
│                                  │                                       │
│                     ┌────────────┴────────────┐                          │
│                     │                         │                          │
│                 NO (Stop)                 YES (Continue)                 │
│                     │                         │                          │
│                     ▼                         ▼                          │
│           Return "no_blood_detected"    ┌────────────┐                  │
│                                         │  PARALLEL   │                  │
│                                         │  EXECUTION  │                  │
│                                         └─────┬──────┘                  │
│                           ┌───────────────────┴───────────────────┐    │
│                           │                                       │     │
│                           ▼                                       ▼     │
│  ┌──────────────────────────────────────┐  ┌──────────────────────────│────┐
│  │  STEP 2: Weapon Classification       │  │  STEP 3: String Method   │    │
│  │  ──────────────────────────────      │  │  ───────────────────────  │    │
│  │  Module: weapon_classification.py    │  │  Module: string_method_  │    │
│  │                                      │  │          analysis.py      │    │
│  │  Deep Learning CNN Model:            │  │                          │    │
│  │  • Loads trained TensorFlow model     │  │  Classical Forensics:    │    │
│  │  • Preprocesses 512x512 → 224x224    │  │  • Detect droplets       │    │
│  │  • Runs inference                     │  │  • Analyze geometry      │    │
│  │  • Classifies: Gun or Melee          │  │  • Calculate elongation  │    │
│  │                                      │  │  • Trace trajectories    │    │
│  │  Gun Pattern:                         │  │  • Find intersections    │    │
│  │  • High-velocity impact               │  │  • Cluster with DBSCAN   │    │
│  │  • Fine mist, small droplets         │  │                          │    │
│  │  • Radial distribution                │  │  Outputs:                │    │
│  │                                      │  │  • Origin: (X, Y) coords  │    │
│  │  Melee Pattern:                       │  │  • Droplets analyzed      │    │
│  │  • Cast-off/impact spatter           │  │  • Impact angles          │    │
│  │  • Larger elongated droplets         │  │  • Visualization          │    │
│  │  • Directional patterns               │  │                          │    │
│  │                                      │  │                          │    │
│  │  Outputs:                             │  │                          │    │
│  │  • Weapon Type: Gun/Melee            │  │                          │    │
│  │  • Confidence: 0-100%                 │  │                          │    │
│  │  • Probabilities for both             │  │                          │    │
│  │  • Visualization: Base64 PNG          │  │                          │    │
│  └──────────────────────────────────────┘  └──────────────────────────────┘
│                           │                                       │     │
│                           └───────────────────┬───────────────────┘    │
│                                              ▼                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  Compile Results                                                 │  │
│  │  • Blood detection results                                       │  │
│  │  • Weapon classification results                                 │  │
│  │  • String method results                                         │  │
│  │  • Generate executive summary                                    │  │
│  │  • Calculate total duration                                      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      PDF REPORT GENERATOR                                │
│                   (pdf_report_generator.py)                              │
│                                                                          │
│  Generates professional PDF with:                                       │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │  1. Cover Page                                                   │  │
│  │     • Title and timestamp                                        │  │
│  │     • Executive summary table                                    │  │
│  │                                                                  │  │
│  │  2. Blood Detection Section                                     │  │
│  │     • Verdict and confidence                                     │  │
│  │     • Color/Pattern/Texture analysis                             │  │
│  │     • Embedded visualization                                     │  │
│  │                                                                  │  │
│  │  3. Weapon Classification Section                               │  │
│  │     • Weapon type and confidence                                 │  │
│  │     • Detailed probabilities                                     │  │
│  │     • Interpretation                                             │  │
│  │     • Embedded visualization                                     │  │
│  │                                                                  │  │
│  │  4. Point of Origin Section                                     │  │
│  │     • Origin coordinates                                         │  │
│  │     • Droplet statistics                                         │  │
│  │     • Impact angle analysis                                      │  │
│  │     • Embedded visualization                                     │  │
│  │                                                                  │  │
│  │  5. Disclaimer                                                   │  │
│  │     • AI-assisted analysis notice                               │  │
│  │     • Verification requirements                                  │  │
│  │     • Model information                                          │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                                                          │
│  Saves to: backend/reports/forensic_report_TIMESTAMP.pdf                │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     RESPONSE TO FRONTEND                                 │
│                                                                          │
│  JSON Response:                                                          │
│  {                                                                       │
│    "status": "success",                                                 │
│    "blood_detection": { ... },                                          │
│    "weapon_classification": { ... },                                    │
│    "string_method": { ... },                                            │
│    "summary": {                                                          │
│      "blood_detected": "🩸 LIKELY BLOOD",                               │
│      "blood_confidence": 85.2,                                          │
│      "weapon_type": "Gun",                                              │
│      "weapon_confidence": 0.92,                                         │
│      "origin_found": true,                                              │
│      "origin_coordinates": "(256.3, 312.7)"                             │
│    },                                                                    │
│    "pdf_report": {                                                       │
│      "filename": "forensic_report_20260310_143022.pdf",                 │
│      "url": "/api/forensic-analysis/download-report/..."                │
│    },                                                                    │
│    "duration_seconds": 8.5                                              │
│  }                                                                       │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        SUPABASE DATABASE                                 │
│                                                                          │
│  INSERT INTO documents (                                                │
│    uploaded_by: user_id,                                                │
│    file_url: storage_path,                                              │
│    document_name: user_input,                                           │
│    analysis_result: summary_text                                        │
│  )                                                                       │
└─────────────────────────────────┬───────────────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      USER SEES RESULTS                                   │
│                                                                          │
│  ✅ Document analyzed successfully!                                     │
│                                                                          │
│  Results:                                                                │
│  • Blood Detection: 🩸 LIKELY BLOOD (85% confidence)                    │
│  • Weapon Type: Gun (92% confidence)                                    │
│  • Point of Origin: (256.3, 312.7)                                      │
│  • PDF Report: [Download] button                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

## 🔄 Data Flow Timeline

```
T+0.0s: User clicks "Analyze Document"
T+0.1s: Image uploaded to backend
T+0.2s: Image resized to 512x512
T+0.3s: Blood detection starts
T+2.0s: Blood detection complete → Confidence: 85%
T+2.1s: Weapon classification & String method start (parallel)
T+3.5s: Weapon classification complete → Gun (92%)
T+6.0s: String method complete → Origin: (256, 312)
T+6.1s: PDF generation starts
T+8.0s: PDF generation complete
T+8.1s: Results returned to frontend
T+8.2s: Saved to database
T+8.3s: User sees results!
```

## 📦 Module Dependencies

```
forensic_orchestrator.py
    ├── blood_detection.py
    │   ├── opencv-python
    │   ├── numpy
    │   ├── matplotlib
    │   └── scikit-image
    │
    ├── weapon_classification.py
    │   ├── tensorflow
    │   ├── opencv-python
    │   └── numpy
    │
    └── string_method_analysis.py
        ├── opencv-python
        ├── numpy
        ├── scikit-learn (DBSCAN)
        └── scikit-image

pdf_report_generator.py
    └── reportlab
```

## 🎯 Key Features

1. **Automatic Preprocessing** - Always resizes to 512x512
2. **Sequential Gating** - Blood detection must pass before others run
3. **Parallel Execution** - Weapon + String methods run simultaneously
4. **Comprehensive Output** - JSON + PDF + Database record
5. **Error Handling** - Graceful failures at each step
6. **Professional Reports** - Publication-ready PDF output

## ✅ System is Complete!

All components are connected and working together to provide comprehensive forensic analysis from a single user action!
