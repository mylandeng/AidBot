import type { ReactNode } from "react";

import { LogoutButton } from "./logout-button";

export type AdminNavKey = "triage" | "chat" | "knowledge" | "feedback" | "settings";

const navItems: Array<{ key: AdminNavKey; href: string; label: string; meta: string }> = [
  { key: "triage", href: "/", label: "问答分诊", meta: "概览" },
  { key: "chat", href: "/admin/chat", label: "聊一聊", meta: "测试" },
  { key: "knowledge", href: "/knowledge", label: "知识入库", meta: "添加" },
  { key: "feedback", href: "/feedback", label: "反馈复盘", meta: "处理" },
  { key: "settings", href: "/admin", label: "后台设置", meta: "Key" },
];

type AdminShellProps = {
  active: AdminNavKey;
  children: ReactNode;
  mainClassName?: string;
  sidebarPanel?: ReactNode;
};

export function AdminShell({ active, children, mainClassName = "main", sidebarPanel }: AdminShellProps) {
  return (
    <div className="app-shell admin-shell">
      <aside className="sidebar admin-sidebar">
        <a className="brand-lockup" href="/" aria-label="AidBot 管理后台">
          <span className="brand-mark">A</span>
          <span>
            <strong>AidBot</strong>
            <small>管理后台</small>
          </span>
        </a>

        <nav className="nav-list" aria-label="管理员导航">
          {navItems.map((item) => (
            <a className={`nav-item ${item.key === active ? "active" : ""}`} href={item.href} key={item.key}>
              <span>{item.label}</span>
              <small>{item.key === active ? "当前" : item.meta}</small>
            </a>
          ))}
        </nav>

        <section className="sidebar-block admin-sidebar-panel">{sidebarPanel}</section>

        <div className="sidebar-footer">
          <LogoutButton />
        </div>
      </aside>

      <main className={mainClassName}>{children}</main>
    </div>
  );
}
