"""社群主理人：社群信息维护 + 本社群活动管理（对齐 Vue ClubManageView）。"""

from __future__ import annotations

import streamlit as st

import auth
from bootstrap import init_page
from db import (
    can_manage_club,
    delete_club_activity,
    get_community,
    insert_club_activity,
    list_activity_enrollments,
    list_club_activities,
    list_club_members,
    list_manageable_clubs,
    update_community_info,
)
from ui import PAGE_PROFILE, render_auth_sidebar, render_chrome_header, render_footer

init_page(title="社群与活动管理")

u = auth.require_login(student_only=True, after="pages/8_社群与活动管理.py")
render_chrome_header("manage")
render_auth_sidebar()
auth.show_flash()

manageable = list_manageable_clubs(u["id"])
if not manageable:
    st.warning("你暂无可管理的社群（需为社群主理人 owner/admin）。")
    st.page_link(PAGE_PROFILE, label="返回个人中心")
    render_footer()
    st.stop()

pick = st.session_state.get("cc_manage_club")
default_idx = 0
if pick is not None:
    for i, r in enumerate(manageable):
        if int(r["id"]) == int(pick):
            default_idx = i
            break
    st.session_state.pop("cc_manage_club", None)

labels = [f"{r['name']}（{r['category']}）" for r in manageable]
idx = st.selectbox("选择要管理的社群", range(len(labels)), index=default_idx, format_func=lambda i: labels[i])
cid = int(manageable[idx]["id"])

if not can_manage_club(cid, u["id"]):
    st.error("无管理权限")
    st.stop()

club = get_community(cid)
if club is None:
    st.stop()

st.markdown(
    f'<div class="cc-section-head"><p class="cc-kicker">主理人</p>'
    f'<h2 class="cc-section-title">管理 · {club["name"]}</h2></div>',
    unsafe_allow_html=True,
)

tab_info, tab_members, tab_acts = st.tabs(["社群信息", "成员", "活动管理"])

with tab_info:
    st.caption(f"分类：{club['category']} · 成员约 {club['member_count']} 人")
    with st.form("club_info_form"):
        intro = st.text_area("简介", value=club["intro"] or "", max_chars=500)
        announcement = st.text_area("公告", value=club["announcement"] or "", max_chars=1000)
        if st.form_submit_button("保存", type="primary"):
            update_community_info(cid, intro=intro.strip(), announcement=announcement.strip())
            auth.set_flash("社群信息已更新", "success")
            st.rerun()
    if club["rules"]:
        st.markdown(f"**群规** {club['rules']}")

with tab_members:
    members = list_club_members(cid)
    if not members:
        st.caption("暂无成员")
    else:
        for m in members:
            role = m["role"] or "member"
            muted = "禁言" if int(m["muted"] or 0) else ""
            st.markdown(
                f"- **{m['nick_name']}** (@{m['user_name']}) · `{role}` {muted}"
            )

with tab_acts:
    acts = list_club_activities(cid)
    st.subheader("已有活动")
    if not acts:
        st.caption("暂无活动，可在下方新建。")
    for a in acts:
        with st.expander(f"{a['title']} · {a['start_time']}"):
            st.write(f"地点：{a['location']} · 标签：{a['tag'] or '-'}")
            st.caption(a["description"] or "")
            enrolls = list_activity_enrollments(int(a["id"]))
            st.caption(f"报名人数：{len(enrolls)}")
            for e in enrolls:
                st.text(f"  · {e['nick_name']} (@{e['user_name']}) · {e['created_at']}")
            if st.button("删除活动", key=f"del_act_{a['id']}", type="secondary"):
                delete_club_activity(int(a["id"]), cid)
                auth.set_flash("活动已删除", "success")
                st.rerun()

    st.divider()
    st.subheader("新建活动")
    with st.form("new_act_form"):
        title = st.text_input("标题", placeholder="例如：周末夜跑")
        c1, c2 = st.columns(2)
        with c1:
            start_time = st.text_input("开始时间", placeholder="05-17 14:00")
        with c2:
            end_time = st.text_input("结束时间", placeholder="17:30")
        location = st.text_input("地点", placeholder="操场")
        tag = st.text_input("标签", placeholder="运动")
        description = st.text_area("说明", max_chars=500)
        if st.form_submit_button("创建活动", type="primary"):
            if not title.strip() or not start_time.strip() or not location.strip():
                st.error("请填写标题、开始时间、地点")
            else:
                insert_club_activity(
                    cid,
                    title.strip(),
                    start_time.strip(),
                    end_time.strip(),
                    location.strip(),
                    tag.strip(),
                    description.strip(),
                )
                auth.set_flash("活动已创建", "success")
                st.rerun()

render_footer()
