"use client";

import { FormEvent, useEffect, useMemo, useRef, useState } from "react";
import { archiveConversation, askQuestionStream, deleteConversation, getConversation, listConversations, restoreConversation } from "@/lib/api";
import type { ConversationMessage, ConversationSummary } from "@/lib/types";

export function ChatWorkbench({ token }: { token: string }) {
  const [items, setItems] = useState<ConversationSummary[]>([]);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [historyQuery, setHistoryQuery] = useState("");
  const [includeArchived, setIncludeArchived] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);
  const [historyBusyId, setHistoryBusyId] = useState<string | null>(null);
  const streamEndRef = useRef<HTMLDivElement | null>(null);
  const lastMessageContent = messages.at(-1)?.content ?? "";
  const messageCount = messages.length;
  const sourceCount = useMemo(
    () => messages.filter((message) => message.role === "assistant").reduce((count, message) => count + message.sources.length, 0),
    [messages],
  );

  async function refreshList() {
    setItems(await listConversations(token, { q: historyQuery, includeArchived }));
  }

  useEffect(() => {
    refreshList().catch(() => setError("会话列表加载失败"));
  }, []);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      refreshList().catch(() => setError("会话列表加载失败"));
    }, 250);
    return () => window.clearTimeout(timer);
  }, [historyQuery, includeArchived]);

  useEffect(() => {
    streamEndRef.current?.scrollIntoView({ behavior: busy ? "auto" : "smooth", block: "end" });
  }, [busy, messageCount, lastMessageContent]);

  async function openConversation(id: string) {
    const detail = await getConversation(id, token);
    setConversationId(id);
    setMessages(detail.messages);
    setError("");
  }

  async function updateConversationStatus(item: ConversationSummary) {
    if (historyBusyId) return;
    setHistoryBusyId(item.id);
    setError("");
    try {
      const nextItem = item.status === "archived" ? await restoreConversation(item.id, token) : await archiveConversation(item.id, token);
      if (nextItem.status === "archived" && item.id === conversationId) {
        setConversationId(null);
        setMessages([]);
      }
      await refreshList();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "会话状态更新失败");
    } finally {
      setHistoryBusyId(null);
    }
  }

  async function removeConversation(item: ConversationSummary) {
    if (historyBusyId || !window.confirm(`删除会话“${item.title}”？此操作会同时删除消息记录。`)) return;
    setHistoryBusyId(item.id);
    setError("");
    try {
      await deleteConversation(item.id, token);
      if (item.id === conversationId) {
        setConversationId(null);
        setMessages([]);
      }
      await refreshList();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "会话删除失败");
    } finally {
      setHistoryBusyId(null);
    }
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!question.trim() || busy) return;

    const text = question.trim();
    const userTempId = `user-${crypto.randomUUID()}`;
    const assistantTempId = `assistant-${crypto.randomUUID()}`;
    setBusy(true);
    setError("");
    setQuestion("");
    setMessages((current) => [
      ...current,
      createTempMessage(userTempId, "user", text),
      createTempMessage(assistantTempId, "assistant", ""),
    ]);

    try {
      const result = await askQuestionStream({ question: text, conversation_id: conversationId }, token, (streamEvent) => {
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
        }
      });
      setConversationId(result.conversation_id);
      await Promise.all([openConversation(result.conversation_id), refreshList()]);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "提问失败");
      setMessages((current) => current.filter((message) => message.id !== assistantTempId));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand-lockup" href="/" aria-label="AidBot 首页">
          <span className="brand-mark">A</span>
          <span>
            <strong>AidBot</strong>
            <small>售后知识中枢</small>
          </span>
        </a>

        <nav className="nav-list" aria-label="主导航">
          <a className="nav-item" href="/">
            <span>问答分诊</span>
            <small>首页</small>
          </a>
          <a className="nav-item active" href="/chat">
            <span>会话记录</span>
            <small>{items.length} 条</small>
          </a>
          <a className="nav-item" href="/knowledge">
            <span>知识入库</span>
            <small>待接入</small>
          </a>
          <a className="nav-item" href="/feedback">
            <span>反馈复盘</span>
            <small>待处理</small>
          </a>
          <a className="nav-item" href="/admin">
            <span>系统设置</span>
            <small>内部</small>
          </a>
        </nav>

        <section className="sidebar-block" aria-labelledby="chat-history-title">
          <h2 id="chat-history-title">最近会话</h2>
          <div className="history-search">
            <input
              aria-label="搜索会话记录"
              placeholder="搜索主题或消息关键字"
              value={historyQuery}
              onChange={(event) => setHistoryQuery(event.target.value)}
            />
            <button className={includeArchived ? "active" : ""} onClick={() => setIncludeArchived((value) => !value)} type="button">
              归档
            </button>
          </div>
          <div className="chat-history-list">
            {items.length ? (
              items.map((item) => (
                <article className={`history-item ${item.id === conversationId ? "active" : ""} ${item.status === "archived" ? "archived" : ""}`} key={item.id}>
                  <button className="history-open" onClick={() => openConversation(item.id)} type="button">
                    <strong>{item.title}</strong>
                    <small>
                      {item.message_count} 条消息 · {item.status === "archived" ? "已归档" : "活跃"}
                    </small>
                  </button>
                  <div className="history-actions">
                    <button disabled={historyBusyId === item.id} onClick={() => updateConversationStatus(item)} type="button">
                      {item.status === "archived" ? "恢复" : "归档"}
                    </button>
                    <button className="danger" disabled={historyBusyId === item.id} onClick={() => removeConversation(item)} type="button">
                      删除
                    </button>
                  </div>
                </article>
              ))
            ) : (
              <p className="sidebar-empty">{historyQuery ? "没有匹配的会话" : "暂无会话"}</p>
            )}
          </div>
        </section>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">会话记录</p>
            <h1>{conversationId ? "继续排查这个售后问题" : "新建一次可追溯的售后问答"}</h1>
          </div>
          <button
            className="secondary-button"
            onClick={() => {
              setConversationId(null);
              setMessages([]);
              setError("");
            }}
            type="button"
          >
            新会话
          </button>
        </header>

        <section className="content chat-content">
          <section className="ask-panel chat-panel" aria-label="会话消息">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">当前问答</p>
                <h2>{messages.length ? "已保存的排查记录" : "从一个真实问题开始"}</h2>
              </div>
              <span className="confidence-chip">来源 {sourceCount} 条</span>
            </div>

            <section className="message-stream">
              {messages.length ? (
                messages.map((message) => (
                  <article className={`message ${message.role}`} key={message.id}>
                    <span>{message.role === "user" ? "客户问题" : "AidBot 建议"}</span>
                    <p>{message.content}</p>
                    {message.solution_steps.length ? (
                      <ol>
                        {message.solution_steps.map((step) => (
                          <li key={step}>{step}</li>
                        ))}
                      </ol>
                    ) : null}
                    {message.role === "assistant" ? (
                      <>
                        <small>
                          置信度：{message.confidence} · 来源 {message.sources.length} 条
                        </small>
                        {message.sources.length ? (
                          <div className="message-sources">
                            {message.sources.map((source) => (
                              <a href="/knowledge" key={source.chunk_id}>
                                <strong>{source.title}</strong>
                                <span>{relevanceLabel(source.score)}</span>
                              </a>
                            ))}
                          </div>
                        ) : null}
                      </>
                    ) : null}
                  </article>
                ))
              ) : (
                <div className="empty-chat">
                  <b>描述现象、型号和已经试过的动作。</b>
                  <p>例如：AX-42 完成配网后，App 仍显示离线，设备指示灯常亮。</p>
                </div>
              )}
              <div aria-hidden="true" ref={streamEndRef} />
            </section>

            <form className="chat-composer" onSubmit={submit}>
              <textarea
                aria-label="售后问题"
                placeholder="输入客户问题、产品型号、已尝试步骤"
                value={question}
                onChange={(event) => setQuestion(event.target.value)}
                onKeyDown={(event) => {
                  if (event.key === "Enter" && !event.shiftKey) {
                    event.preventDefault();
                    event.currentTarget.form?.requestSubmit();
                  }
                }}
              />
              {error ? <p className="form-error">{error}</p> : null}
              <button className="primary-button" disabled={busy} type="submit">
                {busy ? "生成中" : "发送问题"}
              </button>
            </form>
          </section>
        </section>
      </main>
    </div>
  );
}

function relevanceLabel(score: number): string {
  if (score >= 0.22) return "相关度高";
  if (score >= 0.12) return "相关度中";
  return "相关度低";
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
