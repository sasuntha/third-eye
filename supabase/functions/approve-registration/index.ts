import { serve } from "https://deno.land/std@0.168.0/http/server.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";

const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Headers": "authorization, x-client-info, apikey, content-type, x-supabase-client-platform, x-supabase-client-platform-version, x-supabase-client-runtime, x-supabase-client-runtime-version",
};

serve(async (req) => {
  if (req.method === "OPTIONS") return new Response(null, { headers: corsHeaders });

  try {
    const authHeader = req.headers.get("Authorization");
    if (!authHeader) throw new Error("No authorization header");

    const supabaseUrl = Deno.env.get("SUPABASE_URL")!;
    const serviceKey = Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!;
    const supabase = createClient(supabaseUrl, serviceKey);

    // Verify the caller is a chief
    const anonClient = createClient(supabaseUrl, Deno.env.get("SUPABASE_ANON_KEY")!);
    const { data: { user }, error: authError } = await anonClient.auth.getUser(authHeader.replace("Bearer ", ""));
    if (authError || !user) throw new Error("Unauthorized");

    const { data: chiefRole } = await supabase
      .from("user_roles")
      .select("role")
      .eq("user_id", user.id)
      .eq("role", "chief")
      .single();

    if (!chiefRole) throw new Error("Only chiefs can approve registrations");

    const { requestId, action } = await req.json();
    if (!requestId || !action) throw new Error("Missing requestId or action");
    if (!["approved", "rejected"].includes(action)) throw new Error("Invalid action");

    // Get the registration request
    const { data: request, error: reqError } = await supabase
      .from("registration_requests")
      .select("*")
      .eq("id", requestId)
      .single();

    if (reqError || !request) throw new Error("Registration request not found");
    if (request.status !== "pending") throw new Error("Request already processed");

    // Update the request status
    const { error: updateError } = await supabase
      .from("registration_requests")
      .update({
        status: action,
        reviewed_by: user.id,
        reviewed_at: new Date().toISOString(),
      })
      .eq("id", requestId);

    if (updateError) throw new Error("Failed to update request");

    // If approved, add the employee role
    if (action === "approved") {
      const { error: roleError } = await supabase
        .from("user_roles")
        .insert({ user_id: request.user_id, role: "employee" });

      if (roleError) {
        console.error("Role insert error:", roleError);
        throw new Error("Failed to assign employee role");
      }

      // Update profile with employee ID number
      await supabase
        .from("profiles")
        .update({ employee_id_number: request.employee_id_number })
        .eq("user_id", request.user_id);
    }

    return new Response(JSON.stringify({ success: true, status: action }), {
      headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  } catch (e) {
    console.error("approve-registration error:", e);
    return new Response(JSON.stringify({ error: e instanceof Error ? e.message : "Unknown error" }), {
      status: 500, headers: { ...corsHeaders, "Content-Type": "application/json" },
    });
  }
});
