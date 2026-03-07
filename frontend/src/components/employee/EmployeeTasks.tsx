import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/useAuth";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useToast } from "@/hooks/use-toast";
import { ClipboardList } from "lucide-react";

interface Task {
  id: string;
  title: string;
  description: string;
  status: string;
  assigned_to: string;
  created_at: string;
}

export default function EmployeeTasks() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingStatus, setUpdatingStatus] = useState<string | null>(null);

  const fetchTasks = async () => {
    if (!user?.id) return;
    
    try {
      // Fetch tasks assigned to the logged-in employee
      const { data, error } = await supabase
        .from("chief_tasks" as any)
        .select("*")
        .eq("assigned_to", user.id)
        .order("created_at", { ascending: false });
      
      if (error) {
        console.error("Error fetching tasks:", error);
      } else if (data) {
        setTasks(data);
      }
    } catch (err) {
      console.error("Error in fetchTasks:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [user]);

  const handleStatusChange = async (taskId: string, newStatus: string) => {
    setUpdatingStatus(taskId);
    try {
      const { error } = await supabase
        .from("chief_tasks" as any)
        .update({ status: newStatus })
        .eq("id", taskId);
      
      if (error) throw error;
      
      toast({ 
        title: "Status updated", 
        description: `Task status changed to ${newStatus.replace('_', ' ')}` 
      });
      fetchTasks();
    } catch (err: any) {
      console.error("Status update error:", err);
      toast({ 
        title: "Failed to update status", 
        description: err.message, 
        variant: "destructive" 
      });
    } finally {
      setUpdatingStatus(null);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "bg-green-500/20 text-green-700 border-green-300";
      case "in_progress":
        return "bg-blue-500/20 text-blue-700 border-blue-300";
      default:
        return "bg-yellow-500/20 text-yellow-700 border-yellow-300";
    }
  };

  if (loading) return <div className="text-center py-12 text-muted-foreground">Loading tasks...</div>;

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <ClipboardList className="w-5 h-5" /> My Assigned Tasks ({tasks.length})
      </h3>
      {tasks.length === 0 ? (
        <Card className="glass-card">
          <CardContent className="py-8 text-center text-muted-foreground">
            No tasks assigned to you yet
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-4">
          {tasks.map((task) => (
            <Card key={task.id} className="glass-card animate-slide-up">
              <CardContent className="py-4">
                <div className="flex items-start justify-between gap-4 flex-col sm:flex-row">
                  <div className="flex-1 min-w-0 w-full">
                    <div className="flex items-center gap-2 mb-2 flex-wrap">
                      <h4 className="font-semibold text-base">{task.title}</h4>
                      <Badge 
                        variant="outline" 
                        className={`text-xs ${getStatusColor(task.status)}`}
                      >
                        {task.status.replace('_', ' ')}
                      </Badge>
                    </div>
                    <p className="text-sm text-muted-foreground mb-3">{task.description}</p>
                    <p className="text-xs text-muted-foreground">
                      Assigned: <span className="text-foreground">{new Date(task.created_at).toLocaleDateString()}</span>
                    </p>
                  </div>
                  <div className="w-full sm:w-auto sm:min-w-[180px]">
                    <label className="text-xs text-muted-foreground block mb-1">Update Status:</label>
                    <Select 
                      value={task.status} 
                      onValueChange={(value) => handleStatusChange(task.id, value)}
                      disabled={updatingStatus === task.id}
                    >
                      <SelectTrigger className="w-full">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="pending">Pending</SelectItem>
                        <SelectItem value="in_progress">In Progress</SelectItem>
                        <SelectItem value="completed">Completed</SelectItem>
                      </SelectContent>
                    </Select>
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
