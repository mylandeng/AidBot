export type Confidence = "low" | "medium" | "high";
export type SourceType = "upload" | "feishu" | "manual" | "ticket";
export type RetrievalProvider = "local" | "external";
export type FeedbackRating = "useful" | "not_useful" | "needs_review" | "needs_human";
export type FeedbackStatus = "pending" | "processing" | "resolved" | "ignored";

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
  auth_method: "password" | "access_key";
  key_id?: string | null;
  key_expires_at?: string | null;
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
  space_id?: string | null;
  product_line?: string | null;
  retrieval_provider?: RetrievalProvider;
}

export interface SourceCitation {
  title: string;
  source_type: SourceType;
  doc_id: string;
  chunk_id: string;
  score: number;
  updated_at: string;
  section_path: string;
  excerpt: string;
  space_id?: string | null;
  space_name?: string | null;
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

export interface UserChatResponse {
  conversation_id: string;
  message_id: string;
  answer: string;
  handoff_required: boolean;
  handoff_reason: string;
}

export interface ErrorPayload {
  code: string;
  message: string;
  retryable: boolean;
  request_id: string;
  details?: unknown;
}

export type ChatStreamEvent =
  | { event: "message_start"; data: { conversation_id: string } }
  | { event: "answer_delta"; data: { delta: string } }
  | { event: "final"; data: ChatResponse | UserChatResponse }
  | { event: "error"; data: ErrorPayload };

export interface ConversationSummary {
  id: string;
  title: string;
  product_line?: string | null;
  retrieval_provider: RetrievalProvider;
  status: "active" | "archived";
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
  delivery_status?: "failed" | "stopped";
  error_code?: string;
  error_message?: string;
  error_request_id?: string;
  retry_question?: string;
}

export interface ConversationDetail extends ConversationSummary {
  messages: ConversationMessage[];
}

export interface DeleteConversationsResponse {
  deleted_count: number;
}

export interface KnowledgeSource {
  id: string;
  space_id?: string | null;
  space_name?: string | null;
  title: string;
  source_type: SourceType;
  content_format: "text" | "markdown" | "html" | "pdf";
  filename: string;
  visibility: "internal" | "private";
  status: string;
  chunk_count: number;
  updated_at: string;
}

export interface KnowledgeSourceList {
  items: KnowledgeSource[];
}

export interface KnowledgeSpace {
  id: string;
  name: string;
  product_line?: string | null;
  description: string;
  visibility: "internal" | "private";
  status: string;
  source_count: number;
  chunk_count: number;
  updated_at: string;
}

export interface KnowledgeSpaceList {
  items: KnowledgeSpace[];
}

export interface KnowledgeSpaceRequest {
  name: string;
  product_line: string;
  description: string;
  visibility: "internal" | "private";
}

export interface KnowledgeSpaceUpdateRequest {
  name: string;
  product_line: string;
}

export interface ManualKnowledgeRequest {
  title: string;
  content: string;
  visibility: "internal" | "private";
  space_id?: string | null;
}

export interface MarkdownKnowledgeRequest extends ManualKnowledgeRequest {
  filename: string;
}

export interface KnowledgeDocumentRequest extends ManualKnowledgeRequest {
  filename: string;
  content_format: "text" | "markdown" | "html" | "pdf";
}

export interface FeedbackCreateRequest {
  message_id: string;
  rating: FeedbackRating;
  tags?: string[];
  note?: string;
}

export interface FeedbackStatusRequest {
  status: FeedbackStatus;
  admin_note?: string;
}

export interface FeedbackItem {
  id: string;
  message_id: string;
  conversation_id: string;
  product_line?: string | null;
  rating: FeedbackRating;
  status: FeedbackStatus;
  tags: string[];
  note: string;
  admin_note: string;
  answer_preview: string;
  question_preview: string;
  source_count: number;
  created_at: string;
  updated_at: string;
}

export interface FeedbackList {
  items: FeedbackItem[];
  product_lines: string[];
}

export type AccessKeyDuration = "7d" | "30d" | "180d" | "365d";
export type AccessKeyStatus = "active" | "disabled" | "deleted";

export interface AccessKey {
  id: string;
  name: string;
  key_prefix: string;
  status: AccessKeyStatus;
  expires_at: string;
  max_requests?: number | null;
  used_requests: number;
  max_tokens?: number | null;
  used_tokens: number;
  note: string;
  last_used_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface AccessKeyCreateRequest {
  name: string;
  expires_in: AccessKeyDuration;
  max_requests?: number | null;
  max_tokens?: number | null;
  note?: string;
}

export interface AccessKeyCreateResponse {
  item: AccessKey;
  access_key: string;
}
