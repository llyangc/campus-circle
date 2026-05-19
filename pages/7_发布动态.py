"""发布动态（需登录 + 已加入社群）。"""

from __future__ import annotations

import streamlit as st

import auth
from bootstrap import init_page
from db import get_community, insert_post, is_member, list_communities
from ui import navigate_community_detail, render_auth_sidebar, render_chrome_header, render_footer

init_page(title="发布动态")

u = auth.require_login(student_only=True, after="pages/7_发布动态.py")
render_chrome_header("post")
render_auth_sidebar()
auth.show_flash()

st.markdown(
    '<div class="cc-section-head"><p class="cc-kicker">发布</p>'
    '<h2 class="cc-section-title">写一条动态</h2></div>',
    unsafe_allow_html=True,
)

rows = [r for r in list_communities(include_pending=False) if is_member(int(r["id"]), u["id"])]
if not rows:
    st.warning("你还未加入任何社群，请先到「社群」页加入后再发布。")
    if st.button("去社群广场", type="primary"):
        st.switch_page("pages/1_社群广场.py")
    render_footer()
    st.stop()

labels = [f"{r['name']}（{r['category']}）" for r in rows]
idx = st.selectbox("发布到社群", range(len(labels)), format_func=lambda i: labels[i])
club_row = rows[idx]
cid = int(club_row["id"])
club = get_community(cid)

body = st.text_area("内容", max_chars=2000, height=160, placeholder="分享此刻…")
if st.button("发布", type="primary"):
    if not body.strip():
        st.warning("请填写内容")
    elif club:
        insert_post(
            cid,
            u["id"],
            u["nick_name"],
            u.get("avatar") or "",
            club["name"],
            body.strip(),
        )
        auth.set_flash("动态已发布", "success")
        navigate_community_detail(cid)

render_footer()
