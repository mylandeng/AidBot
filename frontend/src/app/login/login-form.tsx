"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { keyLogin, login } from "@/lib/api";
import { SESSION_COOKIE_NAME } from "@/lib/session";

const defaultEmail = "admin@aidbot.local";
type LoginMode = "key" | "admin";

export function LoginForm() {
  const router = useRouter();
  const [mode, setMode] = useState<LoginMode>("key");
  const [accessKey, setAccessKey] = useState("");
  const [email, setEmail] = useState(defaultEmail);
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      const result = mode === "key" ? await keyLogin(accessKey) : await login(email, password);
      const maxAge = result.expires_in;
      document.cookie = `${SESSION_COOKIE_NAME}=${result.access_token}; path=/; max-age=${maxAge}; samesite=lax`;
      router.push(result.user.roles.includes("admin") ? "/" : "/user/chat");
      router.refresh();
    } catch (err) {
      setError(err instanceof Error ? err.message : "登录失败，请稍后重试");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form className="login-form" onSubmit={handleSubmit}>
      <div className="segmented-control">
        <button className={mode === "key" ? "active" : ""} onClick={() => setMode("key")} type="button">
          访问码登录
        </button>
        <button className={mode === "admin" ? "active" : ""} onClick={() => setMode("admin")} type="button">
          管理员登录
        </button>
      </div>

      {mode === "key" ? (
        <>
          <label htmlFor="access-key">访问码</label>
          <input
            id="access-key"
            name="access-key"
            autoComplete="one-time-code"
            placeholder="输入管理员分配的访问码"
            value={accessKey}
            onChange={(event) => setAccessKey(event.target.value)}
          />
        </>
      ) : (
        <>
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
        </>
      )}

      {error ? <p className="form-error">{error}</p> : null}

      <button className="primary-button login-button" type="submit" disabled={isSubmitting}>
        {isSubmitting ? "正在登录" : mode === "key" ? "进入聊天" : "进入后台"}
      </button>
    </form>
  );
}
