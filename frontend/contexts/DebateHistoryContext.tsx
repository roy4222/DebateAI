"use client";

import { createContext, useContext, useState, ReactNode } from "react";
import { DebateSummary } from "@/app/lib/api";

interface DebateHistoryContextType {
    recentDebates: DebateSummary[];
    addNewDebate: (debate: DebateSummary) => void;
    setRecentDebates: (debates: DebateSummary[]) => void;
}

const DebateHistoryContext = createContext<DebateHistoryContextType | null>(null);

export function DebateHistoryProvider({ children }: { children: ReactNode }) {
    const [recentDebates, setRecentDebates] = useState<DebateSummary[]>([]);

    const addNewDebate = (debate: DebateSummary) => {
        setRecentDebates(prev => [debate, ...prev.slice(0, 4)]);
    };

    return (
        <DebateHistoryContext.Provider value={{ recentDebates, addNewDebate, setRecentDebates }}>
            {children}
        </DebateHistoryContext.Provider>
    );
}

export function useDebateHistory() {
    const context = useContext(DebateHistoryContext);
    if (!context) {
        throw new Error("useDebateHistory must be used within DebateHistoryProvider");
    }
    return context;
}
