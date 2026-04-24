# CynosurePalace - 个人知识库与博客网站

本项目是由 Obsidian 驱动，基于 **Hugo (Extended) + Hugo Book 主题** 以及 **Pagefind (静态搜索)** 搭建的个人知识库与博客系统。

网站通过定制化实现了类似 Material for MkDocs / Lotus Docs 的高密度菜单样式、卡片聚合首页和原生的全站离线搜索功能。

---

## 🚀 核心工作流：如何打通 Obsidian 与网站

本项目的一大特色是实现了**“本地记笔记，云端全自动发布”**的无缝工作流。**文章的输入永远在你的本地 Obsidian 仓库（CynosurePalace）中进行，而不是直接修改这个代码仓库。**

### 1. 写作与图片管理 (在 Obsidian 中)
1. 在本地的 Obsidian 仓库中正常写作、记录。
2. 支持图片、PDF等多媒体资源插入：
  - 通用静态资源放在 Obsidian 根目录下的 `static` 文件夹。
  - 文内图片引用（如 Obsidian 附件）放在 Obsidian 根目录下的 `attachments` 文件夹。
3. 当你觉得某篇文章写好了、准备对外发布时，只需要在该文章的 Markdown 头部（Front Matter）加上：
   ```yaml
   ---
   publish: true
   date: 2026-04-12 15:30:00  # 我们对奇特或不规范的时间（如秒数>59）做了兼容保护
   ---
   ```

### 2. 一键发布 (在 VS Code 或终端中)
在本项目根目录下，只需运行一行命令：
```bash
uv run .\one_key_publish.py
```
这根 Python 脚本（我们整合后的终极同步工具）会自动完成以下工作：
* **清空重建：** 清理 `hugo/content` 和对应资源。
* **文件同步：** 扫描你 Obsidian 仓库中的所有 Markdown，筛选出带有 `publish: true` 的文章。
* **格式转换：** 修正含有格式错误的时间字段（转为标准字符串），并将 YAML 头统一强制转为 Hugo 最好解析的 TOML 格式 (+08:00 时区保护)。
* **资源同步：** 将 Obsidian 里的 `static` 同步到 `hugo/static/`，并将 `attachments` 同步到 `hugo/static/attachments/`，避免图片引用失效。
* **Git 发布：** 自动执行 `git add`, `git commit` 以及 `git push` 到 GitHub，触发 GitHub Actions 编译部署上线。

*(注：旧版的 `publish_hugo.py`、`menu.py`、`git_sync.py` 已完全废弃并被此脚本取代。)*

---

## 📂 文章是如何归类的？

现在的栏目分类是完全自动化的：不需要你手动修改菜单配置！
1. **文件夹即分类：** Hugo Book 主题极度智能，只要你的文章在 Obsidian 里按文件夹存放（例如 `Lectures`，`Summaries`，`Tools`），同步到 Hugo 后，侧边栏会自动生成对应的层级目录。
2. **不再需要修改 `hugo.toml`：** 你不再需要手动写菜单区块的配置。

---

## 🎨 网站现在的样式与结构在哪里看？我们如何定制页面的？

本框架区分了**“内容”**和**“架构骨架”**。内容虽然由 Obsidian 管理，但是所有的“皮肤、插件、样式”都由本代码库直接掌控：

* **核心主题配置：** 位于 `hugo/hugo.toml`。在这里可以修改网站标题、个人签名、社交链接 (GitHub, QQ, Email) 等，并关闭了 Book 主题原生的搜索（为了让位于 Pagefind）。
* **高密度菜单与自定义 CSS：** 位于 `hugo/assets/_custom.scss`。我们在这里使用了 SCSS 覆盖了默认主题变量，加入了圆角悬浮、深色模式适配和高密度的侧边栏字体。
* **首页卡片聚合看板：** 位于 `hugo/layouts/index.html` (以及 `hugo/layouts/home/list.html` 等重写模板)。在这里我们用 HTML 徒手画了 Material 风格的快速导航卡片和由 Hugo Data 提取的“最近更新”流。
* **PDF 预览 Shortcode 组件：** 位于 `hugo/layouts/shortcodes/pdf.html`。可以让你在 Markdown 里面用 `{{< pdf src="..." >}}` 自动渲染内置 PDF 查阅框。
* **独立的搜索前端注入：** 位于 `hugo/layouts/_partials/docs/search.html` 和 `inject/head.html`，把 Pagefind 的 UI 挂载到我们首页。

---

## 🗂️ 各个代码文件的管理与职责

如果需要对代码文件进行调试或二开，请参考以下指南：

* **`/hugo/`**：这是主要网站工程目录。
  * `content/`：🚨 **不要在此手动修改内容！** 它是被 `one_key_publish.py` 自动化管理的，任何手动修改都会在下次同步时被覆写。
  * `static/`：被同步的资源文件目录（如图片、PDF），还包括不需要同步的常驻资源如默认头像 `avatarMe.png`。
  * `themes/book/`：原版 Hugo Book 主题文件，不要直接改这里的代码。
  * `layouts/` 和 `assets/`：这是我们覆写原生主题样式的圣地（也是你二开UI的核心区域）。
* **`one_key_publish.py`**：当前整个系统的“护城河”兼发动机，控制了从本地笔记库到 Git 仓库的所有工作流逻辑。
* **`.github/workflows/deploy.yml`**：在 GitHub 云端服务器编译并测试我们站点的脚本（配置有 Node.js 24、Hugo latest 及 `npx pagefind`）。
* **`/mkdocs/`**：这是一个 2025 年 7 月份构建的历史废弃的 MkDocs 版本遗留，可以直接删除。

### 如何在本地预览修改？
如果你改了某个 CSS 或排版，想要预览效果，请在终端执行：
```bash
cd hugo
hugo server -D
```
然后在浏览器中打开 `http://localhost:1313` 即可实时查阅。