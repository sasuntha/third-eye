import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/useAuth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { Upload, ScanLine, FileText, Eye, Loader2 } from "lucide-react";

interface Document {
  id: string;
  document_name: string;
  report_url: string;
  blood_detected: boolean;
  blood_confidence: number;
  weapon_type: string | null;
  weapon_confidence: number;
  origin_coordinates: string | null;
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

  const fetchDocuments = async () => {
    if (!user) return;
    
    const { data } = await supabase
      .from("report_data")
      .select("*")
      .eq("uploaded_by", user.id)
      .order("created_at", { ascending: false });
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
      // Call the forensic analysis API directly
      const formData = new FormData();
      formData.append('file', imageFile);
      
      const response = await fetch(`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/forensic-analysis/analyze-and-report`, {
        method: "POST",
        body: formData,
      });

      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || 'Analysis failed');
      
      // Decode the base64 PDF
      if (!result.pdf_report?.pdf_base64) {
        throw new Error('PDF report not generated');
      }
      
      const pdfBytes = Uint8Array.from(atob(result.pdf_report.pdf_base64), c => c.charCodeAt(0));
      const pdfBlob = new Blob([pdfBytes], { type: 'application/pdf' });
      
      // Upload PDF to Supabase storage bucket "blood_report"
      const pdfFileName = `${user.id}/${docName.replace(/[^a-z0-9]/gi, '_')}_${Date.now()}.pdf`;
      const { error: uploadError } = await supabase.storage
        .from('blood_report')
        .upload(pdfFileName, pdfBlob, {
          contentType: 'application/pdf',
          upsert: false
        });
      
      if (uploadError) {
        console.error('Storage upload error:', uploadError);
        throw new Error(`Upload failed: ${uploadError.message}`);
      }
      
      // Get public URL for the uploaded PDF
      const { data: urlData } = supabase.storage
        .from('blood_report')
        .getPublicUrl(pdfFileName);
      
      const reportUrl = urlData.publicUrl;
      
      // Create a lightweight summary without base64 images (they're already in the PDF)
      const analysisSummary = {
        summary: result.summary,
        blood_detection: {
          verdict: result.blood_detection?.verdict,
          confidence: result.blood_detection?.confidence,
          analysis: result.blood_detection?.analysis,
          // Remove visualization (too large for database)
        },
        weapon_classification: {
          weapon_type: result.weapon_classification?.weapon_type,
          confidence: result.weapon_classification?.confidence,
          probabilities: result.weapon_classification?.probabilities,
          interpretation: result.weapon_classification?.interpretation,
          // Remove visualization
        },
        string_method: {
          status: result.string_method?.status,
          origin: result.string_method?.origin,
          statistics: result.string_method?.statistics,
          // Remove visualization
        }
      };
      
      // Save to report_data table
      const { error: insertError } = await supabase
        .from("report_data")
        .insert({
          uploaded_by: user.id,
          document_name: docName,
          report_url: reportUrl,
          analysis_summary: analysisSummary,
          blood_detected: result.summary?.blood_detected === 'Yes',
          blood_confidence: result.summary?.blood_confidence || 0,
          weapon_type: result.summary?.weapon_type || null,
          weapon_confidence: result.summary?.weapon_confidence || 0,
          origin_coordinates: result.summary?.origin_coordinates || null,
        });
      
      if (insertError) {
        console.error('Insert error details:', insertError);
        throw new Error(`Database insert failed: ${insertError.message}`);
      }

      toast({ 
        title: "Analysis Complete!", 
        description: "Report generated and saved successfully."
      });
      
      setImageFile(null);
      setImagePreview(null);
      setDocName("");
      fetchDocuments();
    } catch (err: any) {
      console.error('Analysis error:', err);
      toast({ 
        title: "Analysis failed", 
        description: err.message, 
        variant: "destructive" 
      });
    } finally {
      setAnalyzing(false);
    }
  };

  const viewDocImage = async (doc: Document) => {
    // Open the PDF report in a new tab
    window.open(doc.report_url, '_blank');
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
                      
                      {/* Analysis Summary */}
                      <div className="mt-2 space-y-1">
                        <div className="flex items-center gap-2 text-xs">
                          <span className={`px-2 py-0.5 rounded ${doc.blood_detected ? 'bg-red-500/20 text-red-400' : 'bg-gray-500/20 text-gray-400'}`}>
                            {doc.blood_detected ? '🩸 Blood Detected' : 'No Blood'}
                          </span>
                          <span className="text-muted-foreground">{doc.blood_confidence.toFixed(1)}%</span>
                        </div>
                        
                        {doc.weapon_type && (
                          <div className="text-xs text-muted-foreground">
                            🔫 Weapon: {doc.weapon_type} ({doc.weapon_confidence.toFixed(1)}%)
                          </div>
                        )}
                        
                        {doc.origin_coordinates && (
                          <div className="text-xs text-muted-foreground">
                            📍 Origin: {doc.origin_coordinates}
                          </div>
                        )}
                      </div>
                    </div>
                    
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="gap-1 shrink-0 ml-2" 
                      onClick={() => viewDocImage(doc)}
                    >
                      <Eye className="w-3 h-3" /> View Report
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
