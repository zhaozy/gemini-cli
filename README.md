# Gemini Digital Workforce (Project MNEMOSYNE)

> **"Turning LLMs into a persistent, multi-expert digital workforce."**

这是一个基于 Gemini CLI 构建的高级 AI 认知架构。它通过“双层管理模式”和“数字雇员阵列”，将松散的对话转变为严谨、可追溯且具备领域专业知识的工程实践。

## 🌟 核心特性

- **数字雇员阵列 (Workforce)**: 内置 11 名具备独立 SOP (标准作业程序) 和执行脚本的专家（法律、数据、财务、产品等）。
- **认知持久化 (Cognitive Persistence)**: 通过 `.gemini/tasks/` 实现跨会话的记忆恢复，确保 AI 永远记得上一步在哪。
- **核壳分离架构 (Core-Shell)**: 严格区分计算逻辑与 IO 边界，遵循 [编程之道 (THE_CODE_TAO)](docs/THE_CODE_TAO.md)。
- **自动化版本控制**: 集成智能 Git 工作流，自动提取任务记录作为提交信息。
- **防腐化容器**: 所有协作话题强制入仓 (`projects/`)，保持根目录极致整洁。

## 📂 目录结构

```text
.
├── GEMINI.md               # [宪法] 全局最高准则与行为规范
├── docs/                   # [哲学] THE_CODE_TAO 等核心方法论
├── employees/              # [人才库] 11 名数字雇员及其 SOP/脚本
├── projects/               # [车间] 所有协作项目与话题容器
├── .gemini/                # [核心] 全局记忆、任务栈与自动化工具
└── gemini-scaffold/        # [母盘] 环境一键初始化工具包
```

## 🚀 快速开始

### 1. 开启新话题
使用内置指令在 `projects/` 下创建一个标准化的协作单元：
```bash
./.gemini/bin/new_project my_new_task
```

### 2. 雇用新专家
为您的团队增加一名特定领域的专家：
```bash
./.gemini/bin/hire_expert.sh FinanceAnalyst
```

### 3. 保存进度
完成阶段性工作后，一键同步至云端：
```bash
./.gemini/bin/git_save
```

## 📜 协作原则
- **简体中文强制**: 所有对话、注释、文档均使用简体中文。
- **原子交接**: 切换项目前必存档、更焦点、再唤醒。
- **联合办公**: 复杂任务需通过 `Co-working Protocol` 调动多名专家协作。
