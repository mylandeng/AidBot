import { redirectAuthenticatedUser } from "@/lib/auth";
import { LoginForm } from "./login-form";

export default async function LoginPage() {
  await redirectAuthenticatedUser();

  return (
    <main className="login-shell">
      <section className="login-panel" aria-labelledby="login-title">
        <div className="brand-lockup login-brand">
          <span className="brand-mark">A</span>
          <span>
            <strong>AidBot</strong>
            <small>售后知识中枢</small>
          </span>
        </div>

        <div className="login-copy">
          <p className="eyebrow">内部访问</p>
          <h1 id="login-title">登录后继续处理售后问题。</h1>
          <p>当前阶段使用内置管理员账号验证登录链路，后续会接入用户表和正式密码策略。</p>
        </div>

        <LoginForm />
      </section>
    </main>
  );
}
