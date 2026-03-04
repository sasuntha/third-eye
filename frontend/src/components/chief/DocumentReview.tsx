import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { FileText, Eye } from "lucide-react";

interface Document {
  id: string;
  document_name: string;
  file_url: string;
  analysis_result: string | null;
  uploaded_by: string;
  created_at: string;
}

interface Profile {
  user_id: string;
  full_name: string;
}

export default function DocumentReview() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [profiles, setProfiles] = useState<Profile[]>([]);
  const [loading, setLoading] = useState(true);
  const [viewingDoc, setViewingDoc] = useState<Document | null>(null);
  const [docImageUrl, setDocImageUrl] = useState<string | null>(null);

  const fetchDocuments = async () => {
    const { data } = await supabase.from("documents").select("*").order("created_at", { ascending: false });
    if (data) {
      setDocuments(data);
      const userIds = [...new Set(data.map((d) => d.uploaded_by))];
      if (userIds.length > 0) {
        const { data: profs } = await supabase.from("profiles").select("user_id, full_name").in("user_id", userIds);
        if (profs) setProfiles(profs);
      }
    }
    setLoading(false);
  };

  useEffect(() => { fetchDocuments(); }, []);

  const getUploaderName = (id: string) => profiles.find((p) => p.user_id === id)?.full_name || "Unknown";

  const viewDocImage = async (doc: Document) => {
    const { data } = await supabase.storage.from("documents").createSignedUrl(doc.file_url, 300);
    if (data?.signedUrl) {
      setDocImageUrl(data.signedUrl);
      setViewingDoc(doc);
    }
  };

  if (loading) return <div className="text-center py-12 text-muted-foreground">Loading documents...</div>;

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <FileText className="w-5 h-5" /> Employee Documents ({documents.length})
      </h3>
      {documents.length === 0 ? (
        <Card className="glass-card"><CardContent className="py-8 text-center text-muted-foreground">No documents uploaded yet</CardContent></Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2">
          {documents.map((doc) => (
            <Card key={doc.id} className="glass-card animate-slide-up">
              <CardContent className="py-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1 min-w-0">
                    <h4 className="font-semibold text-sm truncate">{doc.document_name}</h4>
                    <p className="text-xs text-muted-foreground mt-1">By: {getUploaderName(doc.uploaded_by)}</p>
                    <p className="text-xs text-muted-foreground">{new Date(doc.created_at).toLocaleDateString()}</p>
                    {doc.analysis_result && (
                      <p className="text-xs text-muted-foreground mt-2 line-clamp-3">{doc.analysis_result}</p>
                    )}
                  </div>
                  <Dialog>
                    <DialogTrigger asChild>
                      <Button size="sm" variant="outline" className="gap-1 shrink-0 ml-2" onClick={() => viewDocImage(doc)}>
                        <Eye className="w-3 h-3" /> View
                      </Button>
                    </DialogTrigger>
                    <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                      <DialogHeader><DialogTitle>{doc.document_name}</DialogTitle></DialogHeader>
                      {docImageUrl && <img src={docImageUrl} alt="Document" className="w-full rounded-lg mb-4" />}
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
  );
}
