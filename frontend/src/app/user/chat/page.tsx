import { redirect } from "next/navigation";

import { getCurrentUser, requireSession } from "@/lib/auth";
import { ChatWorkbench } from "../../chat/workbench";

export default async function UserChatPage() {
  const token = await requireSession();
  const user = await getCurrentUser(token);
  if (user?.roles.includes("admin")) {
    redirect("/admin/chat");
  }
  return <ChatWorkbench token={token} />;
}
