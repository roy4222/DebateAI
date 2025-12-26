"use client";

import React, { useState, useRef, useEffect, useCallback } from "react";
import { MessageBubble } from "./MessageBubble";
import { TopicForm } from "./TopicForm";
import { streamDebate, SSEEvent, saveDebate } from "../lib/api";
import {
  Card,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useDebateHistory } from "@/contexts/DebateHistoryContext";
import { useI18n } from "@/lib/i18n";

// 訊息類型
interface Message {
  node: "optimist" | "skeptic" | "moderator" | "system";
  text: string;
  roundInfo?: string;
}

/**
 * DebateUI - 辯論主介面組件 (shadcn/ui 版本)
 *
 * 核心功能：
 * - SSE 串流處理
 * - useRef 解決 React 狀態非同步問題
 * - 自動滾動
 * - 連線階段 30 秒超時（首包後解除）
 * - Phase 4: 自動儲存並更新 sidebar
 */
export function DebateUI() {
  // Phase 4: 使用 context 來更新 sidebar
  const { addNewDebate } = useDebateHistory();
  const { t, locale } = useI18n();

  // ============================================================
  // 狀態管理
  // ============================================================
  const [topic, setTopic] = useState(
    locale === "zh"
      ? "AI 會取代大部分人類工作嗎？"
      : "Will AI replace most human jobs?"
  );
  const [currentTopic, setCurrentTopic] = useState<string>(""); // 保存當前辯論主題
  const [messages, setMessages] = useState<Message[]>([]);
  const [currentText, setCurrentText] = useState<{ [key: string]: string }>({});
  const [currentRound, setCurrentRound] = useState<{ [key: string]: string }>(
    {}
  );
  const [isStreaming, setIsStreaming] = useState(false);
  const [status, setStatus] = useState("");
  const [connectionTime, setConnectionTime] = useState<number | null>(null);
  // Phase 3b: 搜尋狀態
  const [searchStatus, setSearchStatus] = useState<{
    isSearching: boolean;
    query?: string;
    node?: string;
  }>({ isSearching: false });

  // ============================================================
  // Refs - 解決 React 狀態非同步問題
  // ============================================================
  const textBufferRef = useRef<{ [key: string]: string }>({});
  const roundInfoRef = useRef<{ [key: string]: string }>({});
  const messagesRef = useRef<Message[]>([]); // Phase 4: 同步追蹤訊息避免 race condition
  const currentTopicRef = useRef<string>(""); // Phase 4: 避免 stale closure
  const addNewDebateRef = useRef(addNewDebate); // Phase 4: 避免 stale closure
  const abortControllerRef = useRef<AbortController | null>(null);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // ⚠️ 修正：記錄連線開始時間和首包是否到達
  const connectionStartTimeRef = useRef<number>(0);
  const firstChunkReceivedRef = useRef<boolean>(false);
  const connectionTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(
    null
  );

  // Phase 4: 保持 ref 最新
  useEffect(() => {
    addNewDebateRef.current = addNewDebate;
  }, [addNewDebate]);

  // ============================================================
  // 自動滾動
  // ============================================================
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, currentText]);

  // ============================================================
  // 清空所有暫存狀態
  // ============================================================
  const clearAllBuffers = useCallback(() => {
    textBufferRef.current = {};
    roundInfoRef.current = {};
    messagesRef.current = []; // Phase 4: 清空 ref
    setCurrentText({});
    setCurrentRound({});
  }, []);

  // ============================================================
  // Phase 4: 自動儲存辯論
  // ============================================================
  const handleAutoSave = useCallback(
    async (completeText: string) => {
      // 從 complete 訊息解析輪數
      const roundMatch =
        completeText.match(/(\d+)\s*輪/) ||
        completeText.match(/(\d+)\s*round/i);
      const roundsCompleted = roundMatch ? parseInt(roundMatch[1], 10) : 3;

      // ⚠️ 使用 ref 取得最新值，避免 stale closure
      const messagesToSave = [...messagesRef.current];
      const topicToSave = currentTopicRef.current;

      if (!topicToSave || messagesToSave.length === 0) {
        console.log("No topic or messages to save");
        return;
      }

      console.log(
        `Saving debate: ${topicToSave}, ${messagesToSave.length} messages, ${roundsCompleted} rounds`
      );

      try {
        const result = await saveDebate(
          topicToSave,
          messagesToSave,
          3,
          roundsCompleted
        );

        if (result.success && result.debate_id) {
          console.log(`Debate saved: ${result.debate_id}`);
          setStatus(t("debateSavedSuccess"));

          // 使用 ref 呼叫最新的 addNewDebate
          addNewDebateRef.current({
            id: result.debate_id,
            topic: topicToSave,
            created_at: new Date().toISOString(),
            rounds_completed: roundsCompleted,
          });
        } else {
          console.error("Failed to save debate:", result.error);
        }
      } catch (error) {
        console.error("Save debate error:", error);
      }
    },
    [t]
  );

  // ============================================================
  // SSE 事件處理器
  // ============================================================
  const handleSSEEvent = useCallback(
    (event: SSEEvent) => {
      // ⚠️ 修正：首包到達時記錄連線時間並解除超時
      if (!firstChunkReceivedRef.current) {
        firstChunkReceivedRef.current = true;
        const elapsed = Date.now() - connectionStartTimeRef.current;

        // 清除連線超時（首包已到達，改為無限制串流）
        if (connectionTimeoutRef.current) {
          clearTimeout(connectionTimeoutRef.current);
          connectionTimeoutRef.current = null;
        }

        // 只有連線時間 > 3 秒才顯示（表示有冷啟動）
        if (elapsed > 3000) {
          setConnectionTime(elapsed);
        }
      }

      switch (event.type) {
        case "status":
          setStatus(event.text);
          break;

        case "speaker":
          textBufferRef.current[event.node] = "";
          roundInfoRef.current[event.node] = event.text;
          setCurrentRound((prev) => ({
            ...prev,
            [event.node]: event.text,
          }));
          break;

        case "token":
          textBufferRef.current[event.node] =
            (textBufferRef.current[event.node] || "") + event.text;

          setCurrentText((prev) => ({
            ...prev,
            [event.node]: textBufferRef.current[event.node],
          }));
          break;

        case "speaker_end":
          const finalText = textBufferRef.current[event.node] || "";
          const roundInfo = roundInfoRef.current[event.node] || "";

          // Phase 4: 同步更新 ref（先於 state 更新）
          const newMessage = { node: event.node, text: finalText, roundInfo };
          messagesRef.current = [...messagesRef.current, newMessage];

          setMessages((prev) => [...prev, newMessage]);

          textBufferRef.current[event.node] = "";
          roundInfoRef.current[event.node] = "";
          setCurrentText((prev) => ({ ...prev, [event.node]: "" }));
          setCurrentRound((prev) => ({ ...prev, [event.node]: "" }));
          break;

        case "complete":
          setSearchStatus({ isSearching: false });
          setStatus(event.text);

          // Phase 4: 自動儲存辯論
          // 使用 setTimeout 確保 messages 已更新
          setTimeout(() => {
            handleAutoSave(event.text);
          }, 100);
          break;

        case "error":
          setSearchStatus({ isSearching: false }); // Phase 3b: 清除搜尋狀態
          setStatus(`${t("debateError")}${event.text}`);
          break;

        // Phase 3b: 搜尋工具事件
        case "tool_start":
          setSearchStatus({
            isSearching: true,
            query: event.query,
            node: event.node,
          });
          const searchingRole =
            event.node === "optimist"
              ? t("debateOptimistSearching")
              : t("debateSkepticSearching");
          setStatus(`🔍 ${searchingRole}${t("debateSearchFor")}${event.query}`);
          break;

        case "tool_end":
          setSearchStatus({ isSearching: false });
          setStatus(t("debateSearchComplete"));
          break;
      }
    },
    [t, handleAutoSave]
  );

  // ============================================================
  // 開始辯論
  // ============================================================
  const startDebate = async () => {
    // 保存主題並清空輸入框
    const debateTopic = topic.trim();
    setCurrentTopic(debateTopic);
    currentTopicRef.current = debateTopic; // Phase 4: 同步 ref
    setTopic(""); // 清空輸入框

    // 重置狀態
    setIsStreaming(true);
    setMessages([]);
    clearAllBuffers();
    setStatus(t("debateConnecting"));
    setConnectionTime(null);

    // ⚠️ 修正：重置連線追蹤狀態
    connectionStartTimeRef.current = Date.now();
    firstChunkReceivedRef.current = false;

    // 建立 AbortController
    abortControllerRef.current = new AbortController();

    // ⚠️ 修正：30 秒超時僅作用於「連線/首包」階段
    // 收到首個 chunk 後會在 handleSSEEvent 中清除此超時
    connectionTimeoutRef.current = setTimeout(() => {
      if (!firstChunkReceivedRef.current) {
        abortControllerRef.current?.abort();
        setStatus(t("debateTimeout"));
      }
    }, 30000);

    try {
      console.log("🌐 Starting debate with language:", locale);
      await streamDebate(
        { topic: debateTopic, max_rounds: 3, language: locale },
        handleSSEEvent,
        abortControllerRef.current.signal
      );
    } catch (error) {
      if (error instanceof Error && error.name !== "AbortError") {
        setStatus(`${t("debateConnectionFailed")}${error.message}`);
      }
    } finally {
      // 清理超時
      if (connectionTimeoutRef.current) {
        clearTimeout(connectionTimeoutRef.current);
        connectionTimeoutRef.current = null;
      }
      setIsStreaming(false);
    }
  };

  // ============================================================
  // 停止辯論
  // ============================================================
  const stopDebate = () => {
    abortControllerRef.current?.abort();

    // 清理超時
    if (connectionTimeoutRef.current) {
      clearTimeout(connectionTimeoutRef.current);
      connectionTimeoutRef.current = null;
    }

    // ⚠️ 修正：停止時清空所有暫存文字與 round 資訊
    clearAllBuffers();

    setIsStreaming(false);
    setStatus(t("debateStopped"));
  };

  // ============================================================
  // 重置辯論（開始新辯論）
  // ============================================================
  const resetDebate = useCallback(() => {
    // 停止當前辯論（如果正在進行）
    if (isStreaming) {
      abortControllerRef.current?.abort();
      if (connectionTimeoutRef.current) {
        clearTimeout(connectionTimeoutRef.current);
        connectionTimeoutRef.current = null;
      }
    }

    // 完全重置所有狀態
    setMessages([]);
    setCurrentTopic("");
    setStatus("");
    setConnectionTime(null);
    setIsStreaming(false);
    setSearchStatus({ isSearching: false });
    clearAllBuffers();
    currentTopicRef.current = "";

    // 恢復預設主題
    setTopic(
      locale === "zh"
        ? "AI 會取代大部分人類工作嗎？"
        : "Will AI replace most human jobs?"
    );
  }, [isStreaming, locale, clearAllBuffers]);

  // ============================================================
  // 暴露 resetDebate 給父組件使用
  // ============================================================
  useEffect(() => {
    // 將 reset 函數掛載到 window，讓 sidebar/header 可以呼叫
    (window as any).__debateUI_reset = resetDebate;

    return () => {
      delete (window as any).__debateUI_reset;
    };
  }, [resetDebate]);

  // ============================================================
  // 渲染
  // ============================================================
  return (
    <div className="flex flex-col flex-1 h-screen overflow-hidden bg-gradient-to-br from-slate-100 via-slate-50 to-white dark:from-slate-950 dark:via-slate-900 dark:to-slate-950">
      {/* ========== Header (只在有內容時顯示) ========== */}
      {(currentTopic || status) && (
        <header className="flex-shrink-0 px-6 py-3 border-b border-slate-200 dark:border-slate-800/50 bg-white/80 dark:bg-slate-900/95 ">
          <div className="max-w-4xl mx-auto flex items-center justify-between">
            {/* 辯論主題顯示 */}
            <div className="flex-1">
              {currentTopic && (
                <Badge
                  variant="outline"
                  className="px-4 py-2 text-sm border-purple-500/50 bg-purple-500/10"
                >
                  {t("debateTopic")}
                  {currentTopic}
                </Badge>
              )}
            </div>

            {/* 狀態指示 */}
            <div className="text-right flex items-center gap-3">
              {status && (
                <Badge
                  variant="outline"
                  className="text-slate-600 dark:text-slate-400"
                >
                  {status}
                </Badge>
              )}
              {connectionTime && (
                <span className="text-xs text-slate-500 dark:text-slate-500">
                  {t("debateConnectionTime")}
                  {(connectionTime / 1000).toFixed(1)}s
                </span>
              )}
            </div>
          </div>
        </header>
      )}

      {/* ========== Main Chat Area ========== */}
      <main className="flex-1 overflow-y-auto px-6 py-6">
        <div className="max-w-4xl mx-auto space-y-4">
          {/* 歡迎訊息 */}
          {messages.length === 0 && !isStreaming && !currentTopic && (
            <Card className="max-w-lg mx-auto text-center border-slate-200 dark:border-slate-700/50 bg-white/60 dark:bg-slate-800/40">
              <CardHeader className="pt-10 pb-8">
                <div className="text-6xl mb-4">🎭</div>
                <CardTitle className="text-xl text-slate-900 dark:text-white">
                  {t("debateWelcomeTitle")}
                </CardTitle>
                <CardDescription className="text-slate-500 dark:text-slate-400 mt-2">
                  {t("debateWelcomeDescription")}
                </CardDescription>
              </CardHeader>
            </Card>
          )}

          {/* Phase 3b: 搜尋指示器 */}
          {searchStatus.isSearching && (
            <div className="mb-4 p-3 bg-yellow-100/50 dark:bg-yellow-950/20 border border-yellow-300 dark:border-yellow-800/50 rounded-lg flex items-center gap-3">
              <svg
                className="animate-spin h-5 w-5 text-yellow-600 dark:text-yellow-500"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                  fill="none"
                />
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                />
              </svg>
              <div className="flex-1">
                <p className="text-sm font-medium text-yellow-800 dark:text-yellow-100">
                  {t("debateSearching")}
                </p>
                <p className="text-xs text-yellow-700/70 dark:text-yellow-300/70">
                  {searchStatus.query}
                </p>
              </div>
            </div>
          )}

          {/* 已完成的訊息 */}
          {messages.map((msg, idx) => (
            <MessageBubble
              key={idx}
              node={msg.node}
              text={msg.text}
              roundInfo={msg.roundInfo}
            />
          ))}

          {/* 正在輸入的訊息 */}
          {Object.entries(currentText).map(([node, text]) =>
            text ? (
              <MessageBubble
                key={`typing-${node}`}
                node={node as "optimist" | "skeptic"}
                text={text}
                isTyping={true}
                roundInfo={currentRound[node]}
              />
            ) : null
          )}

          {/* 自動滾動 anchor */}
          <div ref={chatEndRef} />
        </div>
      </main>

      {/* ========== Footer (Input Form) ========== */}
      <footer className="flex-shrink-0 px-6 py-4 border-t border-slate-200 dark:border-slate-800/50 backdrop-blur-sm bg-white/50 dark:bg-slate-950/50">
        <div className="max-w-4xl mx-auto">
          <TopicForm
            topic={topic}
            setTopic={setTopic}
            isStreaming={isStreaming}
            onStart={startDebate}
            onStop={stopDebate}
          />
        </div>
      </footer>
    </div>
  );
}

export default DebateUI;
