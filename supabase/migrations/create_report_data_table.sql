-- =====================================================
-- FORENSIC BLOOD PATTERN ANALYSIS SYSTEM
-- Report Data Table Setup
-- =====================================================

-- Drop table if exists (for clean reinstall)
DROP TABLE IF EXISTS report_data;

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

-- Drop existing policies if they exist
DROP POLICY IF EXISTS "Users can view own reports" ON report_data;
DROP POLICY IF EXISTS "Users can insert own reports" ON report_data;
DROP POLICY IF EXISTS "Users can delete own reports" ON report_data;

-- Policy: Users can only view their own reports
CREATE POLICY "Users can view own reports"
  ON report_data
  FOR SELECT
  USING (auth.uid() = uploaded_by);

-- Policy: Users can insert their own reports
CREATE POLICY "Users can insert own reports"
  ON report_data
  FOR INSERT
  WITH CHECK (auth.uid() = uploaded_by);

-- Policy: Users can delete their own reports
CREATE POLICY "Users can delete own reports"
  ON report_data
  FOR DELETE
  USING (auth.uid() = uploaded_by);

-- Create indexes for faster queries
CREATE INDEX idx_report_data_uploaded_by ON report_data(uploaded_by);
CREATE INDEX idx_report_data_created_at ON report_data(created_at DESC);
CREATE INDEX idx_report_data_blood_detected ON report_data(blood_detected);

-- Add comments for documentation
COMMENT ON TABLE report_data IS 'Stores forensic blood pattern analysis reports with PDF links';
COMMENT ON COLUMN report_data.uploaded_by IS 'UUID of the user who uploaded the image for analysis';
COMMENT ON COLUMN report_data.document_name IS 'User-provided name for the analyzed document';
COMMENT ON COLUMN report_data.report_url IS 'Public URL to the PDF report stored in blood_report bucket';
COMMENT ON COLUMN report_data.analysis_summary IS 'Full JSON analysis results from the forensic system';
COMMENT ON COLUMN report_data.blood_detected IS 'Whether blood was detected (boolean)';
COMMENT ON COLUMN report_data.blood_confidence IS 'Confidence percentage for blood detection (0-100)';
COMMENT ON COLUMN report_data.weapon_type IS 'Classified weapon type (e.g., Gun, Melee, Unknown)';
COMMENT ON COLUMN report_data.weapon_confidence IS 'Confidence percentage for weapon classification (0-100)';
COMMENT ON COLUMN report_data.origin_coordinates IS 'Calculated point of origin coordinates';

-- =====================================================
-- STORAGE BUCKET SETUP
-- =====================================================
-- Note: You must manually create the storage bucket via Supabase Dashboard:
-- 1. Go to Storage in Supabase Dashboard
-- 2. Click "New bucket"
-- 3. Name: "blood_report"
-- 4. Make it PUBLIC
-- 5. Click "Create bucket"
--
-- Or run this SQL if storage buckets can be created via SQL:
-- INSERT INTO storage.buckets (id, name, public) 
-- VALUES ('blood_report', 'blood_report', true)
-- ON CONFLICT (id) DO NOTHING;

-- Set up storage policies for blood_report bucket
-- (Run this AFTER creating the bucket)

-- Policy: Anyone can view reports (public bucket)
CREATE POLICY IF NOT EXISTS "Public read access for blood_report"
  ON storage.objects
  FOR SELECT
  USING (bucket_id = 'blood_report');

-- Policy: Authenticated users can upload to their own folder
CREATE POLICY IF NOT EXISTS "Users can upload own reports"
  ON storage.objects
  FOR INSERT
  WITH CHECK (
    bucket_id = 'blood_report' 
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );

-- Policy: Users can delete their own reports
CREATE POLICY IF NOT EXISTS "Users can delete own reports"
  ON storage.objects
  FOR DELETE
  USING (
    bucket_id = 'blood_report' 
    AND auth.role() = 'authenticated'
    AND (storage.foldername(name))[1] = auth.uid()::text
  );

-- =====================================================
-- VERIFICATION QUERIES
-- =====================================================
-- Run these to verify the setup:

-- Check if table exists
-- SELECT * FROM report_data LIMIT 5;

-- Check table structure
-- SELECT column_name, data_type, is_nullable 
-- FROM information_schema.columns 
-- WHERE table_name = 'report_data';

-- Check policies
-- SELECT * FROM pg_policies WHERE tablename = 'report_data';

-- Check indexes
-- SELECT indexname, indexdef 
-- FROM pg_indexes 
-- WHERE tablename = 'report_data';
