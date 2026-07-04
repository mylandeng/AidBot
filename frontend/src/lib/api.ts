import type {
  ChatRequest,
  ChatResponse,
  ChatStreamEvent,
  ConversationDetail,
  ConversationSummary,
  HealthResponse,
  KnowledgeSource,
  KnowledgeSourceList,
  LoginResponse,
  ManualKnowledgeRequest,
  MarkdownKnowledgeRequest,
} from "./types";

const PUBLIC_API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8010";
const SERVER_API_BASE_URL = process.env.API_INTERNAL_BASE_URL ?? PUBLIC_API_BASE_URL;

function apiBaseUrl(): string {
  return typeof window === "undefined" ? SERVER_API_BASE_URL : PUBLIC_API_BASE_URL;
}

export async function getHealth(): Promise<HealthResponse | null> {
  try {
    const response = await fetch(`${apiBaseUrl()}/health`, {
      next: { revalidate: 10 },
    });

    if (!response.ok) {
      return null;
    }

    return response.json();
  } catch {
    return null;
  }
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${apiBaseUrl()}/api/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    throw new Error("邮箱或密码不正确");
  }

  return response.json();
}

async function authorized<T>(path: string, token: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl()}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}`, ...init?.headers },
    cache: "no-store",
  });
  if (!response.ok) throw new Error(response.status === 401 ? "登录已失效，请重新登录" : "请求失败，请稍后重试");
  return response.json();
}

export function askQuestion(request: ChatRequest, token: string): Promise<ChatResponse> {
  return authorized("/api/chat", token, { method: "POST", body: JSON.stringify(request) });
}

export async function askQuestionStream(
  request: ChatRequest,
  token: string,
  onEvent: (event: ChatStreamEvent) => void,
): Promise<ChatResponse> {
  const response = await fetch(`${apiBaseUrl()}/api/chat/stream`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(request),
    cache: "no-store",
  });

  if (!response.ok || !response.body) {
    throw new Error(response.status === 401 ? "登录已失效，请重新登录" : "请求失败，请稍后重试");
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let finalResult: ChatResponse | null = null;

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const events = buffer.split("\n\n");
    buffer = events.pop() ?? "";
    for (const rawEvent of events) {
      const event = parseStreamEvent(rawEvent);
      if (!event) continue;
      onEvent(event);
      if (event.event === "final") {
        finalResult = event.data;
      }
      if (event.event === "error") {
        throw new Error(event.data.message);
      }
    }
  }

  if (!finalResult) {
    throw new Error("回答生成中断，请重试");
  }
  return finalResult;
}

function parseStreamEvent(rawEvent: string): ChatStreamEvent | null {
  const eventName = rawEvent.split("\n").find((line) => line.startsWith("event: "))?.replace("event: ", "").trim();
  const dataLine = rawEvent.split("\n").find((line) => line.startsWith("data: "));
  if (!eventName || !dataLine) return null;

  try {
    const data = JSON.parse(dataLine.replace("data: ", ""));
    if (eventName === "message_start" || eventName === "answer_delta" || eventName === "final" || eventName === "error") {
      return { event: eventName, data } as ChatStreamEvent;
    }
  } catch {
    return null;
  }
  return null;
}

export function listConversations(token: string): Promise<ConversationSummary[]> {
  return authorized("/api/conversations", token);
}

export function getConversation(id: string, token: string): Promise<ConversationDetail> {
  return authorized(`/api/conversations/${id}`, token);
}

export async function listKnowledgeSources(token: string): Promise<KnowledgeSource[]> {
  const payload = await authorized<KnowledgeSourceList>("/api/knowledge/sources", token);
  return payload.items;
}

export function createManualKnowledge(request: ManualKnowledgeRequest, token: string): Promise<KnowledgeSource> {
  return authorized("/api/knowledge/manual", token, { method: "POST", body: JSON.stringify(request) });
}

export function importMarkdownKnowledge(request: MarkdownKnowledgeRequest, token: string): Promise<KnowledgeSource> {
  return authorized("/api/knowledge/markdown", token, { method: "POST", body: JSON.stringify(request) });
}
