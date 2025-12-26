/**
 * MessageBubble Tests
 *
 * 測試訊息氣泡組件
 */

import { describe, it, expect } from "vitest";
import { render, screen } from "@/app/__tests__/test-utils";
import { MessageBubble } from "../MessageBubble";

describe("MessageBubble", () => {
  describe("Optimist Messages", () => {
    it("should render optimist message correctly", () => {
      render(<MessageBubble node="optimist" text="這是樂觀的觀點" />);

      expect(screen.getByText("樂觀者")).toBeInTheDocument();
      expect(screen.getByText("🤖")).toBeInTheDocument();
      expect(screen.getByText("這是樂觀的觀點")).toBeInTheDocument();
    });

    it("should show round info when provided", () => {
      render(
        <MessageBubble node="optimist" text="測試內容" roundInfo="第 1 輪" />
      );

      expect(screen.getByText(/第 1 輪/)).toBeInTheDocument();
    });

    it("should show typing indicator when isTyping is true", () => {
      render(<MessageBubble node="optimist" text="正在輸入" isTyping={true} />);

      expect(screen.getByText("正在輸入...")).toBeInTheDocument();
    });
  });

  describe("Skeptic Messages", () => {
    it("should render skeptic message correctly", () => {
      render(<MessageBubble node="skeptic" text="這是懷疑的觀點" />);

      expect(screen.getByText("懷疑者")).toBeInTheDocument();
      expect(screen.getByText("🧐")).toBeInTheDocument();
      expect(screen.getByText("這是懷疑的觀點")).toBeInTheDocument();
    });
  });

  describe("Moderator Messages", () => {
    it("should render moderator message correctly", () => {
      render(<MessageBubble node="moderator" text="## 總結報告" />);

      expect(screen.getByText("主持人")).toBeInTheDocument();
      expect(screen.getByText("⚖️")).toBeInTheDocument();
    });

    it("should render markdown content", () => {
      render(<MessageBubble node="moderator" text="**粗體文字**" />);

      // Markdown 應該被渲染
      expect(screen.getByText("粗體文字")).toBeInTheDocument();
    });
  });

  describe("System Messages", () => {
    it("should render system message correctly", () => {
      render(<MessageBubble node="system" text="辯論即將開始" />);

      expect(screen.getByText("系統")).toBeInTheDocument();
      expect(screen.getByText("📢")).toBeInTheDocument();
      expect(screen.getByText("辯論即將開始")).toBeInTheDocument();
    });
  });

  describe("Different Node Types", () => {
    it.each([
      ["optimist", "樂觀者", "🤖"],
      ["skeptic", "懷疑者", "🧐"],
      ["moderator", "主持人", "⚖️"],
      ["system", "系統", "📢"],
    ])("should render %s correctly", (node, label, emoji) => {
      render(
        <MessageBubble
          node={node as "optimist" | "skeptic" | "moderator" | "system"}
          text="測試訊息"
        />
      );

      expect(screen.getByText(label)).toBeInTheDocument();
      expect(screen.getByText(emoji)).toBeInTheDocument();
    });
  });
});
