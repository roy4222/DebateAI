"use client";

import { Suspense, useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { getDebatesPaginated, getDebateById, DebateSummary, DebateDetail } from "@/app/lib/api";
import { MessageBubble } from "@/app/components/MessageBubble";
import { Card, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ArrowLeft, ArrowRight, Clock, MessageSquare, CheckCircle } from "lucide-react";

// 格式化日期
function formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString("zh-TW", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit",
    });
}

// 辯論列表視圖
function DebateList() {
    const [debates, setDebates] = useState<DebateSummary[]>([]);
    const [loading, setLoading] = useState(true);
    const [page, setPage] = useState(1);
    const [total, setTotal] = useState(0);
    const pageSize = 10;

    useEffect(() => {
        const fetchDebates = async () => {
            setLoading(true);
            try {
                const result = await getDebatesPaginated(page, pageSize);
                setDebates(result.data);
                setTotal(result.total);
            } catch (error) {
                console.error("Failed to fetch debates:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchDebates();
    }, [page]);

    const totalPages = Math.ceil(total / pageSize);

    if (loading) {
        return (
            <div className="flex items-center justify-center py-20">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
            </div>
        );
    }

    if (debates.length === 0) {
        return (
            <Card className="text-center py-16 border-slate-700/50">
                <CardHeader>
                    <div className="text-6xl mb-4">📭</div>
                    <CardTitle className="text-xl">尚無辯論紀錄</CardTitle>
                    <CardDescription className="text-slate-400 mt-2">
                        開始一場辯論，紀錄會自動儲存在這裡
                    </CardDescription>
                    <Link href="/" className="mt-4 inline-block">
                        <Button className="bg-purple-600 hover:bg-purple-700">
                            開始辯論
                        </Button>
                    </Link>
                </CardHeader>
            </Card>
        );
    }

    return (
        <div className="space-y-4">
            {debates.map((debate) => (
                <Link key={debate.id} href={`/history?id=${debate.id}`}>
                    <Card className="border-slate-700/50 hover:border-purple-500/50 hover:bg-slate-800/30 transition-all cursor-pointer">
                        <CardHeader className="pb-4">
                            <div className="flex items-start justify-between">
                                <div className="flex-1 min-w-0">
                                    <CardTitle className="text-lg text-white truncate">
                                        {debate.topic}
                                    </CardTitle>
                                    <CardDescription className="flex items-center gap-4 mt-2 text-slate-400">
                                        <span className="flex items-center gap-1">
                                            <Clock className="size-4" />
                                            {formatDate(debate.created_at)}
                                        </span>
                                        <span className="flex items-center gap-1">
                                            <MessageSquare className="size-4" />
                                            {debate.rounds_completed} 輪
                                        </span>
                                    </CardDescription>
                                </div>
                                <Badge
                                    variant="outline"
                                    className="border-purple-500/50 text-purple-400 shrink-0"
                                >
                                    查看詳情
                                </Badge>
                            </div>
                        </CardHeader>
                    </Card>
                </Link>
            ))}

            {/* Pagination */}
            {totalPages > 1 && (
                <div className="flex items-center justify-center gap-4 pt-6">
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage((p) => Math.max(1, p - 1))}
                        disabled={page === 1}
                        className="border-slate-700"
                    >
                        <ArrowLeft className="size-4 mr-1" />
                        上一頁
                    </Button>
                    <span className="text-slate-400 text-sm">
                        第 {page} / {totalPages} 頁
                    </span>
                    <Button
                        variant="outline"
                        size="sm"
                        onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                        disabled={page === totalPages}
                        className="border-slate-700"
                    >
                        下一頁
                        <ArrowRight className="size-4 ml-1" />
                    </Button>
                </div>
            )}
        </div>
    );
}

// 辯論詳情視圖
function DebateDetailView({ debateId }: { debateId: string }) {
    const [debate, setDebate] = useState<DebateDetail | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchDebate = async () => {
            setLoading(true);
            try {
                const data = await getDebateById(debateId);
                if (data) {
                    setDebate(data);
                } else {
                    setError("找不到此辯論紀錄");
                }
            } catch (err) {
                console.error("Failed to fetch debate:", err);
                setError("載入失敗，請稍後再試");
            } finally {
                setLoading(false);
            }
        };

        fetchDebate();
    }, [debateId]);

    if (loading) {
        return (
            <div className="flex items-center justify-center py-20">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
            </div>
        );
    }

    if (error || !debate) {
        return (
            <div className="flex flex-col items-center justify-center py-20">
                <div className="text-6xl mb-4">😢</div>
                <h1 className="text-xl text-white mb-2">{error || "找不到此辯論紀錄"}</h1>
                <Link href="/history">
                    <Button variant="outline" className="border-slate-700 mt-4">
                        <ArrowLeft className="size-4 mr-2" />
                        返回歷史紀錄
                    </Button>
                </Link>
            </div>
        );
    }

    const displayMessages = debate.messages.filter(
        (msg) => msg.node && ["optimist", "skeptic", "moderator"].includes(msg.node)
    );

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-start justify-between">
                <div className="flex-1 min-w-0">
                    <Link href="/history">
                        <Button variant="ghost" size="sm" className="mb-3 text-slate-400 hover:text-white p-0">
                            <ArrowLeft className="size-4 mr-1" />
                            返回列表
                        </Button>
                    </Link>
                    <h1 className="text-xl font-bold text-white">{debate.topic}</h1>
                    <div className="flex items-center gap-4 mt-2 text-sm text-slate-400">
                        <span className="flex items-center gap-1">
                            <Clock className="size-4" />
                            {formatDate(debate.created_at)}
                        </span>
                        <span className="flex items-center gap-1">
                            <MessageSquare className="size-4" />
                            {debate.rounds_completed} / {debate.max_rounds} 輪
                        </span>
                    </div>
                </div>
                <Badge className="bg-green-600/20 text-green-400 border-green-500/50">
                    <CheckCircle className="size-3 mr-1" />
                    已儲存
                </Badge>
            </div>

            {/* Messages */}
            <div className="space-y-4">
                {displayMessages.length === 0 ? (
                    <div className="text-center py-16 text-slate-400">
                        此辯論沒有可顯示的訊息
                    </div>
                ) : (
                    displayMessages.map((msg, idx) => (
                        <MessageBubble
                            key={idx}
                            node={msg.node as "optimist" | "skeptic" | "moderator"}
                            text={msg.content}
                            roundInfo={msg.roundInfo}
                        />
                    ))
                )}
            </div>

            {/* Footer */}
            <div className="flex justify-between items-center pt-6 border-t border-slate-800/50">
                <Link href="/history">
                    <Button variant="outline" className="border-slate-700">
                        <ArrowLeft className="size-4 mr-2" />
                        返回列表
                    </Button>
                </Link>
                <Link href="/">
                    <Button className="bg-purple-600 hover:bg-purple-700">
                        開始新辯論
                    </Button>
                </Link>
            </div>
        </div>
    );
}

// 內部元件 - 使用 useSearchParams
function HistoryContent() {
    const searchParams = useSearchParams();
    const debateId = searchParams.get("id");

    return (
        <>
            {/* Header - 只在列表視圖顯示 */}
            {!debateId && (
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">辯論歷史紀錄</h1>
                    <p className="text-slate-400">查看過去的 AI 辯論紀錄</p>
                </div>
            )}

            {/* 根據是否有 id 顯示不同視圖 */}
            {debateId ? (
                <DebateDetailView debateId={debateId} />
            ) : (
                <DebateList />
            )}
        </>
    );
}

// Loading fallback
function LoadingFallback() {
    return (
        <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500"></div>
        </div>
    );
}

// 主頁面 - 用 Suspense 包裝 useSearchParams
export default function HistoryPage() {
    return (
        <div className="flex flex-col flex-1 min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 p-6">
            <div className="max-w-4xl mx-auto w-full">
                <Suspense fallback={<LoadingFallback />}>
                    <HistoryContent />
                </Suspense>
            </div>
        </div>
    );
}
