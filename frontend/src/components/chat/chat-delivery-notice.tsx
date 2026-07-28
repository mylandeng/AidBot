import type { ConversationMessage } from "@/lib/types";

interface ChatDeliveryNoticeProps {
  message: ConversationMessage;
  onRetry: (question: string) => void;
  showDiagnostic?: boolean;
}

export function ChatDeliveryNotice({ message, onRetry, showDiagnostic = false }: ChatDeliveryNoticeProps) {
  if (!message.delivery_status || !message.error_message) return null;

  const stopped = message.delivery_status === "stopped";
  return (
    <div className={`chat-delivery-notice ${stopped ? "stopped" : "failed"}`} role={stopped ? "status" : "alert"}>
      <div>
        <strong>{stopped ? "已停止生成" : "回答生成失败"}</strong>
        <p>{message.error_message}</p>
        {showDiagnostic && message.error_code ? (
          <small>
            错误码：{message.error_code}
            {message.error_request_id ? ` · 请求 ID：${message.error_request_id}` : ""}
          </small>
        ) : null}
      </div>
      {message.retry_question ? (
        <button onClick={() => onRetry(message.retry_question ?? "")} type="button">
          再次提问
        </button>
      ) : null}
    </div>
  );
}
