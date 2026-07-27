"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { MessageContent } from "@/components/chat/message-content";
import { LogoutButton } from "@/components/layout/logout-button";
import { ComposerSendButton } from "@/components/ui/composer-send-button";
import { DeleteConfirmDialog } from "@/components/ui/delete-confirm-dialog";
import { askUserQuestionStream, clearConversations, createUserFeedback, deleteConversation, getConversation, listConversations } from "@/lib/api";
import { createClientId } from "@/lib/client-id";
import type { ConversationMessage, ConversationSummary, FeedbackRating } from "@/lib/types";

const examples = [
  "设备配网成功，但 App 一直显示离线怎么办？",
  "FP10 主控绿灯闪两下代表什么故障？",
  "固件升级失败后，应该先让客户检查哪些信息？",
];

const feedbackReasons = ["准确理解问题", "内容回复简洁明了", "我有其他想法"];
const starScores = [1, 2, 3, 4, 5];
const collapsedHistoryCount = 5;

interface PendingFeedback {
  messageId: string;
  score: number;
}

interface SubmittedFeedback {
  score: number;
}

type DeleteDialogState =
  | { id: string; kind: "single"; title: string }
  | { count: number; kind: "all" }
  | null;

function scoreToRating(score: number): FeedbackRating {
  if (score >= 4) return "useful";
  if (score === 3) return "needs_review";
  return "not_useful";
}

function toggleTag(tags: string[], tag: string): string[] {
  return tags.includes(tag) ? tags.filter((item) => item !== tag) : [...tags, tag];
}

export function ChatWorkbench({ token }: { token: string }) {
  const [items, setItems] = useState<ConversationSummary[]>([]);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [copiedId, setCopiedId] = useState("");
  const [deletingConversationId, setDeletingConversationId] = useState("");
  const [clearingConversations, setClearingConversations] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState<DeleteDialogState>(null);
  const [historyExpanded, setHistoryExpanded] = useState(false);
  const [feedbackByMessage, setFeedbackByMessage] = useState<Record<string, SubmittedFeedback>>({});
  const [pendingFeedback, setPendingFeedback] = useState<PendingFeedback | null>(null);
  const [feedbackTags, setFeedbackTags] = useState<string[]>([]);
  const [feedbackNote, setFeedbackNote] = useState("");
  const [submittingFeedback, setSubmittingFeedback] = useState(false);
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
    setQuestion("");
    setError("");
    setNotice("");
    setCopiedId("");
    setPendingFeedback(null);
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
    setNotice("");
    try {
      await deleteConversation(id, token);
      setItems((current) => current.filter((item) => item.id !== id));
      if (id === conversationId) {
        setConversationId(null);
        setMessages([]);
        setQuestion("");
        setFeedbackByMessage({});
        setPendingFeedback(null);
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
    setNotice("");
    try {
      const result = await clearConversations(token);
      setItems([]);
      setConversationId(null);
      setMessages([]);
      setQuestion("");
      setFeedbackByMessage({});
      setPendingFeedback(null);
      setBusy(false);
      setNotice(result.deleted_count ? `已清空 ${result.deleted_count} 条聊天记录。` : "没有可清空的聊天记录。");
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
    setNotice("");
    setQuestion("");
    setMessages((current) => [
      ...current,
      createTempMessage(userTempId, "user", text),
      createTempMessage(assistantTempId, "assistant", ""),
    ]);

    try {
      const result = await askUserQuestionStream({ question: text, conversation_id: conversationId }, token, (streamEvent) => {
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
          setConversationId(streamEvent.data.conversation_id);
          setMessages((current) => current.map((message) => (message.id === assistantTempId ? { ...message, id: streamEvent.data.message_id } : message)));
        }
      }, controller.signal);
      setConversationId(result.conversation_id);
      await Promise.all([openConversation(result.conversation_id), refreshList()]);
    } catch (reason) {
      if (reason instanceof DOMException && reason.name === "AbortError") return;
      setError(reason instanceof Error ? reason.message : "提问失败");
      setMessages((current) => current.filter((message) => message.id !== assistantTempId));
    } finally {
      abortRef.current = null;
      setBusy(false);
    }
  }

  function openFeedback(messageId: string, score: number) {
    if (messageId.startsWith("assistant-") || submittingFeedback) return;
    setPendingFeedback({ messageId, score });
    setFeedbackTags([]);
    setFeedbackNote("");
    setError("");
    setNotice("");
  }

  function closeFeedback() {
    if (submittingFeedback) return;
    setPendingFeedback(null);
    setFeedbackTags([]);
    setFeedbackNote("");
  }

  async function submitFeedback(includeDetail: boolean) {
    if (!pendingFeedback || submittingFeedback) return;
    const { messageId, score } = pendingFeedback;
    const rating = scoreToRating(score);
    const tags = includeDetail ? [`${score}星`, ...feedbackTags] : [`${score}星`];

    setSubmittingFeedback(true);
    setError("");
    setNotice("");
    try {
      await createUserFeedback(
        {
          message_id: messageId,
          rating,
          tags,
          note: includeDetail ? feedbackNote.trim() : "",
        },
        token,
      );
      setFeedbackByMessage((current) => ({ ...current, [messageId]: { score } }));
      setNotice(`${score} 星反馈已提交，感谢补充。`);
      setPendingFeedback(null);
      setFeedbackTags([]);
      setFeedbackNote("");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "反馈提交失败");
    } finally {
      setSubmittingFeedback(false);
    }
  }

  return (
    <div className="app-shell user-chat-shell">
      <aside className="sidebar">
        <a className="brand-lockup" href="/user/chat" aria-label="AidBot 聊天">
          <span className="brand-mark">A</span>
          <span>
            <strong>AidBot</strong>
            <small>售后问答助手</small>
          </span>
        </a>

        <nav className="nav-list" aria-label="用户导航">
          <a className="nav-item active" href="/user/chat">
            <span>智能问答</span>
            <small>聊天</small>
          </a>
        </nav>

        <section className={historyExpanded ? "sidebar-block history-block expanded" : "sidebar-block history-block"} aria-labelledby="chat-history-title">
          <div className="history-heading">
            <h2 id="chat-history-title">最近会话</h2>
            {items.length ? (
              <button className="history-clear" disabled={clearingConversations} onClick={requestRemoveAllConversations} type="button">
                {clearingConversations ? "清空中" : "清空全部"}
              </button>
            ) : null}
          </div>
          <div className={historyExpanded ? "chat-history-list expanded" : "chat-history-list"}>
            {items.length ? (
              visibleHistoryItems.map((item) => (
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
              ))
            ) : (
              <p className="sidebar-empty">暂无会话</p>
            )}
          </div>
          {hiddenHistoryCount ? (
            <button className="history-expand" onClick={() => setHistoryExpanded((expanded) => !expanded)} type="button">
              {historyExpanded ? "收起会话" : `展开其余 ${hiddenHistoryCount} 条`}
            </button>
          ) : null}
        </section>

        <div className="sidebar-footer">
          <LogoutButton />
        </div>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">售后智能助手</p>
            <h1>描述产品型号、故障现象和已经尝试过的操作。</h1>
          </div>
          <button
            className="secondary-button"
            onClick={() => {
              setConversationId(null);
              setMessages([]);
              setQuestion("");
              setError("");
              setNotice("");
              setPendingFeedback(null);
              setBusy(false);
            }}
            type="button"
          >
            新会话
          </button>
        </header>

        <section className="content chat-content">
          <section className="ask-panel chat-panel" aria-label="聊天消息">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">当前问答</p>
                <h2>{messages.length ? "继续这个问题" : "可以这样提问"}</h2>
              </div>
            </div>

            <section className="message-stream">
              {messages.length ? (
                messages.map((message) => {
                  const submitted = feedbackByMessage[message.id];
                  const activeScore = pendingFeedback?.messageId === message.id ? pendingFeedback.score : submitted?.score ?? 0;
                  return (
                    <article className={`message ${message.role}`} key={message.id}>
                      <div className="message-header">
                        <span>{message.role === "user" ? "你的问题" : "AidBot 回复"}</span>
                        <button className="copy-button" onClick={() => copyText(message.id, message.content)} type="button">
                          {copiedId === message.id ? "已复制" : "复制"}
                        </button>
                      </div>
                      <MessageContent content={message.content} markdown={message.role === "assistant"} />
                      {message.role === "assistant" && !message.id.startsWith("assistant-") ? (
                        <div className="message-feedback" aria-label="回答反馈">
                          <div className="star-rating" role="group" aria-label="五星彩评">
                            {starScores.map((score) => (
                              <button
                                aria-label={`${score} 星`}
                                className={score <= activeScore ? "active" : ""}
                                disabled={submittingFeedback}
                                key={score}
                                onClick={() => openFeedback(message.id, score)}
                                title={`${score} 星`}
                                type="button"
                              >
                                <StarIcon filled={score <= activeScore} />
                              </button>
                            ))}
                          </div>
                          <small className={submitted ? "feedback-status submitted" : "feedback-status"}>
                            {submitted ? `已提交 ${submitted.score} 星` : "点击星星评分"}
                          </small>
                        </div>
                      ) : null}
                    </article>
                  );
                })
              ) : (
                <div className="empty-chat">
                  <b>把现象说具体一点，回答会更准确。</b>
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
                  aria-label="售后问题"
                  placeholder="输入产品型号、故障现象、已尝试步骤"
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
              {notice ? <p className="form-notice">{notice}</p> : null}
            </form>
          </section>
        </section>
      </main>

      {deleteDialog ? (
        <DeleteConfirmDialog
          busy={Boolean(deletingConversationId) || clearingConversations}
          confirmLabel={deleteDialog.kind === "all" ? "清空" : "删除"}
          description={
            deleteDialog.kind === "all"
              ? "这会清空当前账号在此页面保存的所有聊天记录。"
              : "删除后，这段聊天和其中的消息会从最近会话中移除。"
          }
          onCancel={() => setDeleteDialog(null)}
          onConfirm={confirmDeleteDialog}
          subject={deleteDialog.kind === "all" ? `全部 ${deleteDialog.count} 条聊天记录` : deleteDialog.title}
          title={deleteDialog.kind === "all" ? "清空聊天记录？" : "删除聊天？"}
        />
      ) : null}

      {pendingFeedback ? (
        <div className="feedback-dialog-backdrop" role="presentation">
          <section
            aria-describedby="feedback-dialog-description"
            aria-labelledby="feedback-dialog-title"
            aria-modal="true"
            className="feedback-dialog"
            role="dialog"
          >
            <div className="feedback-dialog-heading">
              <div>
                <p className="eyebrow">{pendingFeedback.score} 星</p>
                <h2 id="feedback-dialog-title">这次回答怎么样？</h2>
                <p id="feedback-dialog-description">可以补充原因，也可以直接忽略留言。</p>
              </div>
            </div>

            <div className="feedback-reasons" aria-label="反馈原因">
              {feedbackReasons.map((reason) => (
                <button
                  className={feedbackTags.includes(reason) ? "active" : ""}
                  key={reason}
                  onClick={() => setFeedbackTags((current) => toggleTag(current, reason))}
                  type="button"
                >
                  {reason}
                </button>
              ))}
            </div>

            <label className="feedback-note" htmlFor="feedback-note">
              <span>留言</span>
              <textarea
                id="feedback-note"
                onChange={(event) => setFeedbackNote(event.target.value)}
                placeholder="您的建议，将促使本系统持续进步"
                value={feedbackNote}
              />
            </label>

            <div className="feedback-dialog-actions">
              <button className="secondary-button" disabled={submittingFeedback} onClick={() => submitFeedback(false)} type="button">
                {submittingFeedback ? "提交中" : "忽略"}
              </button>
              <button className="primary-button" disabled={submittingFeedback} onClick={() => submitFeedback(true)} type="button">
                {submittingFeedback ? "提交中" : "提交"}
              </button>
            </div>
            <button aria-label="关闭反馈弹窗" className="dialog-close" disabled={submittingFeedback} onClick={closeFeedback} type="button">
              ×
            </button>
          </section>
        </div>
      ) : null}
    </div>
  );
}

function historyMeta(item: ConversationSummary): string {
  const messageText = `${item.message_count} 条消息`;
  if (item.product_line) return `${item.product_line} · ${messageText}`;
  return messageText;
}

function StarIcon({ filled }: { filled: boolean }) {
  return (
    <svg aria-hidden="true" className={filled ? "star-icon filled" : "star-icon"} focusable="false" viewBox="0 0 24 24">
      <path d="M12 3.15l2.58 5.22 5.76.84-4.17 4.06.98 5.73L12 16.3 6.85 19l.98-5.73-4.17-4.06 5.76-.84L12 3.15z" />
    </svg>
  );
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
