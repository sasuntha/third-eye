import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import DashboardLayout from "@/components/DashboardLayout";
import RegistrationRequests from "@/components/chief/RegistrationRequests";
import TaskManagement from "@/components/chief/TaskManagement";
import DocumentReview from "@/components/chief/DocumentReview";
import { UserCheck, ClipboardList, FileSearch } from "lucide-react";

export default function ChiefDashboard() {
  return (
    <DashboardLayout>
      <div className="animate-fade-in">
        <h2 className="text-2xl font-bold text-foreground mb-6">Chief Dashboard</h2>
        <Tabs defaultValue="registrations" className="w-full">
          <TabsList className="grid grid-cols-3 w-full max-w-lg mb-6">
            <TabsTrigger value="registrations" className="gap-2">
              <UserCheck className="w-4 h-4" />
              <span className="hidden sm:inline">Registrations</span>
            </TabsTrigger>
            <TabsTrigger value="tasks" className="gap-2">
              <ClipboardList className="w-4 h-4" />
              <span className="hidden sm:inline">Tasks</span>
            </TabsTrigger>
            <TabsTrigger value="documents" className="gap-2">
              <FileSearch className="w-4 h-4" />
              <span className="hidden sm:inline">Documents</span>
            </TabsTrigger>
          </TabsList>
          <TabsContent value="registrations"><RegistrationRequests /></TabsContent>
          <TabsContent value="tasks"><TaskManagement /></TabsContent>
          <TabsContent value="documents"><DocumentReview /></TabsContent>
        </Tabs>
      </div>
    </DashboardLayout>
  );
}
