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
          <p className="eyebrow">AidBot 访问</p>
          <h1 id="login-title">输入访问码，开始售后问答。</h1>
          <p>普通用户使用管理员分配的访问码进入聊天；管理员可切换到邮箱密码登录后台。</p>
        </div>

        <LoginForm />
      </section>
    </main>
  );
}
