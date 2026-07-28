"use client";

import { ChangeEvent, FormEvent, useEffect, useMemo, useState } from "react";
import { DeleteConfirmDialog } from "@/components/ui/delete-confirm-dialog";
import {
  createKnowledgeSpace,
  createManualKnowledge,
  deleteKnowledgeSource,
  deleteKnowledgeSpace,
  importKnowledgeDocument,
  listKnowledgeSources,
  listKnowledgeSpaces,
  reindexKnowledgeSource,
  updateKnowledgeSpace,
} from "@/lib/api";
import type { KnowledgeSource, KnowledgeSpace } from "@/lib/types";

type Dialog = "create-space" | "edit-space" | "add-knowledge" | null;
type AddMode = "manual" | "document";

export function KnowledgeWorkbench({ token }: { token: string }) {
  const [spaces, setSpaces] = useState<KnowledgeSpace[]>([]);
  const [sources, setSources] = useState<KnowledgeSource[]>([]);
  const [selectedSpaceId, setSelectedSpaceId] = useState<string | null>(null);
  const [dialog, setDialog] = useState<Dialog>(null);
  const [pendingDeleteSpace, setPendingDeleteSpace] = useState<KnowledgeSpace | null>(null);
  const [pendingDeleteSource, setPendingDeleteSource] = useState<KnowledgeSource | null>(null);
  const [addMode, setAddMode] = useState<AddMode>("manual");
  const [spaceName, setSpaceName] = useState("");
  const [productLine, setProductLine] = useState("");
  const [spaceDescription, setSpaceDescription] = useState("");
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [visibility, setVisibility] = useState<"internal" | "private">("internal");
  const [busy, setBusy] = useState(false);
  const [reindexingSourceId, setReindexingSourceId] = useState("");
  const [error, setError] = useState("");

  const selectedSpace = useMemo(
    () => spaces.find((space) => space.id === selectedSpaceId) ?? null,
    [selectedSpaceId, spaces],
  );

  async function refreshSpaces() {
    setSpaces(await listKnowledgeSpaces(token));
  }

  async function openSpace(space: KnowledgeSpace) {
    setSelectedSpaceId(space.id);
    setError("");
    try {
      setSources(await listKnowledgeSources(token, space.id));
    } catch {
      setError("知识源列表加载失败");
    }
  }

  useEffect(() => {
    refreshSpaces().catch(() => setError("知识库列表加载失败"));
  }, []);

  async function refreshSelectedSpace(spaceId = selectedSpaceId) {
    const [nextSpaces, nextSources] = await Promise.all([
      listKnowledgeSpaces(token),
      spaceId ? listKnowledgeSources(token, spaceId) : Promise.resolve([]),
    ]);
    setSpaces(nextSpaces);
    setSources(nextSources);
  }

  async function createSpace(event: FormEvent) {
    event.preventDefault();
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      const space = await createKnowledgeSpace(
        {
          name: spaceName.trim(),
          product_line: productLine.trim(),
          description: spaceDescription.trim(),
          visibility,
        },
        token,
      );
      setSpaces((current) => [space, ...current]);
      setSpaceName("");
      setProductLine("");
      setSpaceDescription("");
      setDialog(null);
      await openSpace(space);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "知识库创建失败");
    } finally {
      setBusy(false);
    }
  }

  async function submitManual(event: FormEvent) {
    event.preventDefault();
    if (!selectedSpaceId || busy) return;
    setBusy(true);
    setError("");
    try {
      await createManualKnowledge(
        { title: title.trim(), content: content.trim(), visibility, space_id: selectedSpaceId },
        token,
      );
      setTitle("");
      setContent("");
      setDialog(null);
      await refreshSelectedSpace();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "知识入库失败");
    } finally {
      setBusy(false);
    }
  }

  async function editSpace(event: FormEvent) {
    event.preventDefault();
    if (!selectedSpace || busy) return;
    setBusy(true);
    setError("");
    try {
      const updated = await updateKnowledgeSpace(
        selectedSpace.id,
        { name: spaceName.trim(), product_line: productLine.trim() },
        token,
      );
      setSpaces((current) => current.map((space) => (space.id === updated.id ? updated : space)));
      setSpaceName("");
      setProductLine("");
      setDialog(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "知识库更新失败");
    } finally {
      setBusy(false);
    }
  }

  function openCreateSpaceDialog() {
    setSpaceName("");
    setProductLine("");
    setSpaceDescription("");
    setError("");
    setDialog("create-space");
  }

  function openEditSpaceDialog() {
    if (!selectedSpace) return;
    setSpaceName(selectedSpace.name);
    setProductLine(selectedSpace.product_line ?? "");
    setError("");
    setDialog("edit-space");
  }

  async function addKnowledgeFiles(event: ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? []);
    event.target.value = "";
    if (!selectedSpaceId || !files.length || busy) return;
    const unsupported = files.filter((file) => !detectContentFormat(file.name));
    if (unsupported.length) {
      setError(`暂不支持：${unsupported.map((file) => file.name).join("、")}`);
      return;
    }
    if (files.some((file) => detectContentFormat(file.name) === "pdf")) {
      setError("PDF 解析器还未接入，当前可导入 Markdown、HTML 和纯文本文件。");
      return;
    }

    setBusy(true);
    setError("");
    try {
      for (const file of files) {
        const text = await file.text();
        const contentFormat = detectContentFormat(file.name);
        if (!contentFormat || contentFormat === "pdf") continue;
        const fallbackTitle = file.name.replace(/\.(md|markdown|txt|html|htm)$/i, "");
        const firstHeading =
          text.match(/^#\s+(.+)$/m)?.[1]?.trim() ??
          text.match(/<h1[^>]*>(.*?)<\/h1>/i)?.[1]?.replace(/<[^>]+>/g, "").trim();
        await importKnowledgeDocument(
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
      }
      setDialog(null);
      await refreshSelectedSpace();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "文档导入失败");
    } finally {
      setBusy(false);
    }
  }

  async function removeSpace(space: KnowledgeSpace) {
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      await deleteKnowledgeSpace(space.id, token);
      setSpaces((current) => current.filter((item) => item.id !== space.id));
      if (selectedSpaceId === space.id) {
        setSelectedSpaceId(null);
        setSources([]);
      }
      setPendingDeleteSpace(null);
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
    try {
      await deleteKnowledgeSource(source.id, token);
      await refreshSelectedSpace();
      setPendingDeleteSource(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "知识源删除失败");
    } finally {
      setBusy(false);
    }
  }

  async function reindexSource(source: KnowledgeSource) {
    if (busy) return;
    setBusy(true);
    setReindexingSourceId(source.id);
    setError("");
    try {
      const updated = await reindexKnowledgeSource(source.id, token);
      setSources((current) => current.map((item) => (item.id === updated.id ? updated : item)));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "重新索引失败");
    } finally {
      setReindexingSourceId("");
      setBusy(false);
    }
  }

  function closeDialog() {
    if (busy) return;
    setDialog(null);
    setError("");
  }

  return (
    <>
      <header className="topbar knowledge-topbar">
        <div className={selectedSpace ? "knowledge-title-row" : ""}>
          {selectedSpace ? (
            <button aria-label="返回知识库" className="knowledge-back" onClick={() => setSelectedSpaceId(null)} title="返回知识库" type="button">
              <span aria-hidden="true" className="knowledge-back-icon" />
            </button>
          ) : null}
          <h1>{selectedSpace ? selectedSpace.name : "产品知识库"}</h1>
        </div>
        {selectedSpace ? (
          <div className="knowledge-topbar-actions">
            <button className="secondary-button" onClick={openEditSpaceDialog} type="button">
              编辑
            </button>
            <button className="primary-button" onClick={() => setDialog("add-knowledge")} type="button">
              <span aria-hidden="true">+</span> 添加知识
            </button>
          </div>
        ) : (
          <button className="primary-button" onClick={openCreateSpaceDialog} type="button">
            <span aria-hidden="true">+</span> 添加知识库
          </button>
        )}
      </header>

      {error && !dialog ? <div className="knowledge-banner error">{error}</div> : null}

      <main className="content knowledge-workbench">
        {selectedSpace ? (
          <>
            <section className="knowledge-detail-header">
              <div className="knowledge-detail-meta">
                <span>产品线 {selectedSpace.product_line || "未配置"}</span>
                <span>{selectedSpace.source_count} 个源文档</span>
                <span>{selectedSpace.chunk_count} 个知识片段</span>
                <span>{selectedSpace.visibility === "internal" ? "内部共享" : "仅本人"}</span>
              </div>
              {selectedSpace.description ? <p>{selectedSpace.description}</p> : null}
            </section>

            <section className="knowledge-source-section" aria-label="源文档">
              <div className="knowledge-section-heading">
                <div>
                  <p className="eyebrow">源文档</p>
                  <h2>{sources.length ? `${sources.length} 个文档` : "暂无文档"}</h2>
                </div>
                <span>{selectedSpace.chunk_count} 个片段</span>
              </div>
              <div className="knowledge-source-table">
                {sources.length ? (
                  sources.map((source) => (
                    <article className="knowledge-source-row" key={source.id}>
                      <div className="knowledge-file-icon" aria-hidden="true">
                        {formatLabel(source.content_format)}
                      </div>
                      <div className="knowledge-source-copy">
                        <strong>{source.title}</strong>
                        <span>{source.filename || "单条内容"} · {formatDate(source.updated_at)}</span>
                      </div>
                      <div className="knowledge-index-summary">
                        <span className={reindexingSourceId === source.id ? "knowledge-index-status indexing" : "knowledge-index-status"}>
                          {reindexingSourceId === source.id ? "正在索引" : source.status === "active" ? "已建立索引" : "待建立索引"}
                        </span>
                        <b>{source.chunk_count} 片段</b>
                      </div>
                      <div className="knowledge-row-actions">
                        <button
                          aria-busy={reindexingSourceId === source.id}
                          aria-label={reindexingSourceId === source.id ? "正在新建索引" : "重新索引"}
                          className={reindexingSourceId === source.id ? "knowledge-reindex-button spinning" : "knowledge-reindex-button"}
                          disabled={busy}
                          onClick={() => reindexSource(source)}
                          title="重新索引"
                          type="button"
                        >
                          <span aria-hidden="true" className="knowledge-reindex-icon">↻</span>
                        </button>
                        <button className="danger" disabled={busy} onClick={() => setPendingDeleteSource(source)} type="button">
                          删除
                        </button>
                      </div>
                    </article>
                  ))
                ) : (
                  <div className="knowledge-empty-state">
                    <b>这个知识库还是空的</b>
                    <button className="secondary-button" onClick={() => setDialog("add-knowledge")} type="button">
                      添加第一条知识
                    </button>
                  </div>
                )}
              </div>
            </section>
          </>
        ) : (
          <section className="knowledge-library-grid" aria-label="知识库列表">
            {spaces.length ? (
              spaces.map((space) => (
                <article className="knowledge-library-card" key={space.id}>
                  <button className="knowledge-library-open" onClick={() => openSpace(space)} type="button">
                    <div>
                      <h2>{space.name}</h2>
                      <p>{space.description || "暂无说明"}</p>
                    </div>
                    <dl>
                      <div>
                        <dt>源文档</dt>
                        <dd>{space.source_count}</dd>
                      </div>
                      <div>
                        <dt>知识片段</dt>
                        <dd>{space.chunk_count}</dd>
                      </div>
                    </dl>
                    <small>更新于 {formatDate(space.updated_at)}</small>
                  </button>
                  <button className="knowledge-library-delete" disabled={busy} onClick={() => setPendingDeleteSpace(space)} type="button">
                    删除
                  </button>
                </article>
              ))
            ) : (
              <div className="knowledge-empty-state knowledge-empty-library">
                <b>还没有产品知识库</b>
                <button className="primary-button" onClick={openCreateSpaceDialog} type="button">
                  <span aria-hidden="true">+</span> 添加知识库
                </button>
              </div>
            )}
          </section>
        )}
      </main>

      {dialog === "create-space" ? (
        <div className="feedback-dialog-backdrop" role="presentation">
          <section aria-labelledby="create-space-title" aria-modal="true" className="knowledge-modal" role="dialog">
            <div className="knowledge-modal-heading">
              <p className="eyebrow">新建</p>
              <h2 id="create-space-title">添加产品知识库</h2>
            </div>
            <form className="knowledge-modal-form" onSubmit={createSpace}>
              <label htmlFor="space-product-line">所属产品线</label>
              <input
                id="space-product-line"
                maxLength={120}
                minLength={1}
                onChange={(event) => setProductLine(event.target.value)}
                placeholder="例如：FP10"
                required
                value={productLine}
              />
              <label htmlFor="space-name">知识库名称</label>
              <input
                id="space-name"
                maxLength={160}
                minLength={2}
                onChange={(event) => setSpaceName(event.target.value)}
                placeholder="例如：FP10 产品知识库"
                required
                value={spaceName}
              />
              <label htmlFor="space-description">说明</label>
              <textarea
                id="space-description"
                maxLength={1000}
                onChange={(event) => setSpaceDescription(event.target.value)}
                placeholder="记录这个知识库覆盖的产品和资料范围"
                value={spaceDescription}
              />
              <VisibilityControl onChange={setVisibility} value={visibility} />
              {error ? <p className="form-error">{error}</p> : null}
              <div className="knowledge-modal-actions">
                <button className="secondary-button" disabled={busy} onClick={closeDialog} type="button">
                  取消
                </button>
                <button className="primary-button" disabled={busy} type="submit">
                  {busy ? "创建中" : "创建知识库"}
                </button>
              </div>
            </form>
            <button aria-label="关闭" className="dialog-close" onClick={closeDialog} type="button">
              ×
            </button>
          </section>
        </div>
      ) : null}

      {dialog === "edit-space" && selectedSpace ? (
        <div className="feedback-dialog-backdrop" role="presentation">
          <section aria-labelledby="edit-space-title" aria-modal="true" className="knowledge-modal" role="dialog">
            <div className="knowledge-modal-heading">
              <h2 id="edit-space-title">编辑知识库</h2>
            </div>
            <p className="knowledge-modal-note">修改名称或产品线不会影响现有文档和知识片段，也不需要重新索引。</p>
            <form className="knowledge-modal-form" onSubmit={editSpace}>
              <label htmlFor="edit-space-name">知识库名称</label>
              <input
                id="edit-space-name"
                maxLength={160}
                minLength={2}
                onChange={(event) => setSpaceName(event.target.value)}
                required
                value={spaceName}
              />
              <label htmlFor="edit-space-product-line">所属产品线</label>
              <input
                id="edit-space-product-line"
                maxLength={120}
                minLength={1}
                onChange={(event) => setProductLine(event.target.value)}
                placeholder="例如：FP10"
                required
                value={productLine}
              />
              {error ? <p className="form-error">{error}</p> : null}
              <div className="knowledge-modal-actions">
                <button className="secondary-button" disabled={busy} onClick={closeDialog} type="button">
                  取消
                </button>
                <button className="primary-button" disabled={busy} type="submit">
                  {busy ? "保存中" : "保存修改"}
                </button>
              </div>
            </form>
            <button aria-label="关闭" className="dialog-close" onClick={closeDialog} type="button">
              ×
            </button>
          </section>
        </div>
      ) : null}

      {dialog === "add-knowledge" && selectedSpace ? (
        <div className="feedback-dialog-backdrop" role="presentation">
          <section aria-labelledby="add-knowledge-title" aria-modal="true" className="knowledge-modal knowledge-add-modal" role="dialog">
            <div className="knowledge-modal-heading">
              <p className="eyebrow">{selectedSpace.product_line}</p>
              <h2 id="add-knowledge-title">添加知识</h2>
            </div>
            <div className="knowledge-add-modes">
              <button className={addMode === "manual" ? "active" : ""} onClick={() => setAddMode("manual")} type="button">
                <b>单条内容</b>
                <span>售后经验、故障处理或 FAQ</span>
              </button>
              <button className={addMode === "document" ? "active" : ""} onClick={() => setAddMode("document")} type="button">
                <b>导入文档</b>
                <span>Markdown、HTML 或纯文本</span>
              </button>
            </div>
            {addMode === "manual" ? (
              <form className="knowledge-modal-form" onSubmit={submitManual}>
                <label htmlFor="knowledge-title">标题</label>
                <input
                  id="knowledge-title"
                  maxLength={160}
                  minLength={2}
                  onChange={(event) => setTitle(event.target.value)}
                  placeholder="例如：FP10 主控蓝灯呼吸"
                  required
                  value={title}
                />
                <label htmlFor="knowledge-content">内容</label>
                <textarea
                  id="knowledge-content"
                  maxLength={12000}
                  minLength={10}
                  onChange={(event) => setContent(event.target.value)}
                  placeholder="填写现象、判断标准和处理步骤"
                  required
                  value={content}
                />
                <VisibilityControl onChange={setVisibility} value={visibility} />
                {error ? <p className="form-error">{error}</p> : null}
                <div className="knowledge-modal-actions">
                  <button className="secondary-button" disabled={busy} onClick={closeDialog} type="button">
                    取消
                  </button>
                  <button className="primary-button" disabled={busy} type="submit">
                    {busy ? "保存中" : "保存并建立索引"}
                  </button>
                </div>
              </form>
            ) : (
              <div className="knowledge-upload-panel">
                <label className="knowledge-upload-target">
                  <span aria-hidden="true">+</span>
                  <b>选择知识文档</b>
                  <small>支持 .md、.txt、.html，可同时选择多个文件</small>
                  <input
                    accept=".md,.markdown,.txt,.html,.htm,text/markdown,text/plain,text/html"
                    multiple
                    onChange={addKnowledgeFiles}
                    type="file"
                  />
                </label>
                <VisibilityControl onChange={setVisibility} value={visibility} />
                {error ? <p className="form-error">{error}</p> : null}
              </div>
            )}
            <button aria-label="关闭" className="dialog-close" onClick={closeDialog} type="button">
              ×
            </button>
          </section>
        </div>
      ) : null}

      {pendingDeleteSpace ? (
        <DeleteConfirmDialog
          busy={busy}
          description="删除后，该知识库中的源文档和知识片段都会永久删除，且无法恢复。"
          onCancel={() => {
            if (!busy) setPendingDeleteSpace(null);
          }}
          onConfirm={() => removeSpace(pendingDeleteSpace)}
          subject={pendingDeleteSpace.name}
          title="确认删除知识库？"
        />
      ) : null}

      {pendingDeleteSource ? (
        <DeleteConfirmDialog
          busy={busy}
          description="删除后，该条知识及其对应的知识片段会一并永久删除，且无法恢复。"
          onCancel={() => {
            if (!busy) setPendingDeleteSource(null);
          }}
          onConfirm={() => removeSource(pendingDeleteSource)}
          subject={pendingDeleteSource.title}
          title="确认删除这条知识？"
        />
      ) : null}
    </>
  );
}

function VisibilityControl({
  onChange,
  value,
}: {
  onChange: (value: "internal" | "private") => void;
  value: "internal" | "private";
}) {
  return (
    <div aria-label="可见范围" className="segmented-control">
      <button className={value === "internal" ? "active" : ""} onClick={() => onChange("internal")} type="button">
        内部共享
      </button>
      <button className={value === "private" ? "active" : ""} onClick={() => onChange("private")} type="button">
        仅本人
      </button>
    </div>
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

function formatLabel(format: KnowledgeSource["content_format"]): string {
  if (format === "markdown") return "MD";
  if (format === "html") return "HTML";
  if (format === "pdf") return "PDF";
  return "TXT";
}

function formatDate(value: string): string {
  return new Intl.DateTimeFormat("zh-CN", { month: "2-digit", day: "2-digit", year: "numeric" }).format(new Date(value));
}
