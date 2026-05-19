"""个人中心（登录后，对齐 Vue /me）。"""

from __future__ import annotations

import html as html_lib

import streamlit as st

import auth
from bootstrap import init_page
from db import list_manageable_clubs, list_user_communities, list_user_enrollments, update_user_bio
from ui import (
    PAGE_MANAGE,
    navigate_activity_detail,
    navigate_community_detail,
    render_auth_sidebar,
    render_chrome_header,
    render_footer,
)

init_page(title="个人中心")

u = auth.require_login(after="pages/6_个人中心.py")
render_chrome_header("profile")
render_auth_sidebar()
auth.show_flash()

nick = html_lib.escape(u["nick_name"])
uname = html_lib.escape(u["user_name"])

st.markdown(
    f'<div class="cc-section-head"><p class="cc-kicker">个人中心</p>'
    f'<h2 class="cc-section-title">你好，{nick}</h2></div>',
    unsafe_allow_html=True,
)

c1, c2 = st.columns([1, 2])
with c1:
    avatar = (u.get("avatar") or "").strip() or "https://picsum.photos/id/1027/240/240"
    st.image(avatar, width=160)
with c2:
    st.markdown(f"**用户名** @{uname}")
    with st.form("bio_form"):
        bio = st.text_area("个人简介", value=u.get("bio") or "", max_chars=500)
        if st.form_submit_button("保存简介"):
            update_user_bio(u["id"], bio.strip())
            u["bio"] = bio.strip()
            st.session_state[auth.SESSION_KEY]["bio"] = bio.strip()
            auth.set_flash("简介已保存", "success")
            st.rerun()
    if st.button("退出登录", type="secondary"):
        auth.logout()
        auth.set_flash("已退出登录", "success")
        st.switch_page(auth.PAGE_HOME)

st.divider()

manageable = list_manageable_clubs(u["id"])
if manageable:
    st.subheader("我管理的社群")
    for c in manageable:
        mc1, mc2 = st.columns([3, 1])
        with mc1:
            st.markdown(f"**{c['name']}**（{c['category']}）")
        with mc2:
            if st.button("管理", key=f"mgr_{c['id']}", use_container_width=True):
                st.session_state["cc_manage_club"] = int(c["id"])
                st.switch_page(PAGE_MANAGE)
    st.page_link(PAGE_MANAGE, label="进入社群与活动管理", icon="⚙️")
    st.divider()

st.subheader("我加入的社群")
clubs = list_user_communities(u["id"])
if not clubs:
    st.caption("尚未加入社群，去「社群」页逛逛吧。")
    if st.button("去社群广场"):
        st.switch_page("pages/1_社群广场.py")
else:
    for c in clubs:
        role = c["role"] or "member"
        label = "主理人" if role == "owner" else ("管理员" if role == "admin" else "成员")
        cc1, cc2 = st.columns([4, 1])
        with cc1:
            st.markdown(f"**{c['name']}**（{c['category']}）· {label}")
        with cc2:
            if st.button("详情", key=f"myclub_{c['id']}", use_container_width=True):
                navigate_community_detail(int(c["id"]))

st.subheader("我的活动报名")
enrolls = list_user_enrollments(u["id"])
if not enrolls:
    st.caption("暂无报名记录")
    if st.button("去看看活动"):
        st.switch_page("pages/2_活动报名.py")
else:
    for e in enrolls:
        ec1, ec2 = st.columns([4, 1])
        with ec1:
            st.markdown(f"**{e['title']}** · {e['start_time']} @ {e['location']}")
        with ec2:
            if st.button("详情", key=f"myact_{e['id']}", use_container_width=True):
                navigate_activity_detail(int(e["id"]))

render_footer()
