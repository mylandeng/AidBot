import { requireSession } from "@/lib/auth";
import { ChatWorkbench } from "./workbench";

export default async function ChatPage() {
  const token = await requireSession();
  return <ChatWorkbench token={token} />;
}
