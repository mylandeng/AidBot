import type { HealthResponse, LoginResponse } from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8010";

export async function getHealth(): Promise<HealthResponse | null> {
  try {
    const response = await fetch(`${API_BASE_URL}/health`, {
      next: { revalidate: 10 },
    });

    if (!response.ok) {
      return null;
    }

    return response.json();
  } catch {
    return null;
  }
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    throw new Error("邮箱或密码不正确");
  }

  return response.json();
}
