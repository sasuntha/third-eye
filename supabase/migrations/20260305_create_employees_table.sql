-- Create employees table for login authentication
-- This table stores employee credentials and role information

CREATE TABLE IF NOT EXISTS public.employees (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT NOT NULL UNIQUE,
  password TEXT NOT NULL,
  full_name TEXT,
  employee_id TEXT UNIQUE,
  role TEXT CHECK (role IN ('chief', 'employee', NULL)) DEFAULT 'employee',
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Create updated_at trigger
CREATE OR REPLACE FUNCTION update_employees_updated_at()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_employees_timestamp
  BEFORE UPDATE ON public.employees
  FOR EACH ROW
  EXECUTE FUNCTION update_employees_updated_at();

-- Enable Row Level Security
ALTER TABLE public.employees ENABLE ROW LEVEL SECURITY;

-- RLS Policies
-- Allow users to read their own record
CREATE POLICY "Users can read own employee record" ON public.employees
  FOR SELECT USING (auth.uid()::text = id::text);

-- Allow users to update their own record
CREATE POLICY "Users can update own employee record" ON public.employees
  FOR UPDATE USING (auth.uid()::text = id::text);

-- Allow chiefs to read all employee records
CREATE POLICY "Chiefs can read all employees" ON public.employees
  FOR SELECT USING (
    EXISTS (
      SELECT 1 FROM public.employees e2
      WHERE e2.id = auth.uid()::text AND (e2.role = 'chief' OR e2.role IS NULL)
    )
  );

-- Index for faster email lookups during login
CREATE INDEX IF NOT EXISTS idx_employees_email ON public.employees(email);
CREATE INDEX IF NOT EXISTS idx_employees_role ON public.employees(role);
