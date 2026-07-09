"use client";

import { FormEvent, useEffect, useRef, useState } from "react";

import { askAdminQuestionStream, getConversation, listConversations } from "@/lib/api";
import type { ChatResponse, ConversationMessage, ConversationSummary } from "@/lib/types";

const examples = [
  "AX-42 配网后 App 仍显示离线，应该如何排查？",
  "客户反馈固件升级失败，后台应该先看哪些证据？",
  "哪些情况应该建议转人工处理？",
];

export function AdminChatWorkbench({ token }: { token: string }) {
  const [items, setItems] = useState<ConversationSummary[]>([]);
  const [messages, setMessages] = useState<ConversationMessage[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<ChatResponse | null>(null);
  const [question, setQuestion] = useState("");
  const [error, setError] = useState("");
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
    setLastResult(null);
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
      });
      setConversationId(result.conversation_id);
      await Promise.all([openConversation(result.conversation_id), refreshList()]);
      setLastResult(result);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "提问失败");
      setMessages((current) => current.filter((message) => message.id !== assistantTempId));
    } finally {
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
            setError("");
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
                  <span>{message.role === "user" ? "测试问题" : "AidBot 回复"}</span>
                  <p>{message.content}</p>
                  {message.role === "assistant" && message.sources?.length ? (
                    <div className="admin-source-list">
                      {message.sources.map((source) => (
                        <small key={`${message.id}-${source.chunk_id}`}>
                          {source.title} · {source.score.toFixed(2)}
                        </small>
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
            <textarea
              aria-label="测试问题"
              placeholder="输入要验证的售后问题"
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
              {busy ? "生成中" : "发送测试"}
            </button>
          </form>
        </section>

        <aside className="side-stack" aria-label="会话与调试信息">
          <section className="source-panel">
            <div className="panel-heading compact">
              <div>
                <p className="eyebrow">最近会话</p>
                <h2>{items.length ? `${items.length} 条记录` : "暂无记录"}</h2>
              </div>
            </div>
            <div className="chat-history-list">
              {items.map((item) => (
                <article className={`history-item ${item.id === conversationId ? "active" : ""}`} key={item.id}>
                  <button className="history-open" onClick={() => openConversation(item.id)} type="button">
                    <strong>{item.title}</strong>
                    <small>{item.message_count} 条消息</small>
                  </button>
                </article>
              ))}
            </div>
          </section>

          <section className="source-panel">
            <div className="panel-heading compact">
              <div>
                <p className="eyebrow">引用调试</p>
                <h2>{lastResult?.sources.length ? `${lastResult.sources.length} 个来源` : "等待回答"}</h2>
              </div>
            </div>
            <div className="source-list">
              {lastResult?.sources.length ? (
                lastResult.sources.map((source) => (
                  <article className="source-item" key={source.chunk_id}>
                    <div>
                      <strong>{source.title}</strong>
                      <span>
                        {source.source_type} · {source.doc_id}
                      </span>
                    </div>
                    <em>{source.score.toFixed(2)}</em>
                  </article>
                ))
              ) : (
                <p className="feedback-empty">发送测试问题后显示命中的知识片段。</p>
              )}
            </div>
          </section>
        </aside>
      </section>
    </>
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

function confidenceLabel(confidence: ChatResponse["confidence"]): string {
  if (confidence === "high") return "高";
  if (confidence === "medium") return "中";
  return "低";
}
