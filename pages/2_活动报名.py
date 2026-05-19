"""已通过活动列表与报名（报名需登录）。"""

from __future__ import annotations

import html as html_lib

import streamlit as st

import auth
from bootstrap import init_page
from db import enroll_activity, list_activities_public
from ui import (
    PAGE_LOGIN,
    navigate_activity_detail,
    render_auth_sidebar,
    render_chrome_header,
    render_footer,
)

init_page(title="活动")

render_chrome_header("activities")
render_auth_sidebar()
auth.show_flash()

st.markdown(
    '<div class="cc-section-head"><div><p class="cc-kicker">活动中心</p>'
    '<h2 class="cc-section-title">把日程排成期待</h2></div></div>',
    unsafe_allow_html=True,
)

u = auth.current_user()
acts = list_activities_public()
if not acts:
    st.info("暂无已通过审核的活动")
    render_footer()
    st.stop()

acols = st.columns(2)
for idx, a in enumerate(acts):
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
  <p style="margin:8px 0 0;font-size:13px;">
    {html_lib.escape(a["start_time"] or "")} — {html_lib.escape(a["end_time"] or "待定")}
    · {html_lib.escape(a["location"] or "")}
  </p>
</div>
            """,
            unsafe_allow_html=True,
        )
        b_detail, b_action = st.columns(2)
        with b_detail:
            if st.button("查看详情", key=f"detail_{a['id']}", use_container_width=True):
                navigate_activity_detail(int(a["id"]))
        with b_action:
            if u:
                if st.button("报名", key=f"en_{a['id']}", use_container_width=True):
                    r = enroll_activity(int(a["id"]), u["id"])
                    if r == "ok":
                        auth.set_flash("报名成功", "success")
                        st.rerun()
                    else:
                        st.warning("你已报过名")
            else:
                if st.button("登录后报名", key=f"login_{a['id']}", use_container_width=True):
                    auth.set_login_redirect("pages/2_活动报名.py")
                    st.switch_page(PAGE_LOGIN)

render_footer()
