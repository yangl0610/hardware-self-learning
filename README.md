# 硬件自学指南

浙江大学 RM 战队硬件速成教材的 Markdown 与网站版本。24 章、6 个模块，支持中文搜索、公式、代码高亮、明暗主题和移动端阅读。

本网页版已获项目维护者授权公开部署。

在线阅读：https://yangl0610.github.io/hardware-self-learning/

## 本地阅读

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
mkdocs serve -a 127.0.0.1:8000
```

浏览器打开 http://127.0.0.1:8000 。已安装依赖时，只需运行 `.venv/bin/mkdocs serve`。

## 构建静态网站

```sh
.venv/bin/mkdocs build --strict
python3 -m http.server 8000 --directory site --bind 127.0.0.1
```

`site/` 是完整构建产物。公式渲染资源随项目提供，不依赖 CDN。推送到 `main` 后，GitHub Actions 会构建、校验并自动部署到 GitHub Pages；拉取请求仅进行构建校验。

## 内容维护

- `docs/chapters/`：已转换的 24 章 Markdown，可以直接修改并构建。
- `docs/index.md`、`docs/roadmap.md`：首页及阅读路线。
- `mkdocs.yml`：站点配置和章节导航。
- `scripts/convert.py`：从相邻的 `../教材/` 重新生成 Markdown。
- `conversion-report.json`：逐章转换统计。

重新转换需要原教材文件夹与本项目并列，包含 `main.tex` 和 `chapters/*.tex`：

```sh
.venv/bin/python scripts/convert.py
.venv/bin/mkdocs build --strict
```

转换会覆盖 `docs/chapters/`，请先提交手工修改。独立克隆本仓库可直接构建，不需要 LaTeX 源文件或 LaTeX 环境。原文手写章号保留，动态章号按主文档展开；详见网站“编写说明”。

布局参考 [CS 自学指南](https://csdiy.wiki/)，使用 Material for MkDocs。MathJax 的授权声明保留在 `docs/assets/mathjax/LICENSE`。
