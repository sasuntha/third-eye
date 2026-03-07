import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { supabase } from "@/integrations/supabase/client";
import { useNavigate } from "react-router-dom";
import type { User } from "@supabase/supabase-js";

type UserRole = "chief" | "employee" | null;

interface UserData {
  id: string;
  email: string;
  full_name: string;
  employee_id: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  userData: UserData | null;
  role: UserRole;
  loading: boolean;
  fullName: string;
  signOut: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  userData: null,
  role: null,
  loading: true,
  fullName: "",
  signOut: async () => {},
});

export const useAuth = () => useContext(AuthContext);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [userData, setUserData] = useState<UserData | null>(null);
  const [role, setRole] = useState<UserRole>(null);
  const [loading, setLoading] = useState(true);
  const [fullName, setFullName] = useState("");
  const navigate = useNavigate();

  const loadUserFromStorage = () => {
    const storedUser = localStorage.getItem("user");
    if (storedUser) {
      try {
        const userData = JSON.parse(storedUser) as UserData;
        setUserData(userData);
        setRole((userData.role as UserRole) || "employee");
        setFullName(userData.full_name);
        // Create a minimal User object for backward compatibility
        setUser({
          id: userData.id,
          email: userData.email,
        } as User);
      } catch (error) {
        console.error("Failed to parse stored user data:", error);
        localStorage.removeItem("user");
      }
    } else {
      // Clear user if no stored data
      setUser(null);
      setUserData(null);
      setRole(null);
      setFullName("");
    }
  };

  useEffect(() => {
    // Check for stored user data from backend login on mount
    loadUserFromStorage();
    setLoading(false);

    // Listen for localStorage changes (from other tabs or programmatic changes)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === "user") {
        loadUserFromStorage();
      }
    };

    window.addEventListener("storage", handleStorageChange);
    return () => window.removeEventListener("storage", handleStorageChange);
  }, []);

  // Also listen for custom events when localStorage changes within the same tab
  useEffect(() => {
    const handleUserUpdate = () => {
      loadUserFromStorage();
    };

    window.addEventListener("userUpdated", handleUserUpdate);
    return () => window.removeEventListener("userUpdated", handleUserUpdate);
  }, []);

  const signOut = async () => {
    localStorage.removeItem("user");
    setUser(null);
    setUserData(null);
    setRole(null);
    setFullName("");
    navigate("/");
  };

  return (
    <AuthContext.Provider value={{ user, userData, role, loading, fullName, signOut }}>
      {children}
    </AuthContext.Provider>
  );
}
