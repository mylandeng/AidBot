import { AdminShell } from "@/components/layout/admin-shell";
import { requireAdmin } from "@/lib/auth";
import { AdminChatWorkbench } from "./workbench";

export default async function AdminChatPage() {
  const token = await requireAdmin();

  return (
    <AdminShell
      active="chat"
      mainClassName="main admin-chat-main"
      sidebarPanel={
        <>
          <h2>测试聊天</h2>
          <ul>
            <li>
              <a href="/admin/chat">用于验证知识检索、引用来源和置信度。</a>
            </li>
            <li>
              <a href="/knowledge">需要补知识时回到知识入库。</a>
            </li>
          </ul>
        </>
      }
    >
      <AdminChatWorkbench token={token} />
    </AdminShell>
  );
}
