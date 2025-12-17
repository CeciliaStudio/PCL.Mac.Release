# PCL.Mac.Release

PCL.Mac.Refactor 自动发版程序，支持生成更新日志并发布到 GitHub Releases / Gitee Releases。

## 环境要求

- macOS 与任何带有 `open` 命令的 Linux
- 支持 URL Scheme 的 Motrix（用于自动下载）

## 配置

请在根目录添加 `.env` 文件：
```properties name=.env
GITHUB_TOKEN={对目标仓库有读写权限的 Personal Access Token}
GITHUB_REPOSITORY={目标仓库}
```