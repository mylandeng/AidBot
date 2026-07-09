import { AdminShell } from "@/components/layout/admin-shell";
import { requireAdmin } from "@/lib/auth";
import { KnowledgeWorkbench } from "./workbench";

export default async function KnowledgePage() {
  const token = await requireAdmin();

  return (
    <AdminShell
      active="knowledge"
      mainClassName="main knowledge-main"
      sidebarPanel={
        <>
          <h2>知识入库</h2>
          <ul>
            <li>
              <a href="/knowledge">只负责添加、索引和管理知识。</a>
            </li>
            <li>
              <a href="/admin/chat">测试回答请去聊一聊。</a>
            </li>
          </ul>
        </>
      }
    >
      <KnowledgeWorkbench token={token} />
    </AdminShell>
  );
}
