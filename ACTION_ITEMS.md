# 🎯 YOUR ACTION ITEMS - VISUAL GUIDE

## 🟢 STEP 1: CREATE STORAGE BUCKET

**Where:** Supabase Dashboard → Storage

**Steps:**
```
1. Open browser → https://supabase.com/dashboard
2. Click on your project
3. Left sidebar → Click "Storage" 📦
4. Click green "+ New bucket" button
5. Enter bucket name: blood_report
6. Toggle "Public bucket" to ON ✅
7. Click "Create bucket"
```

**Visual Check:**
- You should see "blood_report" listed in your buckets
- The bucket should have a 🌐 icon (indicating it's public)

---

## 🟢 STEP 2: CREATE DATABASE TABLE

**Where:** Supabase Dashboard → SQL Editor

**Steps:**
```
1. Still in Supabase Dashboard
2. Left sidebar → Click "SQL Editor" 📝
3. Click "+ New query" button
4. Copy the SQL below
5. Paste into the editor
6. Click green "Run" button ▶️
7. Should see "Success. No rows returned"
```

**SQL TO RUN:**

```sql
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

ALTER TABLE report_data ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own reports"
  ON report_data FOR SELECT USING (auth.uid() = uploaded_by);

CREATE POLICY "Users can insert own reports"
  ON report_data FOR INSERT WITH CHECK (auth.uid() = uploaded_by);

CREATE POLICY "Users can delete own reports"
  ON report_data FOR DELETE USING (auth.uid() = uploaded_by);

CREATE INDEX idx_report_data_uploaded_by ON report_data(uploaded_by);
CREATE INDEX idx_report_data_created_at ON report_data(created_at DESC);
```

**Visual Check:**
- Go to "Table Editor" in left sidebar
- You should see "report_data" table listed
- Click on it to see the columns

---

## 🟢 VERIFY EVERYTHING IS RUNNING

### Backend Check:
```
Open browser → http://localhost:8000/api/forensic-analysis/health
```

**Should see:**
```json
{
  "status": "healthy",
  "orchestrator_loaded": true,
  "pdf_generator_loaded": true,
  "model_exists": true
}
```

### Frontend Check:
```
Your app should be running at: http://localhost:5173
(or whatever port Vite shows)
```

---

## 🟢 TEST THE COMPLETE SYSTEM

### Test Steps:

```
1. Open your app in browser
2. Login with your credentials
3. Navigate to "Document Scanner" page
4. Fill in document name: "Test Report 001"
5. Click "Upload Image" button
6. Select a crime scene image (with blood)
7. Click "Analyze Document" button
8. Wait 15-30 seconds (watch the spinner)
9. Should see success message!
10. Scroll down to "My Documents" section
11. Should see your report card with:
    - 🩸 Blood badge (red if detected)
    - Confidence percentage
    - Weapon type
    - Point of origin (if found)
12. Click "View Report" button
13. PDF should open in new tab!
```

---

## 🎨 WHAT YOU'LL SEE

### Upload Section:
```
┌─────────────────────────────────────┐
│  🔍 Scan & Analyze Document         │
├─────────────────────────────────────┤
│                                     │
│  Document Name                      │
│  [_________________________]        │
│                                     │
│  Upload Image                       │
│  ┌─────────────────────────────┐   │
│  │  📤 Click to upload image   │   │
│  └─────────────────────────────┘   │
│                                     │
│  [🔍 Analyze Document]              │
└─────────────────────────────────────┘
```

### My Documents Section:
```
┌─────────────────────────────────────┐
│  📄 My Documents (1)                │
├─────────────────────────────────────┤
│  ┌───────────────────────────────┐ │
│  │ Test Report 001               │ │
│  │ Mar 10, 2026                  │ │
│  │                               │ │
│  │ 🩸 Blood Detected   85.2%     │ │
│  │ 🔫 Weapon: Gun (92.5%)        │ │
│  │ 📍 Origin: (125, 89, 45)      │ │
│  │                     [👁️ View]│ │
│  └───────────────────────────────┘ │
└─────────────────────────────────────┘
```

---

## ❌ COMMON ERRORS & FIXES

### Error: "Bucket not found"
**Fix:** Go back to Step 1 - create the `blood_report` bucket

### Error: "relation 'report_data' does not exist"
**Fix:** Go back to Step 2 - run the SQL to create the table

### Error: "Upload failed: new row violates row-level security policy"
**Fix:** Make sure you ran ALL the SQL in Step 2 (including the CREATE POLICY lines)

### Error: "Backend not responding"
**Fix:** 
```powershell
cd C:\Users\User\Desktop\third-eye\backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Analysis takes forever
**Normal!** First analysis can take 20-30 seconds because:
- Loading TensorFlow model
- Processing the image
- Running 3 different analyses
- Generating PDF

---

## ✅ SUCCESS CHECKLIST

Before testing, make sure:

- [x] Backend is running (check terminal - should show "Application startup complete")
- [x] Frontend is running (Vite dev server)
- [ ] Storage bucket `blood_report` created ← **YOU DO THIS**
- [ ] Table `report_data` created ← **YOU DO THIS**
- [x] User is logged in to the app
- [x] ML model file exists in `backend/models/`

---

## 📞 STILL STUCK?

Check these terminal logs:

### Backend Terminal:
- Should show: "Forensic analysis system initialized successfully"
- Should show: "Model loaded successfully"
- Should show: "Application startup complete"

### Browser Console (F12):
- Check for any red errors
- Should see API calls to `/api/forensic-analysis/analyze-and-report`

### Supabase Dashboard:
- Go to "Table Editor" → Check if `report_data` table exists
- Go to "Storage" → Check if `blood_report` bucket exists
- After upload, check "Storage" → `blood_report` → Should see PDFs

---

## 🎉 YOU'RE DONE!

Once you complete Step 1 & 2, the system is ready!

Just:
1. Upload an image
2. Wait for analysis
3. View the beautiful PDF report!

**Each user only sees their own reports** (thanks to Row Level Security) 🔐

---

**Need more help?** Check the other guide files:
- `QUICK_SETUP_STEPS.md` - Quick reference
- `FORENSIC_SYSTEM_SETUP.md` - Detailed setup guide
- `IMPLEMENTATION_SUMMARY.md` - Technical overview
