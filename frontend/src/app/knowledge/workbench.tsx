"use client";

import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react";
import { createManualKnowledge, importMarkdownKnowledge, listKnowledgeSources, reindexKnowledgeSource } from "@/lib/api";
import type { KnowledgeSource } from "@/lib/types";

export function KnowledgeWorkbench({ token }: { token: string }) {
  const [sources, setSources] = useState<KnowledgeSource[]>([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [visibility, setVisibility] = useState<"internal" | "private">("internal");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const totalChunks = useMemo(() => sources.reduce((sum, source) => sum + source.chunk_count, 0), [sources]);

  async function refresh() {
    setSources(await listKnowledgeSources(token));
  }

  useEffect(() => {
    refresh().catch(() => setError("知识库列表加载失败"));
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const source = await createManualKnowledge({ title: title.trim(), content: content.trim(), visibility }, token);
      setSources((current) => [source, ...current]);
      setTitle("");
      setContent("");
      setNotice("已入库，聊天会优先检索这条知识。");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "入库失败，请稍后重试");
    } finally {
      setBusy(false);
    }
  }

  async function importMarkdown(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    event.target.value = "";
    if (!file || busy) return;
    if (!file.name.toLowerCase().match(/\.(md|markdown)$/)) {
      setError("请选择 .md 或 .markdown 文件");
      return;
    }
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const text = await file.text();
      const fallbackTitle = file.name.replace(/\.(md|markdown)$/i, "");
      const firstHeading = text.match(/^#\s+(.+)$/m)?.[1]?.trim();
      const source = await importMarkdownKnowledge(
        {
          title: firstHeading || fallbackTitle,
          content: text,
          filename: file.name,
          visibility,
        },
        token,
      );
      setSources((current) => [source, ...current]);
      setNotice(`已导入 ${file.name}，生成 ${source.chunk_count} 个知识片段。`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Markdown 导入失败");
    } finally {
      setBusy(false);
    }
  }

  async function reindexSource(source: KnowledgeSource) {
    if (busy) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const updated = await reindexKnowledgeSource(source.id, token);
      setSources((current) => current.map((item) => (item.id === updated.id ? updated : item)));
      setNotice(`已重新索引 ${updated.title}，当前 ${updated.chunk_count} 个知识片段。`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "重新索引失败");
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
          <a className="nav-item" href="/chat">
            <span>会话记录</span>
            <small>追溯</small>
          </a>
          <a className="nav-item active" href="/knowledge">
            <span>知识入库</span>
            <small>{sources.length} 条</small>
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

        <section className="sidebar-block" aria-labelledby="knowledge-status-title">
          <h2 id="knowledge-status-title">检索状态</h2>
          <ul>
            <li>
              <a href="/chat">{totalChunks} 个知识片段可用于聊天引用</a>
            </li>
            <li>
              <a href="/knowledge">手动录入即时生效</a>
            </li>
          </ul>
        </section>
      </aside>

      <main className="main knowledge-main">
        <header className="topbar">
          <div>
            <p className="eyebrow">知识入库</p>
            <h1>把可靠答案沉淀成可引用的售后知识</h1>
          </div>
          <span className="status-pill">RAG 已接入</span>
        </header>

        <section className="content knowledge-grid">
          <form className="ask-panel knowledge-editor" onSubmit={submit}>
            <div className="panel-heading">
              <div>
                <p className="eyebrow">手动知识</p>
                <h2>录入一条可被聊天检索的处理方案</h2>
              </div>
              <div className="knowledge-actions">
                <label className="secondary-button import-button">
                  导入 Markdown
                  <input accept=".md,.markdown,text/markdown,text/plain" onChange={importMarkdown} type="file" />
                </label>
                <span className="confidence-chip">{visibility === "internal" ? "内部可见" : "仅本人"}</span>
              </div>
            </div>

            <div className="knowledge-form">
              <label htmlFor="knowledge-title">标题</label>
              <input
                id="knowledge-title"
                minLength={2}
                maxLength={160}
                placeholder="例如：AX-42 配网后 App 显示离线"
                value={title}
                onChange={(event) => setTitle(event.target.value)}
                required
              />

              <label htmlFor="knowledge-content">处理方案</label>
              <textarea
                id="knowledge-content"
                minLength={10}
                maxLength={12000}
                placeholder="写清适用条件、排查步骤、判断标准和转人工条件。"
                value={content}
                onChange={(event) => setContent(event.target.value)}
                required
              />

              <div className="segmented-control" aria-label="可见范围">
                <button className={visibility === "internal" ? "active" : ""} onClick={() => setVisibility("internal")} type="button">
                  内部共享
                </button>
                <button className={visibility === "private" ? "active" : ""} onClick={() => setVisibility("private")} type="button">
                  仅本人
                </button>
              </div>

              {error ? <p className="form-error">{error}</p> : null}
              {notice ? <p className="form-notice">{notice}</p> : null}
              <button className="primary-button" disabled={busy} type="submit">
                {busy ? "入库中" : "保存并建立索引"}
              </button>
            </div>
          </form>

          <section className="source-panel knowledge-list" aria-label="知识来源">
            <div className="panel-heading compact">
              <div>
                <p className="eyebrow">已入库</p>
                <h2>{sources.length ? `${sources.length} 条知识源` : "还没有知识源"}</h2>
              </div>
              <span className="confidence-chip">{totalChunks} 片段</span>
            </div>
            <div className="source-list">
              {sources.length ? (
                sources.map((source) => (
                  <article className="source-item" key={source.id}>
                    <div>
                      <strong>{source.title}</strong>
                      <span>
                        {source.source_type} · {source.visibility === "internal" ? "内部共享" : "仅本人"} · {source.chunk_count} 片段
                      </span>
                    </div>
                    <button className="source-action" disabled={busy} onClick={() => reindexSource(source)} type="button">
                      重新索引
                    </button>
                  </article>
                ))
              ) : (
                <div className="empty-chat knowledge-empty">
                  <b>先录入一条真实售后处理方案。</b>
                  <p>保存后去会话里提相近问题，回答会返回来源引用。</p>
                </div>
              )}
            </div>
          </section>
        </section>
      </main>
    </div>
  );
}
