"""各页统一初始化：数据库 + 页面配置。"""

from __future__ import annotations

import streamlit as st

from campus_theme import inject_campus_styles
from db import init_db


@st.cache_resource
def ensure_db() -> bool:
    init_db()
    return 3  # 演示数据版本；升级种子后改此数字并重启 Streamlit


def init_page(
    *,
    title: str,
    icon: str = "🎓",
    wide: bool = True,
    sidebar: str = "collapsed",
) -> None:
    ensure_db()
    st.set_page_config(
        page_title=title,
        page_icon=icon,
        layout="wide" if wide else "centered",
        initial_sidebar_state=sidebar,
    )
    inject_campus_styles()
    # 移动端视口与主题色（注入 head，改善手机浏览器缩放与地址栏配色）
    st.html(
        """
        <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
        <meta name="theme-color" content="#f5f8fc">
        <meta name="apple-mobile-web-app-capable" content="yes">
        """,
        unsafe_allow_javascript=False,
    )
