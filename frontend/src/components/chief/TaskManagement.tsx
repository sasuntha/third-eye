import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/useAuth";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Badge } from "@/components/ui/badge";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { Plus, ClipboardList, UserPlus, AlertCircle } from "lucide-react";

interface Employee {
  id: string;
  name: string;
  email: string;
  employee_id: string;
}

interface Task {
  id: string;
  title: string;
  description: string;
  assigned_to: string;
  status: string;
  help_requested: boolean;
  help_message: string | null;
  helper_employee_id: string | null;
  created_at: string;
}

export default function TaskManagement() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [assignDialogOpen, setAssignDialogOpen] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [selectedHelper, setSelectedHelper] = useState("");

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [assignTo, setAssignTo] = useState("");

  const fetchData = async () => {
    try {
      // Get all employees from employees table
      const { data: employeesData, error: empError } = await supabase
        .from("employees" as any)
        .select("id, name, email, employee_id")
        .eq("role", "employee");

      if (empError) {
        console.error("Error fetching employees:", empError);
      } else if (employeesData) {
        setEmployees(employeesData);
      }

      // Get tasks created by current chief
      if (user?.id) {
        const { data: tasksData, error: tasksError } = await supabase
          .from("chief_tasks" as any)
          .select("*")
          .eq("created_by", user.id)
          .order("created_at", { ascending: false });

        if (tasksError) {
          console.error("Error fetching tasks:", tasksError);
        } else if (tasksData) {
          setTasks(tasksData);
        }
      }
    } catch (err) {
      console.error("Error in fetchData:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [user]);

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || !assignTo) {
      toast({
        title: "Error",
        description: "Please select an employee to assign",
        variant: "destructive"
      });
      return;
    }

    setCreating(true);
    try {
      const { error } = await supabase
        .from("chief_tasks" as any)
        .insert({
          title,
          description,
          assigned_to: assignTo,
          created_by: user.id,
          status: "pending",
        });

      if (error) throw error;

      toast({ title: "Task created successfully" });
      setTitle("");
      setDescription("");
      setAssignTo("");
      fetchData();
    } catch (err: any) {
      console.error("Create task error:", err);
      toast({
        title: "Failed to create task",
        description: err.message || "Unknown error occurred",
        variant: "destructive"
      });
    } finally {
      setCreating(false);
    }
  };

  const getEmployeeName = (id: string) => {
    const employee = employees.find((e) => e.id === id);
    return employee ? `${employee.name} (${employee.employee_id})` : "Unknown";
  };

  const handleAssignHelper = async () => {
    if (!selectedTask || !selectedHelper) {
      toast({
        title: "Please select a helper",
        variant: "destructive"
      });
      return;
    }

    try {
      const { error } = await supabase
        .from("chief_tasks" as any)
        .update({
          helper_employee_id: selectedHelper,
          help_requested: false // Mark as resolved
        })
        .eq("id", selectedTask.id);

      if (error) throw error;

      toast({
        title: "Helper assigned successfully",
        description: `${getEmployeeName(selectedHelper)} has been assigned to help`
      });

      setAssignDialogOpen(false);
      setSelectedHelper("");
      setSelectedTask(null);
      fetchData();
    } catch (err: any) {
      console.error("Assign helper error:", err);
      toast({
        title: "Failed to assign helper",
        description: err.message,
        variant: "destructive"
      });
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

  if (loading) return <div className="text-center py-12 text-muted-foreground">Loading...</div>;

  return (
    <div className="space-y-8">
      {/* Create Task Form */}
      <Card className="glass-card">
        <CardHeader>
          <CardTitle className="text-lg flex items-center gap-2">
            <Plus className="w-5 h-5 text-accent" /> Create New Task
          </CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleCreateTask} className="space-y-4">
            <div className="grid gap-4 sm:grid-cols-2">
              <div>
                <Label htmlFor="task-title">Task Title</Label>
                <Input
                  id="task-title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  required
                  placeholder="Enter task title"
                />
              </div>
              <div>
                <Label htmlFor="assign-to">Assign To</Label>
                <Select value={assignTo} onValueChange={setAssignTo} required>
                  <SelectTrigger id="assign-to">
                    <SelectValue placeholder="Select employee" />
                  </SelectTrigger>
                  <SelectContent>
                    {employees.length === 0 ? (
                      <div className="px-2 py-1 text-sm text-muted-foreground">
                        No employees available
                      </div>
                    ) : (
                      employees.map((emp) => (
                        <SelectItem key={emp.id} value={emp.id}>
                          {emp.name} ({emp.employee_id})
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label htmlFor="task-description">Description</Label>
              <Textarea
                id="task-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
                placeholder="Describe the task in detail..."
                rows={4}
              />
            </div>
            <Button type="submit" disabled={creating || !assignTo || employees.length === 0}>
              {creating ? "Creating..." : "Create Task"}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Task List */}
      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <ClipboardList className="w-5 h-5" /> My Created Tasks ({tasks.length})
        </h3>
        {tasks.length === 0 ? (
          <Card className="glass-card">
            <CardContent className="py-8 text-center text-muted-foreground">
              No tasks created yet. Create your first task above!
            </CardContent>
          </Card>
        ) : (
          <div className="grid gap-4">
            {tasks.map((task) => (
              <Card key={task.id} className="glass-card animate-slide-up">
                <CardContent className="py-4">
                  <div className="space-y-3">
                    <div className="flex items-start justify-between gap-4">
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center gap-2 mb-2 flex-wrap">
                          <h4 className="font-semibold text-base">{task.title}</h4>
                          <Badge 
                            variant="outline" 
                            className={`text-xs ${getStatusColor(task.status)}`}
                          >
                            {task.status.replace('_', ' ')}
                          </Badge>
                          {task.help_requested && (
                            <Badge variant="outline" className="text-xs bg-red-500/20 text-red-700 border-red-300 gap-1">
                              <AlertCircle className="w-3 h-3" />
                              Help Needed!
                            </Badge>
                          )}
                          {task.helper_employee_id && (
                            <Badge variant="outline" className="text-xs bg-blue-500/20 text-blue-700 border-blue-300 gap-1">
                              <UserPlus className="w-3 h-3" />
                              Helper Assigned
                            </Badge>
                          )}
                        </div>
                        <p className="text-sm text-muted-foreground mb-3">{task.description}</p>
                        <div className="flex gap-4 text-xs text-muted-foreground flex-wrap">
                          <span>
                            Assigned to: <span className="text-foreground font-medium">{getEmployeeName(task.assigned_to)}</span>
                          </span>
                          {task.helper_employee_id && (
                            <span>
                              Helper: <span className="text-foreground font-medium">{getEmployeeName(task.helper_employee_id)}</span>
                            </span>
                          )}
                          <span>
                            Created: <span className="text-foreground">{new Date(task.created_at).toLocaleDateString()}</span>
                          </span>
                        </div>
                        {task.help_requested && task.help_message && (
                          <div className="mt-3 p-3 bg-red-500/10 rounded border border-red-300/50">
                            <p className="text-xs font-medium text-red-700 mb-1 flex items-center gap-1">
                              <AlertCircle className="w-3 h-3" />
                              Help Request:
                            </p>
                            <p className="text-sm text-foreground">{task.help_message}</p>
                          </div>
                        )}
                      </div>
                    </div>
                    {task.help_requested && !task.helper_employee_id && (
                      <div className="flex justify-end pt-2 border-t">
                        <Dialog open={assignDialogOpen && selectedTask?.id === task.id} onOpenChange={(open) => {
                          setAssignDialogOpen(open);
                          if (!open) {
                            setSelectedTask(null);
                            setSelectedHelper("");
                          }
                        }}>
                          <DialogTrigger asChild>
                            <Button 
                              variant="default" 
                              size="sm" 
                              className="gap-2"
                              onClick={() => setSelectedTask(task)}
                            >
                              <UserPlus className="w-4 h-4" />
                              Assign Helper
                            </Button>
                          </DialogTrigger>
                          <DialogContent>
                            <DialogHeader>
                              <DialogTitle>Assign Helper Employee</DialogTitle>
                            </DialogHeader>
                            <div className="space-y-4">
                              <div>
                                <Label className="text-sm font-medium mb-2 block">Task: {task.title}</Label>
                                <p className="text-sm text-muted-foreground mb-2">Assigned to: {getEmployeeName(task.assigned_to)}</p>
                                {task.help_message && (
                                  <div className="p-2 bg-accent/10 rounded border border-accent/20 mb-3">
                                    <p className="text-xs font-medium text-accent mb-1">Help request message:</p>
                                    <p className="text-sm text-muted-foreground">{task.help_message}</p>
                                  </div>
                                )}
                              </div>
                              <div>
                                <Label htmlFor="helper-select">Select Helper Employee</Label>
                                <Select value={selectedHelper} onValueChange={setSelectedHelper}>
                                  <SelectTrigger id="helper-select" className="mt-1">
                                    <SelectValue placeholder="Choose an employee to help" />
                                  </SelectTrigger>
                                  <SelectContent>
                                    {employees.filter(e => e.id !== task.assigned_to).map((emp) => (
                                      <SelectItem key={emp.id} value={emp.id}>
                                        {emp.name} ({emp.employee_id})
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </div>
                              <div className="flex gap-2 justify-end">
                                <Button 
                                  variant="outline" 
                                  onClick={() => {
                                    setAssignDialogOpen(false);
                                    setSelectedHelper("");
                                    setSelectedTask(null);
                                  }}
                                >
                                  Cancel
                                </Button>
                                <Button onClick={handleAssignHelper} disabled={!selectedHelper}>
                                  Assign Helper
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
    </div>
  );
}
