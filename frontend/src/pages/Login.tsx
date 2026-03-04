import { useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { Shield, UserPlus, LogIn, Upload, Eye, EyeOff } from "lucide-react";

export default function Login() {
  const { toast } = useToast();
  const [tab, setTab] = useState("login");
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Login state
  const [loginEmail, setLoginEmail] = useState("");
  const [loginPassword, setLoginPassword] = useState("");

  // Register state
  const [regName, setRegName] = useState("");
  const [regIdNumber, setRegIdNumber] = useState("");
  const [regEmail, setRegEmail] = useState("");
  const [regPassword, setRegPassword] = useState("");
  const [regConfirmPassword, setRegConfirmPassword] = useState("");
  const [idImage, setIdImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setIdImage(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const { error } = await supabase.auth.signInWithPassword({
        email: loginEmail,
        password: loginPassword,
      });
      if (error) throw error;
      // Auth state change will handle redirect
    } catch (err: any) {
      toast({ title: "Login failed", description: err.message, variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    if (regPassword !== regConfirmPassword) {
      toast({ title: "Passwords don't match", variant: "destructive" });
      return;
    }
    if (!idImage) {
      toast({ title: "Please upload your ID image", variant: "destructive" });
      return;
    }
    setLoading(true);
    try {
      // 1. Sign up
      const { data: authData, error: signUpError } = await supabase.auth.signUp({
        email: regEmail,
        password: regPassword,
        options: { data: { full_name: regName } },
      });
      if (signUpError) throw signUpError;
      if (!authData.user) throw new Error("Registration failed");

      // 2. Upload ID image
      const fileExt = idImage.name.split(".").pop();
      const filePath = `${authData.user.id}/id-image.${fileExt}`;
      const { error: uploadError } = await supabase.storage
        .from("id-images")
        .upload(filePath, idImage);
      if (uploadError) throw uploadError;

      const { data: urlData } = supabase.storage.from("id-images").getPublicUrl(filePath);

      // 3. Create registration request
      const { error: reqError } = await supabase.from("registration_requests").insert({
        user_id: authData.user.id,
        full_name: regName,
        employee_id_number: regIdNumber,
        id_image_url: filePath,
      });
      if (reqError) throw reqError;

      // Sign out — they can't login until approved
      await supabase.auth.signOut();

      toast({
        title: "Registration submitted!",
        description: "Your request has been sent to the chief for approval. You'll be able to log in once approved.",
      });
      setTab("login");
      setRegName("");
      setRegIdNumber("");
      setRegEmail("");
      setRegPassword("");
      setRegConfirmPassword("");
      setIdImage(null);
      setImagePreview(null);
    } catch (err: any) {
      toast({ title: "Registration failed", description: err.message, variant: "destructive" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md animate-fade-in">
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-primary mb-4">
            <Shield className="w-7 h-7 text-primary-foreground" />
          </div>
          <h1 className="text-2xl font-bold text-foreground">Employee Manager</h1>
          <p className="text-muted-foreground mt-1">Workforce management system</p>
        </div>

        <Card className="glass-card">
          <Tabs value={tab} onValueChange={setTab}>
            <CardHeader className="pb-4">
              <TabsList className="grid grid-cols-2 w-full">
                <TabsTrigger value="login" className="gap-2">
                  <LogIn className="w-4 h-4" /> Login
                </TabsTrigger>
                <TabsTrigger value="register" className="gap-2">
                  <UserPlus className="w-4 h-4" /> Register
                </TabsTrigger>
              </TabsList>
            </CardHeader>

            <CardContent>
              <TabsContent value="login" className="mt-0">
                <CardTitle className="text-lg mb-1">Welcome back</CardTitle>
                <CardDescription className="mb-6">Sign in to your account</CardDescription>
                <form onSubmit={handleLogin} className="space-y-4">
                  <div>
                    <Label htmlFor="login-email">Email</Label>
                    <Input id="login-email" type="email" value={loginEmail} onChange={(e) => setLoginEmail(e.target.value)} required placeholder="you@company.com" />
                  </div>
                  <div>
                    <Label htmlFor="login-password">Password</Label>
                    <div className="relative">
                      <Input id="login-password" type={showPassword ? "text" : "password"} value={loginPassword} onChange={(e) => setLoginPassword(e.target.value)} required />
                      <button type="button" className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground" onClick={() => setShowPassword(!showPassword)}>
                        {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                      </button>
                    </div>
                  </div>
                  <Button type="submit" className="w-full" disabled={loading}>
                    {loading ? "Signing in..." : "Sign In"}
                  </Button>
                </form>
              </TabsContent>

              <TabsContent value="register" className="mt-0">
                <CardTitle className="text-lg mb-1">New Employee</CardTitle>
                <CardDescription className="mb-6">Register and wait for chief approval</CardDescription>
                <form onSubmit={handleRegister} className="space-y-4">
                  <div>
                    <Label htmlFor="reg-name">Full Name</Label>
                    <Input id="reg-name" value={regName} onChange={(e) => setRegName(e.target.value)} required placeholder="John Doe" />
                  </div>
                  <div>
                    <Label htmlFor="reg-id">Employee ID Number</Label>
                    <Input id="reg-id" value={regIdNumber} onChange={(e) => setRegIdNumber(e.target.value)} required placeholder="EMP-001" />
                  </div>
                  <div>
                    <Label htmlFor="reg-email">Email</Label>
                    <Input id="reg-email" type="email" value={regEmail} onChange={(e) => setRegEmail(e.target.value)} required placeholder="you@company.com" />
                  </div>
                  <div>
                    <Label htmlFor="reg-password">Password</Label>
                    <Input id="reg-password" type="password" value={regPassword} onChange={(e) => setRegPassword(e.target.value)} required minLength={6} />
                  </div>
                  <div>
                    <Label htmlFor="reg-confirm">Confirm Password</Label>
                    <Input id="reg-confirm" type="password" value={regConfirmPassword} onChange={(e) => setRegConfirmPassword(e.target.value)} required minLength={6} />
                  </div>
                  <div>
                    <Label htmlFor="id-image">ID Image</Label>
                    <div className="mt-1">
                      {imagePreview ? (
                        <div className="relative rounded-lg overflow-hidden border border-border">
                          <img src={imagePreview} alt="ID Preview" className="w-full h-40 object-cover" />
                          <button type="button" onClick={() => { setIdImage(null); setImagePreview(null); }} className="absolute top-2 right-2 bg-destructive text-destructive-foreground rounded-full w-6 h-6 flex items-center justify-center text-xs">✕</button>
                        </div>
                      ) : (
                        <label htmlFor="id-image" className="flex flex-col items-center justify-center h-32 border-2 border-dashed border-border rounded-lg cursor-pointer hover:border-accent transition-colors">
                          <Upload className="w-6 h-6 text-muted-foreground mb-2" />
                          <span className="text-sm text-muted-foreground">Click to upload ID image</span>
                        </label>
                      )}
                      <input id="id-image" type="file" accept="image/*" onChange={handleImageChange} className="hidden" />
                    </div>
                  </div>
                  <Button type="submit" className="w-full" disabled={loading}>
                    {loading ? "Submitting..." : "Submit Registration"}
                  </Button>
                </form>
              </TabsContent>
            </CardContent>
          </Tabs>
        </Card>
      </div>
    </div>
  );
}
