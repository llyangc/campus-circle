"""登录页：成功后跳转首页或登录前记录的页面。"""

from __future__ import annotations

import streamlit as st

import auth
from bootstrap import init_page
from ui import render_auth_minimal_header

init_page(title="登录", wide=False, sidebar="collapsed")

if auth.is_logged_in():
    auth.set_flash("您已登录", "success")
    st.switch_page(auth.pop_login_redirect(auth.PAGE_HOME))

render_auth_minimal_header()
auth.show_flash()

st.markdown(
    """
<div class="cc-auth-panel">
  <h1 class="cc-auth-title">校园兴趣社群平台系统</h1>
  <p class="cc-auth-lead">登录后即可加入社群、报名活动、发布动态。</p>
</div>
    """,
    unsafe_allow_html=True,
)

with st.form("login_form", clear_on_submit=False):
    user_name = st.text_input("用户名", placeholder="stu001")
    password = st.text_input("密码", type="password", placeholder="admin123")
    submitted = st.form_submit_button("进入平台", type="primary", use_container_width=True)

if submitted:
    ok, msg = auth.login(user_name, password)
    if ok:
        auth.after_login_success()
    else:
        st.error(msg)

st.caption("演示账号：stu001 / admin123（师生）· admin / admin123（运营）")
c1, c2 = st.columns(2)
with c1:
    if st.button("先逛逛首页（免登录）", use_container_width=True):
        st.switch_page(auth.PAGE_HOME)
with c2:
    if st.button("去注册", use_container_width=True):
        st.switch_page("pages/5_注册.py")
