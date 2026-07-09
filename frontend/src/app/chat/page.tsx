import { redirect } from "next/navigation";

import { getCurrentUser, requireSession } from "@/lib/auth";

export default async function ChatPage() {
  const token = await requireSession();
  const user = await getCurrentUser(token);
  redirect(user?.roles.includes("admin") ? "/admin/chat" : "/user/chat");
}
