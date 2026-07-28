"use client";

import { FormEvent, useEffect, useState } from "react";
import { DeleteConfirmDialog } from "@/components/ui/delete-confirm-dialog";
import { createAccessKey, deleteAccessKey, disableAccessKey, enableAccessKey, listAccessKeys } from "@/lib/api";
import type { AccessKey, AccessKeyDuration } from "@/lib/types";

const durationLabels: Record<AccessKeyDuration, string> = {
  "7d": "7 天",
  "30d": "30 天",
  "180d": "半年",
  "365d": "1 年",
};

export function AdminWorkbench({ token }: { token: string }) {
  const [items, setItems] = useState<AccessKey[]>([]);
  const [name, setName] = useState("");
  const [expiresIn, setExpiresIn] = useState<AccessKeyDuration>("30d");
  const [maxRequests, setMaxRequests] = useState("");
  const [note, setNote] = useState("");
  const [createdKey, setCreatedKey] = useState("");
  const [error, setError] = useState("");
  const [copiedValue, setCopiedValue] = useState("");
  const [pendingDeleteItem, setPendingDeleteItem] = useState<AccessKey | null>(null);
  const [busyId, setBusyId] = useState<string | null>(null);
  const [creating, setCreating] = useState(false);

  async function refresh() {
    setItems(await listAccessKeys(token));
  }

  useEffect(() => {
    refresh().catch(() => setError("访问码列表加载失败"));
  }, []);

  async function submit(event: FormEvent) {
    event.preventDefault();
    if (!name.trim() || creating) return;
    setCreating(true);
    setError("");
    setCreatedKey("");
    try {
      const result = await createAccessKey(
        {
          name: name.trim(),
          expires_in: expiresIn,
          max_requests: maxRequests.trim() ? Number(maxRequests) : null,
          note: note.trim(),
        },
        token,
      );
      setCreatedKey(result.access_key);
      setName("");
      setMaxRequests("");
      setNote("");
      await refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "创建访问码失败");
    } finally {
      setCreating(false);
    }
  }

  async function copyKey(value: string) {
    if (!value) return;
    try {
      if (navigator.clipboard?.writeText) {
        await navigator.clipboard.writeText(value);
      } else {
        const textarea = document.createElement("textarea");
        textarea.value = value;
        textarea.setAttribute("readonly", "true");
        textarea.style.position = "fixed";
        textarea.style.opacity = "0";
        document.body.appendChild(textarea);
        textarea.select();
        document.execCommand("copy");
        document.body.removeChild(textarea);
      }
      setCopiedValue(value);
      setError("");
    } catch {
      setError("复制失败，请手动选择访问码复制");
    }
  }

  async function toggle(item: AccessKey) {
    setBusyId(item.id);
    setError("");
    try {
      await (item.status === "disabled" ? enableAccessKey(item.id, token) : disableAccessKey(item.id, token));
      await refresh();
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "状态更新失败");
    } finally {
      setBusyId(null);
    }
  }

  async function remove(item: AccessKey) {
    setBusyId(item.id);
    setError("");
    try {
      await deleteAccessKey(item.id, token);
      await refresh();
      setPendingDeleteItem(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "删除访问码失败");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <>
        <header className="topbar">
          <div>
            <p className="eyebrow">后台设置</p>
            <h1>分配访问码，控制用户聊天入口。</h1>
          </div>
        </header>

        <section className="content admin-grid">
          <section className="ask-panel" aria-labelledby="key-create-title">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">Key 管理</p>
                <h2 id="key-create-title">创建访问码</h2>
              </div>
            </div>
            <form className="knowledge-form" onSubmit={submit}>
              <label htmlFor="key-name">用户或客户名称</label>
              <input id="key-name" value={name} onChange={(event) => setName(event.target.value)} placeholder="例如：客户A试用" />

              <label htmlFor="key-duration">有效期</label>
              <select id="key-duration" value={expiresIn} onChange={(event) => setExpiresIn(event.target.value as AccessKeyDuration)}>
                {Object.entries(durationLabels).map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>

              <label htmlFor="key-quota">请求次数额度（可选）</label>
              <input id="key-quota" inputMode="numeric" value={maxRequests} onChange={(event) => setMaxRequests(event.target.value)} placeholder="不填则不限次数" />

              <label htmlFor="key-note">备注（可选）</label>
              <textarea id="key-note" value={note} onChange={(event) => setNote(event.target.value)} placeholder="记录用途、客户或交付说明" />

              {error ? <p className="form-error">{error}</p> : null}
              {createdKey ? (
                <div className="created-key">
                  <div className="created-key-header">
                    <span>新访问码</span>
                    <button className="source-action" onClick={() => copyKey(createdKey)} type="button">
                      {copiedValue === createdKey ? "已复制" : "复制"}
                    </button>
                  </div>
                  <code>{createdKey}</code>
                </div>
              ) : null}

              <button className="primary-button" disabled={creating} type="submit">
                {creating ? "创建中" : "创建访问码"}
              </button>
            </form>
          </section>

          <section className="ask-panel key-list-panel" aria-labelledby="key-list-title">
            <div className="panel-heading">
              <div>
                <p className="eyebrow">已分配</p>
                <h2 id="key-list-title">访问码列表</h2>
              </div>
            </div>
            <div className="key-list">
              {items.length ? (
                items.map((item) => (
                  <article className="key-item" key={item.id}>
                    <div className="key-primary">
                      <strong>{item.name}</strong>
                      <code>{item.key_prefix}...</code>
                      <small>完整访问码仅创建后显示一次；如遗失请删除后重新创建。</small>
                    </div>
                    <div className="key-meta">
                      <span>{statusLabel(item.status)}</span>
                      <span>有效至 {new Date(item.expires_at).toLocaleDateString()}</span>
                      <span>
                        请求 {item.used_requests}
                        {item.max_requests ? ` / ${item.max_requests}` : ""}
                      </span>
                    </div>
                    <div className="source-actions">
                      <button className="source-action" disabled={busyId === item.id} onClick={() => toggle(item)} type="button">
                        {item.status === "disabled" ? "启用" : "禁用"}
                      </button>
                      <button className="source-action danger" disabled={busyId === item.id} onClick={() => setPendingDeleteItem(item)} type="button">
                        删除
                      </button>
                    </div>
                  </article>
                ))
              ) : (
                <p className="feedback-empty">还没有访问码。</p>
              )}
            </div>
          </section>
        </section>

        {pendingDeleteItem ? (
          <DeleteConfirmDialog
            busy={busyId === pendingDeleteItem.id}
            description="删除后用户将无法再使用该访问码登录，历史用量记录会保留。"
            onCancel={() => {
              if (!busyId) setPendingDeleteItem(null);
            }}
            onConfirm={() => remove(pendingDeleteItem)}
            subject={pendingDeleteItem.name}
            title="确认删除访问码？"
          />
        ) : null}
    </>
  );
}

function statusLabel(status: AccessKey["status"]): string {
  if (status === "active") return "可用";
  if (status === "disabled") return "已禁用";
  return "已删除";
}
