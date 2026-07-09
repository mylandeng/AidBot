import { AdminShell } from "@/components/layout/admin-shell";
import { requireAdmin } from "@/lib/auth";

export default async function FeedbackPage() {
  await requireAdmin();

  return (
    <AdminShell
      active="feedback"
      mainClassName="main feedback-main"
      sidebarPanel={
        <>
          <h2>反馈复盘</h2>
          <ul>
            <li>
              <a href="/feedback">集中处理用户反馈和低分回答。</a>
            </li>
          </ul>
        </>
      }
    >
      <header className="topbar">
        <div>
          <p className="eyebrow">反馈复盘</p>
          <h1>集中处理用户反馈和需要人工复核的问题。</h1>
        </div>
      </header>
      <section className="content feedback-grid">
        <section className="ask-panel feedback-queue">
          <div className="panel-heading">
            <div>
              <p className="eyebrow">待接入</p>
              <h2>反馈复盘将在阶段 4 接入。</h2>
            </div>
          </div>
          <p className="feedback-empty">用户端提交的“有帮助 / 没帮助 / 需要人工跟进”会在这里集中处理。</p>
        </section>
      </section>
    </AdminShell>
  );
}
