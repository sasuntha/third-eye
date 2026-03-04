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
  full_name: string;
  employee_id_number: string;
  id_image_url: string;
  status: string;
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
      .from("registration_requests")
      .select("*")
      .order("created_at", { ascending: false });
    if (!error && data) setRequests(data);
    setLoading(false);
  };

  useEffect(() => { fetchRequests(); }, []);

  const handleAction = async (requestId: string, action: "approved" | "rejected") => {
    setProcessing(requestId);
    try {
      const { data: { session } } = await supabase.auth.getSession();
      const response = await fetch(`${import.meta.env.VITE_SUPABASE_URL}/functions/v1/approve-registration`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({ requestId, action }),
      });
      const result = await response.json();
      if (!response.ok) throw new Error(result.error);
      toast({ title: `Registration ${action}` });
      fetchRequests();
    } catch (err: any) {
      toast({ title: "Action failed", description: err.message, variant: "destructive" });
    } finally {
      setProcessing(null);
    }
  };

  const viewImage = async (filePath: string) => {
    const { data } = await supabase.storage.from("id-images").createSignedUrl(filePath, 300);
    if (data?.signedUrl) {
      setImageUrl(data.signedUrl);
      setViewingImage(filePath);
    }
  };

  const pending = requests.filter((r) => r.status === "pending");
  const processed = requests.filter((r) => r.status !== "pending");

  if (loading) return <div className="text-center py-12 text-muted-foreground">Loading requests...</div>;

  return (
    <div className="space-y-6">
      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <Clock className="w-5 h-5 text-accent" /> Pending Requests ({pending.length})
        </h3>
        {pending.length === 0 ? (
          <Card className="glass-card"><CardContent className="py-8 text-center text-muted-foreground">No pending requests</CardContent></Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {pending.map((req) => (
              <Card key={req.id} className="glass-card animate-slide-up">
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between">
                    <CardTitle className="text-base">{req.full_name}</CardTitle>
                    <Badge variant="outline" className="text-accent border-accent">Pending</Badge>
                  </div>
                </CardHeader>
                <CardContent className="space-y-3">
                  <p className="text-sm text-muted-foreground">ID: <span className="text-foreground font-medium">{req.employee_id_number}</span></p>
                  <p className="text-xs text-muted-foreground">{new Date(req.created_at).toLocaleDateString()}</p>
                  <div className="flex gap-2">
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button variant="outline" size="sm" className="gap-1" onClick={() => viewImage(req.id_image_url)}>
                          <Eye className="w-3 h-3" /> View ID
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-lg">
                        <DialogHeader><DialogTitle>ID Image - {req.full_name}</DialogTitle></DialogHeader>
                        {imageUrl && <img src={imageUrl} alt="Employee ID" className="w-full rounded-lg" />}
                      </DialogContent>
                    </Dialog>
                    <Button size="sm" className="gap-1 bg-success hover:bg-success/90 text-success-foreground" onClick={() => handleAction(req.id, "approved")} disabled={processing === req.id}>
                      <Check className="w-3 h-3" /> Approve
                    </Button>
                    <Button size="sm" variant="destructive" className="gap-1" onClick={() => handleAction(req.id, "rejected")} disabled={processing === req.id}>
                      <X className="w-3 h-3" /> Reject
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>

      {processed.length > 0 && (
        <div>
          <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <UserCheck className="w-5 h-5" /> Processed ({processed.length})
          </h3>
          <div className="grid gap-3 md:grid-cols-2">
            {processed.map((req) => (
              <Card key={req.id} className="glass-card opacity-75">
                <CardContent className="py-4 flex items-center justify-between">
                  <div>
                    <p className="font-medium text-sm">{req.full_name}</p>
                    <p className="text-xs text-muted-foreground">ID: {req.employee_id_number}</p>
                  </div>
                  <Badge variant={req.status === "approved" ? "default" : "destructive"}>
                    {req.status}
                  </Badge>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
