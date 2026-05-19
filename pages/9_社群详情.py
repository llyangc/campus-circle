"""社群详情：简介 / 公告 / 成员 / 活动 / 动态（对齐 Vue CommunityDetailView 精简版）。"""

from __future__ import annotations

import html as html_lib

import streamlit as st

import auth
from bootstrap import init_page
from db import (
    add_club_member,
    can_manage_club,
    get_community,
    insert_comment,
    insert_post,
    is_member,
    list_club_activities,
    list_club_members,
    list_comments,
    list_posts,
)
from ui import (
    PAGE_COMMUNITIES,
    PAGE_LOGIN,
    PAGE_MANAGE,
    PAGE_POST,
    navigate_activity_detail,
    render_auth_sidebar,
    render_chrome_header,
    render_footer,
)

init_page(title="社群详情")

render_chrome_header("community_detail")
render_auth_sidebar()
auth.show_flash()

cid = st.session_state.get("cc_detail_club_id")
if cid is None:
    st.warning("请从社群广场或首页选择社群。")
    if st.button("去社群广场", type="primary"):
        st.switch_page(PAGE_COMMUNITIES)
    render_footer()
    st.stop()

cid = int(cid)
u = auth.current_user()
club = get_community(cid)
if club is None:
    st.error("社群不存在")
    if st.button("返回社群广场"):
        st.switch_page(PAGE_COMMUNITIES)
    render_footer()
    st.stop()

if club["audit"] != "已通过" and not auth.is_system_admin(u):
    st.warning("该社群未通过审核，师生端仅可预览。")

bc1, bc2 = st.columns([1, 4])
with bc1:
    if st.button("← 社群广场"):
        st.switch_page(PAGE_COMMUNITIES)
with bc2:
    if u and can_manage_club(cid, u["id"]):
        if st.button("管理本社群", type="secondary"):
            st.session_state["cc_manage_club"] = cid
            st.switch_page(PAGE_MANAGE)

cover = (club["cover_url"] or "").strip() or "https://picsum.photos/id/180/900/600"
st.markdown(
    f"""
<div class="cc-card" style="margin-bottom:18px;">
  <div class="cc-detail-hero">
    <div class="cc-card__media" style="background-image:url('{html_lib.escape(cover)}');"></div>
    <div class="cc-card__body">
      <span class="cc-pill">{html_lib.escape(club["category"] or "")}</span>
      <span class="cc-muted">{int(club["member_count"] or 0)} 人</span>
      <div class="cc-card__title" style="font-size:1.45rem;">{html_lib.escape(club["name"] or "")}</div>
      <p class="cc-card__intro">{html_lib.escape(club["intro"] or "暂无简介")}</p>
    </div>
  </div>
</div>
    """,
    unsafe_allow_html=True,
)

if club["audit"] == "已通过":
    if u is None:
        st.caption("登录后可加入社群、评论与发帖。")
        if st.button("登录后加入", type="primary", key="detail_join_login"):
            auth.set_login_redirect("pages/9_社群详情.py")
            st.session_state["cc_detail_club_id"] = cid
            st.switch_page(PAGE_LOGIN)
    elif is_member(cid, u["id"]):
        st.success("你已是本社群成员")
        if st.button("去发布动态", type="primary", key="detail_to_post"):
            st.session_state["cc_pick_club"] = cid
            st.switch_page(PAGE_POST)
    else:
        if st.button("加入社群", type="primary", key="detail_join"):
            if add_club_member(cid, u["id"]):
                auth.set_flash("已加入社群", "success")
            st.rerun()

tab_intro, tab_ann, tab_members, tab_acts, tab_posts = st.tabs(
    ["简介", "公告", "成员", "活动", "动态"]
)

with tab_intro:
    st.markdown(f"**创建时间** {club['created_at'] or '—'}")
    st.markdown(club["intro"] or "暂无简介")
    if club["rules"]:
        st.markdown(f"**群规** {club['rules']}")

with tab_ann:
    ann = (club["announcement"] or "").strip()
    if ann:
        st.info(ann)
        if club["announcement_at"]:
            st.caption(f"更新于 {club['announcement_at']}")
    else:
        st.caption("暂无公告")

with tab_members:
    members = list_club_members(cid)
    if not members:
        st.caption("暂无成员")
    else:
        for m in members:
            role = m["role"] or "member"
            label = "主理人" if role == "owner" else ("管理员" if role == "admin" else "成员")
            st.markdown(f"- **{m['nick_name']}** @{m['user_name']} · {label}")

with tab_acts:
    acts = [a for a in list_club_activities(cid) if a["audit"] == "已通过"]
    if not acts:
        st.caption("暂无已通过审核的活动")
    else:
        for a in acts:
            ac1, ac2 = st.columns([4, 1])
            with ac1:
                st.markdown(f"**{a['title']}** · {a['start_time']} @ {a['location']}")
            with ac2:
                if st.button("详情", key=f"act_{a['id']}", use_container_width=True):
                    navigate_activity_detail(int(a["id"]))

with tab_posts:
    posts = list_posts(cid)
    if not posts:
        st.caption("暂无动态")
    for p in posts:
        body = html_lib.escape(p["content"] or "").replace("\n", "<br/>")
        st.markdown(
            f"""
<div class="cc-feed">
  <div class="cc-feed__meta">{p["created_at"]}</div>
  <strong>{html_lib.escape(p["author"] or "")}</strong>
  <p style="margin:8px 0 0;line-height:1.6;">{body}</p>
</div>
            """,
            unsafe_allow_html=True,
        )
        for cm in list_comments(int(p["id"])):
            st.caption(f"└ {cm['author']}：{cm['content']}")
        if u and club["audit"] == "已通过" and is_member(cid, u["id"]):
            txt = st.text_input(
                "评论", key=f"cmt_{p['id']}", label_visibility="collapsed", placeholder="写评论…"
            )
            if st.button("发送", key=f"btn_{p['id']}"):
                if txt.strip():
                    insert_comment(int(p["id"]), u["id"], u["nick_name"], txt.strip())
                    st.rerun()

    if u and club["audit"] == "已通过" and is_member(cid, u["id"]):
        st.divider()
        body = st.text_area(
            "发布动态", max_chars=2000, label_visibility="collapsed", placeholder="分享此刻…"
        )
        if st.button("发布", type="primary", key="detail_post"):
            if body.strip():
                insert_post(
                    cid,
                    u["id"],
                    u["nick_name"],
                    u.get("avatar") or "",
                    club["name"],
                    body.strip(),
                )
                auth.set_flash("已发布", "success")
                st.rerun()
            else:
                st.warning("请填写内容")

render_footer()
