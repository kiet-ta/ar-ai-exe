import { BadgeCheck, Box, LogIn } from "lucide-react";
import type { ReactNode } from "react";

import type { User } from "../../types";

type AppShellProps = {
  user: User | null;
  children: ReactNode;
};

export function AppShell({ user, children }: AppShellProps) {
  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand-lockup">
          <div className="brand-mark">
            <Box size={18} aria-hidden="true" />
          </div>
          <div>
            <h1>Shoe Visual Customizer</h1>
            <p>Scan review and design package workspace</p>
          </div>
        </div>
        <div className="auth-pill">
          {user ? <BadgeCheck size={16} aria-hidden="true" /> : <LogIn size={16} aria-hidden="true" />}
          <span>{user ? user.email : "Demo login pending"}</span>
        </div>
      </header>
      {children}
    </div>
  );
}
