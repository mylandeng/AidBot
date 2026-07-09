"use client";

import { useRouter } from "next/navigation";

import { SESSION_COOKIE_NAME } from "@/lib/session";

export function LogoutButton({ className = "logout-button" }: { className?: string }) {
  const router = useRouter();

  function logout() {
    document.cookie = `${SESSION_COOKIE_NAME}=; path=/; max-age=0; samesite=lax`;
    router.replace("/login");
    router.refresh();
  }

  return (
    <button className={className} onClick={logout} type="button">
      退出登录
    </button>
  );
}
