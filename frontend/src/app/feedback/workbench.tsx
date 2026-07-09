"use client";

import { useEffect, useMemo, useState } from "react";
import { listFeedback, updateFeedbackStatus } from "@/lib/api";
import type { FeedbackItem, FeedbackStatus } from "@/lib/types";

export function FeedbackWorkbench({ token }: { token: string }) {
  const [items, setItems] = useState<FeedbackItem[]>([]);
  const [status, setStatus] = useState<FeedbackStatus | "all">("pending");
  const [busyId, setBusyId] = useState<string | null>(null);
  const [notice, setNotice] = useState("");
  const [error, setError] = useState("");

  const visibleItems = useMemo(() => items, [items]);

  async function refresh(nextStatus = status) {
    setItems(await listFeedback(token, nextStatus === "all" ? undefined : nextStatus));
  }

  useEffect(() => {
    refresh().catch(() => setError("反馈队列加载失败"));
  }, []);

  async function changeStatus(nextStatus: FeedbackStatus | "all") {
    setStatus(nextStatus);
    setError("");
    setNotice("");
    try {
      await refresh(nextStatus);
    } catch {
      setError("反馈队列加载失败");
    }
  }

  async function processFeedback(item: FeedbackItem, nextStatus: FeedbackStatus) {
    setBusyId(item.id);
    setError("");
    setNotice("");
    try {
      const updated = await updateFeedbackStatus(item.id, { status: nextStatus, admin_note: statusNote(nextStatus) }, token);
      setItems((current) => (status === "all" ? current.map((entry) => (entry.id === updated.id ? updated : entry)) : current.filter((entry) => entry.id !== updated.id)));
      setNotice(`已标记为${statusLabel(nextStatus)}。`);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "反馈状态更新失败");
    } finally {
      setBusyId(null);
    }
  }

  return (
    <>
      <header className="topbar">
        <div>
          <p className="eyebrow">反馈复盘</p>
          <h1>把低分回答转成可处理的知识改进队列</h1>
        </div>
        <div className="feedback-filter" aria-label="反馈状态筛选">
          {statusFilters.map((filter) => (
            <button className={status === filter.value ? "active" : ""} key={filter.value} onClick={() => changeStatus(filter.value)} type="button">
              {filter.label}
            </button>
          ))}
        </div>
      </header>

      {notice ? <div className="feedback-banner">{notice}</div> : null}
      {error ? <div className="feedback-banner error">{error}</div> : null}

      <section className="content feedback-grid">
        <section className="ask-panel feedback-queue" aria-label="反馈队列">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">当前队列</p>
              <h2>{visibleItems.length ? `${visibleItems.length} 条反馈` : "暂无反馈"}</h2>
            </div>
            <span className="confidence-chip">{status === "all" ? "全部状态" : statusLabel(status)}</span>
          </div>

          <div className="feedback-list">
            {visibleItems.length ? (
              visibleItems.map((item) => (
                <article className="feedback-item" key={item.id}>
                  <div className="feedback-meta">
                    <span>{ratingLabel(item.rating)}</span>
                    <span>{statusLabel(item.status)}</span>
                    <span>{item.source_count} 条来源</span>
                  </div>
                  <h3>{item.question_preview || "未找到原问题"}</h3>
                  <p>{item.answer_preview || "未找到回答内容"}</p>
                  {item.note ? <small>用户备注：{item.note}</small> : null}
                  {item.admin_note ? <small>处理备注：{item.admin_note}</small> : null}
                  <div className="feedback-actions">
                    <button disabled={busyId === item.id || item.status === "processing"} onClick={() => processFeedback(item, "processing")} type="button">
                      处理中
                    </button>
                    <button disabled={busyId === item.id || item.status === "resolved"} onClick={() => processFeedback(item, "resolved")} type="button">
                      已解决
                    </button>
                    <button disabled={busyId === item.id || item.status === "ignored"} onClick={() => processFeedback(item, "ignored")} type="button">
                      忽略
                    </button>
                  </div>
                </article>
              ))
            ) : (
              <div className="empty-chat feedback-empty">
                <b>当前状态下没有反馈。</b>
                <p>在用户聊天回答下提交“没帮助”或“需要人工跟进”后，这里会出现处理项。</p>
              </div>
            )}
          </div>
        </section>
      </section>
    </>
  );
}

const statusFilters: { value: FeedbackStatus | "all"; label: string }[] = [
  { value: "pending", label: "待处理" },
  { value: "processing", label: "处理中" },
  { value: "resolved", label: "已解决" },
  { value: "ignored", label: "已忽略" },
  { value: "all", label: "全部" },
];

function ratingLabel(rating: FeedbackItem["rating"]): string {
  if (rating === "useful") return "有用";
  if (rating === "needs_review") return "需复盘";
  if (rating === "needs_human") return "需人工";
  return "无效";
}

function statusLabel(status: FeedbackStatus): string {
  if (status === "processing") return "处理中";
  if (status === "resolved") return "已解决";
  if (status === "ignored") return "已忽略";
  return "待处理";
}

function statusNote(status: FeedbackStatus): string {
  if (status === "processing") return "管理员已接手复盘。";
  if (status === "resolved") return "管理员已完成处理。";
  if (status === "ignored") return "管理员判断暂不处理。";
  return "";
}
