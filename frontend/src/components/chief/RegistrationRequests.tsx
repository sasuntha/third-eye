import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/useAuth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { Check, X, Eye, Clock, UserCheck } from "lucide-react";

interface RegistrationRequest {
  id: string;
  name: string;
  employee_id: string;
  email: string;
  password: string;
  id_image_url: string;
  created_at: string;
}

export default function RegistrationRequests() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [requests, setRequests] = useState<RegistrationRequest[]>([]);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState<string | null>(null);
  const [viewingImage, setViewingImage] = useState<string | null>(null);
  const [imageUrl, setImageUrl] = useState<string | null>(null);

  const fetchRequests = async () => {
    const { data, error } = await supabase
      .from("temp_register" as any)
      .select("*")
      .order("created_at", { ascending: false });
    if (!error && data) setRequests(data);
    setLoading(false);
  };

  useEffect(() => { fetchRequests(); }, []);

  const handleApprove = async (request: RegistrationRequest) => {
    setProcessing(request.id);
    try {
      // 1. Insert into employees table
      const { error: insertError } = await supabase
        .from("employees" as any)
        .insert({
          email: request.email,
          password: request.password,
          name: request.name,
          employee_id: request.employee_id,
          role: 'employee',
          id_image_url: request.id_image_url,
        });

      if (insertError) throw insertError;

      // 2. Delete from temp_register
      const { error: deleteError } = await supabase
        .from("temp_register" as any)
        .delete()
        .eq("id", request.id);

      if (deleteError) throw deleteError;

      toast({
        title: "Registration approved",
        description: `${request.name} has been added as an employee.`
      });
      fetchRequests();
    } catch (err: any) {
      console.error("Approval error:", err);
      toast({
        title: "Approval failed",
        description: err.message || "Failed to approve registration",
        variant: "destructive"
      });
    } finally {
      setProcessing(null);
    }
  };

  const handleReject = async (requestId: string, requestName: string) => {
    setProcessing(requestId);
    try {
      // Delete from temp_register
      const { error: deleteError } = await supabase
        .from("temp_register" as any)
        .delete()
        .eq("id", requestId);

      if (deleteError) throw deleteError;

      toast({
        title: "Registration rejected",
        description: `${requestName}'s registration has been rejected.`
      });
      fetchRequests();
    } catch (err: any) {
      console.error("Rejection error:", err);
      toast({
        title: "Rejection failed",
        description: err.message || "Failed to reject registration",
        variant: "destructive"
      });
    } finally {
      setProcessing(null);
    }
  };

  const viewImage = (imageUrl: string) => {
    setImageUrl(imageUrl);
    setViewingImage(imageUrl);
  };

  if (loading) return <div className="text-center py-12 text-muted-foreground">Loading requests...</div>;

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Clock className="w-5 h-5 text-accent" /> Pending Requests ({requests.length})
        </h3>
        {requests.length === 0 ? (
          <Card className="glass-card"><CardContent className="py-8 text-center text-muted-foreground">No pending requests</CardContent></Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {requests.map((req) => (
              <Card key={req.id} className="glass-card animate-slide-up">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">{req.name}</CardTitle>
                    <Badge variant="outline" className="text-accent border-accent">Pending</Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm text-muted-foreground">
                    Employee ID: <span className="text-foreground font-medium">{req.employee_id}</span>
                  </p>
                  <p className="text-sm text-muted-foreground">
                    Email: <span className="text-foreground font-medium">{req.email}</span>
                  </p>
                  <p className="text-xs text-muted-foreground">{new Date(req.created_at).toLocaleDateString()}</p>
                  <div className="flex gap-2 flex-wrap">
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button variant="outline" size="sm" className="gap-1" onClick={() => viewImage(req.id_image_url)}>
                          <Eye className="w-3 h-3" /> View ID
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-lg">
                        <DialogHeader><DialogTitle>ID Image - {req.name}</DialogTitle></DialogHeader>
                        {imageUrl && <img src={imageUrl} alt="Employee ID" className="w-full rounded-lg" />}
                      </DialogContent>
                    </Dialog>
                    <Button
                      size="sm"
                      className="gap-1 bg-success hover:bg-success/90 text-success-foreground"
                      onClick={() => handleApprove(req)}
                      disabled={processing === req.id}
                    >
                      <Check className="w-3 h-3" /> {processing === req.id ? "Processing..." : "Approve"}
                    </Button>
                    <Button
                      size="sm"
                      variant="destructive"
                      className="gap-1"
                      onClick={() => handleReject(req.id, req.name)}
                      disabled={processing === req.id}
                    >
                      <X className="w-3 h-3" /> {processing === req.id ? "Processing..." : "Reject"}
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
