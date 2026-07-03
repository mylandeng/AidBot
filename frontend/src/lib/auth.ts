import { cookies } from "next/headers";
import { redirect } from "next/navigation";

import { SESSION_COOKIE_NAME } from "./session";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8010";

export async function getSessionToken(): Promise<string | undefined> {
  const cookieStore = await cookies();
  return cookieStore.get(SESSION_COOKIE_NAME)?.value;
}

async function isValidToken(token: string): Promise<boolean> {
  try {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: {
        Authorization: `Bearer ${token}`,
      },
      cache: "no-store",
    });
    return response.ok;
  } catch {
    return false;
  }
}

export async function requireSession(): Promise<string> {
  const token = await getSessionToken();
  if (!token || !(await isValidToken(token))) {
    redirect("/login");
  }
  return token;
}

export async function redirectAuthenticatedUser(): Promise<void> {
  const token = await getSessionToken();
  if (token && (await isValidToken(token))) {
    redirect("/");
  }
}
