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
  answer: string;
  solution_steps: string[];
  confidence: Confidence;
  sources: SourceCitation[];
  handoff_required: boolean;
  handoff_reason: string;
}
