import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { FileText, Eye, User } from "lucide-react";

interface Report {
  id: string;
  uploaded_by: string;
  document_name: string;
  report_url: string;
  analysis_summary: any;
  blood_detected: boolean;
  blood_confidence: number;
  weapon_type: string | null;
  weapon_confidence: number;
  origin_coordinates: string | null;
  created_at: string;
}

interface Employee {
  id: string;
  name: string;
  employee_id: string;
}

export default function DocumentReview() {
  const [reports, setReports] = useState<Report[]>([]);
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchDocuments = async () => {
    try {
      // Fetch all reports
      const { data: reportsData, error: reportsError } = await supabase
        .from("report_data" as any)
        .select("*")
        .order("created_at", { ascending: false });

      if (reportsError) {
        console.error("Error fetching reports:", reportsError);
      } else if (reportsData) {
        console.log("Reports fetched:", reportsData);
        setReports(reportsData);
      }

      // Fetch employees for name lookup
      const { data: employeesData, error: employeesError } = await supabase
        .from("employees" as any)
        .select("id, name, employee_id");

      if (employeesError) {
        console.error("Error fetching employees:", employeesError);
      } else if (employeesData) {
        console.log("Employees fetched:", employeesData);
        setEmployees(employeesData);
      }
    } catch (err) {
      console.error("Error in fetchDocuments:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const getEmployeeName = (id: string) => {
    if (!id) return "Unknown Employee";
    
    // Convert to string for comparison since IDs might be stored differently
    const employee = employees.find((e) => String(e.id) === String(id));
    
    if (employee) {
      return `${employee.name} (${employee.employee_id})`;
    }
    
    // Debug: log if not found
    console.log('Employee not found for ID:', id, 'Available employees:', employees);
    return "Unknown Employee";
  };

  const openReport = (reportUrl: string) => {
    window.open(reportUrl, '_blank');
  };

  if (loading) return <div className="text-center py-12 text-muted-foreground">Loading documents...</div>;

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <FileText className="w-5 h-5" /> Forensic Analysis Reports ({reports.length})
      </h3>
      {reports.length === 0 ? (
        <Card className="glass-card">
          <CardContent className="py-8 text-center text-muted-foreground">
            No reports uploaded yet
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {reports.map((report) => (
            <Card key={report.id} className="glass-card animate-slide-up">
              <CardContent className="py-4">
                <div className="space-y-3">
                  <div className="flex items-start justify-between">
                    <div className="flex-1 min-w-0">
                      <h4 className="font-semibold text-sm truncate mb-1">{report.document_name}</h4>
                      <div className="flex items-center gap-1 text-xs text-muted-foreground mb-2">
                        <User className="w-3 h-3" />
                        <span>{getEmployeeName(report.uploaded_by)}</span>
                      </div>
                      <p className="text-xs text-muted-foreground">
                        {new Date(report.created_at).toLocaleString()}
                      </p>
                    </div>
                  </div>

                  {/* Analysis Summary */}
                  <div className="space-y-2 pt-2 border-t">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-muted-foreground">Blood Detected:</span>
                      <Badge 
                        variant="outline" 
                        className={`text-xs ${report.blood_detected ? 'bg-red-500/20 text-red-700 border-red-300' : 'bg-gray-500/20 text-gray-700 border-gray-300'}`}
                      >
                        {report.blood_detected ? 'Yes' : 'No'} ({report.blood_confidence.toFixed(1)}%)
                      </Badge>
                    </div>
                    {report.weapon_type && (
                      <div className="flex items-center justify-between">
                        <span className="text-xs font-medium text-muted-foreground">Weapon Type:</span>
                        <Badge variant="outline" className="text-xs">
                          {report.weapon_type} ({report.weapon_confidence.toFixed(1)}%)
                        </Badge>
                      </div>
                    )}
                    {report.origin_coordinates && (
                      <div className="text-xs">
                        <span className="font-medium text-muted-foreground">Origin:</span>
                        <span className="ml-1 text-foreground">{report.origin_coordinates}</span>
                      </div>
                    )}
                  </div>

                  {/* Actions */}
                  <div className="pt-2">
                    <Button 
                      size="sm" 
                      variant="outline" 
                      className="gap-2 w-full"
                      onClick={() => openReport(report.report_url)}
                    >
                      <Eye className="w-4 h-4" /> View Report
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
