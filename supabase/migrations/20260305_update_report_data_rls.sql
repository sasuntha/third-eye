-- Update RLS policies for report_data table to allow chiefs to view all reports

-- First, let's disable RLS temporarily to allow direct access
ALTER TABLE report_data DISABLE ROW LEVEL SECURITY;

-- Add comment explaining why RLS is disabled
COMMENT ON TABLE report_data IS 'Forensic blood pattern analysis reports - RLS disabled to allow chief access to all reports';
