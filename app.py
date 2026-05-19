"""校园兴趣社群 Streamlit 入口：未登录可浏览；登录后展示欢迎与完整动线。"""

from __future__ import annotations

import html as html_lib

import streamlit as st

import auth
from bootstrap import init_page
from db import list_activities_public, list_communities, list_posts
from ui import (
    PAGE_ACTIVITIES,
    PAGE_COMMUNITIES,
    PAGE_LOGIN,
    PAGE_POST,
    navigate_activity_detail,
    navigate_community_detail,
    render_auth_sidebar,
    render_chrome_header,
    render_footer,
)

init_page(title="校园兴趣社群")

render_chrome_header("home")
render_auth_sidebar()
auth.show_flash()

u = auth.current_user()
rows = list_communities(include_pending=auth.is_system_admin(u))
approved = [r for r in rows if r["audit"] == "已通过"]
all_acts = list_activities_public()
acts = all_acts[:6]
n_comm = len(approved)
n_act = len(all_acts)

if u:
    c_w1, c_w2 = st.columns([3, 1])
    with c_w1:
        st.success(f"「{u['nick_name']}」，欢迎回来！可逛社群、报名活动或发布动态。")
    with c_w2:
        if auth.is_student() and st.button("去发布", use_container_width=True):
            st.switch_page(PAGE_POST)
else:
    b1, b2, b3 = st.columns([2, 1, 1])
    with b1:
        st.info("登录后可加入社群、报名活动、发布动态。")
    with b2:
        if st.button("登录", type="primary", use_container_width=True):
            auth.set_login_redirect("app.py")
            st.switch_page(PAGE_LOGIN)
    with b3:
        if st.button("注册", use_container_width=True):
            st.switch_page("pages/5_注册.py")

st.markdown(
    f"""
<div class="cc-hero">
  <div class="cc-hero__grid">
    <div class="cc-hero__copy">
      <p class="cc-hero__eyebrow">校园兴趣 · 真实连接</p>
      <h1 class="cc-hero__title">把同频的人，<span>装进同一片光里</span></h1>
      <p class="cc-hero__lead">发现封面好看的社群、海报感十足的活动，和一条像你一样会生活的动态流。</p>
      <div class="cc-hero__chips">
        <span class="cc-chip">杂志排版</span>
        <span class="cc-chip">瀑布流讨论</span>
        <span class="cc-chip">SQLite 演示</span>
      </div>
      <div class="cc-hero__stats">
        <div><div class="cc-hero__stat-num">{n_comm}+</div><div class="cc-hero__stat-label">可见社群</div></div>
        <div style="width:1px;height:36px;background:rgba(15,40,70,0.12);"></div>
        <div><div class="cc-hero__stat-num">{n_act}</div><div class="cc-hero__stat-label">活动场次</div></div>
      </div>
    </div>
    <div class="cc-hero__visual" style="background-image:url('https://picsum.photos/id/164/1200/900');"></div>
  </div>
</div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="cc-section-head" id="clubs"><div><p class="cc-kicker">热门社群</p>'
    '<h2 class="cc-section-title">封面先说话，兴趣后相遇</h2></div></div>',
    unsafe_allow_html=True,
)

if not approved:
    st.warning("暂无已通过审核的社群。")
else:
    for i in range(0, len(approved), 3):
        chunk = approved[i : i + 3]
        cols = st.columns(len(chunk))
        for j, r in enumerate(chunk):
            with cols[j]:
                cover = (r["cover_url"] or "").strip() or "https://picsum.photos/id/24/640/400"
                nm = html_lib.escape(r["name"] or "")
                cat = html_lib.escape(r["category"] or "")
                intro = html_lib.escape((r["intro"] or "")[:120])
                mc = int(r["member_count"] or 0)
                st.markdown(
                    f"""
<div class="cc-card">
  <div class="cc-card__media"><img src="{html_lib.escape(cover)}" alt=""></div>
  <div class="cc-card__body">
    <span class="cc-pill">{cat}</span><span class="cc-muted">{mc} 人</span>
    <div class="cc-card__title">{nm}</div>
    <p class="cc-card__intro">{intro}</p>
  </div>
</div>
                    """,
                    unsafe_allow_html=True,
                )
                if st.button("查看详情", key=f"home_club_{r['id']}", use_container_width=True):
                    navigate_community_detail(int(r["id"]))
    if st.button("查看全部社群", type="primary"):
        st.switch_page(PAGE_COMMUNITIES)

st.markdown(
    '<div class="cc-section-head" id="events"><div><p class="cc-kicker">热门活动</p>'
    '<h2 class="cc-section-title">把日程排成期待</h2></div></div>',
    unsafe_allow_html=True,
)

if not acts:
    st.caption("暂无活动，稍后在「活动」页查看。")
else:
    acols = st.columns(2)
    for idx, a in enumerate(acts[:6]):
        with acols[idx % 2]:
            poster = ""
            try:
                poster = (a["poster_url"] or "").strip()
            except (KeyError, IndexError):
                pass
            img = (
                f'<img src="{html_lib.escape(poster)}" style="width:100%;border-radius:12px;margin-bottom:10px;aspect-ratio:16/9;object-fit:cover;">'
                if poster
                else ""
            )
            st.markdown(
                f"""
<div class="cc-act">
  {img}
  <h4>{html_lib.escape(a["title"] or "")}</h4>
  <div class="cc-muted">{html_lib.escape(a["club_name"] or "")}</div>
  <p style="margin:8px 0 0;font-size:13px;">{html_lib.escape(a["start_time"] or "")} · {html_lib.escape(a["location"] or "")}</p>
</div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("查看详情", key=f"home_act_{a['id']}", use_container_width=True):
                navigate_activity_detail(int(a["id"]))
    if st.button("查看全部活动"):
        st.switch_page(PAGE_ACTIVITIES)

st.markdown(
    '<div class="cc-section-head"><div><p class="cc-kicker">社群动态</p>'
    '<h2 class="cc-section-title">精选一条，感受温度</h2></div></div>',
    unsafe_allow_html=True,
)

shown = 0
for r in approved[:2]:
    for p in list_posts(int(r["id"]))[:2]:
        if shown >= 4:
            break
        st.markdown(
            f"""
<div class="cc-feed">
  <div class="cc-feed__meta">{html_lib.escape(r["name"] or "")} · {p["created_at"]}</div>
  <strong>{html_lib.escape(p["author"] or "")}</strong>
  <p style="margin:8px 0 0;line-height:1.55;">{html_lib.escape((p["content"] or "")[:280])}</p>
</div>
            """,
            unsafe_allow_html=True,
        )
        shown += 1
    if shown >= 4:
        break

if shown == 0:
    st.caption("暂无动态，请至「社群」页浏览。")

render_footer()
