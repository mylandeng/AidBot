"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";

import { MessageContent } from "@/components/chat/message-content";
import { ComposerSendButton } from "@/components/ui/composer-send-button";
import { DeleteConfirmDialog } from "@/components/ui/delete-confirm-dialog";
import { askAdminQuestionStream, clearConversations, deleteConversation, getConversation, listConversations } from "@/lib/api";
import { createClientId } from "@/lib/client-id";
import type { ChatResponse, ConversationMessage, ConversationSummary, SourceCitation } from "@/lib/types";

const examples = [
  "AX-42 配网后 App 仍显示离线，应该如何排查？",
  "客户反馈固件升级失败，后台应该先看哪些证据？",
  "哪些情况应该建议转人工处理？",
];
const collapsedHistoryCount = 5;

type DeleteDialogState =
  | { id: string; kind: "single"; title: string }
  | { count: number; kind: "all" }
  | null;

export function AdminChatWorkbench({ token }: { token: string }) {
  const [items, setItems] = useState<ConversationSummary[]>([]);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<ChatResponse | null>(null);
  const [question, setQuestion] = useState("");
  const [error, setError] = useState("");
  const [copiedId, setCopiedId] = useState("");
  const [selectedSource, setSelectedSource] = useState<SourceCitation | null>(null);
  const [deletingConversationId, setDeletingConversationId] = useState("");
  const [clearingConversations, setClearingConversations] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState<DeleteDialogState>(null);
  const [historyExpanded, setHistoryExpanded] = useState(false);
  const [busy, setBusy] = useState(false);
  const streamEndRef = useRef<HTMLDivElement | null>(null);
  const questionInputRef = useRef<HTMLTextAreaElement | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const lastMessageContent = messages.at(-1)?.content ?? "";
  const visibleHistoryItems = useMemo(
    () => (historyExpanded ? items : items.slice(0, collapsedHistoryCount)),
    [historyExpanded, items],
  );
  const hiddenHistoryCount = Math.max(items.length - collapsedHistoryCount, 0);

  async function refreshList() {
    setItems(await listConversations(token));
  }

  useEffect(() => {
    refreshList().catch(() => setError("会话列表加载失败"));
  }, []);

  useEffect(() => {
    streamEndRef.current?.scrollIntoView({ behavior: busy ? "auto" : "smooth", block: "end" });
  }, [busy, messages.length, lastMessageContent]);

  useEffect(() => {
    const input = questionInputRef.current;
    if (!input) return;
    input.style.height = "auto";
    const nextHeight = Math.min(input.scrollHeight, 132);
    input.style.height = `${nextHeight}px`;
    input.style.overflowY = input.scrollHeight > 132 ? "auto" : "hidden";
  }, [question]);

  async function openConversation(id: string) {
    const detail = await getConversation(id, token);
    setConversationId(id);
    setMessages(detail.messages);
    setLastResult(null);
    setQuestion("");
    setError("");
    setCopiedId("");
    setSelectedSource(null);
    setBusy(false);
  }

  async function copyText(id: string, text: string) {
    if (!text.trim()) return;
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(text);
      } else {
        const textarea = document.createElement("textarea");
        textarea.value = text;
        textarea.style.position = "fixed";
        textarea.style.left = "-9999px";
        document.body.appendChild(textarea);
        textarea.focus();
        textarea.select();
        document.execCommand("copy");
        document.body.removeChild(textarea);
      }
      setCopiedId(id);
      window.setTimeout(() => setCopiedId((current) => (current === id ? "" : current)), 1400);
    } catch {
      setError("复制失败，请手动选择文本复制");
    }
  }

  function requestRemoveConversation(item: ConversationSummary) {
    if (deletingConversationId || clearingConversations) return;
    setDeleteDialog({ id: item.id, kind: "single", title: item.title });
  }

  function requestRemoveAllConversations() {
    if (clearingConversations || !items.length) return;
    setDeleteDialog({ count: items.length, kind: "all" });
  }

  async function removeConversation(id: string) {
    if (deletingConversationId) return;
    setDeletingConversationId(id);
    setError("");
    try {
      await deleteConversation(id, token);
      setItems((current) => current.filter((item) => item.id !== id));
      if (id === conversationId) {
        setConversationId(null);
        setMessages([]);
        setLastResult(null);
        setQuestion("");
        setSelectedSource(null);
        setBusy(false);
      }
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "删除会话失败");
    } finally {
      setDeletingConversationId("");
      setDeleteDialog(null);
    }
  }

  async function removeAllConversations() {
    if (clearingConversations || !items.length) return;
    setClearingConversations(true);
    setError("");
    try {
      await clearConversations(token);
      setItems([]);
      setConversationId(null);
      setMessages([]);
      setLastResult(null);
      setQuestion("");
      setSelectedSource(null);
      setBusy(false);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "清空聊天记录失败");
    } finally {
      setClearingConversations(false);
      setDeleteDialog(null);
    }
  }

  async function confirmDeleteDialog() {
    if (!deleteDialog) return;
    if (deleteDialog.kind === "single") {
      await removeConversation(deleteDialog.id);
      return;
    }
    await removeAllConversations();
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!question.trim() || busy) return;

    const text = question.trim();
    const userTempId = createClientId("user");
    const assistantTempId = createClientId("assistant");
    const controller = new AbortController();
    abortRef.current = controller;
    setBusy(true);
    setError("");
    setQuestion("");
    setLastResult(null);
    setMessages((current) => [
      ...current,
      createTempMessage(userTempId, "user", text),
      createTempMessage(assistantTempId, "assistant", ""),
    ]);

    try {
      const result = await askAdminQuestionStream({ question: text, conversation_id: conversationId }, token, (streamEvent) => {
        if (streamEvent.event === "message_start") {
          setConversationId(streamEvent.data.conversation_id);
          return;
        }
        if (streamEvent.event === "answer_delta") {
          setMessages((current) =>
            current.map((message) =>
              message.id === assistantTempId ? { ...message, content: `${message.content}${streamEvent.data.delta}` } : message,
            ),
          );
          return;
        }
        if (streamEvent.event === "final") {
          const data = streamEvent.data as ChatResponse;
          setLastResult(data);
          setConversationId(data.conversation_id);
          setMessages((current) =>
            current.map((message) =>
              message.id === assistantTempId
                ? { ...message, id: data.message_id, confidence: data.confidence, solution_steps: data.solution_steps, sources: data.sources }
                : message,
            ),
          );
        }
      }, controller.signal);
      setConversationId(result.conversation_id);
      await Promise.all([openConversation(result.conversation_id), refreshList()]);
      setLastResult(result);
    } catch (reason) {
      if (reason instanceof DOMException && reason.name === "AbortError") return;
      setError(reason instanceof Error ? reason.message : "提问失败");
      setMessages((current) => current.filter((message) => message.id !== assistantTempId));
    } finally {
      abortRef.current = null;
      setBusy(false);
    }
  }

  return (
    <>
      <header className="topbar">
        <div>
          <p className="eyebrow">聊一聊</p>
          <h1>用管理员通道测试知识库回答和引用质量。</h1>
        </div>
        <button
          className="secondary-button"
          onClick={() => {
            setConversationId(null);
            setMessages([]);
            setLastResult(null);
            setQuestion("");
            setError("");
            setSelectedSource(null);
            setBusy(false);
          }}
          type="button"
        >
          新会话
        </button>
      </header>

      <section className="content admin-chat-grid">
        <section className="ask-panel chat-panel" aria-label="管理员测试聊天">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">测试问答</p>
              <h2>{messages.length ? "继续测试" : "选择一个测试问题"}</h2>
            </div>
            {lastResult ? <span className="confidence-chip">置信度：{confidenceLabel(lastResult.confidence)}</span> : null}
          </div>

          <section className="message-stream">
            {messages.length ? (
              messages.map((message) => (
                <article className={`message ${message.role}`} key={message.id}>
                  <div className="message-header">
                    <span>{message.role === "user" ? "测试问题" : "AidBot 回复"}</span>
                    <button className="copy-button" onClick={() => copyText(message.id, message.content)} type="button">
                      {copiedId === message.id ? "已复制" : "复制"}
                    </button>
                  </div>
                  <MessageContent content={message.content} markdown={message.role === "assistant"} />
                  {message.role === "assistant" && message.sources?.length ? (
                    <div className="admin-source-list">
                      {message.sources.map((source) => (
                        <button className="source-chip" key={`${message.id}-${source.chunk_id}`} onClick={() => setSelectedSource(source)} type="button">
                          {source.title} · {source.score.toFixed(2)}
                        </button>
                      ))}
                    </div>
                  ) : null}
                </article>
              ))
            ) : (
              <div className="empty-chat">
                <b>这个聊天框只用于管理员测试。</b>
                <p>例如：</p>
                <div className="example-list">
                  {examples.map((example) => (
                    <button key={example} onClick={() => setQuestion(example)} type="button">
                      {example}
                    </button>
                  ))}
                </div>
              </div>
            )}
            <div aria-hidden="true" ref={streamEndRef} />
          </section>

          <form className="chat-composer" onSubmit={submit}>
            <div className="composer-input">
              <textarea
                aria-label="测试问题"
                placeholder="输入要验证的售后问题"
                ref={questionInputRef}
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    event.currentTarget.form?.requestSubmit();
                  }
                }}
              />
              <ComposerSendButton busy={busy} onStop={() => abortRef.current?.abort()} />
            </div>
            {error ? <p className="form-error">{error}</p> : null}
          </form>
        </section>

        <aside className="side-stack" aria-label="会话与调试信息">
          <section className={historyExpanded ? "source-panel history-panel expanded" : "source-panel history-panel"}>
            <div className="panel-heading compact">
              <div>
                <p className="eyebrow">最近会话</p>
                <h2>{items.length ? `${items.length} 条记录` : "暂无记录"}</h2>
              </div>
              {items.length ? (
                <button className="history-clear" disabled={clearingConversations} onClick={requestRemoveAllConversations} type="button">
                  {clearingConversations ? "清空中" : "清空全部"}
                </button>
              ) : null}
            </div>
            <div className={historyExpanded ? "chat-history-list expanded" : "chat-history-list"}>
              {visibleHistoryItems.map((item) => (
                <article className={`history-item ${item.id === conversationId ? "active" : ""}`} key={item.id}>
                  <button className="history-open" onClick={() => openConversation(item.id)} type="button">
                    <strong>{item.title}</strong>
                    <small>{historyMeta(item)}</small>
                  </button>
                  <div className="history-actions">
                    <button className="danger" disabled={deletingConversationId === item.id} onClick={() => requestRemoveConversation(item)} type="button">
                      {deletingConversationId === item.id ? "删除中" : "删除"}
                    </button>
                  </div>
                </article>
              ))}
            </div>
            {hiddenHistoryCount ? (
              <button className="history-expand" onClick={() => setHistoryExpanded((expanded) => !expanded)} type="button">
                {historyExpanded ? "收起会话" : `展开其余 ${hiddenHistoryCount} 条`}
              </button>
            ) : null}
          </section>
        </aside>
      </section>

      {deleteDialog ? (
        <DeleteConfirmDialog
          busy={Boolean(deletingConversationId) || clearingConversations}
          confirmLabel={deleteDialog.kind === "all" ? "清空" : "删除"}
          description={
            deleteDialog.kind === "all"
              ? "这会清空当前管理员账号在此页面保存的所有聊天记录。"
              : "删除后，这段测试聊天和其中的消息会从最近会话中移除。"
          }
          onCancel={() => setDeleteDialog(null)}
          onConfirm={confirmDeleteDialog}
          subject={deleteDialog.kind === "all" ? `全部 ${deleteDialog.count} 条聊天记录` : deleteDialog.title}
          title={deleteDialog.kind === "all" ? "清空聊天记录？" : "删除聊天？"}
        />
      ) : null}

      {selectedSource ? (
        <div className="feedback-dialog-backdrop" role="presentation">
          <section aria-labelledby="source-dialog-title" aria-modal="true" className="source-dialog" role="dialog">
            <div className="feedback-dialog-heading">
              <p className="eyebrow">引用来源</p>
              <h2 id="source-dialog-title">{selectedSource.title}</h2>
            </div>
            <dl className="source-detail-list">
              <div>
                <dt>命中分数</dt>
                <dd>{selectedSource.score.toFixed(4)}</dd>
              </div>
              <div>
                <dt>来源类型</dt>
                <dd>{sourceTypeLabel(selectedSource.source_type)}</dd>
              </div>
              <div>
                <dt>文档 ID</dt>
                <dd>{selectedSource.doc_id}</dd>
              </div>
              <div>
                <dt>片段 ID</dt>
                <dd>{selectedSource.chunk_id}</dd>
              </div>
              {selectedSource.section_path ? (
                <div>
                  <dt>章节</dt>
                  <dd>{selectedSource.section_path}</dd>
                </div>
              ) : null}
            </dl>
            <div className="source-excerpt">
              <span>命中片段</span>
              <p>{selectedSource.excerpt || "这条历史引用没有保存片段摘要。"}</p>
            </div>
            <button aria-label="关闭引用来源弹窗" className="dialog-close" onClick={() => setSelectedSource(null)} type="button">
              ×
            </button>
          </section>
        </div>
      ) : null}
    </>
  );
}

function historyMeta(item: ConversationSummary): string {
  const messageText = `${item.message_count} 条消息`;
  if (item.product_line) return `${item.product_line} · ${messageText}`;
  return messageText;
}

function createTempMessage(id: string, role: "user" | "assistant", content: string): ConversationMessage {
  return {
    id,
    role,
    content,
    solution_steps: [],
    sources: [],
    confidence: "low",
    created_at: new Date().toISOString(),
  };
}

function confidenceLabel(confidence: ChatResponse["confidence"]): string {
  if (confidence === "high") return "高";
  if (confidence === "medium") return "中";
  return "低";
}

function sourceTypeLabel(sourceType: SourceCitation["source_type"]): string {
  if (sourceType === "manual") return "手动知识";
  if (sourceType === "upload") return "上传文档";
  if (sourceType === "ticket") return "工单沉淀";
  return "外部来源";
}
