"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";

import { MessageContent } from "@/components/chat/message-content";
import { ComposerSendButton } from "@/components/ui/composer-send-button";
import { DeleteConfirmDialog } from "@/components/ui/delete-confirm-dialog";
import { askAdminQuestionStream, clearConversations, deleteConversation, getConversation, listConversations, listKnowledgeSpaces } from "@/lib/api";
import { createClientId } from "@/lib/client-id";
import type { ChatResponse, ConversationMessage, ConversationSummary, KnowledgeSpace, SourceCitation } from "@/lib/types";

const examples = [
  "AX-42 配网后 App 仍显示离线，应该如何排查？",
  "客户反馈固件升级失败，后台应该先看哪些证据？",
  "哪些情况应该建议转人工处理？",
];
const maxVisibleMessages = 80;
const streamTimeoutMs = 90_000;

type DeleteDialogState =
  | { id: string; kind: "single"; title: string }
  | { count: number; kind: "all" }
  | null;

export function AdminChatWorkbench({ token }: { token: string }) {
  const [items, setItems] = useState<ConversationSummary[]>([]);
  const [spaces, setSpaces] = useState<KnowledgeSpace[]>([]);
  const [selectedSpaceId, setSelectedSpaceId] = useState("");
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
  const [showAllMessages, setShowAllMessages] = useState(false);
  const [busy, setBusy] = useState(false);
  const streamEndRef = useRef<HTMLDivElement | null>(null);
  const questionInputRef = useRef<HTMLTextAreaElement | null>(null);
  const abortRef = useRef<AbortController | null>(null);
  const deltaBufferRef = useRef("");
  const deltaFrameRef = useRef<number | null>(null);
  const lastMessageContent = messages.at(-1)?.content ?? "";
  const visibleMessages = useMemo(() => (showAllMessages ? messages : messages.slice(-maxVisibleMessages)), [messages, showAllMessages]);
  const hiddenMessageCount = Math.max(messages.length - visibleMessages.length, 0);

  async function refreshList() {
    setItems(await listConversations(token));
  }

  useEffect(() => {
    Promise.all([refreshList(), listKnowledgeSpaces(token).then(setSpaces)]).catch(() => setError("会话或知识库列表加载失败"));
  }, []);

  useEffect(() => {
    return () => {
      abortRef.current?.abort();
      if (deltaFrameRef.current !== null) {
        window.cancelAnimationFrame(deltaFrameRef.current);
      }
    };
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
    abortRef.current?.abort();
    const [detail, nextSpaces] = await Promise.all([getConversation(id, token), listKnowledgeSpaces(token)]);
    setSpaces(nextSpaces);
    setSelectedSpaceId(nextSpaces.find((space) => space.product_line === detail.product_line)?.id ?? "");
    setConversationId(id);
    setMessages(detail.messages);
    setShowAllMessages(false);
    setLastResult(null);
    setQuestion("");
    setError("");
    setCopiedId("");
    setSelectedSource(null);
    setBusy(false);
  }

  function flushAssistantDelta(messageId: string) {
    if (!deltaBufferRef.current) return;
    const delta = deltaBufferRef.current;
    deltaBufferRef.current = "";
    setMessages((current) =>
      current.map((message) => (message.id === messageId ? { ...message, content: `${message.content}${delta}` } : message)),
    );
  }

  function scheduleAssistantDelta(messageId: string, delta: string) {
    deltaBufferRef.current += delta;
    if (deltaFrameRef.current !== null) return;
    deltaFrameRef.current = window.requestAnimationFrame(() => {
      deltaFrameRef.current = null;
      flushAssistantDelta(messageId);
    });
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
        setShowAllMessages(false);
        setLastResult(null);
        setQuestion("");
        setSelectedSpaceId("");
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
      setShowAllMessages(false);
      setLastResult(null);
      setQuestion("");
      setSelectedSpaceId("");
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
    if (!selectedSpaceId) {
      setError("请先选择要调试的产品知识库");
      return;
    }

    const text = question.trim();
    const userTempId = createClientId("user");
    const assistantTempId = createClientId("assistant");
    abortRef.current?.abort();
    const controller = new AbortController();
    abortRef.current = controller;
    let timedOut = false;
    const timeoutId = window.setTimeout(() => {
      timedOut = true;
      controller.abort();
    }, streamTimeoutMs);
    setBusy(true);
    setError("");
    setQuestion("");
    setLastResult(null);
    setMessages((current) => [
      ...current,
      createTempMessage(userTempId, "user", text),
      createTempMessage(assistantTempId, "assistant", ""),
    ]);
    setShowAllMessages(false);

    try {
      const result = await askAdminQuestionStream({ question: text, conversation_id: conversationId, space_id: selectedSpaceId }, token, (streamEvent) => {
        if (streamEvent.event === "message_start") {
          setConversationId(streamEvent.data.conversation_id);
          return;
        }
        if (streamEvent.event === "answer_delta") {
          scheduleAssistantDelta(assistantTempId, streamEvent.data.delta);
          return;
        }
        if (streamEvent.event === "final") {
          flushAssistantDelta(assistantTempId);
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
      if (reason instanceof DOMException && reason.name === "AbortError") {
        setMessages((current) => current.filter((message) => message.id !== assistantTempId || message.content.trim()));
        if (timedOut) {
          setError("回答生成超时，已自动停止。请稍后重试。");
        }
        return;
      }
      setError(reason instanceof Error ? reason.message : "提问失败");
      setMessages((current) => current.filter((message) => message.id !== assistantTempId));
    } finally {
      window.clearTimeout(timeoutId);
      flushAssistantDelta(assistantTempId);
      if (abortRef.current === controller) abortRef.current = null;
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
            setShowAllMessages(false);
            setLastResult(null);
            setQuestion("");
            setError("");
            setSelectedSource(null);
            setSelectedSpaceId("");
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
              <>
                {hiddenMessageCount ? (
                  <button className="message-window-toggle" onClick={() => setShowAllMessages(true)} type="button">
                    仅显示最近 {visibleMessages.length} 条消息，点击查看全部 {messages.length} 条
                  </button>
                ) : null}
                {showAllMessages && messages.length > maxVisibleMessages ? (
                  <button className="message-window-toggle" onClick={() => setShowAllMessages(false)} type="button">
                    正在显示全部 {messages.length} 条消息，点击回到最近 {maxVisibleMessages} 条
                  </button>
                ) : null}
                {visibleMessages.map((message) => (
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
                          {source.space_name ? `${source.space_name} · ` : ""}{source.title} · {source.score.toFixed(2)}
                        </button>
                      ))}
                    </div>
                  ) : null}
                </article>
              ))}
              </>
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
            <label className="chat-space-selector">
              <span>产品知识库</span>
              <select
                disabled={(Boolean(conversationId) && Boolean(selectedSpaceId)) || busy}
                onChange={(event) => setSelectedSpaceId(event.target.value)}
                value={selectedSpaceId}
              >
                <option value="">选择知识库</option>
                {spaces.map((space) => (
                  <option disabled={!space.product_line} key={space.id} value={space.id}>
                    {space.product_line ? `${space.product_line} / ${space.name}` : `${space.name}（未配置产品线）`}
                  </option>
                ))}
              </select>
            </label>
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
          <section className="source-panel history-panel">
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
            <div className="chat-history-list">
              {items.map((item) => (
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
                <dt>知识库</dt>
                <dd>{selectedSource.space_name || "未归属知识库"}</dd>
              </div>
              {selectedSource.space_id ? (
                <div>
                  <dt>知识库 ID</dt>
                  <dd>{selectedSource.space_id}</dd>
                </div>
              ) : null}
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
