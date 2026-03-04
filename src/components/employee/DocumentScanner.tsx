import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/useAuth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { Upload, ScanLine, FileText, Eye, Loader2 } from "lucide-react";

interface Document {
  id: string;
  document_name: string;
  file_url: string;
  analysis_result: string | null;
  created_at: string;
}

export default function DocumentScanner() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [imageFile, setImageFile] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);
  const [docName, setDocName] = useState("");
  const [viewingDoc, setViewingDoc] = useState<Document | null>(null);
  const [docImageUrl, setDocImageUrl] = useState<string | null>(null);

  const fetchDocuments = async () => {
    if (!user) return;
    const { data } = await supabase.from("documents").select("*").eq("uploaded_by", user.id).order("created_at", { ascending: false });
    if (data) setDocuments(data);
    setLoading(false);
  };

  useEffect(() => { fetchDocuments(); }, [user]);

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      setImageFile(file);
      setImagePreview(URL.createObjectURL(file));
    }
  };

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || !imageFile || !docName) return;
    setAnalyzing(true);
    try {
      // Upload image to storage
      const fileExt = imageFile.name.split(".").pop();
      const filePath = `${user.id}/${Date.now()}.${fileExt}`;
      const { error: uploadError } = await supabase.storage.from("documents").upload(filePath, imageFile);
      if (uploadError) throw uploadError;

      // Get a signed URL for the AI to access
      const { data: urlData } = await supabase.storage.from("documents").createSignedUrl(filePath, 600);
      if (!urlData?.signedUrl) throw new Error("Failed to generate URL");

      // Call the analyze edge function
      const { data: { session } } = await supabase.auth.getSession();
      const response = await fetch(`${import.meta.env.VITE_SUPABASE_URL}/functions/v1/analyze-document`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${session?.access_token}`,
        },
        body: JSON.stringify({ imageUrl: urlData.signedUrl, documentName: docName }),
      });

      const result = await response.json();
      if (!response.ok) throw new Error(result.error);

      toast({ title: "Document analyzed successfully!" });
      setImageFile(null);
      setImagePreview(null);
      setDocName("");
      fetchDocuments();
    } catch (err: any) {
      toast({ title: "Analysis failed", description: err.message, variant: "destructive" });
    } finally {
      setAnalyzing(false);
    }
  };

  const viewDocImage = async (doc: Document) => {
    const { data } = await supabase.storage.from("documents").createSignedUrl(doc.file_url, 300);
    if (data?.signedUrl) {
      setDocImageUrl(data.signedUrl);
      setViewingDoc(doc);
    }
  };

  if (loading) return <div className="text-center py-12 text-muted-foreground">Loading...</div>;

  return (
    <div className="space-y-8">
      {/* Upload & Analyze */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <ScanLine className="w-5 h-5 text-accent" /> Scan & Analyze Document
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleAnalyze} className="space-y-4">
            <div>
              <Label>Document Name</Label>
              <Input value={docName} onChange={(e) => setDocName(e.target.value)} required placeholder="e.g. Invoice #123" />
            </div>
            <div>
              <Label>Upload Image</Label>
              <div className="mt-1">
                {imagePreview ? (
                  <div className="relative rounded-lg overflow-hidden border border-border">
                    <img src={imagePreview} alt="Preview" className="w-full h-48 object-cover" />
                    <button type="button" onClick={() => { setImageFile(null); setImagePreview(null); }} className="absolute top-2 right-2 bg-destructive text-destructive-foreground rounded-full w-6 h-6 flex items-center justify-center text-xs">✕</button>
                  </div>
                ) : (
                  <label htmlFor="doc-image" className="flex flex-col items-center justify-center h-32 border-2 border-dashed border-border rounded-lg cursor-pointer hover:border-accent transition-colors">
                    <Upload className="w-6 h-6 text-muted-foreground mb-2" />
                    <span className="text-sm text-muted-foreground">Click to upload document image</span>
                  </label>
                )}
                <input id="doc-image" type="file" accept="image/*" onChange={handleImageChange} className="hidden" />
              </div>
            </div>
            <Button type="submit" disabled={analyzing || !imageFile || !docName} className="gap-2">
              {analyzing ? <><Loader2 className="w-4 h-4 animate-spin" /> Analyzing...</> : <><ScanLine className="w-4 h-4" /> Analyze Document</>}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Document List */}
      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <FileText className="w-5 h-5" /> My Documents ({documents.length})
        </h3>
        {documents.length === 0 ? (
          <Card className="glass-card"><CardContent className="py-8 text-center text-muted-foreground">No documents yet. Upload one above!</CardContent></Card>
        ) : (
          <div className="grid gap-4 md:grid-cols-2">
            {documents.map((doc) => (
              <Card key={doc.id} className="glass-card animate-slide-up">
                <CardContent className="py-4">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h4 className="font-semibold text-sm truncate">{doc.document_name}</h4>
                      <p className="text-xs text-muted-foreground mt-1">{new Date(doc.created_at).toLocaleDateString()}</p>
                      {doc.analysis_result && <p className="text-xs text-muted-foreground mt-2 line-clamp-3">{doc.analysis_result}</p>}
                    </div>
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button size="sm" variant="outline" className="gap-1 shrink-0 ml-2" onClick={() => viewDocImage(doc)}>
                          <Eye className="w-3 h-3" /> View
                        </Button>
                      </DialogTrigger>
                      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                        <DialogHeader><DialogTitle>{doc.document_name}</DialogTitle></DialogHeader>
                        {docImageUrl && viewingDoc?.id === doc.id && <img src={docImageUrl} alt="Document" className="w-full rounded-lg mb-4" />}
                        {doc.analysis_result && (
                          <div>
                            <h4 className="font-semibold text-sm mb-2">Analysis Result</h4>
                            <div className="p-4 bg-muted rounded-lg text-sm whitespace-pre-wrap">{doc.analysis_result}</div>
                          </div>
                        )}
                      </DialogContent>
                    </Dialog>
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
