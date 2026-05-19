"""顶栏导航 + 账户区（对齐 Vue 端 AppHeader 信息架构）。"""

from __future__ import annotations

import streamlit as st

import auth

PAGE_HOME = "app.py"
PAGE_LOGIN = auth.PAGE_LOGIN
PAGE_REGISTER = "pages/5_注册.py"
PAGE_COMMUNITIES = "pages/1_社群广场.py"
PAGE_ACTIVITIES = "pages/2_活动报名.py"
PAGE_ADMIN = "pages/3_运营审核.py"
PAGE_PROFILE = auth.PAGE_PROFILE
PAGE_POST = "pages/7_发布动态.py"
PAGE_MANAGE = "pages/8_社群与活动管理.py"
PAGE_COMMUNITY_DETAIL = "pages/9_社群详情.py"
PAGE_ACTIVITY_DETAIL = "pages/10_活动详情.py"


def navigate_community_detail(club_id: int) -> None:
    st.session_state["cc_detail_club_id"] = int(club_id)
    st.switch_page(PAGE_COMMUNITY_DETAIL)


def navigate_activity_detail(activity_id: int) -> None:
    st.session_state["cc_detail_activity_id"] = int(activity_id)
    st.switch_page(PAGE_ACTIVITY_DETAIL)


def render_auth_minimal_header() -> None:
    """登录/注册页顶栏：仅品牌 + 回首页。"""
    c1, c2 = st.columns([3, 1], gap="small")
    with c1:
        st.markdown(
            '<p class="cc-nav-brand-title">校园兴趣社群</p>'
            '<p class="cc-nav-brand-sub">Campus Circle</p>',
            unsafe_allow_html=True,
        )
    with c2:
        if st.button("回首页", use_container_width=True):
            st.switch_page(PAGE_HOME)


def render_chrome_header(active: str) -> None:
    """active: home | communities | activities | admin | profile | post | manage"""
    c_brand, c_links, c_actions = st.columns([2.15, 3.55, 2.3], gap="small")

    with c_brand:
        st.markdown(
            '<p class="cc-nav-brand-title">校园兴趣社群</p>'
            '<p class="cc-nav-brand-sub">Campus Circle · 师生端</p>',
            unsafe_allow_html=True,
        )

    with c_links:
        u_adm = auth.is_system_admin()
        nav_active = {
            "community_detail": "communities",
            "activity_detail": "activities",
        }.get(active, active)
        n = 4 if u_adm else 3
        gs = st.columns(n, gap="small")
        items = [
            ("home", PAGE_HOME, "首页"),
            ("communities", PAGE_COMMUNITIES, "社群"),
            ("activities", PAGE_ACTIVITIES, "活动"),
        ]
        if u_adm:
            items.append(("admin", PAGE_ADMIN, "运营"))
        for i, (key, path, label) in enumerate(items):
            with gs[i]:
                st.page_link(path, label=label, disabled=nav_active == key)

    with c_actions:
        a1, a2, a3 = st.columns([1.0, 1.0, 1.0], gap="small")
        u = auth.current_user()
        with a1:
            if u:
                st.page_link(PAGE_PROFILE, label="我的", disabled=active == "profile")
            else:
                st.page_link(PAGE_LOGIN, label="登录", disabled=False)
        with a2:
            if u:
                with st.popover(u["nick_name"][:6], use_container_width=True):
                    st.caption(f"@{u['user_name']}")
                    st.page_link(PAGE_PROFILE, label="个人中心")
                    if st.button("退出", key="nav_logout", use_container_width=True):
                        auth.logout()
                        auth.set_flash("已退出登录", "success")
                        st.switch_page(PAGE_HOME)
            else:
                st.page_link(PAGE_REGISTER, label="注册", disabled=False)
        with a3:
            if u and auth.is_student():
                st.page_link(PAGE_POST, label="发布", disabled=active == "post")
            elif u:
                st.page_link(PAGE_ADMIN, label="运营台", disabled=active == "admin")
            else:
                st.page_link(PAGE_LOGIN, label="发布", disabled=False)


def render_footer() -> None:
    st.divider()
    r1, r2 = st.columns([1.35, 1])
    with r1:
        st.caption("校园兴趣社群平台系统 · 校园兴趣社群")
    with r2:
        lf1, lf2, lf3 = st.columns(3)
        with lf1:
            st.page_link(PAGE_COMMUNITIES, label="社群")
        with lf2:
            st.page_link(PAGE_ACTIVITIES, label="活动")
        with lf3:
            if auth.is_logged_in():
                st.page_link(PAGE_PROFILE, label="我的")
            else:
                st.page_link(PAGE_LOGIN, label="登录")
    st.caption("© Campus Circle · Streamlit 演示端")


def render_auth_sidebar() -> None:
    with st.sidebar:
        u = auth.current_user()
        if u:
            st.success(f"已登录：{u['nick_name']}")
        else:
            st.info("未登录：可浏览首页/社群/活动；发帖与报名需登录。")
            if st.button("去登录", use_container_width=True):
                auth.set_login_redirect(PAGE_HOME)
                st.switch_page(PAGE_LOGIN)
        st.divider()
        st.markdown("##### 快捷入口")
        st.page_link(PAGE_COMMUNITIES, label="社群广场")
        st.page_link(PAGE_ACTIVITIES, label="活动报名")
        if auth.is_logged_in() and auth.is_student():
            st.page_link(PAGE_POST, label="发布动态")
            from db import list_manageable_clubs

            u = auth.current_user()
            if u and list_manageable_clubs(u["id"]):
                st.page_link(PAGE_MANAGE, label="社群/活动管理")
        if auth.is_system_admin():
            st.page_link(PAGE_ADMIN, label="运营审核", icon="🛡️")
