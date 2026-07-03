import { getHealth } from "@/lib/api";

export async function HealthBadge() {
  const health = await getHealth();
  const label = health?.status === "ok" ? "服务可用" : "连接异常";

  return <span className="status-pill">{label}</span>;
}
