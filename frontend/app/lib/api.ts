/**
 * API 客戶端 - SSE 串流處理
 */

// SSE 事件類型定義
export type SSEEvent =
    | { type: 'status'; text: string }
    | { type: 'speaker'; node: 'optimist' | 'skeptic' | 'moderator'; text: string }
    | { type: 'token'; node: 'optimist' | 'skeptic' | 'moderator'; text: string }
    | { type: 'speaker_end'; node: 'optimist' | 'skeptic' | 'moderator' }
    | { type: 'tool_start'; tool: string; query: string; node: string }  // Phase 3b
    | { type: 'tool_end'; tool: string; node: string }                   // Phase 3b
    | { type: 'complete'; text: string }
    | { type: 'error'; text: string };

// 辯論請求參數
export interface DebateRequest {
    topic: string;
    max_rounds?: number;
    language?: string;  // "zh" 或 "en"
}

// API URL（從環境變數讀取）
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * 串流辯論 API
 * 
 * @param request - 辯論請求參數
 * @param onEvent - SSE 事件回調
 * @param abortSignal - 用於取消請求的 AbortSignal
 * @returns Promise<void>
 */
export async function streamDebate(
    request: DebateRequest,
    onEvent: (event: SSEEvent) => void,
    abortSignal?: AbortSignal
): Promise<void> {
    const { topic, max_rounds = 3, language = "zh" } = request;

    try {
        const response = await fetch(`${API_URL}/debate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ topic, max_rounds, language }),
            signal: abortSignal,
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        if (!response.body) {
            throw new Error('Response body is null');
        }

        // 使用 ReadableStream 讀取 SSE
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();

            if (done) {
                break;
            }

            // 解碼並累積到 buffer
            buffer += decoder.decode(value, { stream: true });

            // 按行分割處理
            const lines = buffer.split('\n');
            buffer = lines.pop() || ''; // 保留最後一個不完整的行

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6)) as SSEEvent;
                        onEvent(data);
                    } catch (e) {
                        console.error('Failed to parse SSE event:', line, e);
                    }
                }
            }
        }

        // 處理 buffer 中剩餘的資料
        if (buffer.startsWith('data: ')) {
            try {
                const data = JSON.parse(buffer.slice(6)) as SSEEvent;
                onEvent(data);
            } catch {
                // 忽略不完整的最後一行
            }
        }
    } catch (error) {
        if (error instanceof Error) {
            if (error.name === 'AbortError') {
                onEvent({ type: 'status', text: '🛑 辯論已停止' });
            } else {
                onEvent({ type: 'error', text: error.message });
            }
        } else {
            onEvent({ type: 'error', text: '未知錯誤' });
        }
        throw error;
    }
}

/**
 * 健康檢查 API
 */
export async function checkHealth(): Promise<boolean> {
    try {
        const response = await fetch(`${API_URL}/health`, {
            method: 'GET',
        });
        return response.ok;
    } catch {
        return false;
    }
}


// ============================================================
// Phase 4: Debate History Types & API
// ============================================================

/** 訊息格式 (前端使用) */
export interface Message {
    node: "optimist" | "skeptic" | "moderator" | "system";
    text: string;
    roundInfo?: string;
}

/** 辯論摘要 (列表用) */
export interface DebateSummary {
    id: string;
    topic: string;
    created_at: string;
    rounds_completed: number;
}

/** 辯論詳細 */
export interface DebateDetail extends DebateSummary {
    messages: Array<{
        version: number;
        type: string;
        content: string;
        node?: "optimist" | "skeptic" | "moderator" | null;
        roundInfo?: string;
        timestamp?: string;
    }>;
    max_rounds: number;
    updated_at: string;
}

/** 分頁結果 */
export interface PaginatedResult<T> {
    data: T[];
    total: number;
    page: number;
    page_size: number;
}

/**
 * 儲存辯論到資料庫
 */
export async function saveDebate(
    topic: string,
    messages: Message[],
    maxRounds: number = 3,
    roundsCompleted: number = 0
): Promise<{ success: boolean; debate_id?: string; error?: string }> {
    try {
        const response = await fetch(`${API_URL}/debate/save`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                topic,
                messages,
                max_rounds: maxRounds,
                rounds_completed: roundsCompleted,
            }),
        });

        if (!response.ok) {
            return { success: false, error: `HTTP ${response.status}` };
        }

        return await response.json();
    } catch (error) {
        console.error('Save debate failed:', error);
        return { success: false, error: String(error) };
    }
}

/**
 * 取得最近辯論列表 (用於 sidebar)
 */
export async function getRecentDebates(limit: number = 5): Promise<DebateSummary[]> {
    try {
        const response = await fetch(`${API_URL}/debate/history?limit=${limit}`);

        if (!response.ok) {
            return [];
        }

        const data = await response.json();
        return data.debates || [];
    } catch (error) {
        console.error('Get recent debates failed:', error);
        return [];
    }
}

/**
 * 取得單一辯論詳細內容
 */
export async function getDebateById(id: string): Promise<DebateDetail | null> {
    try {
        const response = await fetch(`${API_URL}/debate/history/${id}`);

        if (!response.ok) {
            return null;
        }

        return await response.json();
    } catch (error) {
        console.error('Get debate by id failed:', error);
        return null;
    }
}

/**
 * 分頁取得辯論列表
 */
export async function getDebatesPaginated(
    page: number = 1,
    pageSize: number = 20
): Promise<PaginatedResult<DebateSummary>> {
    try {
        const response = await fetch(
            `${API_URL}/debate/history/list?page=${page}&page_size=${pageSize}`
        );

        if (!response.ok) {
            return { data: [], total: 0, page, page_size: pageSize };
        }

        return await response.json();
    } catch (error) {
        console.error('Get debates paginated failed:', error);
        return { data: [], total: 0, page, page_size: pageSize };
    }
}

