"use client";

import React from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Rocket, Square } from "lucide-react";
import { useI18n } from "@/lib/i18n";

export interface TopicFormProps {
  topic: string;
  setTopic: (topic: string) => void;
  isStreaming: boolean;
  onStart: () => void;
  onStop: () => void;
}

/**
 * 主題輸入表單組件 - shadcn/ui 版本
 *
 * - 固定在底部
 * - 支援 Enter 提交
 * - 串流中顯示停止按鈕
 */
export function TopicForm({
  topic,
  setTopic,
  isStreaming,
  onStart,
  onStop,
}: TopicFormProps) {
  const { t } = useI18n();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!isStreaming && topic.trim()) {
      onStart();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!isStreaming && topic.trim()) {
        onStart();
      }
    }
  };

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <div className="flex gap-3">
        {/* 輸入框 */}
        <div className="flex-1">
          <Input
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isStreaming}
            placeholder={t("topicPlaceholder")}
          />
        </div>

        {/* 按鈕區 */}
        {isStreaming ? (
          <Button type="button" variant="destructive" onClick={onStop}>
            <Square className="size-4" />
            {t("topicStop")}
          </Button>
        ) : (
          <Button type="submit" disabled={!topic.trim()}>
            <Rocket className="size-4" />
            {t("topicStart")}
          </Button>
        )}
      </div>

      {/* 提示文字 */}
      <p className="mt-3 text-center text-xs text-slate-500 dark:text-slate-500">
        {t("topicPoweredBy")} <span className="text-purple-600 dark:text-purple-400">LangGraph 1.0</span> &{" "}
        <span className="text-blue-600 dark:text-blue-400">Groq</span> {t("topicTestVersion")}
      </p>
    </form>
  );
}

export default TopicForm;
