# 更新日志 (Changelog)

所有关于 `gemini-cli` 架构的重要变更都将记录在此文件中。

## [1.0.0] - 2026-02-05

### 🚀 重点新增 (The Big Bang)
- **核心架构**: 确立了“根目录(系统) + projects/(业务)”的双层解耦架构。
- **数字雇员系统**: 复刻了 Anthropic `knowledge-work-plugins` 理念，部署了 11 名具备 SOP 和脚本执行能力的专家。
- **认知生命周期**: 实现了从 Task (任务) -> Memory (记忆) -> Standard (标准) 的自动化升华逻辑。
- **自动化工具链**: 
    - `new_project`: 标准化协作单元生成。
    - `git_save` / `git_task`: 深度集成任务背景的 Git 自动化流。
    - `check_health`: 数字雇员环境自愈系统。
- **工程哲学**: 确立了 `THE_CODE_TAO.md` 为全局技术准则。

### 🛡️ 系统安全
- 部署了基于 SSH (443端口) 的 GitHub 自动化推送机制。
- 引入了 `env_guard` 环境安全审计。

### 📦 安装母盘
- 完成了 `gemini-scaffold` 的构建，支持在任何新电脑上“一键复刻”整套认知系统。
