-- Temporarily disable RLS on employees table to allow direct inserts from frontend
-- This is necessary since the chief authentication is handled by backend, not Supabase auth
ALTER TABLE public.employees DISABLE ROW LEVEL SECURITY;

-- Also ensure temp_register can be read publicly (for chief to view pending registrations)
-- Note: temp_register should already have RLS disabled, but let's make sure
ALTER TABLE public.temp_register DISABLE ROW LEVEL SECURITY;

-- Add comment explaining why RLS is disabled
COMMENT ON TABLE public.employees IS 'Employee authentication table - RLS disabled to allow direct management via frontend';
