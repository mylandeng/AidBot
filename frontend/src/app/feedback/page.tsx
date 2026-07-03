import { requireSession } from "@/lib/auth";

export default async function FeedbackPage() {
  await requireSession();

  return <main className="content">反馈复盘将在阶段 4 接入。</main>;
}
