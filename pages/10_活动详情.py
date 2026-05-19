"""活动详情：海报、说明、报名（对齐 Vue ActivityDetailView 精简版）。"""

from __future__ import annotations

import html as html_lib

import streamlit as st

import auth
from bootstrap import init_page
from db import (
    count_activity_enrollments,
    enroll_activity,
    get_activity,
    is_activity_enrolled,
)
from ui import (
    PAGE_ACTIVITIES,
    PAGE_LOGIN,
    navigate_community_detail,
    render_auth_sidebar,
    render_chrome_header,
    render_footer,
)

init_page(title="活动详情")

render_chrome_header("activity_detail")
render_auth_sidebar()
auth.show_flash()

aid = st.session_state.get("cc_detail_activity_id")
if aid is None:
    st.warning("请从活动列表或首页选择活动。")
    if st.button("去活动中心", type="primary"):
        st.switch_page(PAGE_ACTIVITIES)
    render_footer()
    st.stop()

aid = int(aid)
u = auth.current_user()
act = get_activity(aid)
if act is None:
    st.error("活动不存在")
    if st.button("返回活动中心"):
        st.switch_page(PAGE_ACTIVITIES)
    render_footer()
    st.stop()

if act["audit"] != "已通过" and not auth.is_system_admin(u):
    st.warning("该活动未通过审核，仅可预览。")

if st.button("← 活动中心"):
    st.switch_page(PAGE_ACTIVITIES)

poster = (act["poster_url"] or "").strip()
if poster:
    st.markdown(
        f'<img class="cc-detail-poster" src="{html_lib.escape(poster)}" alt="">',
        unsafe_allow_html=True,
    )

tag = html_lib.escape(act["tag"] or "活动")
club_name = html_lib.escape(act["club_name"] or "")
st.markdown(
    f'<p class="cc-kicker">{tag} · {club_name}</p>'
    f'<h2 class="cc-section-title">{html_lib.escape(act["title"] or "")}</h2>',
    unsafe_allow_html=True,
)

st.markdown(
    f"**时间** {act['start_time'] or '—'} — {act['end_time'] or '待定'}  \n"
    f"**地点** {act['location'] or '—'}"
)
enrolled_n = count_activity_enrollments(aid)
st.caption(f"已报名 {enrolled_n} 人 · 状态：{act['audit']}")

desc = (act["description"] or "").strip()
if desc:
    st.markdown("#### 活动说明")
    st.markdown(desc)
else:
    st.caption("暂无详细说明")

c1, c2 = st.columns(2)
with c1:
    if st.button(f"查看主办社群 · {act['club_name']}", use_container_width=True):
        navigate_community_detail(int(act["club_id"]))
with c2:
    if act["audit"] == "已通过":
        if u is None:
            if st.button("登录后报名", type="primary", use_container_width=True):
                auth.set_login_redirect("pages/10_活动详情.py")
                st.session_state["cc_detail_activity_id"] = aid
                st.switch_page(PAGE_LOGIN)
        elif is_activity_enrolled(aid, u["id"]):
            st.success("你已报名本场活动")
        else:
            if st.button("立即报名", type="primary", use_container_width=True):
                r = enroll_activity(aid, u["id"])
                if r == "ok":
                    auth.set_flash("报名成功", "success")
                    st.rerun()
                else:
                    st.warning("你已报过名")

render_footer()
