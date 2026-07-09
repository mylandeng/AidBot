"use client";

import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react";
import {
  createKnowledgeSpace,
  createManualKnowledge,
  deleteKnowledgeSource,
  deleteKnowledgeSpace,
  importKnowledgeDocument,
  listKnowledgeSources,
  listKnowledgeSpaces,
  reindexKnowledgeSource,
} from "@/lib/api";
import type { KnowledgeSource, KnowledgeSpace } from "@/lib/types";

export function KnowledgeWorkbench({ token }: { token: string }) {
  const [sources, setSources] = useState<KnowledgeSource[]>([]);
  const [spaces, setSpaces] = useState<KnowledgeSpace[]>([]);
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [spaceName, setSpaceName] = useState("");
  const [spaceDescription, setSpaceDescription] = useState("");
  const [selectedSpaceId, setSelectedSpaceId] = useState<string | null>(null);
  const [visibility, setVisibility] = useState<"internal" | "private">("internal");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const totalChunks = useMemo(() => sources.reduce((sum, source) => sum + source.chunk_count, 0), [sources]);

  async function refresh() {
    const [nextSources, nextSpaces] = await Promise.all([listKnowledgeSources(token), listKnowledgeSpaces(token)]);
    setSources(nextSources);
    setSpaces(nextSpaces);
    setSelectedSpaceId((current) => current ?? nextSpaces[0]?.id ?? null);
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
      const source = await createManualKnowledge({ title: title.trim(), content: content.trim(), visibility, space_id: selectedSpaceId }, token);
      setSources((current) => [source, ...current]);
      await refresh();
      setTitle("");
      setContent("");
      setNotice("已入库，聊天会优先检索这条知识。");
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "入库失败，请稍后重试");
    } finally {
      setBusy(false);
    }
  }

  async function addKnowledgeFiles(event: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? []);
    event.target.value = "";
    if (!files.length || busy) return;

    const unsupported = files.filter((file) => !detectContentFormat(file.name));
    if (unsupported.length) {
      setError(`暂不支持：${unsupported.map((file) => file.name).join("、")}`);
      return;
    }

    const pdfFiles = files.filter((file) => detectContentFormat(file.name) === "pdf");
    if (pdfFiles.length) {
      setError("PDF 解析器还未接入，当前可添加 Markdown、HTML 和纯文本文件。");
      return;
    }

    setBusy(true);
    setError("");
    setNotice("");
    try {
      const imported: KnowledgeSource[] = [];
      for (const file of files) {
        const text = await file.text();
        const contentFormat = detectContentFormat(file.name);
        if (!contentFormat || contentFormat === "pdf") continue;
        const fallbackTitle = file.name.replace(/\.(md|markdown|txt|html|htm)$/i, "");
        const firstHeading = text.match(/^#\s+(.+)$/m)?.[1]?.trim() ?? text.match(/<h1[^>]*>(.*?)<\/h1>/i)?.[1]?.replace(/<[^>]+>/g, "").trim();
        const source = await importKnowledgeDocument(
          {
            title: firstHeading || fallbackTitle,
            content: text,
            filename: file.name,
            content_format: contentFormat,
            visibility,
            space_id: selectedSpaceId,
          },
          token,
        );
        imported.push(source);
      }
      setSources((current) => [...imported, ...current]);
      await refresh();
      const chunkCount = imported.reduce((sum, source) => sum + source.chunk_count, 0);
      setNotice(`已添加 ${imported.length} 个文件，生成 ${chunkCount} 个知识片段。`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "添加知识失败");
    } finally {
      setBusy(false);
    }
  }

  async function createSpace(event: FormEvent) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      const space = await createKnowledgeSpace({ name: spaceName.trim(), description: spaceDescription.trim(), visibility }, token);
      setSpaces((current) => [space, ...current]);
      setSelectedSpaceId(space.id);
      setSpaceName("");
      setSpaceDescription("");
      setNotice(`已创建知识库：${space.name}`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "知识库创建失败");
    } finally {
      setBusy(false);
    }
  }

  async function removeSpace(space: KnowledgeSpace) {
    if (busy) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await deleteKnowledgeSpace(space.id, token);
      await refresh();
      setSelectedSpaceId((current) => (current === space.id ? null : current));
      setNotice(`已删除知识库：${space.name}`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "知识库删除失败");
    } finally {
      setBusy(false);
    }
  }

  async function removeSource(source: KnowledgeSource) {
    if (busy) return;
    setBusy(true);
    setError("");
    setNotice("");
    try {
      await deleteKnowledgeSource(source.id, token);
      setSources((current) => current.filter((item) => item.id !== source.id));
      await refresh();
      setNotice(`已删除知识源：${source.title}`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "知识源删除失败");
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
    <>
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
                  添加知识
                  <input accept=".md,.markdown,.txt,.html,.htm,.pdf,text/markdown,text/plain,text/html,application/pdf" multiple onChange={addKnowledgeFiles} type="file" />
                </label>
                <span className="confidence-chip">{visibility === "internal" ? "内部可见" : "仅本人"}</span>
              </div>
            </div>

            <div className="knowledge-form">
              <label htmlFor="knowledge-space">目标知识库</label>
              <select id="knowledge-space" value={selectedSpaceId ?? ""} onChange={(event) => setSelectedSpaceId(event.target.value || null)}>
                <option value="">默认知识空间</option>
                {spaces.map((space) => (
                  <option key={space.id} value={space.id}>
                    {space.name}
                  </option>
                ))}
              </select>

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
                        {source.space_name || "默认知识空间"} · {source.content_format} · {source.visibility === "internal" ? "内部共享" : "仅本人"} · {source.chunk_count} 片段
                      </span>
                    </div>
                    <div className="source-actions">
                      <button className="source-action" disabled={busy} onClick={() => reindexSource(source)} type="button">
                        重新索引
                      </button>
                      <button className="source-action danger" disabled={busy} onClick={() => removeSource(source)} type="button">
                        删除
                      </button>
                    </div>
                  </article>
                ))
              ) : (
                <div className="empty-chat knowledge-empty">
                  <b>先录入一条真实售后处理方案。</b>
                  <p>保存后去聊一聊提相近问题，回答会返回来源引用。</p>
                </div>
              )}
            </div>
          </section>

          <section className="source-panel knowledge-list" aria-label="知识空间">
            <div className="panel-heading compact">
              <div>
                <p className="eyebrow">知识空间</p>
                <h2>{spaces.length ? `${spaces.length} 个知识库` : "创建第一个知识库"}</h2>
              </div>
              <span className="confidence-chip">可删除</span>
            </div>
            <form className="knowledge-form compact" onSubmit={createSpace}>
              <label htmlFor="space-name">知识库名称</label>
              <input id="space-name" placeholder="例如：产品售后常见问题知识库" value={spaceName} onChange={(event) => setSpaceName(event.target.value)} required />
              <label htmlFor="space-description">说明</label>
              <textarea id="space-description" placeholder="写清这个知识库适合被哪些问题引用。" value={spaceDescription} onChange={(event) => setSpaceDescription(event.target.value)} />
              <button className="secondary-button" disabled={busy} type="submit">
                创建知识库
              </button>
            </form>
            <div className="source-list">
              {spaces.map((space) => (
                <article className="source-item" key={space.id}>
                  <div>
                    <strong>{space.name}</strong>
                    <span>
                      {space.description || "暂无说明"} · {space.source_count} 来源 · {space.chunk_count} 片段
                    </span>
                  </div>
                  <button className="source-action danger" disabled={busy} onClick={() => removeSpace(space)} type="button">
                    删除知识库
                  </button>
                </article>
              ))}
            </div>
          </section>
        </section>
    </>
  );
}

function detectContentFormat(filename: string): "text" | "markdown" | "html" | "pdf" | null {
  const lower = filename.toLowerCase();
  if (lower.endsWith(".md") || lower.endsWith(".markdown")) return "markdown";
  if (lower.endsWith(".html") || lower.endsWith(".htm")) return "html";
  if (lower.endsWith(".txt")) return "text";
  if (lower.endsWith(".pdf")) return "pdf";
  return null;
}
