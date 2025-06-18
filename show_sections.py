import os
from pathlib import Path

# 🔧 设置 Hugo 项目根目录（绝对路径）
PROJECT_ROOT = Path(r"D:\desktop\ChenGou-zheng.github.io\hugo")
LAYOUTS_DIR = PROJECT_ROOT / "layouts"
DEFAULT_LAYOUT_DIR = LAYOUTS_DIR / "_default"

def ensure_dir(path):
    """确保目录存在"""
    path.mkdir(parents=True, exist_ok=True)

def get_search_box():
    return '''<div class="mb4">
  <input type="text" id="search-input" placeholder="🔍 输入关键词搜索文章..." class="pa2 w-100 ba b--light-silver br2">
</div>
<ul id="results-container" class="list pl0 mb4"></ul>'''

def get_card_list():
    return '''<div class="flex flex-wrap justify-center">
  {{ range .Pages }}
    <div class="w-third-l w-50 pv3 ph2">
      <div class="ba b--light-silver br2 bg-white pa3 shadow-1 hover-bg-near-white">
        <h2 class="f5 f4-ns fw6 lh-title mv0">
          <a href="{{ .RelPermalink }}" class="link blue hover-dark-red">{{ .Title }}</a>
        </h2>
        <p class="f6 f5-ns measure lh-copy mt2 mb0">
          {{ if .Description }}
            {{ .Description | truncate 80 }}
          {{ else }}
            {{ .Summary | truncate 80 }}
          {{ end }}
        </p>
        <time class="f7 ttu tracked gray db mt2">
          {{ .Date.Format "Jan 2, 2006" }}
        </time>
      </div>
    </div>
  {{ end }}
</div>'''

def get_pagination():
    return '''<nav class="dt w-100 bt bb tc mw8 center">
  {{ template "_internal/pagination.html" . }}
</nav>'''

def get_theme_toggle_button():
    return '''<button id="theme-toggle" class="mt4 pa2 ba b--light-silver bg-white br2 pointer">🌙 切换主题</button>'''

def get_search_script():
    return '''<script src="https://cdn.jsdelivr.net/npm/simple-jekyll-search@latest/dest/simple-jekyll-search.min.js"></script> 
<script>
  window.simpleJekyllSearch = new SimpleJekyllSearch({
    searchInput: document.getElementById('search-input'),
    resultsContainer: document.getElementById('results-container'),
    jsonFile: '/search.json',
    searchResultTemplate: '<li><a href="{url}" class="link blue hover-dark-red db pv2">{title}</a></li>',
    noResultsText: '❌ 没有找到相关文章',
    limit: 10,
    fuzzy: false
  })
</script>'''

def get_theme_toggle_script():
    return '''<script>
  const toggleButton = document.getElementById("theme-toggle");

  function setTheme(themeName) {
    document.documentElement.setAttribute("data-theme", themeName);
    localStorage.setItem("theme", themeName);
  }

  toggleButton.addEventListener("click", () => {
    let currentTheme = document.documentElement.getAttribute("data-theme");
    let nextTheme = currentTheme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
  });

  (function () {
    const savedTheme = localStorage.getItem("theme") || (window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
    setTheme(savedTheme);
  })();
</script>'''

def create_default_list_template():
    print("📄 创建通用 list.html 模板...")
    list_file = DEFAULT_LAYOUT_DIR / "list.html"
    content = '''{{ define "main" }}
  <div class="pa3 pa4-ns">
    <h1 class="f2 lh-solid mv3">{{ .Title }}</h1>

    {{ template "search-box" . }}
    {{ template "card-list" . }}
    {{ template "pagination" . }}
    {{ template "theme-toggle-button" . }}

  </div>

  {{ template "search-script" . }}
  {{ template "theme-toggle-script" . }}
{{ end }}

{{ define "search-box" }}''' + get_search_box() + '''{{ end }}

{{ define "card-list" }}''' + get_card_list() + '''{{ end }}

{{ define "pagination" }}''' + get_pagination() + '''{{ end }}

{{ define "theme-toggle-button" }}''' + get_theme_toggle_button() + '''{{ end }}

{{ define "search-script" }}''' + get_search_script() + '''{{ end }}

{{ define "theme-toggle-script" }}''' + get_theme_toggle_script() + '''{{ end }}'''

    with open(list_file, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✅ 已写入 {list_file}")

def main():
    print(f"📁 当前工作目录: {os.getcwd()}")
    print(f"🔧 将操作目标目录: {PROJECT_ROOT}")

    ensure_dir(DEFAULT_LAYOUT_DIR)
    create_default_list_template()

    print("\n✨ 模板同步完成！现在你的每个 section 页面都会显示卡片式文章列表，并带有搜索栏和主题切换按钮。")

if __name__ == "__main__":
    main()