import type {
  AccessKey,
  AccessKeyCreateRequest,
  AccessKeyCreateResponse,
  ChatRequest,
  ChatResponse,
  ChatStreamEvent,
  ConversationDetail,
  ConversationSummary,
  DeleteConversationsResponse,
  ErrorPayload,
  FeedbackCreateRequest,
  FeedbackItem,
  FeedbackList,
  FeedbackStatus,
  FeedbackStatusRequest,
  HealthResponse,
  KnowledgeSource,
  KnowledgeSourceList,
  KnowledgeSpace,
  KnowledgeSpaceList,
  KnowledgeSpaceRequest,
  KnowledgeSpaceUpdateRequest,
  KnowledgeDocumentRequest,
  LoginResponse,
  ManualKnowledgeRequest,
  MarkdownKnowledgeRequest,
  UserChatResponse,
} from "./types";

declare global {
  interface Window {
    __AIDBOT_CONFIG__?: {
      apiBaseUrl?: string;
    };
  }
}

const BUILD_PUBLIC_API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8010";
const SERVER_API_BASE_URL = process.env.API_INTERNAL_BASE_URL ?? BUILD_PUBLIC_API_BASE_URL;

export class ApiError extends Error {
  readonly code: string;
  readonly retryable: boolean;
  readonly requestId: string;
  readonly status: number;

  constructor(payload: ErrorPayload, status = 0) {
    super(payload.message);
    this.name = "ApiError";
    this.code = payload.code;
    this.retryable = payload.retryable;
    this.requestId = payload.request_id;
    this.status = status;
  }
}

function apiBaseUrl(): string {
  if (typeof window === "undefined") return SERVER_API_BASE_URL;
  return window.__AIDBOT_CONFIG__?.apiBaseUrl || BUILD_PUBLIC_API_BASE_URL;
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
    throw await apiErrorFromResponse(response, "邮箱或密码不正确");
  }

  return response.json();
}

export async function keyLogin(accessKey: string): Promise<LoginResponse> {
  const response = await fetch(`${apiBaseUrl()}/api/auth/key-login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ access_key: accessKey }),
  });

  if (!response.ok) {
    throw await apiErrorFromResponse(response, "访问码无效、已过期或已被禁用");
  }

  return response.json();
}

async function authorized<T>(path: string, token: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBaseUrl()}${path}`, {
    ...init,
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}`, ...init?.headers },
    cache: "no-store",
  });
  if (!response.ok) {
    throw await apiErrorFromResponse(response, response.status === 401 ? "登录已失效，请重新登录" : "请求失败，请稍后重试");
  }
  if (response.status === 204) return undefined as T;
  return response.json();
}

export function askQuestion(request: ChatRequest, token: string): Promise<ChatResponse> {
  return authorized("/api/chat", token, { method: "POST", body: JSON.stringify(request) });
}

export async function askQuestionStream(
  request: ChatRequest,
  token: string,
  onEvent: (event: ChatStreamEvent) => void,
  signal?: AbortSignal,
): Promise<ChatResponse> {
  return askAdminQuestionStream(request, token, onEvent, signal);
}

export async function askAdminQuestionStream(
  request: ChatRequest,
  token: string,
  onEvent: (event: ChatStreamEvent) => void,
  signal?: AbortSignal,
): Promise<ChatResponse> {
  return streamChat<ChatResponse>("/api/admin/chat/stream", request, token, onEvent, signal);
}

export async function askUserQuestionStream(
  request: ChatRequest,
  token: string,
  onEvent: (event: ChatStreamEvent) => void,
  signal?: AbortSignal,
): Promise<UserChatResponse> {
  return streamChat<UserChatResponse>("/api/user/chat/stream", request, token, onEvent, signal);
}

async function streamChat<T extends ChatResponse | UserChatResponse>(
  path: string,
  request: ChatRequest,
  token: string,
  onEvent: (event: ChatStreamEvent) => void,
  signal?: AbortSignal,
): Promise<T> {
  const response = await fetch(`${apiBaseUrl()}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
    body: JSON.stringify(request),
    cache: "no-store",
    signal,
  });

  if (!response.ok || !response.body) {
    if (!response.ok) {
      throw await apiErrorFromResponse(response, response.status === 401 ? "登录已失效，请重新登录" : "请求失败，请稍后重试");
    }
    throw new ApiError(
      {
        code: "STREAM_UNAVAILABLE",
        message: "回答通道不可用，请稍后重试。",
        retryable: true,
        request_id: response.headers.get("X-Request-ID") ?? "",
      },
      response.status,
    );
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  let finalResult: T | null = null;

  try {
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
          finalResult = event.data as T;
        }
        if (event.event === "error") {
          throw new ApiError(event.data, response.status);
        }
      }
    }
  } finally {
    reader.releaseLock();
  }

  if (!finalResult) {
    throw new Error("回答生成中断，请重试");
  }
  return finalResult;
}

export function requestErrorMessage(reason: unknown, fallback = "请求失败，请稍后重试。"): string {
  if (reason instanceof ApiError) return reason.message;
  if (reason instanceof TypeError) return "无法连接到服务器，请检查网络后重试。";
  if (reason instanceof Error && reason.message.trim()) {
    const message = reason.message.trim();
    const normalizedMessage = message.toLowerCase();
    if (
      normalizedMessage.includes("failed to fetch") ||
      normalizedMessage.includes("networkerror") ||
      normalizedMessage.includes("load failed")
    ) {
      return "无法连接到服务器，请检查网络后重试。";
    }
    return message;
  }
  return fallback;
}

async function apiErrorFromResponse(response: Response, fallbackMessage: string): Promise<ApiError> {
  const requestId = response.headers.get("X-Request-ID") ?? "";
  let body: unknown;
  try {
    body = await response.json();
  } catch {
    body = null;
  }

  const payload = errorPayloadFromBody(body, fallbackMessage, requestId);
  return new ApiError(payload, response.status);
}

function errorPayloadFromBody(body: unknown, fallbackMessage: string, requestId: string): ErrorPayload {
  if (isRecord(body) && isRecord(body.error)) {
    const error = body.error;
    return {
      code: stringValue(error.code) || "REQUEST_FAILED",
      message: stringValue(error.message) || fallbackMessage,
      retryable: error.retryable === true,
      request_id: stringValue(error.request_id) || requestId,
      details: error.details,
    };
  }

  if (isRecord(body) && isRecord(body.detail)) {
    return {
      code: stringValue(body.detail.code) || "REQUEST_FAILED",
      message: stringValue(body.detail.message) || fallbackMessage,
      retryable: false,
      request_id: requestId,
    };
  }

  const legacyMessage = isRecord(body) ? stringValue(body.detail) : "";
  return {
    code: "REQUEST_FAILED",
    message: legacyMessage || fallbackMessage,
    retryable: false,
    request_id: requestId,
  };
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function stringValue(value: unknown): string {
  return typeof value === "string" ? value.trim() : "";
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

export function listConversations(token: string, options?: { q?: string; includeArchived?: boolean }): Promise<ConversationSummary[]> {
  const params = new URLSearchParams();
  if (options?.q?.trim()) params.set("q", options.q.trim());
  if (options?.includeArchived) params.set("include_archived", "true");
  const query = params.toString();
  return authorized(`/api/conversations${query ? `?${query}` : ""}`, token);
}

export function getConversation(id: string, token: string): Promise<ConversationDetail> {
  return authorized(`/api/conversations/${id}`, token);
}

export function archiveConversation(id: string, token: string): Promise<ConversationSummary> {
  return authorized(`/api/conversations/${id}/archive`, token, { method: "POST" });
}

export function restoreConversation(id: string, token: string): Promise<ConversationSummary> {
  return authorized(`/api/conversations/${id}/restore`, token, { method: "POST" });
}

export function deleteConversation(id: string, token: string): Promise<void> {
  return authorized(`/api/conversations/${id}`, token, { method: "DELETE" });
}

export function clearConversations(token: string): Promise<DeleteConversationsResponse> {
  return authorized("/api/conversations", token, { method: "DELETE" });
}

export async function listKnowledgeSources(token: string, spaceId?: string): Promise<KnowledgeSource[]> {
  const query = spaceId ? `?space_id=${encodeURIComponent(spaceId)}` : "";
  const payload = await authorized<KnowledgeSourceList>(`/api/knowledge/sources${query}`, token);
  return payload.items;
}

export async function listKnowledgeSpaces(token: string): Promise<KnowledgeSpace[]> {
  const payload = await authorized<KnowledgeSpaceList>("/api/knowledge/spaces", token);
  return payload.items;
}

export function createKnowledgeSpace(request: KnowledgeSpaceRequest, token: string): Promise<KnowledgeSpace> {
  return authorized("/api/knowledge/spaces", token, { method: "POST", body: JSON.stringify(request) });
}

export function updateKnowledgeSpace(id: string, request: KnowledgeSpaceUpdateRequest, token: string): Promise<KnowledgeSpace> {
  return authorized(`/api/knowledge/spaces/${id}`, token, { method: "PATCH", body: JSON.stringify(request) });
}

export function deleteKnowledgeSpace(id: string, token: string): Promise<void> {
  return authorized(`/api/knowledge/spaces/${id}`, token, { method: "DELETE" });
}

export function createManualKnowledge(request: ManualKnowledgeRequest, token: string): Promise<KnowledgeSource> {
  return authorized("/api/knowledge/manual", token, { method: "POST", body: JSON.stringify(request) });
}

export function importMarkdownKnowledge(request: MarkdownKnowledgeRequest, token: string): Promise<KnowledgeSource> {
  return authorized("/api/knowledge/markdown", token, { method: "POST", body: JSON.stringify(request) });
}

export function importKnowledgeDocument(request: KnowledgeDocumentRequest, token: string): Promise<KnowledgeSource> {
  return authorized("/api/knowledge/documents", token, { method: "POST", body: JSON.stringify(request) });
}

export function reindexKnowledgeSource(id: string, token: string): Promise<KnowledgeSource> {
  return authorized(`/api/knowledge/sources/${id}/reindex`, token, { method: "POST" });
}

export function deleteKnowledgeSource(id: string, token: string): Promise<void> {
  return authorized(`/api/knowledge/sources/${id}`, token, { method: "DELETE" });
}

export function listFeedback(token: string, status?: FeedbackStatus, productLine?: string): Promise<FeedbackList> {
  const query = new URLSearchParams();
  if (status) query.set("status", status);
  if (productLine) query.set("product_line", productLine);
  const suffix = query.size ? `?${query.toString()}` : "";
  return authorized<FeedbackList>(`/api/feedback${suffix}`, token);
}

export function createFeedback(request: FeedbackCreateRequest, token: string): Promise<FeedbackItem> {
  return authorized("/api/feedback", token, { method: "POST", body: JSON.stringify(request) });
}

export function createUserFeedback(request: FeedbackCreateRequest, token: string): Promise<{ id: string; status: string }> {
  return authorized("/api/user/feedback", token, { method: "POST", body: JSON.stringify(request) });
}

export function updateFeedbackStatus(id: string, request: FeedbackStatusRequest, token: string): Promise<FeedbackItem> {
  return authorized(`/api/feedback/${id}`, token, { method: "PATCH", body: JSON.stringify(request) });
}

export async function listAccessKeys(token: string): Promise<AccessKey[]> {
  const payload = await authorized<{ items: AccessKey[] }>("/api/admin/access-keys", token);
  return payload.items;
}

export function createAccessKey(request: AccessKeyCreateRequest, token: string): Promise<AccessKeyCreateResponse> {
  return authorized("/api/admin/access-keys", token, { method: "POST", body: JSON.stringify(request) });
}

export function disableAccessKey(id: string, token: string): Promise<AccessKey> {
  return authorized(`/api/admin/access-keys/${id}/disable`, token, { method: "POST" });
}

export function enableAccessKey(id: string, token: string): Promise<AccessKey> {
  return authorized(`/api/admin/access-keys/${id}/enable`, token, { method: "POST" });
}

export function deleteAccessKey(id: string, token: string): Promise<void> {
  return authorized(`/api/admin/access-keys/${id}`, token, { method: "DELETE" });
}
