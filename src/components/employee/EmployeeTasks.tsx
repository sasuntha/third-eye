import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useAuth } from "@/hooks/useAuth";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from "@/components/ui/dialog";
import { useToast } from "@/hooks/use-toast";
import { ClipboardList, HelpCircle, Bell } from "lucide-react";

interface Task {
  id: string;
  title: string;
  description: string;
  status: string;
  help_requested: boolean;
  help_message: string | null;
  additional_assignee: string | null;
  created_at: string;
}

export default function EmployeeTasks() {
  const { user } = useAuth();
  const { toast } = useToast();
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [helpMessage, setHelpMessage] = useState("");
  const [requestingHelp, setRequestingHelp] = useState<string | null>(null);

  const fetchTasks = async () => {
    if (!user) return;
    const { data } = await supabase
      .from("tasks")
      .select("*")
      .or(`assigned_to.eq.${user.id},additional_assignee.eq.${user.id}`)
      .order("created_at", { ascending: false });
    if (data) setTasks(data);
    setLoading(false);
  };

  useEffect(() => { fetchTasks(); }, [user]);

  // Realtime subscription
  useEffect(() => {
    if (!user) return;
    const channel = supabase
      .channel("employee-tasks")
      .on("postgres_changes", { event: "*", schema: "public", table: "tasks" }, (payload) => {
        fetchTasks();
        if (payload.eventType === "UPDATE") {
          const newTask = payload.new as Task;
          if (newTask.additional_assignee === user.id) {
            toast({ title: "You've been assigned to help with a task!", description: newTask.title });
          }
        }
      })
      .subscribe();
    return () => { supabase.removeChannel(channel); };
  }, [user]);

  const handleRequestHelp = async (taskId: string) => {
    try {
      const { error } = await supabase.from("tasks").update({
        help_requested: true,
        help_message: helpMessage || "I need additional help with this task.",
      }).eq("id", taskId);
      if (error) throw error;
      toast({ title: "Help request sent to the chief" });
      setHelpMessage("");
      setRequestingHelp(null);
      fetchTasks();
    } catch (err: any) {
      toast({ title: "Failed to request help", description: err.message, variant: "destructive" });
    }
  };

  const statusColor = (status: string) => {
    if (status === "completed") return "default";
    if (status === "in_progress") return "outline";
    return "secondary";
  };

  if (loading) return <div className="text-center py-12 text-muted-foreground">Loading tasks...</div>;

  return (
    <div>
      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
        <ClipboardList className="w-5 h-5" /> My Tasks ({tasks.length})
      </h3>
      {tasks.length === 0 ? (
        <Card className="glass-card"><CardContent className="py-8 text-center text-muted-foreground">No tasks assigned to you yet</CardContent></Card>
      ) : (
        <div className="grid gap-4">
          {tasks.map((task) => (
            <Card key={task.id} className="glass-card animate-slide-up">
              <CardContent className="py-4">
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h4 className="font-semibold text-sm truncate">{task.title}</h4>
                      <Badge variant={statusColor(task.status)} className="text-xs shrink-0">{task.status}</Badge>
                      {task.additional_assignee && (
                        <Badge variant="outline" className="text-xs shrink-0 gap-1">
                          <Bell className="w-3 h-3" /> Helper assigned
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground">{task.description}</p>
                    <p className="text-xs text-muted-foreground mt-2">{new Date(task.created_at).toLocaleDateString()}</p>
                    {task.help_requested && !task.additional_assignee && (
                      <p className="text-xs mt-2 p-2 bg-accent/10 rounded text-accent">⏳ Help requested — waiting for chief</p>
                    )}
                  </div>
                  {!task.help_requested && !task.additional_assignee && (
                    <Dialog>
                      <DialogTrigger asChild>
                        <Button size="sm" variant="outline" className="gap-1 shrink-0" onClick={() => setRequestingHelp(task.id)}>
                          <HelpCircle className="w-3 h-3" /> Request Help
                        </Button>
                      </DialogTrigger>
                      <DialogContent>
                        <DialogHeader><DialogTitle>Request Help</DialogTitle></DialogHeader>
                        <div className="space-y-4">
                          <p className="text-sm text-muted-foreground">Task: {task.title}</p>
                          <Textarea value={helpMessage} onChange={(e) => setHelpMessage(e.target.value)} placeholder="Describe what help you need..." rows={3} />
                          <Button onClick={() => handleRequestHelp(task.id)}>Send Request</Button>
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
  );
}
