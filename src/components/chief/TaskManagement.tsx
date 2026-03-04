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
import { Plus, ClipboardList, Users } from "lucide-react";

interface Employee {
  user_id: string;
  full_name: string;
}

interface Task {
  id: string;
  title: string;
  description: string;
  assigned_to: string;
  status: string;
  help_requested: boolean;
  help_message: string | null;
  additional_assignee: string | null;
  created_at: string;
}

export default function TaskManagement() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [assignTo, setAssignTo] = useState("");
  const [assignDialogTask, setAssignDialogTask] = useState<Task | null>(null);
  const [additionalEmployee, setAdditionalEmployee] = useState("");

  const fetchData = async () => {
    // Get employees (users with employee role)
    const { data: roles } = await supabase.from("user_roles").select("user_id").eq("role", "employee");
    if (roles && roles.length > 0) {
      const userIds = roles.map((r) => r.user_id);
      const { data: profiles } = await supabase.from("profiles").select("user_id, full_name").in("user_id", userIds);
      if (profiles) setEmployees(profiles);
    }

    const { data: taskData } = await supabase.from("tasks").select("*").order("created_at", { ascending: false });
    if (taskData) setTasks(taskData);
    setLoading(false);
  };

  useEffect(() => { fetchData(); }, []);

  // Realtime subscription for task updates
  useEffect(() => {
    const channel = supabase
      .channel("tasks-realtime")
      .on("postgres_changes", { event: "*", schema: "public", table: "tasks" }, () => fetchData())
      .subscribe();
    return () => { supabase.removeChannel(channel); };
  }, []);

  const handleCreateTask = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user || !assignTo) return;
    setCreating(true);
    try {
      const { error } = await supabase.from("tasks").insert({
        title,
        description,
        assigned_to: assignTo,
        created_by: user.id,
      });
      if (error) throw error;
      toast({ title: "Task created successfully" });
      setTitle("");
      setDescription("");
      setAssignTo("");
      fetchData();
    } catch (err: any) {
      toast({ title: "Failed to create task", description: err.message, variant: "destructive" });
    } finally {
      setCreating(false);
    }
  };

  const handleAssignHelper = async () => {
    if (!assignDialogTask || !additionalEmployee) return;
    try {
      const { error } = await supabase.from("tasks").update({
        additional_assignee: additionalEmployee,
        help_requested: false,
      }).eq("id", assignDialogTask.id);
      if (error) throw error;
      toast({ title: "Helper assigned successfully" });
      setAssignDialogTask(null);
      setAdditionalEmployee("");
      fetchData();
    } catch (err: any) {
      toast({ title: "Failed to assign", description: err.message, variant: "destructive" });
    }
  };

  const getEmployeeName = (id: string) => employees.find((e) => e.user_id === id)?.full_name || "Unknown";

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
                <Label>Task Title</Label>
                <Input value={title} onChange={(e) => setTitle(e.target.value)} required placeholder="Enter task title" />
              </div>
              <div>
                <Label>Assign To</Label>
                <Select value={assignTo} onValueChange={setAssignTo}>
                  <SelectTrigger><SelectValue placeholder="Select employee" /></SelectTrigger>
                  <SelectContent>
                    {employees.map((emp) => (
                      <SelectItem key={emp.user_id} value={emp.user_id}>{emp.full_name}</SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>
            <div>
              <Label>Description</Label>
              <Textarea value={description} onChange={(e) => setDescription(e.target.value)} required placeholder="Describe the task..." rows={3} />
            </div>
            <Button type="submit" disabled={creating || !assignTo}>
              {creating ? "Creating..." : "Create Task"}
            </Button>
          </form>
        </CardContent>
      </Card>

      {/* Task List */}
      <div>
        <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
          <ClipboardList className="w-5 h-5" /> Assigned Tasks ({tasks.length})
        </h3>
        {tasks.length === 0 ? (
          <Card className="glass-card"><CardContent className="py-8 text-center text-muted-foreground">No tasks yet</CardContent></Card>
        ) : (
          <div className="grid gap-4">
            {tasks.map((task) => (
              <Card key={task.id} className="glass-card animate-slide-up">
                <CardContent className="py-4">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <h4 className="font-semibold text-sm truncate">{task.title}</h4>
                        <Badge variant={task.status === "completed" ? "default" : "outline"} className="text-xs shrink-0">
                          {task.status}
                        </Badge>
                        {task.help_requested && (
                          <Badge className="bg-accent text-accent-foreground text-xs shrink-0">Help Needed</Badge>
                        )}
                      </div>
                      <p className="text-sm text-muted-foreground line-clamp-2">{task.description}</p>
                      <div className="flex gap-4 mt-2 text-xs text-muted-foreground">
                        <span>Assigned to: <span className="text-foreground">{getEmployeeName(task.assigned_to)}</span></span>
                        {task.additional_assignee && (
                          <span>Helper: <span className="text-foreground">{getEmployeeName(task.additional_assignee)}</span></span>
                        )}
                      </div>
                      {task.help_message && (
                        <p className="text-xs mt-2 p-2 bg-accent/10 rounded text-accent">💬 {task.help_message}</p>
                      )}
                    </div>
                    {task.help_requested && (
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button size="sm" variant="outline" className="gap-1 shrink-0" onClick={() => setAssignDialogTask(task)}>
                            <Users className="w-3 h-3" /> Assign Helper
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader><DialogTitle>Assign Additional Help</DialogTitle></DialogHeader>
                          <div className="space-y-4">
                            <p className="text-sm text-muted-foreground">Task: {task.title}</p>
                            <div>
                              <Label>Select Employee</Label>
                              <Select value={additionalEmployee} onValueChange={setAdditionalEmployee}>
                                <SelectTrigger><SelectValue placeholder="Choose an employee" /></SelectTrigger>
                                <SelectContent>
                                  {employees.filter((e) => e.user_id !== task.assigned_to).map((emp) => (
                                    <SelectItem key={emp.user_id} value={emp.user_id}>{emp.full_name}</SelectItem>
                                  ))}
                                </SelectContent>
                              </Select>
                            </div>
                            <Button onClick={handleAssignHelper} disabled={!additionalEmployee}>Assign</Button>
                          </div>
                        </DialogContent>
                      </Dialog>
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
