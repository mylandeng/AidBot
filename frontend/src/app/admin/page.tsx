import { requireSession } from "@/lib/auth";

export default async function AdminPage() {
  await requireSession();

  return <main className="content">系统设置将在阶段 1 后逐步接入。</main>;
}
