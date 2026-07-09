import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { SESSION_COOKIE_NAME } from "./session";
import type { CurrentUser } from "./types";

const API_BASE_URL = process.env.API_INTERNAL_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8010";

export async function getSessionToken(): Promise<string | undefined> {
  const cookieStore = await cookies();
  return cookieStore.get(SESSION_COOKIE_NAME)?.value;
}

async function isValidToken(token: string): Promise<boolean> {
  return Boolean(await getCurrentUser(token));
}

export async function getCurrentUser(token: string): Promise<CurrentUser | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    });
    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}

export async function requireSession(): Promise<string> {
  const token = await getSessionToken();
  if (!token || !(await isValidToken(token))) {
    redirect("/login");
  }
  return token;
}

export async function requireAdmin(): Promise<string> {
  const token = await requireSession();
  const user = await getCurrentUser(token);
  if (!user?.roles.includes("admin")) {
    redirect("/user/chat");
  }
  return token;
}

export async function redirectAuthenticatedUser(): Promise<void> {
  const token = await getSessionToken();
  const user = token ? await getCurrentUser(token) : null;
  if (user) {
    redirect(user.roles.includes("admin") ? "/" : "/user/chat");
  }
}
