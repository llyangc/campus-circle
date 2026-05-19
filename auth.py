"""登录态、跳转与权限（对齐 Vue router meta.requiresAuth）。"""

from __future__ import annotations

import bcrypt
import streamlit as st

from db import fetch_user_by_name

SESSION_KEY = "campus_user"
FLASH_KEY = "campus_flash"
REDIRECT_KEY = "campus_login_redirect"

PAGE_LOGIN = "pages/0_登录.py"
PAGE_HOME = "app.py"
PAGE_PROFILE = "pages/6_个人中心.py"


def _pwd_bytes(password: str) -> bytes:
    return password.encode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(_pwd_bytes(plain), hashed.encode("ascii"))
    except (ValueError, TypeError):
        return False


def set_flash(message: str, kind: str = "success") -> None:
    st.session_state[FLASH_KEY] = (kind, message)


def show_flash() -> None:
    item = st.session_state.pop(FLASH_KEY, None)
    if not item:
        return
    kind, message = item
    if kind == "success":
        st.success(message)
    elif kind == "warning":
        st.warning(message)
    else:
        st.error(message)


def set_login_redirect(target: str) -> None:
    st.session_state[REDIRECT_KEY] = target


def pop_login_redirect(default: str = PAGE_HOME) -> str:
    return st.session_state.pop(REDIRECT_KEY, default)


def login(user_name: str, password: str) -> tuple[bool, str]:
    row = fetch_user_by_name(user_name.strip())
    if row is None:
        return False, "用户不存在或已禁用"
    if not verify_password(password, row["password"]):
        return False, "密码错误"
    st.session_state[SESSION_KEY] = {
        "id": int(row["id"]),
        "user_name": row["user_name"],
        "nick_name": row["nick_name"] or row["user_name"],
        "avatar": row["avatar"] or "",
        "bio": row["bio"] or "",
        "campus_kind": row["campus_kind"],
    }
    return True, "ok"


def logout() -> None:
    st.session_state.pop(SESSION_KEY, None)


def current_user() -> dict | None:
    return st.session_state.get(SESSION_KEY)


def is_logged_in() -> bool:
    return current_user() is not None


def is_system_admin(u: dict | None = None) -> bool:
    u = u if u is not None else current_user()
    return u is not None and u.get("campus_kind") == "SYSTEM_ADMIN"


def is_student(u: dict | None = None) -> bool:
    u = u if u is not None else current_user()
    return u is not None and u.get("campus_kind") == "STUDENT"


def redirect_to_login(message: str | None = None, *, after: str | None = None) -> None:
    if message:
        set_flash(message, "warning")
    if after:
        set_login_redirect(after)
    st.switch_page(PAGE_LOGIN)


def require_login(*, student_only: bool = False, after: str | None = None) -> dict:
    """未登录 → 登录页；student_only 时拒绝运营账号（与 Vue 端提示一致）。"""
    u = current_user()
    if u is None:
        redirect_to_login("请先登录后再继续", after=after or PAGE_HOME)
    if student_only and is_system_admin(u):
        set_flash("请使用师生账号登录；运维管理请使用顶栏「运营」入口。", "warning")
        st.switch_page(PAGE_HOME)
    return u


def after_login_success() -> None:
    u = current_user()
    if u and is_system_admin(u):
        set_flash(
            f"欢迎，{u['nick_name']}！运营请用顶栏「运营」；体验师生功能请用 stu001 登录。",
            "success",
        )
    else:
        set_flash(f"欢迎回来，{u['nick_name']}！", "success")
    st.switch_page(pop_login_redirect(PAGE_HOME))
