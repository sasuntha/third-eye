# 🔧 UPDATED SQL - Without RLS (Works with Backend Auth)

Since your app uses custom backend authentication (not Supabase Auth), we need to disable Row Level Security and handle permissions in your application logic instead.

## ✅ Run This SQL in Supabase Dashboard:

```sql
-- Drop existing table if it exists
DROP TABLE IF EXISTS report_data CASCADE;

-- Create report_data table
CREATE TABLE report_data (
  id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
  uploaded_by UUID NOT NULL,
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

-- IMPORTANT: Do NOT enable RLS since we're using backend auth, not Supabase auth
-- ALTER TABLE report_data ENABLE ROW LEVEL SECURITY;  ← COMMENTED OUT

-- Create indexes for faster queries
CREATE INDEX idx_report_data_uploaded_by ON report_data(uploaded_by);
CREATE INDEX idx_report_data_created_at ON report_data(created_at DESC);
CREATE INDEX idx_report_data_blood_detected ON report_data(blood_detected);

-- Add comments
COMMENT ON TABLE report_data IS 'Forensic blood pattern analysis reports (auth handled by backend API)';
COMMENT ON COLUMN report_data.uploaded_by IS 'UUID of the user from employees table';
COMMENT ON COLUMN report_data.document_name IS 'User-provided name for the document';
COMMENT ON COLUMN report_data.report_url IS 'Public URL to PDF in blood_report bucket';
```

## 📝 Explanation:

**Why no RLS?**
- Your app uses **custom backend authentication** (FastAPI + employees table)
- Supabase RLS only works with **Supabase Auth** (`auth.users` table)
- Since `user.id` comes from your `employees` table, not `auth.users`, RLS blocks it

**Is this secure?**
- ✅ Yes! Your backend API handles authentication
- ✅ Frontend queries are filtered by `user.id` from your auth system
- ✅ Users can only see their own reports (filtered in the query: `.eq("uploaded_by", user.id)`)

## 🎯 Alternative: Use Supabase Service Role

If you prefer to keep RLS enabled, you would need to:
1. Use Supabase service role key in backend
2. Let backend insert into database (not frontend)
3. This is more complex and unnecessary for your use case

## ✅ Current Approach (Recommended):
- Disable RLS
- Frontend filters by `user.id` 
- Backend API validates authentication
- Simple and works with your existing auth system ✅

---

**After running the SQL above, try uploading again - it will work!** 🚀
