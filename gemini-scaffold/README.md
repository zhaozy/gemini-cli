# Gemini Cognitive Scaffold (Project MNEMOSYNE)

这是一个**“AI 认知脚手架”**，用于在任何新环境中快速复刻一套具备**长期记忆**与**严格工程规范**的 Gemini CLI 工作流。

## 核心组件

1.  **Constitutional AI (`GEMINI.md`)**: 定义了 AI 的行为准则（核壳分离、简体中文、自动化原则）。
2.  **Cognition Persistence (`.gemini/tasks/`)**: 预置了 AI 的记忆存储结构，使其能记住你的偏好。
3.  **Automation (`install.sh`)**: 一键部署环境。

## 🤖 数字雇员 (Digital Workforce)

本脚手架复刻了 Anthropic `knowledge-work-plugins` 的设计理念，将 AI 代理从通才转化为领域专家。

### 如何“雇用”新专家
使用内置脚本一键生成专家框架：
```bash
.gemini/bin/new_employee FinanceAnalyst
```

### 专家目录结构
每个专家都拥有的三要素：
- **`manifest.json`**: 定义专家的身份与边界。
- **`commands.json`**: 定义专家可用的 Slash 指令。
- **`SOPs/`**: 存放专家的执行逻辑 (Markdown 格式)，AI 会在激活该专家时自动遵循这些 SOP。

## 🚀 快速开始 (迁移指南)

### 1. 初始化新环境
将本文件夹 (`gemini-scaffold`) 复制到新电脑的项目根目录，然后运行：

```bash
./gemini-scaffold/install.sh
```

**脚本将自动执行：**
- 检测并安装 `uv` (Python 包管理器)。
- 建立根目录的 `GEMINI.md` (宪法)。
- 建立 `.gemini/tasks/` (全局记忆)。
- 部署 `employees/` (数字雇员集群)。

### 2. 创建新项目
安装完成后，使用内置命令快速创建符合“核壳分离”标准的子项目：

```bash
.gemini/bin/new_project order_analysis_v2
```

这将自动生成：
- 项目目录 `order_analysis_v2/`
- 项目级宪法 `GEMINI.md`
- 认知锚点目录 `.gemini/tasks/`

### 3. 唤醒 AI
在 CLI 中输入以下指令，AI 将立即读取配置并进入工作状态：

> "按照根目录 GEMINI.md 的协议，初始化当前环境。"

## 目录结构说明

```text
root/
├── GEMINI.md           # [核心] 全局宪法
├── .gemini/
│   └── tasks/          # [记忆] 全局任务与偏好
├── employees/          # [大脑] 数字雇员及其 SOP
└── projects/           # [车间] 协作话题容器
```
