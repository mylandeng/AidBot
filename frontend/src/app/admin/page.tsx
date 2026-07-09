import { AdminShell } from "@/components/layout/admin-shell";
import { requireAdmin } from "@/lib/auth";
import { AdminWorkbench } from "./workbench";

export default async function AdminPage() {
  const token = await requireAdmin();

  return (
    <AdminShell
      active="settings"
      mainClassName="main admin-main"
      sidebarPanel={
        <>
          <h2>后台设置</h2>
          <ul>
            <li>
              <a href="/admin">分配、禁用或删除访问码。</a>
            </li>
            <li>
              <a href="/admin">额度限制记录请求次数，用于控制用户使用量。</a>
            </li>
          </ul>
        </>
      }
    >
      <AdminWorkbench token={token} />
    </AdminShell>
  );
}
