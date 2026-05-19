"""社群列表；点击进入详情页加入、发帖与评论。"""

from __future__ import annotations

import html as html_lib

import streamlit as st

import auth
from bootstrap import init_page
from db import list_communities
from ui import (
    PAGE_LOGIN,
    navigate_community_detail,
    render_auth_sidebar,
    render_chrome_header,
    render_footer,
)

init_page(title="社群")

render_chrome_header("communities")
render_auth_sidebar()
auth.show_flash()

st.markdown(
    '<div class="cc-section-head"><div><p class="cc-kicker">社群广场</p>'
    '<h2 class="cc-section-title">选一间社群，开始说话</h2></div></div>',
    unsafe_allow_html=True,
)

u = auth.current_user()
rows = list_communities(include_pending=auth.is_system_admin(u))
if not rows:
    st.warning("暂无社群")
    render_footer()
    st.stop()

pick = st.session_state.get("cc_pick_club")
if pick is not None:
    st.session_state.pop("cc_pick_club", None)
    navigate_community_detail(int(pick))

for i in range(0, len(rows), 3):
    chunk = rows[i : i + 3]
    cols = st.columns(len(chunk))
    for j, r in enumerate(chunk):
        with cols[j]:
            cover = (r["cover_url"] or "").strip() or "https://picsum.photos/id/24/640/400"
            nm = html_lib.escape(r["name"] or "")
            cat = html_lib.escape(r["category"] or "")
            intro = html_lib.escape((r["intro"] or "")[:100])
            mc = int(r["member_count"] or 0)
            audit = html_lib.escape(r["audit"] or "")
            st.markdown(
                f"""
<div class="cc-card">
  <div class="cc-card__media"><img src="{html_lib.escape(cover)}" alt=""></div>
  <div class="cc-card__body">
    <span class="cc-pill">{cat}</span><span class="cc-muted">{mc} 人 · {audit}</span>
    <div class="cc-card__title">{nm}</div>
    <p class="cc-card__intro">{intro}</p>
  </div>
</div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("查看详情", key=f"club_{r['id']}", use_container_width=True):
                navigate_community_detail(int(r["id"]))

if u is None:
    st.caption("登录后可加入社群、评论与发帖。")
    if st.button("去登录", type="secondary"):
        auth.set_login_redirect("pages/1_社群广场.py")
        st.switch_page(PAGE_LOGIN)

render_footer()
