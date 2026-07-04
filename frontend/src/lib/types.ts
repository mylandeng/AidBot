export type Confidence = "low" | "medium" | "high";
export type SourceType = "upload" | "feishu" | "manual" | "ticket";

export interface HealthResponse {
  status: "ok";
  service: string;
  environment: string;
}

export interface CurrentUser {
  id: string;
  email: string;
  name: string;
  roles: string[];
}

export interface LoginResponse {
  access_token: string;
  token_type: "bearer";
  expires_in: number;
  user: CurrentUser;
}

export interface ChatRequest {
  question: string;
  conversation_id?: string | null;
  product_line?: string | null;
}

export interface SourceCitation {
  title: string;
  source_type: SourceType;
  doc_id: string;
  chunk_id: string;
  score: number;
  updated_at: string;
}

export interface ChatResponse {
  conversation_id: string;
  message_id: string;
  answer: string;
  solution_steps: string[];
  confidence: Confidence;
  sources: SourceCitation[];
  handoff_required: boolean;
  handoff_reason: string;
}

export type ChatStreamEvent =
  | { event: "message_start"; data: { conversation_id: string } }
  | { event: "answer_delta"; data: { delta: string } }
  | { event: "final"; data: ChatResponse }
  | { event: "error"; data: { message: string } };

export interface ConversationSummary {
  id: string;
  title: string;
  product_line?: string | null;
  updated_at: string;
  message_count: number;
}

export interface ConversationMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  solution_steps: string[];
  sources: SourceCitation[];
  confidence: Confidence;
  created_at: string;
}

export interface ConversationDetail extends ConversationSummary {
  messages: ConversationMessage[];
}
