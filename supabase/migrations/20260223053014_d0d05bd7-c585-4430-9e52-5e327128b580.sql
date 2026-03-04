
-- Role enum
CREATE TYPE public.app_role AS ENUM ('chief', 'employee');

-- Profiles table
CREATE TABLE public.profiles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL UNIQUE,
  full_name TEXT NOT NULL,
  employee_id_number TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- User roles table
CREATE TABLE public.user_roles (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  role app_role NOT NULL,
  UNIQUE(user_id, role)
);
ALTER TABLE public.user_roles ENABLE ROW LEVEL SECURITY;

-- Registration requests
CREATE TABLE public.registration_requests (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  full_name TEXT NOT NULL,
  employee_id_number TEXT NOT NULL,
  id_image_url TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
  reviewed_by UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  reviewed_at TIMESTAMPTZ
);
ALTER TABLE public.registration_requests ENABLE ROW LEVEL SECURITY;

-- Tasks table
CREATE TABLE public.tasks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  description TEXT NOT NULL,
  assigned_to UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  created_by UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'in_progress', 'completed')),
  help_requested BOOLEAN NOT NULL DEFAULT false,
  help_message TEXT,
  additional_assignee UUID REFERENCES auth.users(id),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE public.tasks ENABLE ROW LEVEL SECURITY;

-- Documents table
CREATE TABLE public.documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  uploaded_by UUID REFERENCES auth.users(id) ON DELETE CASCADE NOT NULL,
  file_url TEXT NOT NULL,
  document_name TEXT NOT NULL,
  analysis_result TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

-- Helper function: has_role
CREATE OR REPLACE FUNCTION public.has_role(_user_id UUID, _role app_role)
RETURNS BOOLEAN
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public
AS $$
  SELECT EXISTS (
    SELECT 1 FROM public.user_roles
    WHERE user_id = _user_id AND role = _role
  )
$$;

-- RLS: profiles
CREATE POLICY "Users can view own profile" ON public.profiles FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can update own profile" ON public.profiles FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own profile" ON public.profiles FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Chiefs can view all profiles" ON public.profiles FOR SELECT USING (public.has_role(auth.uid(), 'chief'));

-- RLS: user_roles
CREATE POLICY "Users can view own role" ON public.user_roles FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Chiefs can view all roles" ON public.user_roles FOR SELECT USING (public.has_role(auth.uid(), 'chief'));
CREATE POLICY "Chiefs can insert roles" ON public.user_roles FOR INSERT WITH CHECK (public.has_role(auth.uid(), 'chief'));

-- RLS: registration_requests
CREATE POLICY "Chiefs can view all requests" ON public.registration_requests FOR SELECT USING (public.has_role(auth.uid(), 'chief'));
CREATE POLICY "Chiefs can update requests" ON public.registration_requests FOR UPDATE USING (public.has_role(auth.uid(), 'chief'));
CREATE POLICY "Anyone can insert requests" ON public.registration_requests FOR INSERT WITH CHECK (auth.uid() = user_id);

-- RLS: tasks
CREATE POLICY "Chiefs can do all with tasks" ON public.tasks FOR ALL USING (public.has_role(auth.uid(), 'chief'));
CREATE POLICY "Employees see assigned tasks" ON public.tasks FOR SELECT USING (assigned_to = auth.uid() OR additional_assignee = auth.uid());
CREATE POLICY "Employees can update own tasks" ON public.tasks FOR UPDATE USING (assigned_to = auth.uid() OR additional_assignee = auth.uid());

-- RLS: documents
CREATE POLICY "Chiefs can view all documents" ON public.documents FOR SELECT USING (public.has_role(auth.uid(), 'chief'));
CREATE POLICY "Employees can view own documents" ON public.documents FOR SELECT USING (uploaded_by = auth.uid());
CREATE POLICY "Employees can insert own documents" ON public.documents FOR INSERT WITH CHECK (auth.uid() = uploaded_by);

-- Storage buckets
INSERT INTO storage.buckets (id, name, public) VALUES ('id-images', 'id-images', false);
INSERT INTO storage.buckets (id, name, public) VALUES ('documents', 'documents', false);

-- Storage policies: id-images (only chiefs can view, authenticated can upload)
CREATE POLICY "Authenticated users can upload id images" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'id-images' AND auth.role() = 'authenticated');
CREATE POLICY "Chiefs can view id images" ON storage.objects FOR SELECT USING (bucket_id = 'id-images' AND public.has_role(auth.uid(), 'chief'));

-- Storage policies: documents
CREATE POLICY "Authenticated users can upload documents" ON storage.objects FOR INSERT WITH CHECK (bucket_id = 'documents' AND auth.role() = 'authenticated');
CREATE POLICY "Chiefs can view all doc files" ON storage.objects FOR SELECT USING (bucket_id = 'documents' AND public.has_role(auth.uid(), 'chief'));
CREATE POLICY "Users can view own doc files" ON storage.objects FOR SELECT USING (bucket_id = 'documents' AND auth.uid()::text = (storage.foldername(name))[1]);

-- Trigger to create profile on signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
BEGIN
  INSERT INTO public.profiles (user_id, full_name)
  VALUES (NEW.id, COALESCE(NEW.raw_user_meta_data->>'full_name', 'User'));
  RETURN NEW;
END;
$$;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW
  EXECUTE FUNCTION public.handle_new_user();

-- Enable realtime for tasks (for notifications)
ALTER PUBLICATION supabase_realtime ADD TABLE public.tasks;
