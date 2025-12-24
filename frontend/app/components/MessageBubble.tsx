"use client";

import React from "react";
import ReactMarkdown from "react-markdown";
import { cn } from "@/lib/utils";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { useI18n } from "@/lib/i18n";

export interface MessageBubbleProps {
  node: "optimist" | "skeptic" | "moderator" | "system";
  text: string;
  isTyping?: boolean;
  roundInfo?: string;
}

/**
 * 訊息氣泡組件 - shadcn/ui 版本
 *
 * - 樂觀者：綠色，靠左
 * - 懷疑者：紅色，靠右
 * - 主持人：藍色，置中，支援 Markdown 渲染
 * - 系統：灰色，置中
 */
export function MessageBubble({
  node,
  text,
  isTyping = false,
  roundInfo,
}: MessageBubbleProps) {
  const { t } = useI18n();

  // 角色配置
  const roleConfig = {
    optimist: {
      emoji: "🤖",
      labelKey: "roleOptimist" as const,
      containerClass: "mr-16",
      cardClass: "bg-emerald-100/60 dark:bg-emerald-950/40 border-emerald-300 dark:border-emerald-500/30",
      textClass: "text-emerald-800 dark:text-emerald-100",
    },
    skeptic: {
      emoji: "🧐",
      labelKey: "roleSkeptic" as const,
      containerClass: "ml-16",
      cardClass: "bg-rose-100/60 dark:bg-rose-950/40 border-rose-300 dark:border-rose-500/30",
      textClass: "text-rose-800 dark:text-rose-100",
    },
    // Phase 3d: 新增 moderator 配置（藍色主題，置中且稍寬）
    moderator: {
      emoji: "⚖️",
      labelKey: "roleModerator" as const,
      containerClass: "mx-auto max-w-3xl",
      cardClass: "bg-blue-100/60 dark:bg-blue-950/40 border-blue-300 dark:border-blue-500/30",
      textClass: "text-blue-800 dark:text-blue-100",
    },
    system: {
      emoji: "📢",
      labelKey: "roleSystem" as const,
      containerClass: "mx-auto max-w-md",
      cardClass: "bg-slate-100/60 dark:bg-slate-800/50 border-slate-300 dark:border-slate-600/30",
      textClass: "text-slate-700 dark:text-slate-300",
    },
  };

  const config = roleConfig[node];

  // Moderator 使用 Markdown 渲染
  const renderContent = () => {
    if (node === "moderator") {
      return (
        <div
          className={cn(
            config.textClass,
            "prose prose-slate dark:prose-invert prose-sm max-w-none"
          )}
        >
          <ReactMarkdown
            components={{
              // 自定義標題樣式
              h2: ({ children }) => (
                <h2 className="text-lg font-bold text-blue-700 dark:text-blue-200 mt-4 mb-2 border-b border-blue-300 dark:border-blue-500/30 pb-1">
                  {children}
                </h2>
              ),
              h3: ({ children }) => (
                <h3 className="text-base font-semibold text-blue-600 dark:text-blue-300 mt-3 mb-1">
                  {children}
                </h3>
              ),
              // 粗體
              strong: ({ children }) => (
                <strong className="font-bold text-blue-700 dark:text-blue-100">{children}</strong>
              ),
              // 列表
              ul: ({ children }) => (
                <ul className="list-disc list-inside space-y-1 my-2">
                  {children}
                </ul>
              ),
              li: ({ children }) => (
                <li className="text-blue-700/90 dark:text-blue-100/90">{children}</li>
              ),
              // 段落
              p: ({ children }) => (
                <p className="text-blue-700/90 dark:text-blue-100/90 leading-relaxed my-2">
                  {children}
                </p>
              ),
            }}
          >
            {text}
          </ReactMarkdown>
          {isTyping && (
            <span className="inline-block w-2 h-4 ml-1 bg-blue-400 animate-pulse" />
          )}
        </div>
      );
    }

    // 其他角色使用純文字
    return (
      <p className={cn(config.textClass, "leading-relaxed")}>
        {text}
        {isTyping && (
          <span className="inline-block w-2 h-4 ml-1 bg-current animate-pulse" />
        )}
      </p>
    );
  };

  return (
    <div
      className={cn(
        config.containerClass,
        "animate-in fade-in slide-in-from-bottom-2"
      )}
    >
      <Card
        className={cn(
          config.cardClass,
          isTyping && "border-dashed animate-pulse"
        )}
      >
        <CardContent className="p-4">
          {/* 角色標籤 */}
          <div className="flex items-center gap-2 mb-2">
            <Badge variant={node}>
              <span>{config.emoji}</span>
              <span>{t(config.labelKey)}</span>
            </Badge>
            {roundInfo && (
              <span className="text-xs text-slate-500">• {roundInfo}</span>
            )}
            {isTyping && (
              <span className="text-xs text-slate-500">{t("isTyping")}</span>
            )}
          </div>

          {/* 訊息內容 */}
          {renderContent()}
        </CardContent>
      </Card>
    </div>
  );
}

export default MessageBubble;
