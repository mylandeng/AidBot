"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { LogoutButton } from "@/components/layout/logout-button";
import { askUserQuestionStream, createUserFeedback, getConversation, listConversations } from "@/lib/api";
import type { ConversationMessage, ConversationSummary } from "@/lib/types";

const examples = [
  "设备配网成功，但 App 一直显示离线怎么办？",
  "FP10 主控绿灯闪两下代表什么故障？",
  "固件升级失败后，应该先让客户检查哪些信息？",
];

export function ChatWorkbench({ token }: { token: string }) {
  const [items, setItems] = useState<ConversationSummary[]>([]);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [question, setQuestion] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);
  const streamEndRef = useRef<HTMLDivElement | null>(null);
  const lastMessageContent = messages.at(-1)?.content ?? "";

  async function refreshList() {
    setItems(await listConversations(token));
  }

  useEffect(() => {
    refreshList().catch(() => setError("会话列表加载失败"));
  }, []);

  useEffect(() => {
    streamEndRef.current?.scrollIntoView({ behavior: busy ? "auto" : "smooth", block: "end" });
  }, [busy, messages.length, lastMessageContent]);

  async function openConversation(id: string) {
    const detail = await getConversation(id, token);
    setConversationId(id);
    setMessages(detail.messages);
    setError("");
    setNotice("");
  }

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!question.trim() || busy) return;

    const text = question.trim();
    const userTempId = `user-${crypto.randomUUID()}`;
    const assistantTempId = `assistant-${crypto.randomUUID()}`;
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

  async function sendFeedback(messageId: string, rating: "useful" | "not_useful" | "needs_human") {
    setNotice("");
    setError("");
    try {
      await createUserFeedback({ message_id: messageId, rating, note: "" }, token);
      setNotice("反馈已提交，感谢补充。");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "反馈提交失败");
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

        <section className="sidebar-block" aria-labelledby="chat-history-title">
          <h2 id="chat-history-title">最近会话</h2>
          <div className="chat-history-list">
            {items.length ? (
              items.map((item) => (
                <article className={`history-item ${item.id === conversationId ? "active" : ""}`} key={item.id}>
                  <button className="history-open" onClick={() => openConversation(item.id)} type="button">
                    <strong>{item.title}</strong>
                    <small>{item.message_count} 条消息</small>
                  </button>
                </article>
              ))
            ) : (
              <p className="sidebar-empty">暂无会话</p>
            )}
          </div>
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
              setError("");
              setNotice("");
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
                messages.map((message) => (
                  <article className={`message ${message.role}`} key={message.id}>
                    <span>{message.role === "user" ? "你的问题" : "AidBot 回复"}</span>
                    <p>{message.content}</p>
                    {message.role === "assistant" && !message.id.startsWith("assistant-") ? (
                      <div className="message-feedback" aria-label="回答反馈">
                        <button onClick={() => sendFeedback(message.id, "useful")} type="button">
                          有帮助
                        </button>
                        <button onClick={() => sendFeedback(message.id, "not_useful")} type="button">
                          没帮助
                        </button>
                        <button onClick={() => sendFeedback(message.id, "needs_human")} type="button">
                          需要人工跟进
                        </button>
                      </div>
                    ) : null}
                  </article>
                ))
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
              <textarea
                aria-label="售后问题"
                placeholder="输入产品型号、故障现象、已尝试步骤"
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
              {notice ? <p className="form-notice">{notice}</p> : null}
              <button className="primary-button" disabled={busy} type="submit">
                {busy ? "生成中" : "发送"}
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
