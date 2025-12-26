/**
 * TopicForm Tests
 *
 * 測試主題輸入表單組件
 */

import { describe, it, expect, vi, beforeEach } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { TopicForm } from "../TopicForm";

describe("TopicForm", () => {
  const mockSetTopic = vi.fn();
  const mockOnStart = vi.fn();
  const mockOnStop = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  const renderTopicForm = (props = {}) => {
    const defaultProps = {
      topic: "",
      setTopic: mockSetTopic,
      isStreaming: false,
      onStart: mockOnStart,
      onStop: mockOnStop,
    };
    return render(<TopicForm {...defaultProps} {...props} />);
  };

  describe("Rendering", () => {
    it("should render input and start button", () => {
      renderTopicForm();

      expect(screen.getByPlaceholderText(/輸入辯論主題/)).toBeInTheDocument();
      expect(
        screen.getByRole("button", { name: /開始辯論/ })
      ).toBeInTheDocument();
    });

    it("should show stop button when streaming", () => {
      renderTopicForm({ isStreaming: true });

      expect(screen.getByRole("button", { name: /停止/ })).toBeInTheDocument();
      expect(
        screen.queryByRole("button", { name: /開始辯論/ })
      ).not.toBeInTheDocument();
    });

    it("should disable input when streaming", () => {
      renderTopicForm({ isStreaming: true });

      const input = screen.getByPlaceholderText(/輸入辯論主題/);
      expect(input).toBeDisabled();
    });

    it("should show powered by text", () => {
      renderTopicForm();

      expect(screen.getByText(/LangGraph/)).toBeInTheDocument();
      expect(screen.getByText(/Groq/)).toBeInTheDocument();
    });
  });

  describe("Interactions", () => {
    it("should call setTopic when typing", async () => {
      const user = userEvent.setup();
      renderTopicForm();

      const input = screen.getByPlaceholderText(/輸入辯論主題/);
      await user.type(input, "A");

      expect(mockSetTopic).toHaveBeenCalled();
    });

    it("should call onStart when form is submitted", () => {
      renderTopicForm({ topic: "AI 會取代人類嗎？" });

      const button = screen.getByRole("button", { name: /開始辯論/ });
      fireEvent.click(button);

      expect(mockOnStart).toHaveBeenCalled();
    });

    it("should not call onStart when topic is empty", () => {
      renderTopicForm({ topic: "" });

      const button = screen.getByRole("button", { name: /開始辯論/ });
      fireEvent.click(button);

      expect(mockOnStart).not.toHaveBeenCalled();
    });

    it("should not call onStart when topic is only whitespace", () => {
      renderTopicForm({ topic: "   " });

      const button = screen.getByRole("button", { name: /開始辯論/ });
      fireEvent.click(button);

      expect(mockOnStart).not.toHaveBeenCalled();
    });

    it("should call onStop when stop button is clicked", () => {
      renderTopicForm({ isStreaming: true });

      const button = screen.getByRole("button", { name: /停止/ });
      fireEvent.click(button);

      expect(mockOnStop).toHaveBeenCalled();
    });

    it("should call onStart when Enter is pressed", () => {
      renderTopicForm({ topic: "測試主題" });

      const input = screen.getByPlaceholderText(/輸入辯論主題/);
      fireEvent.keyDown(input, { key: "Enter" });

      expect(mockOnStart).toHaveBeenCalled();
    });

    it("should not call onStart when Shift+Enter is pressed", () => {
      renderTopicForm({ topic: "測試主題" });

      const input = screen.getByPlaceholderText(/輸入辯論主題/);
      fireEvent.keyDown(input, { key: "Enter", shiftKey: true });

      expect(mockOnStart).not.toHaveBeenCalled();
    });
  });

  describe("Button State", () => {
    it("should disable start button when topic is empty", () => {
      renderTopicForm({ topic: "" });

      const button = screen.getByRole("button", { name: /開始辯論/ });
      expect(button).toBeDisabled();
    });

    it("should enable start button when topic has content", () => {
      renderTopicForm({ topic: "有內容的主題" });

      const button = screen.getByRole("button", { name: /開始辯論/ });
      expect(button).not.toBeDisabled();
    });
  });
});
