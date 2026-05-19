# 校园兴趣社群 · Streamlit 轻量版说明

## 1. 项目定位

本目录 **`campus-streamlit`** 是与现有 **RuoYi + `ruoyi-campus`（Spring Boot）** 平行的 **Python + Streamlit** 演示端，只覆盖校园社群核心链路：**师生登录 / 浏览社群 / 发帖与评论 / 浏览活动 / 简单管理审核**。不包含若依自带的部门、岗位、代码生成、定时任务、Redis、JWT 双端等模块，避免体量过大。

Java 后端与 Vue 前端仍保留在仓库其它目录；Streamlit 版适合快速演示、无服务器托管或给非技术同事试用。

**界面说明**：Streamlit **不能**直接跑 `campus-community-web` 的 Vue 组件；当前通过 **`campus_theme.py` 注入 CSS**（色板、字体、玻璃拟态、Hero、杂志风卡片等）与 **`ui.py` 顶栏**（首页 / 社群 / 活动 / 校园助手 / 运营）尽量对齐师生端视觉与信息架构。交互细节仍受 Streamlit 控件限制，与 Vue 不会 1:1 像素一致。

## 2. SQLite 能否放在 Streamlit Community Cloud 上？

**可以运行，但不适合把 SQLite 当作长期、可靠的线上主库。**

| 场景 | 说明 |
|------|------|
| **本地开发** | SQLite 文件放在本机 `data/app.db`，完全正常。 |
| **Streamlit Community Cloud** | 应用跑在容器中，**磁盘多为临时或不可预期持久**；应用休眠、重建、发布新版本后，**库文件可能丢失或被重置**。同一时刻多副本时也不适合共写单个 SQLite 文件。 |
| **建议** | 若需要「云上数据长期保存」，请使用 **托管 PostgreSQL**（如 Neon、Supabase、Railway 免费档）或 **Turso（libSQL）** 等，通过环境变量连接；本项目的存储层集中在 `db.py`，后续替换连接方式即可。 |

结论：**没有自己的服务器时，仍可以把应用部署到 Streamlit Cloud**；若只接受「演示数据可丢」，用内置 SQLite 即可；若需要持久化，请增加外置数据库（无需自备整机，多数有免费层）。

## 3. 目录与入口

| 路径 | 作用 |
|------|------|
| `app.py` | Streamlit 主入口（部署时指定此文件）。 |
| `db.py` | SQLite 建表、连接、演示数据种子。 |
| `auth.py` | 登录态（`st.session_state`）与密码校验。 |
| `campus_theme.py` | 对齐 `campus-community-web` 的全局样式（`global.css` 色板与组件风格）。 |
| `ui.py` | 顶栏导航、页脚、`st.sidebar` 上的演示说明与运营入口。 |
| `pages/` | 多页面：社群、活动、运营审核、校园助手（占位）。 |
| `requirements.txt` | Python 依赖。 |
| `.streamlit/config.toml` | 浅色主题、`showSidebarNavigation=false`（隐藏默认侧栏多页菜单，改用顶栏）。 |

数据库文件默认：`campus-streamlit/data/app.db`（已在 `.gitignore` 中忽略，避免把个人数据提交进 Git）。**若拉取代码更新后无法登录，删除该文件可让程序按新种子重建库。**

## 4. 启动步骤（本地）

### 4.1 环境要求

| 项目 | 要求 |
|------|------|
| Python | **3.10+**（推荐 3.10 / 3.11） |
| 依赖 | 仅需本目录 `requirements.txt`（Streamlit + bcrypt） |
| 数据库 | **不需要** MySQL / Redis；**不需要** 单独运行 `db.py` |
| Java / Vue | 跑 Streamlit 时 **不必** 启动若依后端或 `campus-community-web` |

### 4.2 第一次在本机启动（完整流程）

在 PowerShell 或 CMD 中执行（路径按你本机仓库位置修改）：

```powershell
# 1. 进入 Streamlit 子项目目录
cd d:\workAAA\ruoyi\campusCommunity\campus-streamlit

# 2.（推荐）创建并启用虚拟环境
py -3 -m venv .venv
.\.venv\Scripts\activate

# 3. 安装依赖（国内网络慢可用清华镜像，见下方）
py -3 -m pip install -r requirements.txt

# 4. 启动应用（主入口 app.py）
py -3 -m streamlit run app.py
```

终端出现类似下面一行即表示成功：

```text
Local URL: http://localhost:8501
```

用浏览器打开 **http://localhost:8501** 即可。

**国内 pip 较慢时**（可选）：

```powershell
py -3 -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple --default-timeout=120
```

### 4.3 第二次及以后（日常启动）

虚拟环境已建好时，只需三步：

```powershell
cd d:\workAAA\ruoyi\campusCommunity\campus-streamlit
.\.venv\Scripts\activate
py -3 -m streamlit run app.py
```

### 4.4 数据库会自动初始化

- 首次启动时，程序通过 `bootstrap.py` → `db.init_db()` 自动创建 **`data/app.db`** 并写入演示账号。
- **不要** 手动执行 `python db.py`。
- 若登录异常或想**换一批更丰富的演示数据**：关闭 Streamlit，删除 `data\app.db`，再重新执行 `streamlit run app.py`。
- 若只是更新了代码里的种子数据：同样**重启 Streamlit**（或删库），启动时会自动补全（社群少于 10 个时会写入更多社群/活动/动态，图片使用 picsum.photos）。

### 4.5 启动后建议自测（演示账号）

| 账号 | 密码 | 可测功能 |
|------|------|----------|
| `stu001` | `admin123` | 首页 → 登录 → 社群加入/发帖 → 活动报名 → **个人中心** → **社群与活动管理** |
| `admin` | `admin123` | 顶栏 **运营** → 审核「待审摄影社」 |

### 4.6 常见问题（本地）

| 现象 | 处理 |
|------|------|
| 提示找不到 `streamlit` | 确认已 `activate` 虚拟环境，并重新 `pip install -r requirements.txt` |
| 端口 8501 被占用 | 换端口：`py -3 -m streamlit run app.py --server.port 8502` |
| 页面满屏 CSS 文字 | 拉取最新代码，确认 `streamlit>=1.40`，浏览器 **Ctrl+F5** 强刷 |
| 停止服务 | 在运行 Streamlit 的终端按 **Ctrl+C** |

**日志**：本地看启动 Streamlit 的那个终端窗口；线上看 Streamlit Cloud 的 **Logs**。

## 5. Streamlit Community Cloud（当前方案：Cloud + 可访问 URL + SQLite）

你已选择 **只用 Streamlit Cloud** 上线，数据用 **SQLite**，界面在 **`campus-streamlit`** 里用 Streamlit + CSS 尽量贴近原 Vue 师生端（见第 1 节说明）。后续可在本目录继续改 `campus_theme.py` / `ui.py` / 各页做「打磨」。

### 5.1 部署步骤

1. 将本仓库推送到 **GitHub**（或 Streamlit Cloud 支持的 Git 托管）。
2. 打开 [Streamlit Community Cloud](https://streamlit.io/cloud)，用 GitHub 登录，**New app**。
3. **Repository** 选本仓库；**Main file path** 填：`campus-streamlit/app.py`（子目录部署时必须填对）。
4. **Branch** 选主分支，**Deploy**。
5. 部署完成后在 Cloud 控制台打开 **Logs**，确认无依赖或启动错误；国内拉依赖慢时可在本地用镜像装好锁版本后再推（见第 4 节）。

无需自备服务器；SQLite 在云端的行为见 **第 2 节**。若以后要外置库，可在 **App settings → Secrets** 配置变量，并在 `db.py` 中读取 `st.secrets`（当前未接）。

### 5.2 「域名」在 Streamlit Cloud 上通常指什么

- **默认可用地址**：`https://<子域名>.streamlit.app`（部署后 Cloud 会分配；可在 **App settings → General → App URL** 查看或修改）。
- **自定义子域名**：同一页面将子域名改为 **6～63 个字符** 的可用名称，保存后即固定为 `https://你的名称.streamlit.app`。说明见官方 [App settings](https://docs.streamlit.io/deploy/streamlit-community-cloud/manage-your-app/app-settings) 中 *View or change your app's URL*。
- **完全使用自己购买的顶级域（如 `app.xxx.edu.cn`）**：Community Cloud 常见形态仍是 **`*.streamlit.app`**；若必须自有域，需查阅你当前 Workspace 套餐是否提供 **自定义域 / CNAME**（随产品更新而变化），或在外部用 **Cloudflare 等做反代**（需处理 Streamlit 的 WebSocket 等，维护成本较高）。**多数教学/演示场景**，用 **`你的项目名.streamlit.app`** 即满足「有固定链接、可分享、可收藏」。

### 5.3 上线后「打磨」建议（可选）

| 方向 | 可改位置 |
|------|----------|
| 颜色、圆角、顶栏、卡片 | `campus_theme.py`（对照 `campus-community-web/src/styles/global.css`） |
| 导航文案、登录区、页脚 | `ui.py` |
| 首页模块顺序、文案、示例图 | `app.py` |
| 社群/活动/运营流程与字段 | `pages/*.py` + `db.py` |
| 依赖与 Python 版本 | `requirements.txt` + Cloud **Advanced** 里 Python 版本 |

若某页样式被 Streamlit 升级打断，优先在 `campus_theme.py` 里用 `[data-testid="..."]` 做小范围覆盖（以浏览器开发者工具为准）。

## 6. 业务动线（登录 → 首页 → 功能页）

| 步骤 | 页面 | 说明 |
|------|------|------|
| 1 | `pages/0_登录.py` | 未登录时从顶栏「登录」或需权限操作进入；成功后跳回 **首页** 或登录前页面。 |
| 2 | `app.py`（首页） | 未登录可浏览社群/活动摘要；登录后显示欢迎条。 |
| 3 | `pages/1_社群广场.py` | 加入社群、评论、发帖（后两者需已加入）。 |
| 4 | `pages/7_发布动态.py` | 需 **师生** 登录且已加入社群。 |
| 5 | `pages/2_活动报名.py` | 浏览公开；**报名** 需登录。 |
| 6 | `pages/6_个人中心.py` | 资料与简介、我加入的社群、报名记录；**主理人**可进管理页。 |
| 7 | `pages/8_社群与活动管理.py` | **社群管理**（公告/简介）+ **活动管理**（新建/删除、报名名单）；需 owner/admin。 |
| 8 | `pages/3_运营审核.py` | 平台运营：审核待通过社群（`admin`）。 |
| 9 | `pages/5_注册.py` | 注册后自动登录并进首页。 |

演示账号见下表。

## 7. 演示账号（与 README-校园模块 对齐思路）

| 用户名 | 密码 | 说明 |
|--------|------|------|
| `stu001` | `admin123` | 师生演示（哈希由本项目的 Python bcrypt 写入，与 MySQL 里 `$2a$10$7JB...` 不必相同）。 |
| `admin` | `admin123` | 简易管理台登录（仅存于本 Streamlit 库，**非**若依 `sys_user`）。 |

管理台仅用于演示「待审核社群」列表与通过/拒绝，不对接若依权限字。

## 8. 与 Java 校园模块的差异

- 未实现：支付订单、会员方案、首页轮播维护、SSE、文件上传、若依运营后台全量接口等。
- 数据 **不** 与 MySQL 自动同步；若要对齐，需自行导出/迁移或改连同一逻辑库。

## 9. 后续可扩展方向（按需再做）

- Secrets + 外置 PostgreSQL，替换 `sqlite3` 连接层。  
- OAuth / 学校统一认证。  
- 与现有 `POST /campus/auth/login` 互通（Streamlit 作为纯前端，请求 Java API）。

## 10. 常见问题

### 页面上出现一大段 CSS 文字、样式不生效

**原因**：新版 Streamlit 对 `st.markdown(..., unsafe_allow_html=True)` 会做 **HTML 消毒**，`<style>`、`<link>` 等常被剥离，只剩 CSS 内容被当成普通文本渲染。

**处理**：本项目已改为使用 **`st.html()`** 注入样式（见 `campus_theme.py` 中 `inject_campus_styles`）。请拉取最新代码并确认 `requirements.txt` 中 **Streamlit ≥ 1.40**；重新部署 Cloud 后硬刷新浏览器（Ctrl+F5）。

---

维护说明：若仓库根目录 `README-校园模块.md` 中的 SQL 文件名或路径有变更，请以该文件为准更新本地 Java 环境；本文档仅描述 **Streamlit 子项目**。
