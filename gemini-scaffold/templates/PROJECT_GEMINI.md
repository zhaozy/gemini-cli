# Project Context: {{PROJECT_NAME}}

本文件定义了 `{{PROJECT_NAME}}` 项目的业务逻辑、技术架构与标准作业程序 (SOP)。

## 1. 项目定位
[在此描述项目的核心目标与业务价值]

## 2. 核心架构
遵循全局“核壳分离”原则：
- **Core**: 业务逻辑核心。
- **Shell**: 数据加载与报告生成。

## 3. 认知持久化 (Persistence of Cognition)
项目任务、决策过程与长期记忆存储于以下位置：
- `.gemini/tasks/current_task.md`: 当前活跃任务与子进度。
- `.gemini/tasks/memory.md`: 项目级长期记忆（业务洞察、技术债）。
- `.gemini/tasks/walkthrough.md`: 关键决策记录。

## 4. 运行指令
```bash
# 示例
uv run python -m {{PROJECT_NAME}}.main
```

## 5. 数据契约
所有输出报告必须为标准 JSON 或 Markdown。
