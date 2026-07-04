"use client";

import { FormEvent, useEffect, useState } from "react";
import { askQuestionStream, getConversation, listConversations } from "@/lib/api";
import type { ConversationMessage, ConversationSummary } from "@/lib/types";

export function ChatWorkbench({ token }: { token: string }) {
  const [items, setItems] = useState<ConversationSummary[]>([]);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function refreshList() {
    setItems(await listConversations(token));
  }

  useEffect(() => {
    refreshList().catch(() => setError("会话列表加载失败"));
  }, []);

  async function openConversation(id: string) {
    const detail = await getConversation(id, token);
    setConversationId(id);
    setMessages(detail.messages);
    setError("");
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
          <div className="chat-history-list">
            {items.length ? (
              items.slice(0, 5).map((item) => (
                <button
                  className={item.id === conversationId ? "active" : ""}
                  key={item.id}
                  onClick={() => openConversation(item.id)}
                  type="button"
                >
                  <strong>{item.title}</strong>
                  <small>{item.message_count} 条消息</small>
                </button>
              ))
            ) : (
              <p className="sidebar-empty">暂无会话</p>
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
              <span className="confidence-chip">来源 {messages.filter((message) => message.role === "assistant").reduce((count, message) => count + message.sources.length, 0)} 条</span>
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
                      <small>
                        置信度：{message.confidence} · 来源 {message.sources.length} 条
                      </small>
                    ) : null}
                  </article>
                ))
              ) : (
                <div className="empty-chat">
                  <b>描述现象、型号和已经试过的动作。</b>
                  <p>例如：AX-42 完成配网后，App 仍显示离线，设备指示灯常亮。</p>
                </div>
              )}
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
