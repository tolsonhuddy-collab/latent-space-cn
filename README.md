# Latent Space 中文精读

把一期科学长谈，读成一部中文长文。

本项目为 **Latent Space**（主要为 Science 子频道）非官方中文精读站点，基于官方公开英文逐字稿进行结构重排、中文长文改写与编辑校订。

## 在线阅读与订阅

- **GitHub Pages 站点**：https://tolsonhuddy-collab.github.io/latent-space-cn/
- **全文 Atom 订阅**：https://tolsonhuddy-collab.github.io/latent-space-cn/feed.xml
- **播客分订阅源**：https://tolsonhuddy-collab.github.io/latent-space-cn/podcasts/latent-space/feed.xml
- **OPML 订阅清单**：https://tolsonhuddy-collab.github.io/latent-space-cn/latent-space-rss.opml

## 目录与进度

- **节目目录**：10 期（Latent Space Science 子频道）
- **已定稿发布**：2 篇（`001` Leash Bio、`004` Chai Discovery），其余节目持续更新中。

## 本地构建与测试

本项目仅依赖 Python 3.9+ 标准库，无需 Node.js、前端打包器或数据库：

```bash
# 运行单元测试
make test

# 查看目录与发布状态
make status

# 构建公开静态站点到 dist/
make published
```

## 版权与免责说明

- 原播客节目、音频与逐字稿版权归 Latent Space 及原嘉宾所有。
- 本站中文精读为基于公开逐字稿编译的衍生作品，不构成科研、医疗或投资建议。
