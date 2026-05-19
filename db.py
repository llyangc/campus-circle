"""SQLite 存储：校园 Streamlit 轻量模型。"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path

# 密码均为 admin123（由 Python bcrypt 生成；）
_DEMO_BCRYPT = b"$2b$10$sllzS8/AmOHQl2LKpY9ku./ErN/DG5EwWv1DYujFma54l7scUTh0K"


def get_db_path() -> Path:
    root = Path(__file__).resolve().parent
    data = root / "data"
    data.mkdir(parents=True, exist_ok=True)
    return data / "app.db"


@contextmanager
def get_conn():
    path = get_db_path()
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        c = conn.cursor()
        c.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS app_user (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_name TEXT NOT NULL UNIQUE,
              password TEXT NOT NULL,
              nick_name TEXT NOT NULL DEFAULT '',
              avatar TEXT DEFAULT '',
              bio TEXT DEFAULT '',
              status TEXT NOT NULL DEFAULT '正常',
              campus_kind TEXT NOT NULL DEFAULT 'STUDENT'
            );

            CREATE TABLE IF NOT EXISTS community (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              owner_user_id INTEGER NOT NULL DEFAULT 0,
              name TEXT NOT NULL,
              category TEXT NOT NULL,
              intro TEXT DEFAULT '',
              member_count INTEGER NOT NULL DEFAULT 0,
              cover_url TEXT DEFAULT '',
              announcement TEXT DEFAULT '',
              announcement_at TEXT,
              rules TEXT DEFAULT '',
              audit TEXT NOT NULL DEFAULT '待审核',
              created_at TEXT DEFAULT (datetime('now','localtime'))
            );

            CREATE TABLE IF NOT EXISTS club_member (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              club_id INTEGER NOT NULL,
              user_id INTEGER NOT NULL,
              role TEXT NOT NULL DEFAULT 'member',
              muted INTEGER NOT NULL DEFAULT 0,
              UNIQUE(club_id, user_id)
            );

            CREATE TABLE IF NOT EXISTS post (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              club_id INTEGER NOT NULL,
              author_user_id INTEGER,
              author TEXT NOT NULL,
              avatar_url TEXT DEFAULT '',
              club_name TEXT DEFAULT '',
              content TEXT NOT NULL,
              likes INTEGER NOT NULL DEFAULT 0,
              comments INTEGER NOT NULL DEFAULT 0,
              created_at TEXT DEFAULT (datetime('now','localtime'))
            );

            CREATE TABLE IF NOT EXISTS comment (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              post_id INTEGER NOT NULL,
              author_user_id INTEGER,
              author TEXT NOT NULL,
              content TEXT NOT NULL,
              parent_id INTEGER,
              created_at TEXT DEFAULT (datetime('now','localtime'))
            );

            CREATE TABLE IF NOT EXISTS activity (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              club_id INTEGER NOT NULL,
              title TEXT NOT NULL,
              start_time TEXT NOT NULL,
              end_time TEXT DEFAULT '',
              location TEXT NOT NULL,
              tag TEXT DEFAULT '',
              description TEXT DEFAULT '',
              audit TEXT NOT NULL DEFAULT '待审核',
              created_at TEXT DEFAULT (datetime('now','localtime'))
            );

            CREATE TABLE IF NOT EXISTS activity_enroll (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              activity_id INTEGER NOT NULL,
              user_id INTEGER NOT NULL,
              created_at TEXT DEFAULT (datetime('now','localtime')),
              UNIQUE(activity_id, user_id)
            );

            CREATE TABLE IF NOT EXISTS app_meta (
              key TEXT PRIMARY KEY,
              value TEXT NOT NULL
            );
            """
        )
        _schema_patch(c)
        row = c.execute("SELECT COUNT(*) FROM app_user").fetchone()
        if row and row[0] == 0:
            _seed(c)
            c.execute(
                "INSERT OR REPLACE INTO app_meta (key, value) VALUES ('demo_seed_version', '2')"
            )
        else:
            _patch_demo_if_sparse(c)


def _schema_patch(c: sqlite3.Cursor) -> None:
    cols = {r[1] for r in c.execute("PRAGMA table_info(activity)").fetchall()}
    if "poster_url" not in cols:
        c.execute("ALTER TABLE activity ADD COLUMN poster_url TEXT DEFAULT ''")


def _patch_demo_if_sparse(c: sqlite3.Cursor) -> None:
    """旧库社群过少时补全演示数据（不删已有注册用户）。"""
    ver = c.execute(
        "SELECT value FROM app_meta WHERE key='demo_seed_version'"
    ).fetchone()
    n = c.execute("SELECT COUNT(*) FROM community").fetchone()[0]
    if ver and ver[0] == "2" and n >= 10:
        return
    _seed_users(c)
    _seed_communities_and_content(c)
    c.execute(
        "INSERT OR REPLACE INTO app_meta (key, value) VALUES ('demo_seed_version', '2')"
    )


def _user_id(c: sqlite3.Cursor, user_name: str) -> int | None:
    r = c.execute("SELECT id FROM app_user WHERE user_name=?", (user_name,)).fetchone()
    return int(r[0]) if r else None


def _club_id(c: sqlite3.Cursor, name: str) -> int | None:
    r = c.execute("SELECT id FROM community WHERE name=?", (name,)).fetchone()
    return int(r[0]) if r else None


def _seed_users(c: sqlite3.Cursor) -> None:
    pwd = _DEMO_BCRYPT.decode("ascii")
    users = [
        ("stu001", "阿梨", "https://picsum.photos/id/1027/240/240", "把兴趣过成日常。", "STUDENT"),
        ("stu002", "小北", "https://picsum.photos/id/64/240/240", "夜跑爱好者", "STUDENT"),
        ("stu003", "阿夏", "https://picsum.photos/id/65/240/240", "手帐与咖啡", "STUDENT"),
        ("stu004", "老周", "https://picsum.photos/id/91/240/240", "独立音乐 digging", "STUDENT"),
        ("stu005", "橙子", "https://picsum.photos/id/338/240/240", "徒步与建筑摄影", "STUDENT"),
        ("stu006", "Mia", "https://picsum.photos/id/836/240/240", "辩论队", "STUDENT"),
        ("stu007", "K", "https://picsum.photos/id/1005/240/240", "电竞社交", "STUDENT"),
        ("stu008", "阿树", "https://picsum.photos/id/1003/240/240", "自习打卡", "STUDENT"),
        ("admin", "运营演示", "https://picsum.photos/id/1000/240/240", "平台运营账号", "SYSTEM_ADMIN"),
    ]
    for uname, nick, av, bio, kind in users:
        if c.execute("SELECT 1 FROM app_user WHERE user_name=?", (uname,)).fetchone():
            continue
        c.execute(
            """
            INSERT INTO app_user (user_name, password, nick_name, avatar, bio, campus_kind)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (uname, pwd, nick, av, bio, kind),
        )


def _seed_communities_and_content(c: sqlite3.Cursor) -> None:
    """社群 / 成员 / 动态 / 活动 / 报名（按名称幂等插入）。"""
    communities = [
        ("胶片与暗房", "stu001", "影像", "胶片拍摄、暗房冲洗与校园影展。", 324,
         "https://picsum.photos/id/180/900/1200", "本周三晚暗房分享会，新人带护目镜。", "尊重差异，禁止攻击", "已通过"),
        ("夜跑补给站", "stu002", "运动", "每周二四夜跑，配速分组，跑后拉伸。", 513,
         "https://picsum.photos/id/177/900/1200", "周四集合点在东门，雨天改体育馆。", "注意热身与补水", "已通过"),
        ("独立音乐客厅", "stu001", "音乐", "小众专辑试听、校园原创、周末不插电。", 305,
         "https://picsum.photos/id/145/900/1300", "周五晚开放麦报名中。", "尊重版权，禁商业拉群", "已通过"),
        ("咖啡感官实验室", "stu003", "美食", "杯测入门、豆子团购、拉花互助。", 341,
         "https://picsum.photos/id/225/900/1150", "本周杯测豆单已更新。", "禁止硬广", "已通过"),
        ("城市徒步计划", "stu005", "户外", "周末轻徒步、建筑观察、摄影打卡。", 198,
         "https://picsum.photos/id/164/900/1250", "周日集合时间见置顶。", "量力而行", "已通过"),
        ("自习室联盟", "stu008", "学习", "期末周互助、资料共享、番茄钟打卡。", 412,
         "https://picsum.photos/id/24/900/1100", "静音区规则请遵守。", "保持安静", "已通过"),
        ("滑板公园", "stu002", "运动", "平地招、道具线、护具互助。", 156,
         "https://picsum.photos/id/399/900/1200", "雨天改室内体育馆。", "护具必戴", "已通过"),
        ("手帐与文具坑", "stu003", "生活美学", "拼贴灵感、纸张测评、同城换物。", 267,
         "https://picsum.photos/id/119/900/1000", "换物请先私信。", "诚信交换", "已通过"),
        ("辩论与演讲", "stu006", "学习", "校赛备赛、即兴表达训练。", 89,
         "https://picsum.photos/id/180/900/1000", "本周辩题公示。", "对事不对人", "已通过"),
        ("电竞社交局", "stu007", "科技", "开黑组队、观赛、线下水友赛。", 278,
         "https://picsum.photos/id/3/900/1200", "文明游戏公约。", "拒绝辱骂", "已通过"),
        ("胶片新人社", "stu004", "影像", "面向零基础同学的胶片入门。", 45,
         "https://picsum.photos/id/250/900/1200", "欢迎投稿样片。", "友善交流", "已通过"),
        ("待审摄影社", "stu001", "影像", "新社群待审核演示。", 0,
         "https://picsum.photos/id/348/900/1200", "", "遵守校规", "待审核"),
        ("校园动漫同好会", "stu007", "生活美学", "番剧讨论、同人展组团。", 0,
         "https://picsum.photos/id/452/900/1200", "", "禁剧透", "待审核"),
    ]
    for name, owner, cat, intro, mc, cover, ann, rules, audit in communities:
        if _club_id(c, name):
            continue
        oid = _user_id(c, owner) or 1
        c.execute(
            """
            INSERT INTO community (owner_user_id, name, category, intro, member_count,
              cover_url, announcement, rules, audit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (oid, name, cat, intro, mc, cover, ann, rules, audit),
        )
        cid = c.execute("SELECT last_insert_rowid()").fetchone()[0]
        c.execute(
            "INSERT OR IGNORE INTO club_member (club_id, user_id, role) VALUES (?, ?, 'owner')",
            (cid, oid),
        )

    members_extra = [
        ("胶片与暗房", "stu003", "member"),
        ("胶片与暗房", "stu004", "member"),
        ("夜跑补给站", "stu001", "member"),
        ("夜跑补给站", "stu005", "member"),
        ("独立音乐客厅", "stu002", "member"),
        ("独立音乐客厅", "stu004", "member"),
        ("咖啡感官实验室", "stu001", "member"),
        ("咖啡感官实验室", "stu005", "member"),
        ("城市徒步计划", "stu001", "member"),
        ("城市徒步计划", "stu005", "member"),
        ("自习室联盟", "stu001", "member"),
        ("自习室联盟", "stu006", "member"),
        ("滑板公园", "stu007", "member"),
        ("手帐与文具坑", "stu006", "member"),
        ("辩论与演讲", "stu008", "member"),
        ("电竞社交局", "stu002", "member"),
        ("电竞社交局", "stu004", "member"),
    ]
    for cname, uname, role in members_extra:
        cid, uid = _club_id(c, cname), _user_id(c, uname)
        if cid and uid:
            c.execute(
                "INSERT OR IGNORE INTO club_member (club_id, user_id, role) VALUES (?, ?, ?)",
                (cid, uid, role),
            )

    posts = [
        ("胶片与暗房", "stu001", "今天试了新胶卷，颗粒感很喜欢。", 12, 2),
        ("胶片与暗房", "stu001", "暗房安全须知整理好了，新人先看置顶。", 28, 5),
        ("夜跑补给站", "stu002", "配速分组表更新，跟不上的别硬跟。", 45, 8),
        ("独立音乐客厅", "stu004", "这张专辑封面太美了，推荐一起听。", 67, 4),
        ("咖啡感官实验室", "stu003", "第一次杯测笔记分享，酸质明亮。", 33, 6),
        ("城市徒步计划", "stu005", "这条路线树荫多，夏天友好。", 19, 2),
        ("自习室联盟", "stu008", "番茄钟 4 轮结束，去喝水。", 12, 3),
        ("滑板公园", "stu002", "Ollie 终于过两立了！", 88, 11),
        ("手帐与文具坑", "stu003", "新到的和纸胶带试贴。", 41, 5),
        ("辩论与演讲", "stu006", "立论框架模板放资料区了。", 22, 4),
        ("电竞社交局", "stu007", "今晚友谊赛缺辅助，来的滴滴。", 103, 15),
        ("胶片新人社", "stu004", "第一次拍人像，求点评。", 8, 1),
    ]
    avatars = {
        "stu001": "https://picsum.photos/id/1027/120/120",
        "stu002": "https://picsum.photos/id/64/120/120",
        "stu003": "https://picsum.photos/id/65/120/120",
        "stu004": "https://picsum.photos/id/91/120/120",
        "stu005": "https://picsum.photos/id/338/120/120",
        "stu006": "https://picsum.photos/id/836/120/120",
        "stu007": "https://picsum.photos/id/1005/120/120",
        "stu008": "https://picsum.photos/id/1003/120/120",
    }
    for cname, author_u, content, likes, comments in posts:
        cid = _club_id(c, cname)
        uid = _user_id(c, author_u)
        if not cid or not uid:
            continue
        if c.execute(
            "SELECT 1 FROM post WHERE club_id=? AND author_user_id=? AND content=?",
            (cid, uid, content),
        ).fetchone():
            continue
        nick = c.execute("SELECT nick_name FROM app_user WHERE id=?", (uid,)).fetchone()[0]
        c.execute(
            """
            INSERT INTO post (club_id, author_user_id, author, avatar_url, club_name,
              content, likes, comments)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (cid, uid, nick, avatars.get(author_u, ""), cname, content, likes, comments),
        )

    activities = [
        ("夜跑补给站", "周末夜跑", "05-17 14:00", "17:30", "操场", "运动", "配速训练+拉伸",
         "https://picsum.photos/id/1074/640/400"),
        ("胶片与暗房", "暗房冲洗工作坊", "06-01 14:00", "17:30", "创客中心 B102", "影像", "胶片冲洗实操与答疑",
         "https://picsum.photos/id/1060/640/900"),
        ("独立音乐客厅", "独立音乐开放麦", "06-02 19:00", "21:00", "小剧场", "音乐", "原创与翻唱均可报名",
         "https://picsum.photos/id/452/640/900"),
        ("咖啡感官实验室", "咖啡杯测入门", "06-03 15:00", "16:30", "咖啡角", "美食", "三款豆子横向对比",
         "https://picsum.photos/id/431/640/900"),
        ("城市徒步计划", "城市轻徒步", "06-07 09:00", "12:00", "地铁 A 口", "户外", "约 8km，自备饮水",
         "https://picsum.photos/id/164/640/900"),
        ("自习室联盟", "期末自习马拉松", "06-10 08:00", "22:00", "图书馆三楼", "学习", "静音打卡，番茄钟互助",
         "https://picsum.photos/id/24/640/900"),
        ("滑板公园", "滑板新人护具体验", "06-05 16:00", "18:00", "体育馆南门", "运动", "护具试戴与平地基础",
         "https://picsum.photos/id/399/640/900"),
        ("电竞社交局", "水友赛观赛夜", "06-06 20:00", "23:00", "电竞馆", "科技", "大屏观赛+轻食",
         "https://picsum.photos/id/3/640/900"),
        ("辩论与演讲", "即兴演讲夜", "06-08 19:00", "21:00", "教学楼 A201", "学习", "1 分钟即兴 + 点评",
         "https://picsum.photos/id/180/640/900"),
        ("手帐与文具坑", "和纸胶带交换局", "06-09 15:00", "17:00", "学生活动中心", "生活美学", "带 3 款以上来换",
         "https://picsum.photos/id/119/640/900"),
        ("胶片新人社", "校园扫街团", "06-11 09:00", "12:00", "南门集合", "影像", "胶片/数码均可",
         "https://picsum.photos/id/250/640/900"),
        ("咖啡感官实验室", "拉花体验课", "06-12 14:00", "16:00", "咖啡角", "美食", "限量 20 人",
         "https://picsum.photos/id/225/640/900"),
    ]
    for cname, title, st, et, loc, tag, desc, poster in activities:
        cid = _club_id(c, cname)
        if not cid:
            continue
        if c.execute(
            "SELECT 1 FROM activity WHERE club_id=? AND title=?", (cid, title)
        ).fetchone():
            c.execute(
                "UPDATE activity SET poster_url=? WHERE club_id=? AND title=? AND (poster_url IS NULL OR poster_url='')",
                (poster, cid, title),
            )
            continue
        c.execute(
            """
            INSERT INTO activity (club_id, title, start_time, end_time, location, tag, description, audit, poster_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, '已通过', ?)
            """,
            (cid, title, st, et, loc, tag, desc, poster),
        )

    enroll_pairs = [
        ("周末夜跑", "stu001"),
        ("独立音乐开放麦", "stu001"),
        ("咖啡杯测入门", "stu002"),
        ("城市轻徒步", "stu005"),
        ("期末自习马拉松", "stu008"),
        ("水友赛观赛夜", "stu007"),
        ("暗房冲洗工作坊", "stu003"),
        ("即兴演讲夜", "stu006"),
    ]
    for title, uname in enroll_pairs:
        uid = _user_id(c, uname)
        if not uid:
            continue
        aid = c.execute("SELECT id FROM activity WHERE title=?", (title,)).fetchone()
        if not aid:
            continue
        c.execute(
            "INSERT OR IGNORE INTO activity_enroll (activity_id, user_id) VALUES (?, ?)",
            (int(aid[0]), uid),
        )


def _seed(c: sqlite3.Cursor) -> None:
    _seed_users(c)
    _seed_communities_and_content(c)


def register_user(user_name: str, password: str, nick_name: str) -> tuple[bool, str]:
    import bcrypt

    name = user_name.strip()
    if not name or len(name) < 3:
        return False, "用户名至少 3 个字符"
    if len(password) < 6:
        return False, "密码至少 6 位"
    if fetch_user_by_name(name):
        return False, "用户名已存在"
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=10)).decode("ascii")
    nick = (nick_name or name).strip()[:64]
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO app_user (user_name, password, nick_name, avatar, bio, campus_kind)
            VALUES (?, ?, ?, '', '', 'STUDENT')
            """,
            (name, hashed, nick),
        )
    return True, "ok"


def get_user_by_id(user_id: int) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM app_user WHERE id = ?", (user_id,)).fetchone()


def list_user_communities(user_id: int) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return list(
            conn.execute(
                """
                SELECT c.*, m.role FROM community c
                JOIN club_member m ON m.club_id = c.id
                WHERE m.user_id = ? AND c.audit = '已通过'
                ORDER BY c.id
                """,
                (user_id,),
            ).fetchall()
        )


def list_user_enrollments(user_id: int) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return list(
            conn.execute(
                """
                SELECT a.id, a.title, a.start_time, a.location, e.created_at
                FROM activity_enroll e
                JOIN activity a ON a.id = e.activity_id
                WHERE e.user_id = ?
                ORDER BY e.id DESC
                """,
                (user_id,),
            ).fetchall()
        )


def fetch_user_by_name(user_name: str) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute(
            "SELECT * FROM app_user WHERE user_name = ? AND status = '正常'",
            (user_name,),
        ).fetchone()


def list_communities(*, include_pending: bool) -> list[sqlite3.Row]:
    with get_conn() as conn:
        if include_pending:
            q = "SELECT * FROM community ORDER BY id"
        else:
            q = "SELECT * FROM community WHERE audit = '已通过' ORDER BY id"
        return list(conn.execute(q).fetchall())


def list_pending_communities() -> list[sqlite3.Row]:
    with get_conn() as conn:
        return list(
            conn.execute(
                "SELECT * FROM community WHERE audit = '待审核' ORDER BY id"
            ).fetchall()
        )


def set_community_audit(community_id: int, audit: str) -> None:
    with get_conn() as conn:
        conn.execute(
            "UPDATE community SET audit = ? WHERE id = ?",
            (audit, community_id),
        )


def get_community(cid: int) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute("SELECT * FROM community WHERE id = ?", (cid,)).fetchone()


def is_member(club_id: int, user_id: int) -> bool:
    with get_conn() as conn:
        r = conn.execute(
            "SELECT 1 FROM club_member WHERE club_id = ? AND user_id = ?",
            (club_id, user_id),
        ).fetchone()
        return r is not None


def add_club_member(club_id: int, user_id: int) -> bool:
    """加入社群；若已加入则返回 False。"""
    with get_conn() as conn:
        if conn.execute(
            "SELECT 1 FROM club_member WHERE club_id = ? AND user_id = ?",
            (club_id, user_id),
        ).fetchone():
            return False
        conn.execute(
            "INSERT INTO club_member (club_id, user_id, role) VALUES (?, ?, 'member')",
            (club_id, user_id),
        )
        conn.execute(
            "UPDATE community SET member_count = member_count + 1 WHERE id = ?",
            (club_id,),
        )
        return True


def list_posts(club_id: int) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return list(
            conn.execute(
                "SELECT * FROM post WHERE club_id = ? ORDER BY id DESC",
                (club_id,),
            ).fetchall()
        )


def insert_post(
    club_id: int,
    author_user_id: int,
    author: str,
    avatar_url: str,
    club_name: str,
    content: str,
) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO post (club_id, author_user_id, author, avatar_url, club_name, content)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (club_id, author_user_id, author, avatar_url, club_name, content),
        )


def list_comments(post_id: int) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return list(
            conn.execute(
                "SELECT * FROM comment WHERE post_id = ? ORDER BY id",
                (post_id,),
            ).fetchall()
        )


def insert_comment(
    post_id: int,
    author_user_id: int | None,
    author: str,
    content: str,
) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO comment (post_id, author_user_id, author, content)
            VALUES (?, ?, ?, ?)
            """,
            (post_id, author_user_id, author, content),
        )
        conn.execute(
            "UPDATE post SET comments = comments + 1 WHERE id = ?",
            (post_id,),
        )


def list_activities_public() -> list[sqlite3.Row]:
    with get_conn() as conn:
        return list(
            conn.execute(
                """
                SELECT a.*, c.name AS club_name FROM activity a
                JOIN community c ON c.id = a.club_id
                WHERE a.audit = '已通过' ORDER BY a.id DESC
                """
            ).fetchall()
        )


def get_activity(activity_id: int) -> sqlite3.Row | None:
    with get_conn() as conn:
        return conn.execute(
            """
            SELECT a.*, c.name AS club_name FROM activity a
            JOIN community c ON c.id = a.club_id
            WHERE a.id = ?
            """,
            (activity_id,),
        ).fetchone()


def is_activity_enrolled(activity_id: int, user_id: int) -> bool:
    with get_conn() as conn:
        r = conn.execute(
            "SELECT 1 FROM activity_enroll WHERE activity_id = ? AND user_id = ?",
            (activity_id, user_id),
        ).fetchone()
        return r is not None


def count_activity_enrollments(activity_id: int) -> int:
    with get_conn() as conn:
        r = conn.execute(
            "SELECT COUNT(*) FROM activity_enroll WHERE activity_id = ?",
            (activity_id,),
        ).fetchone()
        return int(r[0]) if r else 0


def enroll_activity(activity_id: int, user_id: int) -> str:
    with get_conn() as conn:
        try:
            conn.execute(
                """
                INSERT INTO activity_enroll (activity_id, user_id)
                VALUES (?, ?)
                """,
                (activity_id, user_id),
            )
            return "ok"
        except sqlite3.IntegrityError:
            return "dup"


def update_user_bio(user_id: int, bio: str) -> None:
    with get_conn() as conn:
        conn.execute("UPDATE app_user SET bio = ? WHERE id = ?", (bio[:500], user_id))


def get_member_role(club_id: int, user_id: int) -> str | None:
    with get_conn() as conn:
        r = conn.execute(
            "SELECT role FROM club_member WHERE club_id = ? AND user_id = ?",
            (club_id, user_id),
        ).fetchone()
        return r["role"] if r else None


def can_manage_club(club_id: int, user_id: int) -> bool:
    club = get_community(club_id)
    if club is None:
        return False
    if int(club["owner_user_id"] or 0) == user_id:
        return True
    role = get_member_role(club_id, user_id)
    return role in ("owner", "admin")


def list_manageable_clubs(user_id: int) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return list(
            conn.execute(
                """
                SELECT DISTINCT c.* FROM community c
                LEFT JOIN club_member m ON m.club_id = c.id AND m.user_id = ?
                WHERE c.audit = '已通过'
                  AND (c.owner_user_id = ? OR m.role IN ('owner', 'admin'))
                ORDER BY c.id
                """,
                (user_id, user_id),
            ).fetchall()
        )


def list_club_members(club_id: int) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return list(
            conn.execute(
                """
                SELECT m.role, m.muted, u.id AS user_id, u.user_name, u.nick_name, u.avatar
                FROM club_member m
                JOIN app_user u ON u.id = m.user_id
                WHERE m.club_id = ?
                ORDER BY CASE m.role WHEN 'owner' THEN 0 WHEN 'admin' THEN 1 ELSE 2 END, u.id
                """,
                (club_id,),
            ).fetchall()
        )


def update_community_info(
    club_id: int,
    *,
    announcement: str | None = None,
    intro: str | None = None,
) -> None:
    with get_conn() as conn:
        if announcement is not None:
            conn.execute(
                """
                UPDATE community SET announcement = ?, announcement_at = datetime('now','localtime')
                WHERE id = ?
                """,
                (announcement[:1000], club_id),
            )
        if intro is not None:
            conn.execute("UPDATE community SET intro = ? WHERE id = ?", (intro[:500], club_id))


def list_club_activities(club_id: int) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return list(
            conn.execute(
                "SELECT * FROM activity WHERE club_id = ? ORDER BY id DESC",
                (club_id,),
            ).fetchall()
        )


def insert_club_activity(
    club_id: int,
    title: str,
    start_time: str,
    end_time: str,
    location: str,
    tag: str,
    description: str,
    poster_url: str = "",
) -> None:
    with get_conn() as conn:
        conn.execute(
            """
            INSERT INTO activity (club_id, title, start_time, end_time, location, tag, description, audit, poster_url)
            VALUES (?, ?, ?, ?, ?, ?, ?, '已通过', ?)
            """,
            (club_id, title, start_time, end_time, location, tag, description, poster_url),
        )


def delete_club_activity(activity_id: int, club_id: int) -> bool:
    with get_conn() as conn:
        cur = conn.execute(
            "DELETE FROM activity WHERE id = ? AND club_id = ?",
            (activity_id, club_id),
        )
        conn.execute("DELETE FROM activity_enroll WHERE activity_id = ?", (activity_id,))
        return cur.rowcount > 0


def list_activity_enrollments(activity_id: int) -> list[sqlite3.Row]:
    with get_conn() as conn:
        return list(
            conn.execute(
                """
                SELECT e.id, e.created_at, u.nick_name, u.user_name
                FROM activity_enroll e
                JOIN app_user u ON u.id = e.user_id
                WHERE e.activity_id = ?
                ORDER BY e.id DESC
                """,
                (activity_id,),
            ).fetchall()
        )
