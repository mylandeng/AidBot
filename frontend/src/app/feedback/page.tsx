import { AdminShell } from "@/components/layout/admin-shell";
import { requireAdmin } from "@/lib/auth";
import { FeedbackWorkbench } from "./workbench";

export default async function FeedbackPage() {
  const token = await requireAdmin();

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
            <li>
              <a href="/knowledge">复盘后可沉淀为知识。</a>
            </li>
          </ul>
        </>
      }
    >
      <FeedbackWorkbench token={token} />
    </AdminShell>
  );
}
