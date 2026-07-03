import { HealthBadge } from "@/components/layout/health-badge";
import { requireSession } from "@/lib/auth";

const sources = [
  { title: "AX-42 联网排查手册", type: "上传文档", score: "0.86" },
  { title: "售后标准话术库", type: "手动知识", score: "0.78" },
  { title: "上周高频工单摘要", type: "工单沉淀", score: "0.71" },
];

const conversations = [
  "网关灯常亮但 App 显示离线",
  "设备配网后 5 分钟断连",
  "客户要求远程恢复出厂设置",
];

export default async function Home() {
  await requireSession();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand-lockup" href="/" aria-label="AidBot 首页">
          <span className="brand-mark">A</span>
          <span>
            <strong>AidBot</strong>
            <small>售后知识中枢</small>
          </span>
        </a>

        <nav className="nav-list" aria-label="主导航">
          <a className="nav-item active" href="/">
            <span>问答分诊</span>
            <small>当前</small>
          </a>
          <a className="nav-item" href="/chat">
            <span>会话记录</span>
            <small>3 条</small>
          </a>
          <a className="nav-item" href="/knowledge">
            <span>知识入库</span>
            <small>待接入</small>
          </a>
          <a className="nav-item" href="/feedback">
            <span>反馈复盘</span>
            <small>待处理</small>
          </a>
          <a className="nav-item" href="/admin">
            <span>系统设置</span>
            <small>内部</small>
          </a>
        </nav>

        <section className="sidebar-block" aria-labelledby="recent-title">
          <h2 id="recent-title">最近问题</h2>
          <ul>
            {conversations.map((item) => (
              <li key={item}>
                <a href="/chat">{item}</a>
              </li>
            ))}
          </ul>
        </section>
      </aside>

      <main className="main">
        <header className="topbar">
          <div>
            <p className="eyebrow">内部支持台</p>
            <h1>把问题、证据和下一步放在同一屏</h1>
          </div>
          <HealthBadge />
        </header>

        <section className="content">
          <section className="hero-workbench" aria-labelledby="workbench-title">
            <div className="workbench-copy">
              <p className="eyebrow">今日分诊</p>
              <h2 id="workbench-title">客户说“设备连不上网”，先把可验证的信息问完整。</h2>
              <p>
                AidBot 会把问题拆成排查顺序、客户追问和引用来源。回答上线前保留人工判断，低置信度自动提示转人工。
              </p>
            </div>

            <div className="signal-rail" aria-label="问答处理进度">
              <span className="rail-node active">提问</span>
              <span className="rail-node active">检索</span>
              <span className="rail-node">回答</span>
              <span className="rail-node">反馈</span>
            </div>
          </section>

          <div className="workspace-grid">
            <section className="ask-panel" aria-labelledby="ask-title">
              <div className="panel-heading">
                <div>
                  <p className="eyebrow">新问题</p>
                  <h2 id="ask-title">售后问题分诊</h2>
                </div>
                <span className="confidence-chip">置信度预估：低</span>
              </div>

              <form className="question-box">
                <label htmlFor="question">客户描述</label>
                <textarea
                  id="question"
                  defaultValue="客户反馈 AX-42 已经完成配网，但 App 仍显示离线。路由器正常，设备指示灯常亮。"
                />
                <div className="composer-actions">
                  <button className="secondary-button" type="button">
                    保存草稿
                  </button>
                  <button className="primary-button" type="button">
                    生成排查建议
                  </button>
                </div>
              </form>

              <article className="answer-draft">
                <div className="answer-label">建议回复</div>
                <h3>先确认网络环境，再判断设备是否完成云端注册。</h3>
                <ol>
                  <li>请客户确认手机和设备是否在同一 2.4GHz Wi-Fi 环境。</li>
                  <li>让客户拍摄设备指示灯状态，并确认是否出现重启或闪烁。</li>
                  <li>查询后台设备序列号，确认最后一次心跳时间。</li>
                  <li>若 10 分钟内无心跳，建议转人工排查路由器隔离或设备注册异常。</li>
                </ol>
              </article>
            </section>

            <aside className="side-stack" aria-label="来源与质量">
              <section className="status-card">
                <span>当前链路</span>
                <strong>接口在线</strong>
                <p>后端、前端和聊天合同已接通，等待接入真实知识检索。</p>
              </section>

              <section className="source-panel">
                <div className="panel-heading compact">
                  <div>
                    <p className="eyebrow">引用来源</p>
                    <h2>候选证据</h2>
                  </div>
                </div>
                <div className="source-list">
                  {sources.map((source) => (
                    <article className="source-item" key={source.title}>
                      <div>
                        <strong>{source.title}</strong>
                        <span>{source.type}</span>
                      </div>
                      <em>{source.score}</em>
                    </article>
                  ))}
                </div>
              </section>

              <section className="review-panel">
                <p className="eyebrow">质量闭环</p>
                <h2>低分回答进入复盘队列</h2>
                <p>知识缺失、检索未命中和话术不清会被分开处理，避免问题只停留在聊天记录里。</p>
              </section>
            </aside>
          </div>
        </section>
      </main>
    </div>
  );
}
