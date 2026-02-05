# 全局长期记忆 (Global Memory)

## 用户偏好
- **语言**：简体中文 (强制)。**严格执行**：除文件名、代码关键字外，避免在文本中使用英文术语对照；**所有思维推理过程 (Thought) 也必须使用纯中文**。
- **输出规范**：所有的分析类工作，最终输出必须是 `reports/` 目录下的 Markdown 文档及配套的 HTML 渲染报告。
- **报告准则**：遵循 **DeepSearch 标准**。
    1. **结构**：先数据 (Data) -> 后定义 (Definition) -> 再解读 (Observation)。
    2. **客观**：解读必须严格基于数据现象，**禁止**无依据的猜测（如用户动机、生活场景等）。
    3. **精细**：粒度必须下钻到具体特征。
- **技术栈**：uv, ruff, pytest, pandera。
- **风格**：核壳分离 (Core-Shell)，显式契约 (Explicit Contracts)。

## 核心职责与自动化原则
- **反向同步原则 (Reverse Syncing)**：活跃工程升级需同步至 `gemini-scaffold/`。
- **强制项目入仓 (Project Containerization)**：**所有**业务分析项目必须位于 `projects/` 目录下。Agent 在发起新任务时应主动引导或自动在 `projects/` 下创建目录。

## 工作区状态

- **上次活跃目录**：`order_analysis/`

- **关键事件**：

    - 2026-01-22 在 `GEMINI.md` 中引入“认知生命周期”（沉淀/升华）。

    - 2026-02-05 完成全局配置对齐，补全 `data_analysis` 认知锚点，规范化子项目 `GEMINI.md`。
    - 2026-02-05 完成“业务归位”：将所有业务项目迁移至 `projects/` 目录，退役旧版 `_skills/`。
