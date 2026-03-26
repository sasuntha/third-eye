import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { supabase } from "@/integrations/supabase/client";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { useToast } from "@/hooks/use-toast";
import { UserPlus, LogIn, Upload, Eye, EyeOff } from "lucide-react";
import EyeIcon from "@/components/icons/EyeIcon";

// Backend API URL
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

interface LoginResponse {
  status: string;
  message: string;
  user?: {
    id: string;
    email: string;
    full_name: string;
    employee_id: string;
    role: string;
  };
  role?: string;
}

export default function Login() {
  const { toast } = useToast();
  const navigate = useNavigate();
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
      // Call backend login endpoint
      const response = await fetch(`${API_URL}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          email: loginEmail,
          password: loginPassword,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Login failed");
      }

      const data: LoginResponse = await response.json();

      if (data.status === "success" && data.user) {
        // Store user data and role in localStorage for session management
        localStorage.setItem(
          "user",
          JSON.stringify({
            id: data.user.id,
            email: data.user.email,
            full_name: data.user.full_name,
            employee_id: data.user.employee_id,
            role: data.role,
          })
        );

        // Dispatch a custom event to notify other listeners (e.g., useAuth hook)
        window.dispatchEvent(new Event("userUpdated"));

        toast({
          title: "Login successful",
          description: `Welcome, ${data.user.full_name}!`,
        });

        // Small delay to ensure auth context updates before navigation
        setTimeout(() => {
          // Redirect based on role
          if (data.role === "chief") {
            navigate("/chief-dashboard", { replace: true });
          } else {
            navigate("/employee-dashboard", { replace: true });
          }
        }, 100);
      } else {
        throw new Error(data.message || "Login failed");
      }
    } catch (err: any) {
      toast({
        title: "Login failed",
        description: err.message || "Invalid email or password",
        variant: "destructive",
      });
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
      // 1. Upload ID image to id_images bucket
      const fileExt = idImage.name.split(".").pop();
      const timestamp = Date.now();
      const fileName = `${regIdNumber}-${timestamp}.${fileExt}`;

      console.log("Uploading image:", fileName);
      const { error: uploadError } = await supabase.storage
        .from("id_images")
        .upload(fileName, idImage);

      if (uploadError) {
        console.error("Upload error:", uploadError);
        throw uploadError;
      }

      // 2. Get the public URL of the uploaded image
      const { data: urlData } = supabase.storage
        .from("id_images")
        .getPublicUrl(fileName);

      const imageUrl = urlData.publicUrl;
      console.log("Image uploaded, URL:", imageUrl);

      // 3. Insert registration data into temp_register table
      console.log("Inserting into temp_register:", {
        name: regName,
        employee_id: regIdNumber,
        email: regEmail,
        id_image_url: imageUrl,
      });

      const { data: insertData, error: insertError } = await supabase
        .from("temp_register" as any)
        .insert({
          name: regName,
          employee_id: regIdNumber,
          email: regEmail,
          password: regPassword,
          id_image_url: imageUrl,
        })
        .select();

      if (insertError) {
        console.error("Insert error details:", insertError);
        throw new Error(`Database error: ${insertError.message} (Code: ${insertError.code}, Details: ${insertError.details})`);
      }

      console.log("Registration successful:", insertData);
      toast({
        title: "Registration submitted!",
        description: "Your request has been sent to the chief for approval. You'll be able to log in once approved.",
      });

      // Clear form
      setTab("login");
      setRegName("");
      setRegIdNumber("");
      setRegEmail("");
      setRegPassword("");
      setRegConfirmPassword("");
      setIdImage(null);
      setImagePreview(null);
    } catch (err: any) {
      console.error("Registration error:", err);
      toast({
        title: "Registration failed",
        description: err.message || "Unknown error occurred",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex ">
      {/* Left Side - Branding */}
      <div className="hidden lg:flex lg:w-1/2 bg-gradient-to-br from-primary via-primary/90 to-primary/80 relative overflow-hidden rounded-3xl mt-5 mb-5 ml-5">
        {/* Animated background pattern */}
        <div className="absolute inset-0 opacity-10">
          <div className="absolute top-0 left-0 w-96 h-96 bg-white rounded-full blur-3xl animate-pulse" />
          <div className="absolute bottom-0 right-0 w-96 h-96 bg-white rounded-full blur-3xl animate-pulse delay-700" />
        </div>

        {/* Content */}
        <div className="relative z-10 flex flex-col justify-center items-center w-full p-12 text-white">
          {/* Logo/Icon */}
          <div className="mb-8 relative">
            <div className="absolute inset-0 bg-white/20 rounded-3xl blur-2xl animate-pulse" />
            <div className="relative bg-white/10 backdrop-blur-sm p-8 rounded-3xl border border-white/20 shadow-2xl">
              <EyeIcon className="w-24 h-24 text-white drop-shadow-lg" />
            </div>
          </div>

          {/* App Name */}
          <h1 className="text-6xl font-bold mb-4 tracking-tight">Third-Eye</h1>


          {/* Features */}

        </div>
      </div>

      {/* Right Side - Login/Register Forms */}
      <div className="w-full lg:w-1/2 flex items-center justify-center p-4 bg-background">
        <div className="w-full max-w-md animate-fade-in">
          {/* Mobile Logo */}
          <div className="lg:hidden text-center mb-8">
            <div className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-primary mb-4">
              <EyeIcon className="w-8 h-8 text-primary-foreground" />
            </div>
            <h1 className="text-3xl font-bold text-foreground">Third-Eye</h1>
          </div>

          <Card className="glass-card border-2 shadow-xl">
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
                      <Input id="reg-name" value={regName} onChange={(e) => setRegName(e.target.value)} required placeholder="Sasun Tovmasyan" />
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
    </div>
  );
}
