"""待审核社群（仅运营账号）。"""

from __future__ import annotations

import streamlit as st

import auth
from bootstrap import init_page
from db import list_pending_communities, set_community_audit
from ui import PAGE_LOGIN, render_auth_sidebar, render_chrome_header, render_footer

init_page(title="运营审核")

u = auth.current_user()
if u is None:
    auth.redirect_to_login("请先使用运营账号登录", after="pages/3_运营审核.py")
if not auth.is_system_admin(u):
    st.switch_page("app.py")

render_chrome_header("admin")
render_auth_sidebar()
auth.show_flash()

st.markdown(
    '<div class="cc-section-head"><div><p class="cc-kicker">运营</p>'
    '<h2 class="cc-section-title">待审核社群</h2></div></div>',
    unsafe_allow_html=True,
)

pending = list_pending_communities()
if not pending:
    st.success("当前没有待审核社群")
    render_footer()
    st.stop()

for row in pending:
    with st.container(border=True):
        st.subheader(row["name"])
        st.write(row["intro"] or "无简介")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("通过", key=f"ok_{row['id']}", type="primary"):
                set_community_audit(int(row["id"]), "已通过")
                auth.set_flash("已通过审核", "success")
                st.rerun()
        with c2:
            if st.button("拒绝", key=f"no_{row['id']}"):
                set_community_audit(int(row["id"]), "已拒绝")
                auth.set_flash("已拒绝", "success")
                st.rerun()

render_footer()
