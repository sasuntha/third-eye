# 🎯 What You Need to Do - Quick Summary

## 1️⃣ CREATE SUPABASE STORAGE BUCKET

**Go to Supabase Dashboard:**
1. Open: https://supabase.com/dashboard
2. Select your project
3. Click **Storage** (left sidebar)
4. Click **"New bucket"**
5. Bucket name: **`blood_report`**
6. ✅ Make it **PUBLIC**
7. Click **"Create bucket"**

---

## 2️⃣ CREATE DATABASE TABLE

**Go to Supabase SQL Editor:**
1. Click **SQL Editor** (left sidebar)
2. Click **"New query"**
3. **Copy and paste this SQL:**

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
  ON report_data FOR SELECT
  USING (auth.uid() = uploaded_by);

CREATE POLICY "Users can insert own reports"
  ON report_data FOR INSERT
  WITH CHECK (auth.uid() = uploaded_by);

CREATE POLICY "Users can delete own reports"
  ON report_data FOR DELETE
  USING (auth.uid() = uploaded_by);

CREATE INDEX idx_report_data_uploaded_by ON report_data(uploaded_by);
CREATE INDEX idx_report_data_created_at ON report_data(created_at DESC);
```

4. Click **"Run"**
5. You should see: **"Success. No rows returned"**

---

## 3️⃣ RESTART YOUR BACKEND

The backend code has been updated. Stop and restart it:

```powershell
# Press Ctrl+C to stop the current backend
# Then restart:
cd C:\Users\User\Desktop\third-eye\backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

---

## 4️⃣ TEST THE SYSTEM

1. Make sure frontend is running (npm run dev)
2. Login to your application
3. Go to **Document Scanner** page
4. Upload a crime scene image
5. Enter a document name (e.g., "Test Report 001")
6. Click **"Analyze Document"**
7. Wait ~10-30 seconds
8. Report should appear in "My Documents" section
9. Click **"View Report"** to open the PDF

---

## ✅ How It Works Now

```
User uploads image
    ↓
Python backend analyzes it (blood, weapon, origin)
    ↓
Python generates PDF report
    ↓
Frontend uploads PDF to Supabase bucket "blood_report"
    ↓
Frontend saves record to "report_data" table
    ↓
User sees report in "My Documents"
    ↓
Clicking "View Report" opens the PDF in new tab
```

---

## 🔍 What You'll See in "My Documents"

Each report card shows:
- 📄 Document name
- 📅 Date created
- 🩸 Blood detection status (badge with confidence %)
- 🔫 Weapon type (if blood detected)
- 📍 Point of origin coordinates (if found)
- 👁️ "View Report" button (opens PDF)

**Important:** Each user only sees their OWN reports (secured by Row Level Security)

---

## 🐛 If Something Goes Wrong

**"Bucket not found"**
→ Create the `blood_report` bucket in Supabase Storage (Step 1)

**"relation 'report_data' does not exist"**
→ Run the SQL to create the table (Step 2)

**"Upload failed"**
→ Make sure the bucket is set to PUBLIC

**Backend errors**
→ Check the backend terminal for detailed error messages

---

## 📊 What Gets Saved

### In `report_data` table:
- User ID (who uploaded)
- Document name (what you typed)
- PDF URL (link to the report in storage)
- Blood detected (yes/no)
- Blood confidence (percentage)
- Weapon type (Gun/Melee/Unknown)
- Weapon confidence (percentage)
- Origin coordinates (x, y, z)
- Full analysis JSON

### In `blood_report` bucket:
- PDF files organized by user ID
- Named like: `{userId}/{documentName}_{timestamp}.pdf`
- Publicly accessible via URL

---

**That's it! Follow steps 1-4 above and you're ready to go! 🚀**
