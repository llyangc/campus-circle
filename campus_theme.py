"""对齐 campus-community-web（Vue）的浅色玻璃拟态与顶栏视觉，通过全局 CSS 注入 Streamlit。"""

from __future__ import annotations

import streamlit as st


def inject_campus_styles() -> None:
    # 勿用 st.markdown 注入 <style>：新版本会消毒 HTML，导致样式被剥掉、CSS 以纯文本显示在页面上。
    # 使用 st.html 原样插入样式（Streamlit 文档推荐用于纯 HTML/CSS 片段）。
    _CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,600;0,9..40,700&family=Noto+Sans+SC:wght@400;500;600;700&display=swap');
:root {
  --cc-bg: #f5f8fc;
  --cc-surface: rgba(255, 255, 255, 0.72);
  --cc-surface-strong: rgba(255, 255, 255, 0.92);
  --cc-line: rgba(15, 40, 70, 0.08);
  --cc-ink: #0f2238;
  --cc-ink-soft: rgba(15, 34, 56, 0.62);
  --cc-blue-1: #7ec8ff;
  --cc-blue-2: #4a9fe8;
  --cc-blue-3: #2f6bcc;
  --cc-primary: #3d8fd9;
  --cc-radius-lg: 26px;
  --cc-radius-md: 18px;
  --cc-shadow: 0 18px 50px rgba(20, 60, 120, 0.12);
}

html, body, .stApp, [data-testid="stAppViewContainer"] {
  font-family: 'Noto Sans SC', 'DM Sans', system-ui, sans-serif !important;
  color: var(--cc-ink);
}

.stApp {
  background: radial-gradient(1200px 700px at 10% -10%, #e3f2ff 0%, transparent 55%),
    radial-gradient(900px 600px at 90% 0%, #dbeafe 0%, transparent 50%),
    linear-gradient(180deg, #fbfdff 0%, var(--cc-bg) 38%, #f3f6fa 100%) !important;
}

[data-testid="stAppViewContainer"] > .main {
  background: transparent !important;
}

section.main > div {
  max-width: 1220px !important;
  margin: 0 auto;
}

div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlockBorderWrapper"],
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
  border: none !important;
}

.block-container {
  padding-top: 0.75rem !important;
  padding-bottom: 3rem !important;
  padding-left: 1.25rem !important;
  padding-right: 1.25rem !important;
}

/* 隐藏 Streamlit 默认顶栏（Deploy / ⋮ 菜单） */
[data-testid="stHeader"],
[data-testid="stToolbar"],
[data-testid="stDecoration"],
header[data-testid="stHeader"] {
  display: none !important;
  height: 0 !important;
  min-height: 0 !important;
  visibility: hidden !important;
}

.stDeployButton,
#MainMenu,
footer[data-testid="stFooter"],
[data-testid="stStatusWidget"] {
  display: none !important;
  visibility: hidden !important;
}

[data-testid="stAppViewContainer"] .main .block-container {
  padding-top: 1.25rem !important;
}

[data-testid="stSidebar"] {
  background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(245,248,252,0.98)) !important;
  border-right: 1px solid var(--cc-line) !important;
}

[data-testid="stSidebar"] .block-container {
  padding-top: 1rem !important;
}

h1, h2, h3 {
  font-weight: 800 !important;
  letter-spacing: 0.02em !important;
  color: var(--cc-ink) !important;
}

/* 顶栏：玻璃胶囊 + 导航链接（st.page_link） */
.cc-nav-shell {
  margin: 0 0 18px 0;
  padding: 10px 14px 10px 18px;
  border-radius: 999px;
  background: var(--cc-surface-strong);
  border: 1px solid rgba(255, 255, 255, 0.65);
  box-shadow: 0 10px 40px rgba(15, 60, 120, 0.08);
  backdrop-filter: blur(22px) saturate(150%);
  -webkit-backdrop-filter: blur(22px) saturate(150%);
}

.cc-nav-brand-title {
  font-weight: 800;
  letter-spacing: 0.06em;
  font-size: 1.05rem;
  line-height: 1.25;
  background: linear-gradient(120deg, var(--cc-blue-3), var(--cc-blue-1));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  margin: 0;
}

.cc-nav-brand-sub {
  font-size: 11px;
  color: var(--cc-ink-soft);
  letter-spacing: 0.12em;
  text-transform: uppercase;
  margin: 2px 0 0 0;
}

section[data-testid="stMain"] a[data-testid^="stPageLink-"] {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 8px 14px !important;
  border-radius: 999px !important;
  font-size: 0.95rem !important;
  font-weight: 600 !important;
  color: var(--cc-ink-soft) !important;
  background: transparent !important;
  border: none !important;
  text-decoration: none !important;
  transition: color 0.2s ease, background 0.2s ease, transform 0.2s ease;
}

section[data-testid="stMain"] a[data-testid^="stPageLink-"]:hover {
  color: var(--cc-ink) !important;
  background: rgba(74, 159, 232, 0.12) !important;
  transform: translateY(-1px);
}

section[data-testid="stMain"] a[data-testid^="stPageLink-"].st-emotion-cache-disabled,
section[data-testid="stMain"] a[data-testid^="stPageLink-"][aria-disabled="true"] {
  color: var(--cc-ink) !important;
  background: rgba(74, 159, 232, 0.14) !important;
}

/* Hero（首页） */
.cc-hero {
  position: relative;
  border-radius: var(--cc-radius-lg);
  overflow: hidden;
  margin-bottom: 22px;
  box-shadow: var(--cc-shadow);
  background: linear-gradient(135deg, rgba(255,255,255,0.55), rgba(227,242,255,0.9));
  border: 1px solid rgba(255,255,255,0.65);
}

.cc-hero__grid {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(0, 0.9fr);
  gap: 0;
}

@media (max-width: 900px) {
  .cc-hero__grid { grid-template-columns: 1fr; }
}

.cc-hero__copy {
  padding: 32px 28px 36px;
}

.cc-hero__eyebrow {
  font-size: 13px;
  font-weight: 700;
  color: var(--cc-blue-3);
  letter-spacing: 0.08em;
  margin: 0 0 10px 0;
}

.cc-hero__title {
  font-size: clamp(1.6rem, 3.2vw, 2.35rem);
  font-weight: 800;
  line-height: 1.2;
  margin: 0 0 12px 0;
  color: var(--cc-ink);
}

.cc-hero__title span {
  background: linear-gradient(120deg, var(--cc-blue-3), var(--cc-blue-1));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
}

.cc-hero__lead {
  margin: 0 0 18px 0;
  color: var(--cc-ink-soft);
  font-size: 0.98rem;
  line-height: 1.65;
}

.cc-hero__chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 20px;
}

.cc-chip {
  font-size: 12px;
  font-weight: 700;
  padding: 6px 12px;
  border-radius: 999px;
  background: rgba(74, 159, 232, 0.12);
  color: var(--cc-blue-3);
  border: 1px solid rgba(74, 159, 232, 0.22);
}

.cc-hero__cta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  margin-bottom: 22px;
}

.cc-btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 10px 18px;
  border-radius: 999px;
  font-weight: 700;
  font-size: 0.9rem;
  color: #fff !important;
  background: linear-gradient(120deg, var(--cc-blue-2), var(--cc-blue-3)) !important;
  box-shadow: 0 14px 34px rgba(47, 107, 204, 0.28);
  text-decoration: none !important;
}

.cc-btn-secondary {
  padding: 10px 16px;
  border-radius: 999px;
  font-weight: 600;
  font-size: 0.88rem;
  color: var(--cc-ink) !important;
  background: rgba(255,255,255,0.45) !important;
  border: 1px solid rgba(15, 40, 70, 0.1) !important;
  text-decoration: none !important;
}

.cc-hero__stats {
  display: flex;
  gap: 18px;
  align-items: center;
  padding: 14px 18px;
  border-radius: var(--cc-radius-md);
  background: var(--cc-surface);
  border: 1px solid rgba(255,255,255,0.55);
  max-width: 360px;
}

.cc-hero__stat-num {
  font-size: 1.35rem;
  font-weight: 800;
  color: var(--cc-blue-3);
}

.cc-hero__stat-label {
  font-size: 12px;
  color: var(--cc-ink-soft);
}

.cc-hero__visual {
  min-height: 260px;
  background-size: cover;
  background-position: center;
}

/* 区块标题 */
.cc-section-head {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 16px;
  margin: 28px 0 14px 0;
}

.cc-kicker {
  font-size: 13px;
  font-weight: 700;
  color: var(--cc-blue-3);
  letter-spacing: 0.06em;
  margin: 0 0 4px 0;
}

.cc-section-title {
  font-size: clamp(1.25rem, 2.2vw, 1.6rem);
  font-weight: 800;
  margin: 0;
  color: var(--cc-ink);
}

.cc-more-link {
  font-size: 14px;
  font-weight: 700;
  color: var(--cc-blue-3) !important;
  text-decoration: none !important;
}

/* 社群卡片（杂志风） */
.cc-magazine {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

@media (max-width: 960px) {
  .cc-magazine { grid-template-columns: repeat(2, minmax(0, 1fr)); }
}
@media (max-width: 600px) {
  .cc-magazine { grid-template-columns: 1fr; }
}

.cc-card {
  border-radius: var(--cc-radius-lg);
  overflow: hidden;
  background: var(--cc-surface);
  border: 1px solid rgba(255, 255, 255, 0.55);
  box-shadow: 0 10px 40px rgba(15, 60, 120, 0.08);
  backdrop-filter: blur(18px) saturate(140%);
}

.cc-card__media {
  aspect-ratio: 16 / 11;
  overflow: hidden;
  background: #e8f0fa;
}

.cc-card__media img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.cc-card__body {
  padding: 14px 16px 16px;
}

.cc-pill {
  display: inline-block;
  font-size: 12px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(74, 159, 232, 0.12);
  color: var(--cc-blue-3);
}

.cc-muted {
  font-size: 13px;
  color: var(--cc-ink-soft);
  margin-left: 8px;
}

.cc-card__title {
  font-size: 1.05rem;
  font-weight: 800;
  margin: 10px 0 6px;
  color: var(--cc-ink);
}

.cc-card__intro {
  font-size: 13px;
  color: var(--cc-ink-soft);
  line-height: 1.5;
  margin: 0;
}

/* 活动条 */
.cc-act-row {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

@media (max-width: 720px) {
  .cc-act-row { grid-template-columns: 1fr; }
}

.cc-act {
  border-radius: var(--cc-radius-md);
  padding: 16px 18px;
  background: var(--cc-surface-strong);
  border: 1px solid rgba(255,255,255,0.65);
  box-shadow: 0 8px 28px rgba(15, 60, 120, 0.06);
}

.cc-act h4 {
  margin: 0 0 6px 0;
  font-size: 1rem;
}

/* 动态流卡片 */
.cc-feed {
  border-radius: var(--cc-radius-md);
  padding: 16px 18px;
  margin-bottom: 12px;
  background: var(--cc-surface-strong);
  border: 1px solid rgba(255,255,255,0.65);
}

.cc-feed__meta {
  font-size: 13px;
  color: var(--cc-ink-soft);
  margin-bottom: 8px;
}

/* 页脚 */
.cc-footer {
  margin-top: 36px;
  padding: 26px 8px 8px;
  border-top: 1px solid var(--cc-line);
  color: var(--cc-ink-soft);
  font-size: 13px;
}

.cc-footer a {
  color: var(--cc-blue-3) !important;
  font-weight: 600;
  margin-right: 14px;
}

/* Streamlit 原生控件微调 */
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
  border-radius: 14px !important;
}

.stButton > button[kind="primary"] {
  border-radius: 999px !important;
  background: linear-gradient(120deg, var(--cc-blue-2), var(--cc-blue-3)) !important;
  border: none !important;
  font-weight: 700 !important;
  box-shadow: 0 10px 26px rgba(47, 107, 204, 0.22) !important;
}

.stButton > button[kind="secondary"] {
  border-radius: 999px !important;
  border: 1px solid rgba(15, 40, 70, 0.1) !important;
  background: rgba(255,255,255,0.5) !important;
}

[data-testid="stExpander"] details {
  border-radius: var(--cc-radius-md) !important;
  border: 1px solid rgba(255,255,255,0.65) !important;
  background: var(--cc-surface) !important;
}

div[data-testid="stMetric"] {
  background: var(--cc-surface-strong);
  padding: 12px 16px;
  border-radius: var(--cc-radius-md);
  border: 1px solid rgba(255,255,255,0.65);
}

/* 顶栏整行玻璃胶囊（首行含品牌标题的横向块） */
div[data-testid="stHorizontalBlock"]:has(p.cc-nav-brand-title) {
  padding: 10px 18px !important;
  border-radius: 999px !important;
  background: var(--cc-surface-strong) !important;
  border: 1px solid rgba(255, 255, 255, 0.65) !important;
  box-shadow: 0 10px 40px rgba(15, 60, 120, 0.08) !important;
  backdrop-filter: blur(22px) saturate(150%);
  -webkit-backdrop-filter: blur(22px) saturate(150%);
  margin-bottom: 18px !important;
}

/* 登录 / 注册 */
.cc-auth-panel {
  max-width: 440px;
  margin: 12px auto 24px;
  padding: 28px 26px;
  border-radius: var(--cc-radius-lg);
  background: var(--cc-surface-strong);
  border: 1px solid rgba(255, 255, 255, 0.65);
  box-shadow: var(--cc-shadow);
}
.cc-auth-title {
  margin: 0 0 8px;
  font-size: clamp(1.35rem, 3vw, 1.75rem);
  font-weight: 900;
  color: var(--cc-ink);
}
.cc-auth-lead {
  margin: 0 0 16px;
  color: var(--cc-ink-soft);
  font-size: 14px;
  line-height: 1.6;
}
.cc-welcome-banner {
  padding: 12px 16px;
  border-radius: var(--cc-radius-md);
  background: rgba(74, 159, 232, 0.1);
  border: 1px solid rgba(74, 159, 232, 0.22);
  margin-bottom: 16px;
}

/* 详情页顶图（社群详情） */
.cc-detail-hero {
  display: grid;
  grid-template-columns: minmax(0, 1.2fr) minmax(0, 1fr);
  gap: 0;
}

.cc-detail-hero .cc-card__media {
  aspect-ratio: 16 / 9;
  min-height: 200px;
  background-size: cover;
  background-position: center;
}

.cc-detail-hero .cc-card__body {
  align-self: center;
  padding: 20px 22px;
}

.cc-detail-poster {
  width: 100%;
  max-height: min(360px, 50vh);
  object-fit: cover;
  border-radius: 16px;
  margin-bottom: 16px;
  display: block;
}

/* ========== 手机 / 窄屏适配 ========== */
@media (max-width: 768px) {
  .block-container {
    padding-left: 0.85rem !important;
    padding-right: 0.85rem !important;
    padding-top: 0.5rem !important;
    padding-bottom: calc(2.5rem + env(safe-area-inset-bottom, 0px)) !important;
    max-width: 100% !important;
  }

  section.main > div {
    max-width: 100% !important;
  }

  .cc-hero__copy {
    padding: 22px 18px 24px;
  }

  .cc-hero__visual {
    min-height: 180px;
  }

  .cc-hero__stats {
    max-width: 100%;
    flex-wrap: wrap;
  }

  .cc-section-head {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
    margin: 22px 0 12px 0;
  }

  .cc-detail-hero {
    grid-template-columns: 1fr;
  }

  .cc-detail-hero .cc-card__body {
    padding: 16px 18px 18px;
  }

  .cc-auth-panel {
    margin: 8px 0 20px;
    padding: 22px 18px;
    max-width: 100%;
  }

  /* 顶栏：品牌 / 导航 / 账户 纵向排列 */
  div[data-testid="stHorizontalBlock"]:has(p.cc-nav-brand-title) {
    flex-direction: column !important;
    align-items: stretch !important;
    gap: 10px !important;
    border-radius: 20px !important;
    padding: 12px 14px !important;
    margin-bottom: 14px !important;
  }

  div[data-testid="stHorizontalBlock"]:has(p.cc-nav-brand-title) > div[data-testid="column"] {
    width: 100% !important;
    min-width: 0 !important;
    flex: 1 1 auto !important;
  }

  .cc-nav-brand-title {
    font-size: 0.98rem !important;
    line-height: 1.3 !important;
  }

  .cc-nav-brand-sub {
    font-size: 10px !important;
    letter-spacing: 0.08em !important;
  }

  /* 主导航链接：横向滑动，避免挤成一团 */
  div[data-testid="stHorizontalBlock"]:has(p.cc-nav-brand-title)
    div[data-testid="column"]:nth-child(2)
    div[data-testid="stHorizontalBlock"] {
    flex-wrap: nowrap !important;
    overflow-x: auto !important;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    gap: 6px !important;
    padding-bottom: 2px;
  }

  div[data-testid="stHorizontalBlock"]:has(p.cc-nav-brand-title)
    div[data-testid="column"]:nth-child(2)
    div[data-testid="stHorizontalBlock"]::-webkit-scrollbar {
    display: none;
  }

  div[data-testid="stHorizontalBlock"]:has(p.cc-nav-brand-title)
    div[data-testid="column"]:nth-child(2)
    div[data-testid="column"] {
    flex: 0 0 auto !important;
    min-width: 0 !important;
    width: auto !important;
  }

  section[data-testid="stMain"] a[data-testid^="stPageLink-"] {
    padding: 10px 14px !important;
    font-size: 0.88rem !important;
    white-space: nowrap;
    min-height: 44px;
  }

  /* 右侧账户区 */
  div[data-testid="stHorizontalBlock"]:has(p.cc-nav-brand-title)
    div[data-testid="column"]:nth-child(3)
    div[data-testid="stHorizontalBlock"] {
    flex-wrap: wrap !important;
    gap: 8px !important;
  }

  div[data-testid="stHorizontalBlock"]:has(p.cc-nav-brand-title)
    div[data-testid="column"]:nth-child(3)
    div[data-testid="column"] {
    flex: 1 1 calc(33.33% - 6px) !important;
    min-width: 72px !important;
  }

  /* 含社群/活动卡片的行 → 单列 */
  section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(.cc-card),
  section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(.cc-act) {
    flex-direction: column !important;
    gap: 12px !important;
  }

  section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(.cc-card) > div[data-testid="column"],
  section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(.cc-act) > div[data-testid="column"] {
    width: 100% !important;
    min-width: 100% !important;
    flex: 1 1 100% !important;
  }

  /* 页脚链接区 */
  section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has([data-testid="stCaptionContainer"]) {
    flex-direction: column !important;
    gap: 10px !important;
  }

  section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has([data-testid="stCaptionContainer"])
    > div[data-testid="column"] {
    width: 100% !important;
    min-width: 100% !important;
  }

  /* Tab 可横向滑动 */
  [data-baseweb="tab-list"],
  [data-testid="stTabs"] [role="tablist"] {
    overflow-x: auto !important;
    flex-wrap: nowrap !important;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
  }

  [data-baseweb="tab-list"]::-webkit-scrollbar,
  [data-testid="stTabs"] [role="tablist"]::-webkit-scrollbar {
    display: none;
  }

  [data-baseweb="tab"] {
    flex: 0 0 auto !important;
    min-height: 44px;
    padding: 10px 14px !important;
    font-size: 0.88rem !important;
  }

  /* 按钮触控区域 */
  .stButton > button {
    min-height: 44px !important;
    padding: 0.55rem 1rem !important;
    font-size: 0.92rem !important;
  }

  [data-testid="stTextInput"] input,
  [data-testid="stTextArea"] textarea {
    font-size: 16px !important; /* 避免 iOS 聚焦时自动放大 */
  }

  [data-testid="stImage"] img {
    max-width: 100% !important;
    height: auto !important;
  }

  .cc-card__title {
    font-size: 1rem;
  }

  .cc-act {
    padding: 14px 16px;
  }

  .cc-feed {
    padding: 14px 16px;
  }
}

@media (max-width: 480px) {
  .cc-nav-brand-title {
    font-size: 0.92rem !important;
  }

  .cc-hero__title {
    font-size: 1.45rem;
  }

  .cc-hero__chips {
    gap: 6px;
  }

  .cc-chip {
    font-size: 11px;
    padding: 5px 10px;
  }

  /* 双按钮行（详情+报名）保持并排但更易点 */
  section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(.stButton)
    > div[data-testid="column"] {
    flex: 1 1 48% !important;
    min-width: 0 !important;
  }
}

/* 平板：社群卡片两列 */
@media (min-width: 769px) and (max-width: 960px) {
  section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(.cc-card) {
    flex-wrap: wrap !important;
  }

  section[data-testid="stMain"] div[data-testid="stHorizontalBlock"]:has(.cc-card) > div[data-testid="column"] {
    flex: 1 1 calc(50% - 8px) !important;
    min-width: calc(50% - 8px) !important;
    max-width: calc(50% - 8px) !important;
  }
}
</style>
"""
    st.html(_CSS.strip())
