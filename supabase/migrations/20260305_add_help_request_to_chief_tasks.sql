-- Add help request columns to chief_tasks table
ALTER TABLE public.chief_tasks 
ADD COLUMN IF NOT EXISTS help_requested BOOLEAN DEFAULT false,
ADD COLUMN IF NOT EXISTS help_message TEXT,
ADD COLUMN IF NOT EXISTS helper_employee_id BIGINT;

-- Add index for helper_employee_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_chief_tasks_helper ON public.chief_tasks(helper_employee_id);

-- Add comment
COMMENT ON COLUMN public.chief_tasks.help_requested IS 'Whether the assigned employee has requested help';
COMMENT ON COLUMN public.chief_tasks.help_message IS 'Message from employee explaining what help they need';
COMMENT ON COLUMN public.chief_tasks.helper_employee_id IS 'ID of additional employee assigned to help';
