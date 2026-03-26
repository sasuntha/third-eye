import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/useAuth";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { useToast } from "@/hooks/use-toast";
import { ClipboardList, HelpCircle, UserPlus } from "lucide-react";

interface Task {
  id: string;
  title: string;
  description: string;
  status: string;
  assigned_to: string;
  help_requested: boolean;
  help_message: string | null;
  helper_employee_id: string | null;
  created_at: string;
}

export default function EmployeeTasks() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [employees, setEmployees] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [updatingStatus, setUpdatingStatus] = useState<string | null>(null);
  const [helpDialogOpen, setHelpDialogOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [helpMessage, setHelpMessage] = useState("");

  const fetchTasks = async () => {
    if (!user?.id) return;
    
    try {
      // Fetch employees for name lookup
      const { data: employeesData } = await supabase
        .from("employees" as any)
        .select("id, name, employee_id");
      
      if (employeesData) {
        setEmployees(employeesData);
      }

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

  const handleRequestHelp = async () => {
    if (!selectedTask || !helpMessage.trim()) {
      toast({
        title: "Message required",
        description: "Please describe what help you need",
        variant: "destructive"
      });
      return;
    }

    try {
      const { error } = await supabase
        .from("chief_tasks" as any)
        .update({
          help_requested: true,
          help_message: helpMessage
        })
        .eq("id", selectedTask.id);

      if (error) throw error;

      toast({
        title: "Help request sent",
        description: "The chief will be notified and can assign someone to help you"
      });

      setHelpDialogOpen(false);
      setHelpMessage("");
      setSelectedTask(null);
      fetchTasks();
    } catch (err: any) {
      console.error("Help request error:", err);
      toast({
        title: "Failed to send help request",
        description: err.message,
        variant: "destructive"
      });
    }
  };

  const getHelperName = (helperId: string | null) => {
    if (!helperId) return null;
    const helper = employees.find(e => e.id === helperId);
    return helper ? `${helper.name} (${helper.employee_id})` : "Unknown";
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
                <div className="space-y-4">
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
                        {task.help_requested && !task.helper_employee_id && (
                          <Badge variant="outline" className="text-xs bg-yellow-500/20 text-yellow-700 border-yellow-300">
                            Help Requested
                          </Badge>
                        )}
                        {task.helper_employee_id && (
                          <Badge variant="outline" className="text-xs bg-blue-500/20 text-blue-700 border-blue-300">
                            <UserPlus className="w-3 h-3 mr-1" /> Helper Assigned
                          </Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground mb-3">{task.description}</p>
                      <p className="text-xs text-muted-foreground">
                        Assigned: <span className="text-foreground">{new Date(task.created_at).toLocaleDateString()}</span>
                      </p>
                      {task.helper_employee_id && (
                        <div className="mt-2 p-2 bg-blue-500/10 rounded border border-blue-300/50">
                          <p className="text-xs font-medium text-blue-700 mb-1 flex items-center gap-1">
                            <UserPlus className="w-3 h-3" />
                            Helper Assigned:
                          </p>
                          <p className="text-sm text-foreground font-medium">{getHelperName(task.helper_employee_id)}</p>
                        </div>
                      )}
                      {task.help_requested && task.help_message && (
                        <div className="mt-2 p-2 bg-accent/10 rounded border border-accent/20">
                          <p className="text-xs font-medium text-accent mb-1">Your help request:</p>
                          <p className="text-xs text-muted-foreground">{task.help_message}</p>
                        </div>
                      )}
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
                  
                  {!task.help_requested && !task.helper_employee_id && (
                    <div className="flex justify-end pt-2 border-t">
                      <Dialog open={helpDialogOpen && selectedTask?.id === task.id} onOpenChange={(open) => {
                        setHelpDialogOpen(open);
                        if (!open) {
                          setSelectedTask(null);
                          setHelpMessage("");
                        }
                      }}>
                        <DialogTrigger asChild>
                          <Button 
                            variant="outline" 
                            size="sm" 
                            className="gap-2"
                            onClick={() => setSelectedTask(task)}
                          >
                            <HelpCircle className="w-4 h-4" />
                            Request Help
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>Request Help</DialogTitle>
                          </DialogHeader>
                          <div className="space-y-4">
                            <div>
                              <Label className="text-sm font-medium mb-2 block">Task: {task.title}</Label>
                              <p className="text-sm text-muted-foreground">{task.description}</p>
                            </div>
                            <div>
                              <Label htmlFor="help-message">What help do you need?</Label>
                              <Textarea
                                id="help-message"
                                value={helpMessage}
                                onChange={(e) => setHelpMessage(e.target.value)}
                                placeholder="Describe what help you need with this task..."
                                rows={4}
                                className="mt-1"
                              />
                            </div>
                            <div className="flex gap-2 justify-end">
                              <Button 
                                variant="outline" 
                                onClick={() => {
                                  setHelpDialogOpen(false);
                                  setHelpMessage("");
                                  setSelectedTask(null);
                                }}
                              >
                                Cancel
                              </Button>
                              <Button onClick={handleRequestHelp}>
                                Send Request
                              </Button>
                            </div>
                          </div>
                        </DialogContent>
                      </Dialog>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
