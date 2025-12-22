"use client";

import { ReactNode } from "react";
import { DebateHistoryProvider } from "@/contexts/DebateHistoryContext";

export function Providers({ children }: { children: ReactNode }) {
    return (
        <DebateHistoryProvider>
            {children}
        </DebateHistoryProvider>
    );
}
