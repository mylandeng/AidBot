import { requireSession } from "@/lib/auth";
import { KnowledgeWorkbench } from "./workbench";

export default async function KnowledgePage() {
  const token = await requireSession();

  return <KnowledgeWorkbench token={token} />;
}
