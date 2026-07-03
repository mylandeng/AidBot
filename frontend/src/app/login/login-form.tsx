"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { login } from "@/lib/api";
import { SESSION_COOKIE_NAME } from "@/lib/session";

const defaultEmail = "admin@aidbot.local";

export function LoginForm() {
  const router = useRouter();
  const [email, setEmail] = useState(defaultEmail);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const result = await login(email, password);
      const maxAge = result.expires_in;
      document.cookie = `${SESSION_COOKIE_NAME}=${result.access_token}; path=/; max-age=${maxAge}; samesite=lax`;
      router.push("/");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "登录失败，请稍后重试");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="login-form" onSubmit={handleSubmit}>
      <label htmlFor="email">邮箱</label>
      <input
        id="email"
        name="email"
        autoComplete="username"
        value={email}
        onChange={(event) => setEmail(event.target.value)}
      />

      <label htmlFor="password">密码</label>
      <input
        id="password"
        name="password"
        type="password"
        autoComplete="current-password"
        placeholder="默认 aidbot123"
        value={password}
        onChange={(event) => setPassword(event.target.value)}
      />

      {error ? <p className="form-error">{error}</p> : null}

      <button className="primary-button login-button" type="submit" disabled={isSubmitting}>
        {isSubmitting ? "正在登录" : "进入工作台"}
      </button>
    </form>
  );
}
