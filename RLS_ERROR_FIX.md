# 🔧 RLS Error Fix Guide

## Error: "new row violates row-level security policy"

This error occurs when trying to insert into the `report_data` table, but the Row Level Security (RLS) policy is blocking it.

---

## ✅ **I've Already Fixed the Frontend Code**

The code now properly uses the authenticated Supabase user ID (`authUser.id`), which should match the `auth.uid()` in the RLS policy.

---

## 🎯 **What You Need To Check:**

### 1. **Did you create the `report_data` table?**

Go to Supabase Dashboard → **SQL Editor** → Run this:

```sql
-- Check if the table exists
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' AND table_name = 'report_data';
```

**If empty:** You need to create the table! See `QUICK_SETUP_STEPS.md`

---

### 2. **Did you create the RLS policies?**

Go to Supabase Dashboard → **SQL Editor** → Run this:

```sql
-- Check if policies exist
SELECT policyname FROM pg_policies WHERE tablename = 'report_data';
```

**Should show 3 policies:**
- `Users can view own reports`
- `Users can insert own reports`
- `Users can delete own reports`

**If empty or missing:** Run the full SQL from `QUICK_SETUP_STEPS.md`

---

### 3. **Quick Fix: Run This Complete SQL**

If you're not sure, just run this complete SQL to create everything:

```sql
-- Drop and recreate the table with proper RLS
DROP TABLE IF EXISTS report_data CASCADE;

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

-- Drop old policies if they exist
DROP POLICY IF EXISTS "Users can view own reports" ON report_data;
DROP POLICY IF EXISTS "Users can insert own reports" ON report_data;
DROP POLICY IF EXISTS "Users can delete own reports" ON report_data;

-- Create policies
CREATE POLICY "Users can view own reports"
  ON report_data FOR SELECT
  USING (auth.uid() = uploaded_by);

CREATE POLICY "Users can insert own reports"
  ON report_data FOR INSERT
  WITH CHECK (auth.uid() = uploaded_by);

CREATE POLICY "Users can delete own reports"
  ON report_data FOR DELETE
  USING (auth.uid() = uploaded_by);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_report_data_uploaded_by ON report_data(uploaded_by);
CREATE INDEX IF NOT EXISTS idx_report_data_created_at ON report_data(created_at DESC);
```

---

### 4. **Verify You're Logged In**

Make sure you're logged into the app with a valid Supabase user account. The frontend now checks:

```typescript
const { data: { user: authUser } } = await supabase.auth.getUser();
```

If this returns `null`, you're not authenticated.

---

### 5. **Check Storage Bucket Exists**

Go to Supabase Dashboard → **Storage** → Check for bucket named **`blood_report`**

**If missing:** Create it and make it **PUBLIC**

---

## 🧪 **Test the Fix:**

1. **Make sure you're logged in** to the app
2. **Refresh the page**
3. Try uploading and analyzing an image again
4. Should work now! ✅

---

## 🐛 **Still Not Working?**

### Check Browser Console:

Press `F12` → Console tab → Look for:
- Any red errors
- "Not authenticated" message
- Insert error details

### Check Supabase Dashboard:

**Table Editor** → `report_data` → Try manually inserting a row:
```
uploaded_by: (copy your user UUID from auth.users table)
document_name: "Test"
report_url: "https://example.com/test.pdf"
```

If manual insert fails, the RLS policy is the issue.

---

## 💡 **Quick Checklist:**

- [ ] `report_data` table created
- [ ] RLS enabled on `report_data`
- [ ] 3 RLS policies created
- [ ] `blood_report` storage bucket created
- [ ] User is logged in to the app
- [ ] Frontend code updated (already done ✅)

---

**After running the SQL above, try uploading again!** 🚀
