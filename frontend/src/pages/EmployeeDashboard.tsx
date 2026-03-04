import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import DashboardLayout from "@/components/DashboardLayout";
import DocumentScanner from "@/components/employee/DocumentScanner";
import EmployeeTasks from "@/components/employee/EmployeeTasks";
import { ScanLine, ClipboardList } from "lucide-react";

export default function EmployeeDashboard() {
  return (
    <DashboardLayout>
      <div className="animate-fade-in">
        <h2 className="text-2xl font-bold text-foreground mb-6">My Dashboard</h2>
        <Tabs defaultValue="scanner" className="w-full">
          <TabsList className="grid grid-cols-2 w-full max-w-md mb-6">
            <TabsTrigger value="scanner" className="gap-2">
              <ScanLine className="w-4 h-4" /> Documents
            </TabsTrigger>
            <TabsTrigger value="tasks" className="gap-2">
              <ClipboardList className="w-4 h-4" /> Tasks
            </TabsTrigger>
          </TabsList>
          <TabsContent value="scanner"><DocumentScanner /></TabsContent>
          <TabsContent value="tasks"><EmployeeTasks /></TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
