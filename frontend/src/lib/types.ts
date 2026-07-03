export type Confidence = "low" | "medium" | "high";
export type SourceType = "upload" | "feishu" | "manual" | "ticket";

export interface HealthResponse {
  status: "ok";
  service: string;
  environment: string;
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
