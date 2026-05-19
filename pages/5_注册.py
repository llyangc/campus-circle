"""注册页：创建师生账号后自动登录并进入首页。"""

from __future__ import annotations

import streamlit as st

import auth
from bootstrap import init_page
from db import register_user
from ui import render_auth_minimal_header

init_page(title="注册", wide=False, sidebar="collapsed")

if auth.is_logged_in():
    st.switch_page(auth.PAGE_HOME)

render_auth_minimal_header()

st.markdown(
    """
<div class="cc-auth-panel">
  <h1 class="cc-auth-title">创建师生账号</h1>
  <p class="cc-auth-lead">注册成功后将自动登录并进入首页。</p>
</div>
    """,
    unsafe_allow_html=True,
)

with st.form("reg_form"):
    user_name = st.text_input("用户名", placeholder="至少 3 个字符")
    nick_name = st.text_input("昵称", placeholder="显示名称")
    password = st.text_input("密码", type="password", placeholder="至少 6 位")
    password2 = st.text_input("确认密码", type="password")
    go = st.form_submit_button("注册并进入", type="primary", use_container_width=True)

if go:
    if password != password2:
        st.error("两次密码不一致")
    else:
        ok, msg = register_user(user_name, password, nick_name)
        if not ok:
            st.error(msg)
        else:
            auth.login(user_name, password)
            auth.set_login_redirect(auth.PAGE_HOME)
            auth.after_login_success()

if st.button("已有账号？去登录", use_container_width=True):
    st.switch_page(auth.PAGE_LOGIN)
