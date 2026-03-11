# 🩸 Forensic Blood Pattern Analysis System - Complete Setup Guide

## 📋 Overview

This system allows users to:
1. Upload crime scene images
2. Analyze them using ML-powered forensic analysis (blood detection, weapon classification, point of origin)
3. Generate comprehensive PDF reports
4. Store reports in Supabase storage
5. View their own analyzed reports

---

## 🚀 Step-by-Step Setup

### **Step 1: Create Supabase Storage Bucket**

1. Go to your **Supabase Dashboard**: https://supabase.com/dashboard
2. Select your project
3. Click **Storage** in the left sidebar
4. Click **"New bucket"**
5. Enter bucket name: **`blood_report`**
6. ✅ Check **"Public bucket"** (so users can access their PDFs)
7. Click **"Create bucket"**

---

### **Step 2: Create Database Table**

1. In Supabase Dashboard, go to **SQL Editor**
2. Click **"New query"**
3. Copy and paste the SQL from: `supabase/migrations/create_report_data_table.sql`
4. Click **"Run"**
5. Verify the table was created successfully

**Quick SQL (copy this):**

```sql
-- Create report_data table
CREATE TABLE report_data (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  uploaded_by UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  document_name TEXT NOT NULL,
  report_url TEXT NOT NULL,
  analysis_summary JSONB,
  blood_detected BOOLEAN DEFAULT false,
  blood_confidence DECIMAL(5,2) DEFAULT 0,
  weapon_type TEXT,
  weapon_confidence DECIMAL(5,2) DEFAULT 0,
  origin_coordinates TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable Row Level Security
ALTER TABLE report_data ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only view their own reports
CREATE POLICY "Users can view own reports"
  ON report_data FOR SELECT
  USING (auth.uid() = uploaded_by);

-- Policy: Users can insert their own reports
CREATE POLICY "Users can insert own reports"
  ON report_data FOR INSERT
  WITH CHECK (auth.uid() = uploaded_by);

-- Policy: Users can delete their own reports
CREATE POLICY "Users can delete own reports"
  ON report_data FOR DELETE
  USING (auth.uid() = uploaded_by);

-- Create indexes
CREATE INDEX idx_report_data_uploaded_by ON report_data(uploaded_by);
CREATE INDEX idx_report_data_created_at ON report_data(created_at DESC);
```

---

### **Step 3: Verify Backend is Running**

Make sure your Python backend is running:

```powershell
cd C:\Users\User\Desktop\third-eye\backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Check health status:**
- Open browser: http://localhost:8000/api/forensic-analysis/health
- Should show: `"status": "healthy"`

---

### **Step 4: Verify Frontend is Running**

Make sure your frontend is running:

```powershell
cd C:\Users\User\Desktop\third-eye\frontend
npm run dev
```

---

### **Step 5: Test the System**

1. **Login** to your application
2. Navigate to **Document Scanner** page
3. **Upload a crime scene image** with blood patterns
4. Enter a **document name** (e.g., "Crime Scene 001")
5. Click **"Analyze Document"**
6. Wait for analysis to complete (~10-30 seconds)
7. PDF report should be generated and uploaded to Supabase
8. Report should appear in **"My Documents"** section

---

## 📊 Database Schema

### **report_data Table**

| Column | Type | Description |
|--------|------|-------------|
| `id` | UUID | Primary key |
| `uploaded_by` | UUID | User who uploaded (foreign key to auth.users) |
| `document_name` | TEXT | User-provided name |
| `report_url` | TEXT | Public URL to PDF in blood_report bucket |
| `analysis_summary` | JSONB | Complete analysis JSON results |
| `blood_detected` | BOOLEAN | Whether blood was found |
| `blood_confidence` | DECIMAL | Blood detection confidence (0-100) |
| `weapon_type` | TEXT | Classified weapon (Gun/Melee/Unknown) |
| `weapon_confidence` | DECIMAL | Weapon classification confidence (0-100) |
| `origin_coordinates` | TEXT | Point of origin coordinates |
| `created_at` | TIMESTAMP | When report was created |

---

## 🔐 Security & Permissions

### **Row Level Security (RLS)**

✅ **Enabled** - Users can only see their own reports

### **Policies**

1. **SELECT**: Users can view only their own reports (`uploaded_by = auth.uid()`)
2. **INSERT**: Users can only insert reports for themselves
3. **DELETE**: Users can delete their own reports

### **Storage Policies**

1. **Public Read**: Anyone with the URL can view PDFs (public bucket)
2. **Upload**: Authenticated users can upload to their own folder (`user_id/`)
3. **Delete**: Users can delete their own files

---

## 🔄 System Flow

```
User uploads image
    ↓
Frontend sends to Python backend API
    ↓
Backend analyzes image:
  - Blood detection (OpenCV + image analysis)
  - Weapon classification (CNN ML model)
  - Point of origin (String method + DBSCAN)
    ↓
Backend generates PDF report
    ↓
Backend returns PDF as base64
    ↓
Frontend decodes PDF and uploads to Supabase storage (blood_report bucket)
    ↓
Frontend saves record to report_data table with:
  - PDF URL
  - Analysis results
  - User ID
    ↓
Frontend displays report in "My Documents"
    ↓
User clicks "View Report" → Opens PDF in new tab
```

---

## 🐛 Troubleshooting

### **Error: "Bucket not found"**
- ✅ Create the `blood_report` bucket in Supabase Storage
- Make sure it's set to **Public**

### **Error: "relation 'report_data' does not exist"**
- ✅ Run the SQL migration to create the table

### **Error: "new row violates row-level security policy"**
- ✅ Check that RLS policies are created correctly
- ✅ Make sure user is authenticated

### **Backend not responding**
- ✅ Check backend is running: `http://localhost:8000/api/forensic-analysis/health`
- ✅ Check model file exists: `backend/models/my_weapon_model_v2.h5`
- ✅ Check TensorFlow version: `pip list | grep tensorflow`

### **Analysis takes too long**
- Normal processing time: **10-30 seconds** per image
- Large images may take longer
- Check backend terminal for progress logs

---

## 📁 File Structure

```
third-eye/
├── backend/
│   ├── models/
│   │   └── my_weapon_model_v2.h5          # ML model
│   ├── blood_detection.py                  # Blood detection module
│   ├── string_method_analysis.py           # Point of origin module
│   ├── weapon_classification.py            # Weapon classification module
│   ├── forensic_orchestrator.py            # Orchestrates all analyses
│   ├── pdf_report_generator.py             # Generates PDF reports
│   └── app/api/routes/
│       └── forensic_analysis.py            # API endpoints
├── frontend/src/components/employee/
│   └── DocumentScanner.tsx                 # Main UI component
└── supabase/migrations/
    └── create_report_data_table.sql        # Database schema
```

---

## 🎯 Features

### **Blood Detection**
- HSV color range analysis
- Splatter pattern detection
- Texture analysis
- Confidence scoring

### **Weapon Classification**
- CNN-based ML model
- Categories: Gun vs Melee
- Transfer learning (MobileNetV2)
- Confidence scoring

### **Point of Origin Analysis**
- Droplet detection
- Impact angle calculation
- Backward trajectory tracing
- DBSCAN clustering for origin point

### **PDF Report**
- Professional multi-page report
- Analysis summary tables
- Visualization images
- Confidence metrics
- Timestamp and metadata

---

## 📞 Support

For issues or questions:
1. Check the terminal logs (backend and frontend)
2. Check browser console for errors
3. Verify Supabase configuration
4. Check backend health endpoint

---

## ✅ Quick Checklist

Before using the system, verify:

- [ ] Supabase storage bucket `blood_report` created and set to **Public**
- [ ] Database table `report_data` created with RLS policies
- [ ] Backend running on port 8000
- [ ] Frontend running (usually port 5173)
- [ ] ML model file exists: `backend/models/my_weapon_model_v2.h5`
- [ ] TensorFlow 2.18.0 installed
- [ ] User is logged in to the application

---

**🎉 You're all set! Upload a crime scene image and watch the forensic analysis magic happen!**
