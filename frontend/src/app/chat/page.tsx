import { requireSession } from "@/lib/auth";

export default async function ChatPage() {
  await requireSession();

  return <main className="content">会话历史将在阶段 2 接入。</main>;
}
