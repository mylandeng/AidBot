import { requireSession } from "@/lib/auth";

export default async function KnowledgePage() {
  await requireSession();

  return <main className="content">知识库管理将在阶段 3 接入。</main>;
}
